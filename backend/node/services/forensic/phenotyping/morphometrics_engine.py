"""
FORENZA Craniofacial Morphometrics & 3D Shape Space Reconstruction Engine — Module 13.

Implements verbatim from Pillar 3 Research §3:
  - §3.1 Primary Craniofacial Predictor Loci (PAX3, PAX9, PRDM16, DCHS2, PCDH15)
  - §3.2 3D Cephalometric Landmark Reconstruction Equations (N, Prn, Sn, Al_L, Al_R, Ls, Me in mm)
  - Clinical Facial Indices: Morphological Facial Height, Alar Breadth, Nasal Projection, Facial Index (I_F)
  - Claes et al. PCA Shape Space Modulation Paradigm & Bilateral Midline Symmetry Invariants
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union


# ── Primary Morphometric Predictor Loci ───────────────────────────────────────

MORPHOMETRIC_LOCI = {
    "rs974448":   {"gene": "PAX3",   "effect_allele": "T", "effect_size_sd": 0.412, "trait": "Cranial Vault Width & Nasion Position"},
    "rs12882923": {"gene": "PAX9",   "effect_allele": "C", "effect_size_sd": 0.385, "trait": "Bizygomatic Breadth & Midface Breadth"},
    "rs11130635": {"gene": "PRDM16", "effect_allele": "A", "effect_size_sd": 0.452, "trait": "Nasal Bridge Elevation & Projection"},
    "rs13289":    {"gene": "DCHS2",  "effect_allele": "G", "effect_size_sd": -0.321, "trait": "Nasal Tip Morphology & Subnasale Angle"},
    "rs7559252":  {"gene": "PCDH15", "effect_allele": "C", "effect_size_sd": 0.298, "trait": "Chin Prominence & Mandibular Convexity"},
}


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class Point3D:
    x: float  # Left (-X) to Right (+X) in mm (Midline = 0.0)
    y: float  # Posterior (-Y) to Anterior (+Y) in mm
    z: float  # Inferior (-Z) to Superior (+Z) in mm

    def to_dict(self) -> Dict[str, float]:
        return {"x": round(self.x, 3), "y": round(self.y, 3), "z": round(self.z, 3)}

    def distance_to(self, other: "Point3D") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)


@dataclass
class CephalometricLandmarks:
    nasion: Point3D              # N: Forehead-nasal junction
    pronasale: Point3D           # Prn: Nasal apex / tip
    subnasale: Point3D           # Sn: Base of columella / subnasal point
    alare_left: Point3D          # Al_L: Most lateral point on left nasal alar curvature
    alare_right: Point3D         # Al_R: Most lateral point on right nasal alar curvature
    labiale_superius: Point3D    # Ls: Midpoint of upper vermilion border
    menton: Point3D              # Me: Inferior-most midline point of chin


@dataclass
class FacialIndices:
    morphological_facial_height_mm: float  # Distance Nasion to Menton (N - Me)
    alar_breadth_mm: float                 # Distance Alare Left to Alare Right (Al_L - Al_R)
    nasal_height_mm: float                 # Distance Nasion to Subnasale (N - Sn)
    nasal_projection_mm: float             # Distance Pronasale to Subnasale (Prn - Sn)
    facial_index_ratio: float              # I_F = (Facial Height / Alar Breadth) * 100
    facial_typology: str                   # "EURYPROSOPIC", "MESOPROSOPIC", or "LEPTOPROSOPIC"


@dataclass
class CraniofacialReconstructionResult:
    landmarks: CephalometricLandmarks
    indices: FacialIndices
    assayed_loci_count: int
    prosecutors_fallacy_shield: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class MorphometricsEngine:
    """
    FORENZA Craniofacial Morphometrics & 3D Shape Space Reconstruction Engine.
    
    Derives verbatim from Pillar 3 Research §3.
    """

    def __init__(self):
        self.loci = MORPHOMETRIC_LOCI

    def reconstruct_3d_landmarks(
        self,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> CephalometricLandmarks:
        """
        Reconstructs 7 primary 3D cephalometric landmarks (N, Prn, Sn, Al_L, Al_R, Ls, Me)
        using additive linear dosage models (Research §3.2).

        Enforces Bilateral Midline Symmetry Invariant:
          x_N = x_Prn = x_Sn = x_Ls = x_Me = 0.00
          x_Al_L = -x_Al_R
        """
        x_pax3 = float(snp_dosages.get("rs974448", 0))
        x_pax9 = float(snp_dosages.get("rs12882923", 0))
        x_prdm16 = float(snp_dosages.get("rs11130635", 0))
        x_dchs2 = float(snp_dosages.get("rs13289", 0))
        x_pcdh15 = float(snp_dosages.get("rs7559252", 0))

        # 1. Nasion (N)
        nasion = Point3D(
            x=0.00,
            y=12.4 + (1.25 * x_pax3),
            z=45.2 + (0.85 * x_pax3),
        )

        # 2. Pronasale (Prn - Nasal Tip)
        pronasale = Point3D(
            x=0.00,
            y=48.5 + (2.10 * x_prdm16) - (1.45 * x_dchs2),
            z=12.1 + (1.15 * x_prdm16),
        )

        # 3. Subnasale (Sn)
        subnasale = Point3D(
            x=0.00,
            y=38.2 - (1.10 * x_dchs2),
            z=-2.5 - (0.65 * x_dchs2),
        )

        # 4. Alare Left (Al_L) & Alare Right (Al_R)
        alar_x_offset = 18.5 + (0.95 * x_pax9)
        alar_y = 36.1 + (0.45 * x_pax9)
        alar_z = 2.1 + (0.30 * x_pax9)

        alare_left = Point3D(x=-alar_x_offset, y=alar_y, z=alar_z)
        alare_right = Point3D(x=+alar_x_offset, y=alar_y, z=alar_z)

        # 5. Labiale Superius (Ls)
        labiale_superius = Point3D(
            x=0.00,
            y=34.5 + (0.60 * x_pcdh15),
            z=-12.4 - (0.40 * x_pcdh15),
        )

        # 6. Menton (Me - Chin Base)
        menton = Point3D(
            x=0.00,
            y=18.2 + (1.85 * x_pcdh15),
            z=-68.5 - (1.20 * x_pcdh15),
        )

        return CephalometricLandmarks(
            nasion=nasion,
            pronasale=pronasale,
            subnasale=subnasale,
            alare_left=alare_left,
            alare_right=alare_right,
            labiale_superius=labiale_superius,
            menton=menton,
        )

    def calculate_facial_indices(
        self,
        landmarks: CephalometricLandmarks,
    ) -> FacialIndices:
        """
        Calculates morphological facial dimensions and clinical Facial Index (I_F).
        """
        # Morphological Facial Height: Distance Nasion to Menton
        facial_height = landmarks.nasion.distance_to(landmarks.menton)

        # Alar Breadth: Distance Alare Left to Alare Right
        alar_breadth = landmarks.alare_left.distance_to(landmarks.alare_right)

        # Nasal Height: Distance Nasion to Subnasale
        nasal_height = landmarks.nasion.distance_to(landmarks.subnasale)

        # Nasal Projection: Distance Pronasale to Subnasale
        nasal_proj = landmarks.pronasale.distance_to(landmarks.subnasale)

        # Facial Index Ratio I_F = (Height / Breadth) * 100
        if alar_breadth > 0:
            index_ratio = (facial_height / alar_breadth) * 100.0
        else:
            index_ratio = 100.0

        # Typology Classification
        # Research standard: Euryprosopic < 280 (broad), Mesoprosopic 280-310, Leptoprosopic > 310 (scaled relative to alar breadth)
        # Or standard morphological:
        if index_ratio < 290.0:
            typology = "EURYPROSOPIC (Broad Face)"
        elif index_ratio <= 315.0:
            typology = "MESOPROSOPIC (Average Face)"
        else:
            typology = "LEPTOPROSOPIC (Narrow/Long Face)"

        return FacialIndices(
            morphological_facial_height_mm=round(facial_height, 2),
            alar_breadth_mm=round(alar_breadth, 2),
            nasal_height_mm=round(nasal_height, 2),
            nasal_projection_mm=round(nasal_proj, 2),
            facial_index_ratio=round(index_ratio, 2),
            facial_typology=typology,
        )

    def analyze_craniofacial_morphology(
        self,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> CraniofacialReconstructionResult:
        """
        Full pipeline for 3D craniofacial reconstruction and clinical index extraction.
        """
        landmarks = self.reconstruct_3d_landmarks(snp_dosages)
        indices = self.calculate_facial_indices(landmarks)

        assayed_count = sum(1 for rsid in self.loci if rsid in snp_dosages)

        shield_statement = (
            "IMPORTANT (3D Craniofacial Legal Shield): Reconstructed 3D cephalometric landmarks "
            "and shape parameters represent statistical approximations of skeletal and soft-tissue morphology "
            "derived from validated GWAS effect sizes (Claes et al.). They indicate general anatomical proportions "
            "and must NEVER be used as a photo-exact facial identity match."
        )

        return CraniofacialReconstructionResult(
            landmarks=landmarks,
            indices=indices,
            assayed_loci_count=assayed_count,
            prosecutors_fallacy_shield=shield_statement,
        )
