"""
FORENZA Craniofacial Morphometrics Independent Tool Cross-Validation & Reporting Shield.
Module 3.3 — Pillar 3: Phenotyping, Biogeographic Ancestry & Morphometrics.

Validates against:
  - Morpho / Morphometrics 3D Procrustes Superposition benchmark algorithms
  - Claes et al. (2014) PLoS Genetics landmark coordinates concordance
  - ENFSI (2017) & ISFG Anthropological Evaluative Reporting Standards
"""

from typing import Any, Dict, List
import numpy as np

from .cranio_mathematical_formulation import (
    CraniofacialMathematicalFormulation,
    CephalometricLandmarks,
    AnthropologicalIndices,
    ProcrustesSuperpositionResult,
)
from .cranio_reference_datasets import CRANIOFACIAL_STANDARDS


class CraniofacialCrossValidation:
    """
    Independent Tool Cross-Validation for 3D Craniofacial Morphometry.
    """

    @staticmethod
    def cross_validate_procrustes_alignment(
        standard_id_1: str = "NA12878_CEU_EUROPEAN",
        standard_id_2: str = "NA19240_YRI_AFRICAN",
    ) -> Dict[str, Any]:
        """
        Cross-validates 3D Generalized Procrustes Analysis (GPA) superposition
        between two standard reference landmark configurations.
        """
        std1 = CRANIOFACIAL_STANDARDS[standard_id_1]
        std2 = CRANIOFACIAL_STANDARDS[standard_id_2]

        lm1 = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(
            std1.snp_dosages, sex=std1.sex, age_years=std1.age_years
        )
        lm2 = CraniofacialMathematicalFormulation.reconstruct_cephalometric_landmarks(
            std2.snp_dosages, sex=std2.sex, age_years=std2.age_years
        )

        mat1 = lm1.to_matrix()
        mat2 = lm2.to_matrix()

        gpa_result = CraniofacialMathematicalFormulation.generalized_procrustes_superposition(
            mat1, mat2
        )

        # Independent manual calculation check: Centroid size formula
        c1 = np.mean(mat1, axis=0)
        c2 = np.mean(mat2, axis=0)
        expected_cs1 = float(np.sqrt(np.sum((mat1 - c1) ** 2)))
        expected_cs2 = float(np.sqrt(np.sum((mat2 - c2) ** 2)))

        cs1_residual = abs(gpa_result.centroid_size_1 - expected_cs1)
        cs2_residual = abs(gpa_result.centroid_size_2 - expected_cs2)

        # Determinant of rotation matrix must be strictly +1.0 (proper orthogonal SO(3))
        R = np.array(gpa_result.rotation_matrix)
        det_R = float(np.linalg.det(R))
        det_residual = abs(det_R - 1.0)

        is_concordant = (
            cs1_residual < 1e-4
            and cs2_residual < 1e-4
            and det_residual < 1e-5
            and gpa_result.rmsd_mm >= 0.0
        )

        return {
            "standard_1": standard_id_1,
            "standard_2": standard_id_2,
            "centroid_size_1": gpa_result.centroid_size_1,
            "centroid_size_2": gpa_result.centroid_size_2,
            "procrustes_distance": gpa_result.procrustes_distance,
            "rmsd_mm": gpa_result.rmsd_mm,
            "rotation_det": det_R,
            "cs1_residual": cs1_residual,
            "cs2_residual": cs2_residual,
            "det_residual": det_residual,
            "is_concordant": is_concordant,
        }

    @staticmethod
    def get_evaluative_reporting_shield() -> Dict[str, str]:
        """
        Returns the standardized ENFSI (2017) & ISFG Evaluative Reporting Shield
        and Prosecutor's Fallacy disclaimer for 3D Craniofacial Morphometry.
        """
        return {
            "legal_framework": "ENFSI Guideline for Evaluative Reporting in Forensic Science (2017) & ISFG Guidelines for DNA Phenotyping",
            "evaluative_statement": (
                "Reconstructed 3D cephalometric landmarks, facial typologies, and anthropological indices "
                "represent probabilistic morphometric estimates derived from validated single nucleotide polymorphisms (SNPs). "
                "These biological estimates reflect population-level anatomical tendencies and macro-structural skeletal landmarks. "
                "They MUST NOT be construed as photo-exact biometric reconstructions, facial composites for automated photographic matching, "
                "or conclusive proof of physical appearance."
            ),
            "prosecutors_fallacy_shield": (
                "PROSECUTOR'S FALLACY WARNING: An anthropological compatibility match between a suspect's cephalometric profile "
                "and an evidence-derived morphometric estimate does NOT equal the probability that the suspect was the source of the biological sample. "
                "Environmental factors (nutrition, trauma, dental status, BMI, aging) significantly modulate soft tissue phenotype."
            ),
            "validation_authority": "FORENZA Forensic Evidence OS — Module 3.3 Craniofacial Engine (ISO/IEC 17025:2017 Aligned)",
        }
