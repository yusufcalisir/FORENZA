"""
FORENZA Craniofacial Morphometry & Anthropological Landmarks Mathematical Formulation Engine.
Module 3.3 — Pillar 3: Phenotyping, Biogeographic Ancestry & Morphometrics.

Derives verbatim from:
  - Pillar 3 Research Specification (§3: 3D Craniofacial Morphology & Cephalometric Reconstruction)
  - Claes et al. (2014) PLoS Genetics Craniofacial Shape Space & Morphometric GWAS Loci
  - Generalized Procrustes Analysis (GPA) 3D Superposition (Gower 1975, Rohlf & Slice 1990)
  - Anthropological Cephalometric Indices (Martin & Saller 1957, Farkas 1994)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


# ── Primary Morphometric Predictor Loci ───────────────────────────────────────

CRANIOFACIAL_LOCI: Dict[str, Dict[str, Any]] = {
    "rs974448": {
        "gene": "PAX3",
        "effect_allele": "T",
        "effect_size_sd": 0.412,
        "trait": "Cranial Vault Width & Nasion Position",
        "standard_dosage_weights": {"nasion_y": 1.25, "nasion_z": 0.85},
    },
    "rs12882923": {
        "gene": "PAX9",
        "effect_allele": "C",
        "effect_size_sd": 0.385,
        "trait": "Bizygomatic Breadth & Midface Breadth",
        "standard_dosage_weights": {"alar_x": 0.95, "alar_y": 0.45, "alar_z": 0.30, "bizygomatic": 3.20},
    },
    "rs11130635": {
        "gene": "PRDM16",
        "effect_allele": "A",
        "effect_size_sd": 0.452,
        "trait": "Nasal Bridge Elevation & Projection",
        "standard_dosage_weights": {"pronasale_y": 2.10, "pronasale_z": 1.15},
    },
    "rs13289": {
        "gene": "DCHS2",
        "effect_allele": "G",
        "effect_size_sd": -0.321,
        "trait": "Nasal Tip Morphology & Subnasale Angle",
        "standard_dosage_weights": {"pronasale_y": -1.45, "subnasale_y": -1.10, "subnasale_z": -0.65},
    },
    "rs7559252": {
        "gene": "PCDH15",
        "effect_allele": "C",
        "effect_size_sd": 0.298,
        "trait": "Chin Prominence & Mandibular Convexity",
        "standard_dosage_weights": {"labiale_y": 0.60, "labiale_z": -0.40, "menton_y": 1.85, "menton_z": -1.20},
    },
}


# ── 3D Geometric Primitives ───────────────────────────────────────────────────

@dataclass(frozen=True)
class Point3D:
    """Represents a 3D coordinate point in millimeters (mm)."""
    x: float  # Left (-X) to Right (+X) relative to sagittal midline (0.0)
    y: float  # Posterior (-Y) to Anterior (+Y)
    z: float  # Inferior (-Z) to Superior (+Z)

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=np.float64)

    def to_dict(self) -> Dict[str, float]:
        return {"x": round(self.x, 3), "y": round(self.y, 3), "z": round(self.z, 3)}

    def distance_to(self, other: Point3D) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)


@dataclass
class CephalometricLandmarks:
    """Canonical 3D Cephalometric Landmarks."""
    nasion: Point3D              # N: Forehead-nasal junction
    pronasale: Point3D           # Prn: Nasal apex / tip
    subnasale: Point3D           # Sn: Base of columella / subnasal point
    alare_left: Point3D          # Al_L: Left nasal alar curvature
    alare_right: Point3D         # Al_R: Right nasal alar curvature
    labiale_superius: Point3D    # Ls: Midpoint of upper vermilion border
    menton: Point3D              # Me: Inferior-most midline point of chin
    zygion_left: Point3D         # Zy_L: Most lateral point on left zygomatic arch
    zygion_right: Point3D        # Zy_R: Most lateral point on right zygomatic arch
    cheilion_left: Point3D       # Ch_L: Left corner of mouth
    cheilion_right: Point3D      # Ch_R: Right corner of mouth

    def to_dict(self) -> Dict[str, Dict[str, float]]:
        return {
            "nasion": self.nasion.to_dict(),
            "pronasale": self.pronasale.to_dict(),
            "subnasale": self.subnasale.to_dict(),
            "alare_left": self.alare_left.to_dict(),
            "alare_right": self.alare_right.to_dict(),
            "labiale_superius": self.labiale_superius.to_dict(),
            "menton": self.menton.to_dict(),
            "zygion_left": self.zygion_left.to_dict(),
            "zygion_right": self.zygion_right.to_dict(),
            "cheilion_left": self.cheilion_left.to_dict(),
            "cheilion_right": self.cheilion_right.to_dict(),
        }

    def to_matrix(self) -> np.ndarray:
        """Returns landmark coordinates as an (11, 3) matrix."""
        return np.array([
            self.nasion.to_array(),
            self.pronasale.to_array(),
            self.subnasale.to_array(),
            self.alare_left.to_array(),
            self.alare_right.to_array(),
            self.labiale_superius.to_array(),
            self.menton.to_array(),
            self.zygion_left.to_array(),
            self.zygion_right.to_array(),
            self.cheilion_left.to_array(),
            self.cheilion_right.to_array(),
        ], dtype=np.float64)


@dataclass
class AnthropologicalIndices:
    """Clinical Cephalometric and Anthropological Facial Indices."""
    nasal_height_mm: float                 # N - Sn distance
    alar_breadth_mm: float                 # Al_L - Al_R distance
    nasal_index: float                     # (Alar Breadth / Nasal Height) * 100
    nasal_typology: str                    # LEPTORRHINE (<70), MESORRHINE (70-84.9), PLATYRRHINE (>=85)
    morphological_facial_height_mm: float  # N - Me distance
    bizygomatic_breadth_mm: float          # Zy_L - Zy_R distance
    morphological_facial_index: float      # (Facial Height / Bizygomatic Breadth) * 100
    facial_typology: str                   # EURYPROSOPIC, MESOPROSOPIC, LEPTOPROSOPIC, etc.
    nasal_bridge_elevation_index: float    # (z_Prn - z_Sn) / (y_Prn - y_Sn)
    facial_convexity_angle_deg: float      # Angle N-Sn-Me in degrees
    mandibular_breadth_mm: float           # Mandibular width (including sexual dimorphism)
    sexual_dimorphism_offset_mm: float     # Male vs Female offset applied


@dataclass
class ProcrustesSuperpositionResult:
    """Output of Generalized Orthogonal Procrustes 3D Alignment."""
    centroid_size_1: float
    centroid_size_2: float
    procrustes_distance: float             # Sum of squared deviations
    rmsd_mm: float                         # Root Mean Square Deviation in mm
    rotation_matrix: List[List[float]]     # 3x3 orthogonal rotation matrix
    translation_vector: List[float]        # 3D translation offset
    aligned_matrix: List[List[float]]      # Aligned coordinates


# ── Core Mathematical Formulation ──────────────────────────────────────────────

class CraniofacialMathematicalFormulation:
    """
    Mathematical engine for 3D Craniofacial Morphometry & Anthropological Landmarks.
    """

    @staticmethod
    def reconstruct_cephalometric_landmarks(
        snp_dosages: Dict[str, Union[int, float]],
        sex: str = "FEMALE",  # "MALE" or "FEMALE"
        age_years: float = 25.0,
    ) -> CephalometricLandmarks:
        """
        Reconstructs 3D cephalometric landmarks from SNP dosages and demographic modulations.

        Equations from Research §3.2:
          Nasion (N):
            x = 0.00, y = 12.4 + 1.25 * X_PAX3, z = 45.2 + 0.85 * X_PAX3
          Pronasale (Prn):
            x = 0.00, y = 48.5 + 2.10 * X_PRDM16 - 1.45 * X_DCHS2, z = 12.1 + 1.15 * X_PRDM16
          Subnasale (Sn):
            x = 0.00, y = 38.2 - 1.10 * X_DCHS2, z = -2.5 - 0.65 * X_DCHS2
          Alare (Al_L, Al_R):
            x = +- (18.5 + 0.95 * X_PAX9), y = 36.1 + 0.45 * X_PAX9, z = 2.1 + 0.30 * X_PAX9
          Labiale Superius (Ls):
            x = 0.00, y = 34.5 + 0.60 * X_PCDH15, z = -12.4 - 0.40 * X_PCDH15
          Menton (Me):
            x = 0.00, y = 18.2 + 1.85 * X_PCDH15, z = -68.5 - 1.20 * X_PCDH15
        """
        x_pax3 = float(snp_dosages.get("rs974448", 0.0))
        x_pax9 = float(snp_dosages.get("rs12882923", 0.0))
        x_prdm16 = float(snp_dosages.get("rs11130635", 0.0))
        x_dchs2 = float(snp_dosages.get("rs13289", 0.0))
        x_pcdh15 = float(snp_dosages.get("rs7559252", 0.0))

        is_male = str(sex).upper() == "MALE"
        male_scale = 1.045 if is_male else 1.000
        male_mandible_boost = 8.40 if is_male else 0.00

        # 1. Nasion (N)
        n_x = 0.00
        n_y = (12.40 + 1.25 * x_pax3) * male_scale
        n_z = (45.20 + 0.85 * x_pax3) * male_scale

        # 2. Pronasale (Prn)
        prn_x = 0.00
        prn_y = (48.50 + 2.10 * x_prdm16 - 1.45 * x_dchs2) * male_scale
        prn_z = (12.10 + 1.15 * x_prdm16) * male_scale

        # 3. Subnasale (Sn)
        sn_x = 0.00
        sn_y = (38.20 - 1.10 * x_dchs2) * male_scale
        sn_z = (-2.50 - 0.65 * x_dchs2) * male_scale

        # 4. Alare Left & Right (Al_L, Al_R)
        alar_offset = (18.50 + 0.95 * x_pax9) * male_scale
        alar_y = (36.10 + 0.45 * x_pax9) * male_scale
        alar_z = (2.10 + 0.30 * x_pax9) * male_scale

        al_l = Point3D(x=-alar_offset, y=alar_y, z=alar_z)
        al_r = Point3D(x=+alar_offset, y=alar_y, z=alar_z)

        # 5. Labiale Superius (Ls)
        ls_x = 0.00
        ls_y = (34.50 + 0.60 * x_pcdh15) * male_scale
        ls_z = (-12.40 - 0.40 * x_pcdh15) * male_scale

        # 6. Menton (Me)
        me_x = 0.00
        me_y = (18.20 + 1.85 * x_pcdh15) * male_scale + (male_mandible_boost * 0.25)
        me_z = (-68.50 - 1.20 * x_pcdh15) * male_scale

        # 7. Zygion Left & Right (Zy_L, Zy_R)
        zy_offset = (67.50 + 1.60 * x_pax9) * male_scale
        zy_y = (15.20 + 0.35 * x_pax9) * male_scale
        zy_z = (18.40 + 0.25 * x_pax3) * male_scale
        zy_l = Point3D(x=-zy_offset, y=zy_y, z=zy_z)
        zy_r = Point3D(x=+zy_offset, y=zy_y, z=zy_z)

        # 8. Cheilion Left & Right (Ch_L, Ch_R)
        ch_offset = (24.50 + 0.40 * x_pcdh15) * male_scale
        ch_y = (31.00 + 0.50 * x_pcdh15) * male_scale
        ch_z = (-18.20 - 0.30 * x_pcdh15) * male_scale
        ch_l = Point3D(x=-ch_offset, y=ch_y, z=ch_z)
        ch_r = Point3D(x=+ch_offset, y=ch_y, z=ch_z)

        return CephalometricLandmarks(
            nasion=Point3D(x=n_x, y=n_y, z=n_z),
            pronasale=Point3D(x=prn_x, y=prn_y, z=prn_z),
            subnasale=Point3D(x=sn_x, y=sn_y, z=sn_z),
            alare_left=al_l,
            alare_right=al_r,
            labiale_superius=Point3D(x=ls_x, y=ls_y, z=ls_z),
            menton=Point3D(x=me_x, y=me_y, z=me_z),
            zygion_left=zy_l,
            zygion_right=zy_r,
            cheilion_left=ch_l,
            cheilion_right=ch_r,
        )

    @staticmethod
    def compute_anthropological_indices(
        landmarks: CephalometricLandmarks,
        sex: str = "FEMALE",
    ) -> AnthropologicalIndices:
        """
        Computes clinical cephalometric ratios and anthropological facial typologies.
        """
        # Nasal Dimensions
        alar_breadth = landmarks.alare_left.distance_to(landmarks.alare_right)
        nasal_height = landmarks.nasion.distance_to(landmarks.subnasale)
        nasal_index = (alar_breadth / max(nasal_height, 1e-6)) * 100.0

        # Farkas Soft-Tissue Nasal Index Thresholds
        if nasal_index < 70.0:
            nasal_typology = "LEPTORRHINE (Narrow Nasal Aperture - European)"
        elif nasal_index < 75.0:
            nasal_typology = "MESORRHINE (Medium Nasal Aperture - Asian/Admixed)"
        else:
            nasal_typology = "PLATYRRHINE (Broad Nasal Aperture - African/Australasian)"

        # Morphological Facial Dimensions
        facial_height = landmarks.nasion.distance_to(landmarks.menton)
        bizygomatic_breadth = landmarks.zygion_left.distance_to(landmarks.zygion_right)
        facial_index = (facial_height / max(bizygomatic_breadth, 1e-6)) * 100.0

        if facial_index < 80.0:
            facial_typology = "HYPEREURYPROSOPIC (Very Broad Face)"
        elif facial_index < 85.0:
            facial_typology = "EURYPROSOPIC (Broad Face)"
        elif facial_index < 90.0:
            facial_typology = "MESOPROSOPIC (Medium/Harmonious Face)"
        elif facial_index < 95.0:
            facial_typology = "LEPTOPROSOPIC (Narrow/Long Face)"
        else:
            facial_typology = "HYPERLEPTOPROSOPIC (Very Narrow/Long Face)"

        # Nasal Bridge Elevation Index
        dy_nasal = landmarks.pronasale.y - landmarks.subnasale.y
        dz_nasal = landmarks.pronasale.z - landmarks.subnasale.z
        nbei = dz_nasal / max(abs(dy_nasal), 1e-6)

        # Facial Convexity Angle (N - Sn - Me)
        v_sn_n = landmarks.nasion.to_array() - landmarks.subnasale.to_array()
        v_sn_me = landmarks.menton.to_array() - landmarks.subnasale.to_array()
        dot_prod = np.dot(v_sn_n, v_sn_me)
        norm_prod = np.linalg.norm(v_sn_n) * np.linalg.norm(v_sn_me)
        cos_angle = np.clip(dot_prod / max(norm_prod, 1e-12), -1.0, 1.0)
        convexity_angle_deg = float(np.degrees(np.arccos(cos_angle)))

        is_male = str(sex).upper() == "MALE"
        dimorphism_offset = 8.40 if is_male else 0.00
        # Mandibular breadth (Bigonial breadth Go_L - Go_R) incorporates baseline ratio + male dimorphism offset
        mandibular_breadth = (bizygomatic_breadth * 0.72) + dimorphism_offset

        return AnthropologicalIndices(
            nasal_height_mm=round(float(nasal_height), 2),
            alar_breadth_mm=round(float(alar_breadth), 2),
            nasal_index=round(float(nasal_index), 2),
            nasal_typology=nasal_typology,
            morphological_facial_height_mm=round(float(facial_height), 2),
            bizygomatic_breadth_mm=round(float(bizygomatic_breadth), 2),
            morphological_facial_index=round(float(facial_index), 2),
            facial_typology=facial_typology,
            nasal_bridge_elevation_index=round(float(nbei), 3),
            facial_convexity_angle_deg=round(float(convexity_angle_deg), 2),
            mandibular_breadth_mm=round(float(mandibular_breadth), 2),
            sexual_dimorphism_offset_mm=round(float(dimorphism_offset), 2),
        )

    @staticmethod
    def generalized_procrustes_superposition(
        landmarks_target: np.ndarray,
        landmarks_source: np.ndarray,
    ) -> ProcrustesSuperpositionResult:
        """
        Performs 3D Generalized Orthogonal Procrustes Analysis (GPA) Superposition.
        Translates, scales to centroid size, and orthogonally rotates source matrix to target.
        """
        X1 = np.asarray(landmarks_target, dtype=np.float64)
        X2 = np.asarray(landmarks_source, dtype=np.float64)

        if X1.shape != X2.shape or X1.ndim != 2:
            raise ValueError(f"Incompatible landmark shapes: {X1.shape} vs {X2.shape}")

        k, m = X1.shape

        # 1. Translation centering
        c1 = np.mean(X1, axis=0)
        c2 = np.mean(X2, axis=0)
        X1_c = X1 - c1
        X2_c = X2 - c2

        # 2. Centroid Size
        cs1 = float(np.sqrt(np.sum(X1_c ** 2)))
        cs2 = float(np.sqrt(np.sum(X2_c ** 2)))

        if cs1 < 1e-12 or cs2 < 1e-12:
            raise ValueError("Degenerate landmark configuration with zero centroid size")

        X1_norm = X1_c / cs1
        X2_norm = X2_c / cs2

        # 3. Orthogonal Rotation via SVD (Kabsch algorithm)
        H = np.dot(X2_norm.T, X1_norm)
        U, S, Vt = np.linalg.svd(H)
        R = np.dot(U, Vt)

        # Reflection correction for proper SO(3) rotation
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = np.dot(U, Vt)

        # 4. Aligned Source in Target Space (scaled back to target centroid size)
        X2_aligned = (np.dot(X2_norm, R) * cs1) + c1

        # 5. Procrustes Distance & RMSD
        diff = X1 - X2_aligned
        procrustes_dist = float(np.sum(diff ** 2))
        rmsd = float(np.sqrt(procrustes_dist / k))

        translation_offset = (c1 - c2).tolist()

        return ProcrustesSuperpositionResult(
            centroid_size_1=round(cs1, 4),
            centroid_size_2=round(cs2, 4),
            procrustes_distance=round(procrustes_dist, 6),
            rmsd_mm=round(rmsd, 4),
            rotation_matrix=R.round(6).tolist(),
            translation_vector=[round(x, 4) for x in translation_offset],
            aligned_matrix=X2_aligned.round(3).tolist(),
        )
