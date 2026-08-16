"""
FORENZA Module 30 Test Suite: 3D Spatial Crime Scene Reconstruction & Interactive Juror Visualizer.

Research: Pillar 6 §5.1, §5.2
Test Vectors:
  VECTOR_30_SPATIAL_A: Identity transform (R=I, T=0) => X_scene = X_local
  VECTOR_30_SPATIAL_B: 90° Euler rotations (yaw, pitch, roll) — orthogonality & determinant invariants
  VECTOR_30_SPATIAL_C: Pure translation (R=I, T=[tx,ty,tz])
  VECTOR_30_SPATIAL_D: 95% CI ellipsoid semi-axes & volume — isotropic & anisotropic covariance
  VECTOR_30_SPATIAL_E: Multi-sensor precision conformance (LiDAR, BPA, Ballistics, DNA)
  VECTOR_30_SPATIAL_F: Domain validation (non-positive covariance eigenvalues → ValueError)
  VECTOR_30_SPATIAL_G: FastAPI REST integration — all 3 spatial endpoints
"""

import math
import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.node.services.forensic.court.spatial_reconstruction_engine import (
    SpatialReconstructionEngine,
    build_rotation_matrix,
    CHI2_3_95,
    SENSOR_PRECISION_M,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def engine() -> SpatialReconstructionEngine:
    return SpatialReconstructionEngine()


@pytest.fixture(scope="module")
def client():
    from backend.app.main import app
    return TestClient(app)


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR_30_SPATIAL_A: Identity Transform Invariant
# R = I, T = [0,0,0] => X_scene = X_local (verbatim)
# ═══════════════════════════════════════════════════════════════════════════════
class TestVECTOR30SpatialA:
    """VECTOR_30_SPATIAL_A — SE(3) Identity Transform: R=I, T=0 => X_scene = X_local."""

    @pytest.mark.parametrize("point", [
        (0.0, 0.0, 0.0),
        (1.0, 2.5, -3.7),
        (125.4, -45.2, 142.8),  # Ground-truth BPA origin from Module 21
        (-100.0, 200.0, 50.0),
    ])
    def test_identity_preserves_coordinates(self, point):
        result = SpatialReconstructionEngine.transform_se3(
            x_local=point,
            roll_phi_rad=0.0,
            pitch_theta_rad=0.0,
            yaw_psi_rad=0.0,
            translation=(0.0, 0.0, 0.0),
        )
        assert result.x_scene == pytest.approx(point, abs=1e-10), (
            f"Identity transform must preserve coordinates: got {result.x_scene}, expected {point}"
        )

    def test_identity_rotation_matrix_is_identity(self):
        result = SpatialReconstructionEngine.transform_se3(x_local=(1.0, 0.0, 0.0))
        R = np.array(result.rotation_matrix)
        np.testing.assert_allclose(R, np.eye(3), atol=1e-12)

    def test_identity_orthogonality_residual(self):
        result = SpatialReconstructionEngine.transform_se3(x_local=(1.0, 0.0, 0.0))
        assert result.orthogonality_residual < 1e-10
        assert result.det_residual < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR_30_SPATIAL_B: 3D Euler Rotation Invariants
# R = R_z(psi) * R_y(theta) * R_x(phi); R·R^T = I, det(R) = +1
# ═══════════════════════════════════════════════════════════════════════════════
class TestVECTOR30SpatialB:
    """VECTOR_30_SPATIAL_B — Euler ZYX rotation orthogonality and determinant invariants."""

    @pytest.mark.parametrize("phi_deg,theta_deg,psi_deg", [
        (90.0, 0.0, 0.0),     # Pure roll
        (0.0, 90.0, 0.0),     # Pure pitch
        (0.0, 0.0, 90.0),     # Pure yaw
        (45.0, 30.0, 60.0),   # Mixed Euler angles
        (180.0, 90.0, 45.0),  # Large angles
    ])
    def test_rotation_matrix_orthogonality(self, phi_deg, theta_deg, psi_deg):
        phi = math.radians(phi_deg)
        theta = math.radians(theta_deg)
        psi = math.radians(psi_deg)
        R = build_rotation_matrix(phi, theta, psi)
        # R · R^T must equal I within floating-point precision
        np.testing.assert_allclose(R @ R.T, np.eye(3), atol=1e-10,
                                   err_msg=f"R·R^T ≠ I for angles ({phi_deg},{theta_deg},{psi_deg})")

    @pytest.mark.parametrize("phi_deg,theta_deg,psi_deg", [
        (90.0, 0.0, 0.0),
        (0.0, 90.0, 0.0),
        (0.0, 0.0, 90.0),
        (123.0, -45.0, 67.5),
    ])
    def test_rotation_determinant_is_plus_one(self, phi_deg, theta_deg, psi_deg):
        R = build_rotation_matrix(
            math.radians(phi_deg), math.radians(theta_deg), math.radians(psi_deg)
        )
        assert abs(np.linalg.det(R) - 1.0) < 1e-10, (
            f"det(R)={np.linalg.det(R):.10f} ≠ +1 for angles ({phi_deg},{theta_deg},{psi_deg})"
        )

    def test_pure_yaw_90_deg_x_axis(self):
        """90° yaw (psi=90°): point (1,0,0) should map to approximately (0,1,0)."""
        result = SpatialReconstructionEngine.transform_se3(
            x_local=(1.0, 0.0, 0.0),
            roll_phi_rad=0.0,
            pitch_theta_rad=0.0,
            yaw_psi_rad=math.pi / 2,
        )
        assert result.x_scene[0] == pytest.approx(0.0, abs=1e-10)
        assert result.x_scene[1] == pytest.approx(1.0, abs=1e-10)
        assert result.x_scene[2] == pytest.approx(0.0, abs=1e-10)

    def test_pure_pitch_90_deg(self):
        """90° pitch (theta=90°): point (1,0,0) should map to approximately (0,0,-1)."""
        result = SpatialReconstructionEngine.transform_se3(
            x_local=(1.0, 0.0, 0.0),
            roll_phi_rad=0.0,
            pitch_theta_rad=math.pi / 2,
            yaw_psi_rad=0.0,
        )
        assert result.x_scene[0] == pytest.approx(0.0, abs=1e-10)
        assert result.x_scene[1] == pytest.approx(0.0, abs=1e-10)
        assert result.x_scene[2] == pytest.approx(-1.0, abs=1e-10)

    def test_pure_roll_90_deg(self):
        """90° roll (phi=90°): point (0,1,0) should map to approximately (0,0,1)."""
        result = SpatialReconstructionEngine.transform_se3(
            x_local=(0.0, 1.0, 0.0),
            roll_phi_rad=math.pi / 2,
            pitch_theta_rad=0.0,
            yaw_psi_rad=0.0,
        )
        assert result.x_scene[0] == pytest.approx(0.0, abs=1e-10)
        assert result.x_scene[1] == pytest.approx(0.0, abs=1e-10)
        assert result.x_scene[2] == pytest.approx(1.0, abs=1e-10)

    def test_orthogonality_residual_below_threshold(self):
        result = SpatialReconstructionEngine.transform_se3(
            x_local=(1.0, 1.0, 1.0),
            roll_phi_rad=math.radians(37.0),
            pitch_theta_rad=math.radians(-22.5),
            yaw_psi_rad=math.radians(115.0),
        )
        assert result.orthogonality_residual < 1e-10
        assert result.det_residual < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR_30_SPATIAL_C: Pure Translation Invariant
# R = I, T = [tx,ty,tz] => X_scene = X_local + T
# ═══════════════════════════════════════════════════════════════════════════════
class TestVECTOR30SpatialC:
    """VECTOR_30_SPATIAL_C — Pure translation: X_scene = X_local + T."""

    @pytest.mark.parametrize("point,translation", [
        ((1.0, 2.0, 3.0), (10.0, 20.0, 30.0)),
        ((0.0, 0.0, 0.0), (5.5, -3.2, 1.1)),
        ((-1.0, -2.0, -3.0), (1.0, 2.0, 3.0)),
    ])
    def test_pure_translation_additive(self, point, translation):
        result = SpatialReconstructionEngine.transform_se3(
            x_local=point,
            roll_phi_rad=0.0,
            pitch_theta_rad=0.0,
            yaw_psi_rad=0.0,
            translation=translation,
        )
        expected = (
            point[0] + translation[0],
            point[1] + translation[1],
            point[2] + translation[2],
        )
        assert result.x_scene == pytest.approx(expected, abs=1e-10)

    def test_translation_independence_of_rotation(self):
        """Translation vector T must be applied in global frame (after rotation)."""
        result = SpatialReconstructionEngine.transform_se3(
            x_local=(0.0, 0.0, 0.0),   # Origin: rotation has no effect
            roll_phi_rad=math.radians(45.0),
            pitch_theta_rad=math.radians(30.0),
            yaw_psi_rad=math.radians(60.0),
            translation=(3.0, 4.0, 5.0),
        )
        # When X_local=(0,0,0), X_scene = R·0 + T = T
        assert result.x_scene == pytest.approx((3.0, 4.0, 5.0), abs=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR_30_SPATIAL_D: 95% Confidence Ellipsoid & Volume
# §5.2: a=sqrt(lambda_1*7.815), b=sqrt(lambda_2*7.815), c=sqrt(lambda_3*7.815)
# V = (4/3)*pi*a*b*c
# Ground-truth: Sigma=I_3 => a=b=c=sqrt(7.815)=2.7955 m, V≈91.588 m^3
# ═══════════════════════════════════════════════════════════════════════════════
class TestVECTOR30SpatialD:
    """VECTOR_30_SPATIAL_D — 95% CI ellipsoid semi-axes and volume invariants."""

    def test_isotropic_covariance_identity(self):
        """Isotropic Sigma=I: a=b=c=sqrt(7.815)≈2.7955 m, V≈91.588 m^3."""
        result = SpatialReconstructionEngine.calculate_95ci_ellipsoid(
            centroid_mu=(0.0, 0.0, 0.0),
            covariance_matrix=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        )
        expected_axis = math.sqrt(CHI2_3_95)   # sqrt(7.815) ≈ 2.7955
        assert result.semi_axis_a == pytest.approx(expected_axis, abs=1e-4)
        assert result.semi_axis_b == pytest.approx(expected_axis, abs=1e-4)
        assert result.semi_axis_c == pytest.approx(expected_axis, abs=1e-4)

        expected_volume = (4.0 / 3.0) * math.pi * expected_axis ** 3
        assert result.volume_m3 == pytest.approx(expected_volume, rel=1e-5)
        assert result.chi2_threshold == pytest.approx(7.815, abs=1e-6)

    def test_anisotropic_covariance_descending_axes(self):
        """Anisotropic Sigma=diag(4,2,1): a=sqrt(4*7.815), b=sqrt(2*7.815), c=sqrt(7.815)."""
        result = SpatialReconstructionEngine.calculate_95ci_ellipsoid(
            centroid_mu=(1.0, 2.0, 3.0),
            covariance_matrix=[[4.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 1.0]],
        )
        assert result.semi_axis_a == pytest.approx(math.sqrt(4.0 * CHI2_3_95), rel=1e-6)
        assert result.semi_axis_b == pytest.approx(math.sqrt(2.0 * CHI2_3_95), rel=1e-6)
        assert result.semi_axis_c == pytest.approx(math.sqrt(1.0 * CHI2_3_95), rel=1e-6)
        # Descending order invariant: a >= b >= c > 0
        assert result.semi_axis_a >= result.semi_axis_b >= result.semi_axis_c > 0.0

    def test_volume_formula_exact(self):
        """Volume = (4/3)*pi*a*b*c must hold analytically."""
        result = SpatialReconstructionEngine.calculate_95ci_ellipsoid(
            centroid_mu=(0.0, 0.0, 0.0),
            covariance_matrix=[[9.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 1.0]],
        )
        expected = (4.0 / 3.0) * math.pi * result.semi_axis_a * result.semi_axis_b * result.semi_axis_c
        assert result.volume_m3 == pytest.approx(expected, rel=1e-8)

    def test_eigenvalues_positive_and_descending(self):
        result = SpatialReconstructionEngine.calculate_95ci_ellipsoid(
            centroid_mu=(0.0, 0.0, 0.0),
            covariance_matrix=[[3.0, 0.5, 0.0], [0.5, 2.0, 0.1], [0.0, 0.1, 1.0]],
        )
        lam = result.eigenvalues
        assert lam[0] >= lam[1] >= lam[2] > 0.0

    def test_sensor_precision_covariance_bpa(self):
        """BPA precision ±0.012 m: Sigma=diag(0.012^2,0.012^2,0.012^2)."""
        sig = SENSOR_PRECISION_M["BPA"] ** 2
        result = SpatialReconstructionEngine.calculate_95ci_ellipsoid(
            centroid_mu=(125.4, -45.2, 142.8),
            covariance_matrix=[[sig, 0, 0], [0, sig, 0], [0, 0, sig]],
        )
        expected_axis = math.sqrt(sig * CHI2_3_95)
        assert result.semi_axis_a == pytest.approx(expected_axis, rel=1e-6)
        assert result.volume_m3 > 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR_30_SPATIAL_E: Multi-Sensor Precision Conformance
# LiDAR: ±0.002 m | BPA: ±0.012 m | Ballistics: ±0.005 m | DNA: ±0.008 m
# ═══════════════════════════════════════════════════════════════════════════════
class TestVECTOR30SpatialE:
    """VECTOR_30_SPATIAL_E — Multi-sensor precision table from Research §5.1."""

    def test_sensor_precision_constants(self):
        assert SENSOR_PRECISION_M["LIDAR"]      == pytest.approx(0.002, abs=1e-9)
        assert SENSOR_PRECISION_M["BPA"]        == pytest.approx(0.012, abs=1e-9)
        assert SENSOR_PRECISION_M["BALLISTICS"] == pytest.approx(0.005, abs=1e-9)
        assert SENSOR_PRECISION_M["DNA"]        == pytest.approx(0.008, abs=1e-9)

    def test_fuse_all_sensor_types(self):
        result = SpatialReconstructionEngine.fuse_multimodal_scene_evidence(
            scene_id="SCENE-2026-TEST-E",
            lidar_points=[
                {"label": "LIDAR-01", "coords": (1.0, 2.0, 3.0)},
                {"label": "LIDAR-02", "coords": (4.0, 5.0, 6.0)},
            ],
            bpa_origins=[(125.4, -45.2, 142.8)],
            ballistics_vectors=[{"origin": (2.0, 3.0, 4.0), "direction": (0.0, 0.0, 1.0)}],
            dna_landmarks=[(1.5, 2.2, 0.4), (3.1, 0.8, 0.0)],
        )
        assert result.n_sensors == 6      # 2 LiDAR + 1 BPA + 1 Ballistics + 2 DNA
        assert result.scene_id == "SCENE-2026-TEST-E"

    def test_sensor_type_labels_assigned_correctly(self):
        result = SpatialReconstructionEngine.fuse_multimodal_scene_evidence(
            scene_id="SCENE-TYPE-CHECK",
            lidar_points=[{"label": "L-01", "coords": (0.0, 0.0, 0.0)}],
            bpa_origins=[(1.0, 1.0, 1.0)],
            ballistics_vectors=[{"origin": (2.0, 2.0, 2.0), "direction": (1.0, 0.0, 0.0)}],
            dna_landmarks=[(3.0, 3.0, 3.0)],
        )
        types = {sp.sensor_type for sp in result.sensor_points}
        assert "LIDAR" in types
        assert "BPA" in types
        assert "BALLISTICS" in types
        assert "DNA" in types

    def test_sensor_precision_m_assigned_correctly(self):
        result = SpatialReconstructionEngine.fuse_multimodal_scene_evidence(
            scene_id="SCENE-PREC",
            lidar_points=[{"label": "L", "coords": (0.0, 0.0, 0.0)}],
            bpa_origins=[(1.0, 0.0, 0.0)],
            ballistics_vectors=[{"origin": (2.0, 0.0, 0.0), "direction": (1.0, 0.0, 0.0)}],
            dna_landmarks=[(3.0, 0.0, 0.0)],
        )
        prec_map = {sp.sensor_type: sp.precision_m for sp in result.sensor_points}
        assert prec_map["LIDAR"]      == pytest.approx(0.002, abs=1e-9)
        assert prec_map["BPA"]        == pytest.approx(0.012, abs=1e-9)
        assert prec_map["BALLISTICS"] == pytest.approx(0.005, abs=1e-9)
        assert prec_map["DNA"]        == pytest.approx(0.008, abs=1e-9)

    def test_scene_centroid_computed(self):
        result = SpatialReconstructionEngine.fuse_multimodal_scene_evidence(
            scene_id="SCENE-CENTROID",
            lidar_points=[{"label": "L", "coords": (0.0, 0.0, 0.0)}],
            dna_landmarks=[(2.0, 2.0, 2.0)],
        )
        # Centroid of (0,0,0) and (2,2,2) = (1,1,1)
        assert result.scene_centroid == pytest.approx((1.0, 1.0, 1.0), abs=1e-10)

    def test_bounding_box_min_max(self):
        result = SpatialReconstructionEngine.fuse_multimodal_scene_evidence(
            scene_id="SCENE-BB",
            lidar_points=[
                {"label": "L1", "coords": (0.0, 0.0, 0.0)},
                {"label": "L2", "coords": (10.0, 5.0, 3.0)},
            ],
        )
        assert result.scene_bounding_box["min"] == pytest.approx((0.0, 0.0, 0.0), abs=1e-10)
        assert result.scene_bounding_box["max"] == pytest.approx((10.0, 5.0, 3.0), abs=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR_30_SPATIAL_F: Domain Validation
# Non-positive covariance eigenvalues, wrong matrix shape => ValueError
# ═══════════════════════════════════════════════════════════════════════════════
class TestVECTOR30SpatialF:
    """VECTOR_30_SPATIAL_F — Domain validation: ValueError on invalid inputs."""

    def test_non_positive_definite_covariance_raises(self):
        """Singular covariance (zero eigenvalue) must raise ValueError."""
        with pytest.raises(ValueError, match="positive-definite"):
            SpatialReconstructionEngine.calculate_95ci_ellipsoid(
                centroid_mu=(0.0, 0.0, 0.0),
                covariance_matrix=[[1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
            )

    def test_negative_eigenvalue_covariance_raises(self):
        """Indefinite covariance (negative eigenvalue) must raise ValueError."""
        with pytest.raises(ValueError, match="positive-definite"):
            SpatialReconstructionEngine.calculate_95ci_ellipsoid(
                centroid_mu=(0.0, 0.0, 0.0),
                covariance_matrix=[[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]],
            )

    def test_wrong_covariance_shape_raises(self):
        """2×2 covariance must raise ValueError (requires 3×3)."""
        with pytest.raises(ValueError, match="3×3"):
            SpatialReconstructionEngine.calculate_95ci_ellipsoid(
                centroid_mu=(0.0, 0.0, 0.0),
                covariance_matrix=[[1.0, 0.0], [0.0, 1.0]],
            )

    def test_empty_scene_raises(self):
        """fuse_multimodal_scene_evidence with no points must raise ValueError."""
        with pytest.raises(ValueError, match="At least one evidence point"):
            SpatialReconstructionEngine.fuse_multimodal_scene_evidence(
                scene_id="SCENE-EMPTY",
            )

    def test_point_to_plane_empty_raises(self):
        """Empty correspondence lists must raise ValueError."""
        R = np.eye(3)
        T = np.zeros(3)
        with pytest.raises(ValueError, match="At least one point"):
            SpatialReconstructionEngine.point_to_plane_residual(
                source_points=[], target_points=[], normals=[], R=R, T=T
            )

    def test_point_to_plane_mismatched_lengths_raises(self):
        """Mismatched source/target lengths must raise ValueError."""
        R = np.eye(3)
        T = np.zeros(3)
        with pytest.raises(ValueError):
            SpatialReconstructionEngine.point_to_plane_residual(
                source_points=[(0.0, 0.0, 0.0)],
                target_points=[(1.0, 1.0, 1.0), (2.0, 2.0, 2.0)],
                normals=[(0.0, 0.0, 1.0)],
                R=R, T=T,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR_30_SPATIAL_G: FastAPI REST Integration
# All 3 endpoints: /spatial/transform-se3, /spatial/confidence-ellipsoid,
#                  /spatial/reconstruct-scene
# ═══════════════════════════════════════════════════════════════════════════════
class TestVECTOR30SpatialG:
    """VECTOR_30_SPATIAL_G — FastAPI REST integration for all 3 spatial endpoints."""

    BASE = "/api/v1/forensic/court/spatial"

    def test_transform_se3_identity(self, client):
        resp = client.post(f"{self.BASE}/transform-se3", json={
            "x_local": [1.0, 2.0, 3.0],
            "roll_phi_deg": 0.0,
            "pitch_theta_deg": 0.0,
            "yaw_psi_deg": 0.0,
            "translation": [0.0, 0.0, 0.0],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["x_scene"] == pytest.approx([1.0, 2.0, 3.0], abs=1e-8)
        assert data["orthogonality_residual"] < 1e-10
        assert data["det_residual"] < 1e-10

    def test_transform_se3_yaw_90(self, client):
        resp = client.post(f"{self.BASE}/transform-se3", json={
            "x_local": [1.0, 0.0, 0.0],
            "roll_phi_deg": 0.0,
            "pitch_theta_deg": 0.0,
            "yaw_psi_deg": 90.0,
            "translation": [0.0, 0.0, 0.0],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["x_scene"][0] == pytest.approx(0.0, abs=1e-8)
        assert data["x_scene"][1] == pytest.approx(1.0, abs=1e-8)

    def test_confidence_ellipsoid_isotropic(self, client):
        resp = client.post(f"{self.BASE}/confidence-ellipsoid", json={
            "centroid_mu": [0.0, 0.0, 0.0],
            "covariance_matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        })
        assert resp.status_code == 200
        data = resp.json()
        expected_axis = math.sqrt(7.815)
        assert data["semi_axis_a"] == pytest.approx(expected_axis, rel=1e-4)
        assert data["semi_axis_b"] == pytest.approx(expected_axis, rel=1e-4)
        assert data["semi_axis_c"] == pytest.approx(expected_axis, rel=1e-4)
        assert data["chi2_threshold"] == pytest.approx(7.815, abs=1e-6)
        assert data["volume_m3"] > 0.0

    def test_confidence_ellipsoid_negative_definite_returns_400(self, client):
        resp = client.post(f"{self.BASE}/confidence-ellipsoid", json={
            "centroid_mu": [0.0, 0.0, 0.0],
            "covariance_matrix": [[1.0, 0.0, 0.0], [0.0, -2.0, 0.0], [0.0, 0.0, 1.0]],
        })
        assert resp.status_code == 400

    def test_reconstruct_scene_full_sensor_types(self, client):
        resp = client.post(f"{self.BASE}/reconstruct-scene", json={
            "scene_id": "SCENE-API-TEST-G",
            "lidar_points": [
                {"label": "L-01", "coords": [1.0, 2.0, 3.0]},
            ],
            "bpa_origins": [[125.4, -45.2, 142.8]],
            "ballistics_vectors": [{"origin": [2.0, 3.0, 4.0], "direction": [0.0, 0.0, 1.0]}],
            "dna_landmarks": [[1.5, 2.2, 0.4]],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["scene_id"] == "SCENE-API-TEST-G"
        assert data["n_sensors"] == 4
        sensor_types = {sp["sensor_type"] for sp in data["sensor_points"]}
        assert sensor_types == {"LIDAR", "BPA", "BALLISTICS", "DNA"}

    def test_reconstruct_scene_empty_returns_400(self, client):
        resp = client.post(f"{self.BASE}/reconstruct-scene", json={
            "scene_id": "SCENE-EMPTY",
        })
        assert resp.status_code == 400

    def test_chi2_threshold_exact_constant(self, client):
        """chi2_threshold in response must always equal 7.815 (Research §5.2)."""
        resp = client.post(f"{self.BASE}/confidence-ellipsoid", json={
            "centroid_mu": [5.0, 10.0, 15.0],
            "covariance_matrix": [[4.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 1.0]],
        })
        assert resp.status_code == 200
        assert resp.json()["chi2_threshold"] == pytest.approx(7.815, abs=1e-6)
