"""
FORENZA 3D Spatial Crime Scene Reconstruction & Interactive Juror Visualizer Engine (Module 30).

Research Reference: Pillar 6 Research §5.1, §5.2 (Courtroom Interactive 3D Evidence Presenter).
Implements:
  - SE(3) Special Euclidean Group Coordinate Transformation (§5.1)
      X_scene = R(phi, theta, psi) · X_local + T
      R = R_z(psi) · R_y(theta) · R_x(phi)      [Euler ZYX convention]
  - Multi-Sensor Registration: Point-to-Plane Residual Minimization (§5.1)
      min_{R,T} sum_k || n_k^T · (R·p_k + T - q_k) ||^2
  - Sensor Calibration Precision Table (§5.1):
      LiDAR: ±0.002 m | BPA: ±0.012 m | Ballistics: ±0.005 m | DNA: ±0.008 m
  - 95% Probabilistic Volumetric Ellipsoid (§5.2):
      (X - mu)^T · Sigma^-1 · (X - mu) <= chi2_{3,0.95} ≈ 7.815
      Eigendecomposition: a = sqrt(lambda_1 * 7.815), b = sqrt(lambda_2 * 7.815),
                          c = sqrt(lambda_3 * 7.815)
      Volume: V = (4/3) * pi * a * b * c

Ground-Truth VECTOR_30_SPATIAL_D:
  Sigma = diag(sigma^2, sigma^2, sigma^2), sigma=1.0 m
  => a = b = c = sqrt(1.0 * 7.815) = 2.7955 m
  => V = (4/3) * pi * 2.7955^3 ≈ 91.588 m^3
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

# ── Research Constants (verbatim from §5.1, §5.2) ─────────────────────────────
# Chi-squared quantile for 3 DOF at 95% confidence: chi2_{3, 0.95} ≈ 7.815
CHI2_3_95: float = 7.815

# Sensor calibration target global precision (m) — from §5.1 Table
SENSOR_PRECISION_M: Dict[str, float] = {
    "LIDAR":      0.002,   # Terrestrial LiDAR Scanning
    "BPA":        0.012,   # BPA Trajectory Flight Origin (ellipsoid radius)
    "BALLISTICS": 0.005,   # Ballistics Terminal Trajectory
    "DNA":        0.008,   # Suspect / Biological Landmark Coordinates
}


# ── Data Classes ───────────────────────────────────────────────────────────────
@dataclass
class SE3TransformResult:
    """Result of a single SE(3) coordinate transformation."""
    x_local: Tuple[float, float, float]
    x_scene: Tuple[float, float, float]
    rotation_matrix: List[List[float]]       # 3×3 R matrix (row-major)
    translation_vector: Tuple[float, float, float]
    roll_phi_rad: float
    pitch_theta_rad: float
    yaw_psi_rad: float
    orthogonality_residual: float            # ||R·R^T - I||_F (must be < 1e-10)
    det_residual: float                      # |det(R) - 1.0| (must be < 1e-10)


@dataclass
class ConfidenceEllipsoid:
    """95% volumetric confidence ellipsoid around a spatial centroid (§5.2)."""
    centroid_mu: Tuple[float, float, float]
    semi_axis_a: float    # sqrt(lambda_1 * CHI2_3_95) [m]
    semi_axis_b: float    # sqrt(lambda_2 * CHI2_3_95) [m]
    semi_axis_c: float    # sqrt(lambda_3 * CHI2_3_95) [m]
    volume_m3: float      # V = (4/3)*pi*a*b*c [m^3]
    eigenvectors: List[List[float]]          # 3×3 V matrix (column = eigenvector)
    eigenvalues: Tuple[float, float, float]  # lambda_1 >= lambda_2 >= lambda_3 > 0
    chi2_threshold: float = CHI2_3_95


@dataclass
class SensorPoint:
    """A registered evidence point with sensor type and precision metadata."""
    sensor_type: str                          # "LIDAR" | "BPA" | "BALLISTICS" | "DNA"
    label: str                                # e.g., "EVID-BLOOD-101"
    x_scene: Tuple[float, float, float]       # Transformed global coordinates [m]
    precision_m: float                        # Target global precision from §5.1 Table
    ellipsoid: Optional[ConfidenceEllipsoid] = None


@dataclass
class ReconstructedScene:
    """Complete multi-sensor crime scene reconstruction output."""
    scene_id: str
    sensor_points: List[SensorPoint]
    bpa_origins: List[Tuple[float, float, float]]        # 3D area-of-origin [m]
    ballistics_vectors: List[Dict[str, Tuple[float, float, float]]]  # {origin, direction}
    dna_landmarks: List[Tuple[float, float, float]]      # Biological sample positions [m]
    scene_centroid: Tuple[float, float, float]
    scene_bounding_box: Dict[str, Tuple[float, float, float]]  # {min, max}
    point_to_plane_residual: float
    n_sensors: int


# ── SE(3) Rotation Matrix Builders (verbatim from §5.1) ──────────────────────
def _rx(phi_rad: float) -> np.ndarray:
    """Roll rotation matrix R_x(phi) around X-axis."""
    c, s = math.cos(phi_rad), math.sin(phi_rad)
    return np.array([
        [1.0,  0.0, 0.0],
        [0.0,    c,  -s],
        [0.0,    s,   c],
    ], dtype=float)


def _ry(theta_rad: float) -> np.ndarray:
    """Pitch rotation matrix R_y(theta) around Y-axis."""
    c, s = math.cos(theta_rad), math.sin(theta_rad)
    return np.array([
        [ c,  0.0,   s],
        [0.0, 1.0, 0.0],
        [-s,  0.0,   c],
    ], dtype=float)


def _rz(psi_rad: float) -> np.ndarray:
    """Yaw rotation matrix R_z(psi) around Z-axis."""
    c, s = math.cos(psi_rad), math.sin(psi_rad)
    return np.array([
        [ c,  -s, 0.0],
        [ s,   c, 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=float)


def build_rotation_matrix(roll_phi_rad: float, pitch_theta_rad: float,
                           yaw_psi_rad: float) -> np.ndarray:
    """
    Compose Euler ZYX rotation matrix: R = R_z(psi) * R_y(theta) * R_x(phi).

    Research: §5.1 — R = R_z(psi) R_y(theta) R_x(phi)
    """
    return _rz(yaw_psi_rad) @ _ry(pitch_theta_rad) @ _rx(roll_phi_rad)


# ── Core SE(3) Transformation Engine ─────────────────────────────────────────
class SpatialReconstructionEngine:
    """
    FORENZA 3D Spatial Reconstruction Engine (Module 30).

    Implements SE(3) coordinate registration, 95% confidence ellipsoid
    rendering, and multi-sensor crime scene fusion per Research §5.1–§5.2.
    """

    # ── SE(3) Transformation ─────────────────────────────────────────────────
    @staticmethod
    def transform_se3(
        x_local: Tuple[float, float, float],
        roll_phi_rad: float = 0.0,
        pitch_theta_rad: float = 0.0,
        yaw_psi_rad: float = 0.0,
        translation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> SE3TransformResult:
        """
        Apply SE(3) rigid-body transformation to a 3D point.

        X_scene = R(phi, theta, psi) · X_local + T
        R = R_z(psi) · R_y(theta) · R_x(phi)   [Research §5.1]

        Args:
            x_local:          Input point in local sensor coordinates (x, y, z) [m].
            roll_phi_rad:     Roll angle φ around X-axis [radians].
            pitch_theta_rad:  Pitch angle θ around Y-axis [radians].
            yaw_psi_rad:      Yaw angle ψ around Z-axis [radians].
            translation:      Translation vector T = (tx, ty, tz) [m].

        Returns:
            SE3TransformResult with scene coordinates and rotation matrix.
        """
        R = build_rotation_matrix(roll_phi_rad, pitch_theta_rad, yaw_psi_rad)
        T = np.array(translation, dtype=float)
        p = np.array(x_local, dtype=float)

        x_scene = R @ p + T

        # Orthogonality invariant: ||R·R^T - I||_F < 1e-10
        orth_residual = float(np.linalg.norm(R @ R.T - np.eye(3)))
        det_residual = abs(np.linalg.det(R) - 1.0)

        return SE3TransformResult(
            x_local=tuple(p),
            x_scene=tuple(x_scene),
            rotation_matrix=R.tolist(),
            translation_vector=tuple(T),
            roll_phi_rad=roll_phi_rad,
            pitch_theta_rad=pitch_theta_rad,
            yaw_psi_rad=yaw_psi_rad,
            orthogonality_residual=orth_residual,
            det_residual=det_residual,
        )

    # ── 95% Confidence Ellipsoid ──────────────────────────────────────────────
    @staticmethod
    def calculate_95ci_ellipsoid(
        centroid_mu: Tuple[float, float, float],
        covariance_matrix: List[List[float]],
    ) -> ConfidenceEllipsoid:
        """
        Compute 95% volumetric confidence ellipsoid from 3×3 spatial covariance.

        (X - mu)^T · Sigma^-1 · (X - mu) <= chi2_{3,0.95} ≈ 7.815   [§5.2]
        Via eigendecomposition Sigma = V · Lambda · V^T:
          a = sqrt(lambda_1 * 7.815)
          b = sqrt(lambda_2 * 7.815)
          c = sqrt(lambda_3 * 7.815)
        Volume: V_ell = (4/3) * pi * a * b * c

        Args:
            centroid_mu:       Scene centroid (x, y, z) [m].
            covariance_matrix: 3×3 symmetric positive-definite covariance Sigma [m^2].

        Returns:
            ConfidenceEllipsoid with semi-axes (a, b, c) in descending order.

        Raises:
            ValueError: If covariance matrix is not 3×3 or not positive-definite.
        """
        Sigma = np.array(covariance_matrix, dtype=float)
        if Sigma.shape != (3, 3):
            raise ValueError(
                f"Covariance matrix must be 3×3, got {Sigma.shape}."
            )

        # Symmetrize numerical noise
        Sigma = 0.5 * (Sigma + Sigma.T)

        # Eigendecomposition (scipy not needed — numpy suffices for 3×3)
        eigenvalues, eigenvectors = np.linalg.eigh(Sigma)  # eigh: symmetric → real eigenvalues

        # Sort descending
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # Positive-definiteness check
        if eigenvalues[-1] <= 0.0:
            raise ValueError(
                f"Covariance matrix is not positive-definite: "
                f"smallest eigenvalue = {eigenvalues[-1]:.6e}."
            )

        # Semi-axis lengths from §5.2
        a = math.sqrt(eigenvalues[0] * CHI2_3_95)
        b = math.sqrt(eigenvalues[1] * CHI2_3_95)
        c = math.sqrt(eigenvalues[2] * CHI2_3_95)

        # Ellipsoid volume: V = (4/3) * pi * a * b * c
        volume = (4.0 / 3.0) * math.pi * a * b * c

        return ConfidenceEllipsoid(
            centroid_mu=tuple(centroid_mu),
            semi_axis_a=a,
            semi_axis_b=b,
            semi_axis_c=c,
            volume_m3=volume,
            eigenvectors=eigenvectors.tolist(),
            eigenvalues=(float(eigenvalues[0]), float(eigenvalues[1]), float(eigenvalues[2])),
            chi2_threshold=CHI2_3_95,
        )

    # ── Point-to-Plane Residual ───────────────────────────────────────────────
    @staticmethod
    def point_to_plane_residual(
        source_points: List[Tuple[float, float, float]],
        target_points: List[Tuple[float, float, float]],
        normals: List[Tuple[float, float, float]],
        R: np.ndarray,
        T: np.ndarray,
    ) -> float:
        """
        Compute point-to-plane registration residual (§5.1):
            sum_k || n_k^T · (R·p_k + T - q_k) ||^2

        Args:
            source_points: Source sensor point cloud p_k [m].
            target_points: Target scene point cloud q_k [m].
            normals:       Surface normals n_k at target points (unit vectors).
            R:             3×3 rotation matrix.
            T:             Translation vector [m].

        Returns:
            Total residual energy (scalar, lower is better).
        """
        if len(source_points) != len(target_points) or len(source_points) != len(normals):
            raise ValueError("source_points, target_points, and normals must have equal length.")
        if len(source_points) == 0:
            raise ValueError("At least one point correspondence is required.")

        total = 0.0
        for p, q, n in zip(source_points, target_points, normals):
            p_arr = np.array(p, dtype=float)
            q_arr = np.array(q, dtype=float)
            n_arr = np.array(n, dtype=float)
            residual = float(n_arr @ (R @ p_arr + T - q_arr))
            total += residual ** 2
        return total

    # ── Multi-Sensor Scene Fusion ─────────────────────────────────────────────
    @staticmethod
    def fuse_multimodal_scene_evidence(
        scene_id: str,
        lidar_points: Optional[List[Dict]] = None,
        bpa_origins: Optional[List[Tuple[float, float, float]]] = None,
        ballistics_vectors: Optional[List[Dict]] = None,
        dna_landmarks: Optional[List[Tuple[float, float, float]]] = None,
    ) -> ReconstructedScene:
        """
        Fuse multi-modal forensic evidence into unified 3D scene coordinates.

        Each sensor type uses calibrated precision bound from §5.1 Table:
          LiDAR: ±0.002 m | BPA: ±0.012 m | Ballistics: ±0.005 m | DNA: ±0.008 m

        Args:
            scene_id:            Scene identifier string.
            lidar_points:        List of {"label": str, "coords": (x,y,z)} dicts.
            bpa_origins:         List of 3D BPA area-of-origin points [m].
            ballistics_vectors:  List of {"origin": (x,y,z), "direction": (dx,dy,dz)}.
            dna_landmarks:       List of (x, y, z) biological sample positions [m].

        Returns:
            ReconstructedScene with all sensor points and scene metadata.
        """
        lidar_points = lidar_points or []
        bpa_origins = bpa_origins or []
        ballistics_vectors = ballistics_vectors or []
        dna_landmarks = dna_landmarks or []

        sensor_points: List[SensorPoint] = []
        all_coords: List[np.ndarray] = []

        # --- Register LiDAR points ---
        for lp in lidar_points:
            coords = tuple(lp["coords"])
            sp = SensorPoint(
                sensor_type="LIDAR",
                label=lp.get("label", "LIDAR-PT"),
                x_scene=coords,
                precision_m=SENSOR_PRECISION_M["LIDAR"],
            )
            sensor_points.append(sp)
            all_coords.append(np.array(coords, dtype=float))

        # --- Register BPA origins ---
        for i, origin in enumerate(bpa_origins):
            coords = tuple(origin)
            sp = SensorPoint(
                sensor_type="BPA",
                label=f"BPA-ORIGIN-{i + 1:02d}",
                x_scene=coords,
                precision_m=SENSOR_PRECISION_M["BPA"],
            )
            sensor_points.append(sp)
            all_coords.append(np.array(coords, dtype=float))

        # --- Register ballistics vectors (origin only for spatial anchor) ---
        for i, bv in enumerate(ballistics_vectors):
            coords = tuple(bv["origin"])
            sp = SensorPoint(
                sensor_type="BALLISTICS",
                label=f"BULLET-{i + 1:02d}",
                x_scene=coords,
                precision_m=SENSOR_PRECISION_M["BALLISTICS"],
            )
            sensor_points.append(sp)
            all_coords.append(np.array(coords, dtype=float))

        # --- Register DNA landmarks ---
        for i, dl in enumerate(dna_landmarks):
            coords = tuple(dl)
            sp = SensorPoint(
                sensor_type="DNA",
                label=f"DNA-LM-{i + 1:02d}",
                x_scene=coords,
                precision_m=SENSOR_PRECISION_M["DNA"],
            )
            sensor_points.append(sp)
            all_coords.append(np.array(coords, dtype=float))

        if not all_coords:
            raise ValueError("At least one evidence point must be provided for scene fusion.")

        stacked = np.stack(all_coords, axis=0)  # N × 3

        # Scene centroid (unweighted mean)
        centroid = stacked.mean(axis=0)

        # Bounding box
        bb_min = stacked.min(axis=0)
        bb_max = stacked.max(axis=0)

        # Point-to-plane residual: use scene centroid as target plane (normal = mean direction)
        # Simplified single-plane residual for scene-level alignment quality metric
        centered = stacked - centroid
        _, _, Vt = np.linalg.svd(centered, full_matrices=False)
        dominant_normal = Vt[0]  # First principal component
        residuals = centered @ dominant_normal
        p2p_residual = float(np.sum(residuals ** 2))

        return ReconstructedScene(
            scene_id=scene_id,
            sensor_points=sensor_points,
            bpa_origins=list(map(tuple, bpa_origins)),
            ballistics_vectors=ballistics_vectors,
            dna_landmarks=list(map(tuple, dna_landmarks)),
            scene_centroid=tuple(centroid.tolist()),
            scene_bounding_box={
                "min": tuple(bb_min.tolist()),
                "max": tuple(bb_max.tolist()),
            },
            point_to_plane_residual=p2p_residual,
            n_sensors=len(sensor_points),
        )
