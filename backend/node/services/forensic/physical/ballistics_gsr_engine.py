"""
FORENZA Forensic Ballistics, SEM-EDX GSR & 3D CMC Striation Engine — Module 22.

Implements verbatim from Pillar 5 Research §2 & §6:
  - §2.1 Quantitative SEM-EDX GSR Particle Classification (ASTM E1588-20)
  - §2.2 Congruent Matching Cells (CMC) Algorithm for 3D Toolmarks & Striations
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union


# ── Constants ─────────────────────────────────────────────────────────────────

MIN_ELEMENT_THRESHOLD_PERCENT: float = 10.0
MAX_CHARACTERISTIC_ASPECT_RATIO: float = 1.3
MAX_CONSISTENT_ASPECT_RATIO: float = 1.5

MIN_CCF_THRESHOLD: float = 0.55
MAX_TRANSLATION_TOLERANCE_UM: float = 15.0
MAX_ROTATION_TOLERANCE_DEG: float = 1.0
MIN_CMC_FOR_IDENTIFICATION: int = 6


# ── Engine ─────────────────────────────────────────────────────────────────────

class BallisticsGsrEngine:
    """
    FORENZA Forensic Ballistics, SEM-EDX GSR & 3D CMC Striation Engine.

    Derives verbatim from Pillar 5 Research §2 & §6.
    """

    def evaluate_sem_edx_gsr(
        self,
        particles: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Classifies SEM-EDX GSR particles according to ASTM E1588-20 and computes
        the evidentiary Likelihood Ratio (Research §2.1 & §6).
        """
        if not particles:
            raise ValueError("Particles list must be non-empty for SEM-EDX GSR evaluation.")

        characteristic_count = 0
        consistent_count = 0
        associated_count = 0
        particle_classifications = []

        for idx, p in enumerate(particles):
            pb = float(p.get("pb", p.get("pb_percent", 0.0)))
            ba = float(p.get("ba", p.get("ba_percent", 0.0)))
            sb = float(p.get("sb", p.get("sb_percent", 0.0)))
            al = float(p.get("al", p.get("al_percent", 0.0)))
            aspect_ratio = float(p.get("aspect_ratio", 1.0))


            if aspect_ratio <= 0.0:
                raise ValueError(f"Aspect ratio for particle {idx} must be positive, got {aspect_ratio}.")

            # Characteristic GSR: Pb-Ba-Sb triad >= 10% wt and aspect ratio <= 1.3
            if (
                pb >= MIN_ELEMENT_THRESHOLD_PERCENT
                and ba >= MIN_ELEMENT_THRESHOLD_PERCENT
                and sb >= MIN_ELEMENT_THRESHOLD_PERCENT
                and aspect_ratio <= MAX_CHARACTERISTIC_ASPECT_RATIO
            ):
                tier = "CHARACTERISTIC_GSR"
                characteristic_count += 1
            # Consistent with GSR: 2-component pairs >= 10% wt and aspect ratio <= 1.5
            elif (
                (
                    (pb >= MIN_ELEMENT_THRESHOLD_PERCENT and ba >= MIN_ELEMENT_THRESHOLD_PERCENT)
                    or (pb >= MIN_ELEMENT_THRESHOLD_PERCENT and sb >= MIN_ELEMENT_THRESHOLD_PERCENT)
                    or (ba >= MIN_ELEMENT_THRESHOLD_PERCENT and sb >= MIN_ELEMENT_THRESHOLD_PERCENT)
                )
                and aspect_ratio <= MAX_CONSISTENT_ASPECT_RATIO
            ):
                tier = "CONSISTENT_WITH_GSR"
                consistent_count += 1
            # Commonly Associated: Single elements or Ba-Al
            elif (
                pb >= MIN_ELEMENT_THRESHOLD_PERCENT
                or ba >= MIN_ELEMENT_THRESHOLD_PERCENT
                or (ba >= MIN_ELEMENT_THRESHOLD_PERCENT and al >= MIN_ELEMENT_THRESHOLD_PERCENT)
            ):
                tier = "COMMONLY_ASSOCIATED"
                associated_count += 1
            else:
                tier = "ENVIRONMENTAL_BACKGROUND"

            particle_classifications.append({
                "particle_id": p.get("particle_id", f"p_{idx+1}"),
                "classification_tier": tier,
                "pb_percent": pb,
                "ba_percent": ba,
                "sb_percent": sb,
                "aspect_ratio": aspect_ratio,
            })

        # Likelihood Ratio & Evaluative Strength (Research §2.1 & §6)
        if characteristic_count >= 3:
            strength = "Extremely Strong Support for Firearm Discharge (LR > 10,000)"
            lr = 10000.0
        elif characteristic_count >= 1 or consistent_count >= 5:
            strength = "Strong Support for Firearm Discharge (100 < LR <= 10,000)"
            lr = 500.0
        elif consistent_count >= 1:
            strength = "Moderate Support for Firearm Discharge (10 < LR <= 100)"
            lr = 25.0
        else:
            strength = "Inconclusive / Neutral Support (LR = 1.0)"
            lr = 1.0

        shield_statement = (
            "IMPORTANT (ASTM E1588-20 SEM-EDX GSR Evaluative Legal Shield): Finding characteristic Pb-Ba-Sb particles "
            "indicates proximity to a firearm discharge event, but cannot identify the specific shooter or exclude "
            "secondary transfer from contaminated law enforcement environments."
        )

        return {
            "total_particles_scanned": len(particles),
            "characteristic_particles": characteristic_count,
            "consistent_particles": consistent_count,
            "commonly_associated_particles": associated_count,
            "likelihood_ratio": lr,
            "evidence_strength": strength,
            "classified_particles": particle_classifications,
            "prosecutors_fallacy_shield": shield_statement,
        }

    def evaluate_3d_cmc_striations(
        self,
        cells: List[Dict[str, Any]],
        mean_delta_x_um: float = 0.0,
        mean_delta_y_um: float = 0.0,
        mean_delta_theta_deg: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Evaluates 3D Congruent Matching Cells (CMC) for firearm land engraved striation comparison
        (Research §2.2).
        """
        if not cells:
            raise ValueError("Cells list must be non-empty for 3D CMC striation analysis.")

        cmc_count = 0
        evaluated_cells = []

        for idx, cell in enumerate(cells):
            cid = cell.get("cell_id", f"cell_{idx+1}")
            ccf_max = float(cell.get("ccf_max", 0.0))
            dx = float(cell.get("delta_x_um", 0.0))
            dy = float(cell.get("delta_y_um", 0.0))
            dtheta = float(cell.get("delta_theta_deg", 0.0))

            # Tri-threshold test
            is_ccf_passed = ccf_max >= MIN_CCF_THRESHOLD
            is_trans_passed = (
                abs(dx - mean_delta_x_um) <= MAX_TRANSLATION_TOLERANCE_UM
                and abs(dy - mean_delta_y_um) <= MAX_TRANSLATION_TOLERANCE_UM
            )
            is_rot_passed = abs(dtheta - mean_delta_theta_deg) <= MAX_ROTATION_TOLERANCE_DEG

            is_cmc = is_ccf_passed and is_trans_passed and is_rot_passed
            if is_cmc:
                cmc_count += 1

            evaluated_cells.append({
                "cell_id": cid,
                "ccf_max": ccf_max,
                "delta_x_um": dx,
                "delta_y_um": dy,
                "delta_theta_deg": dtheta,
                "is_congruent_matching_cell": is_cmc,
            })

        # Identification criteria (Research §2.2: K >= 6 CMC -> P_false < 10^-6)
        if cmc_count >= MIN_CMC_FOR_IDENTIFICATION:
            verdict = "POSITIVE_IDENTIFICATION"
            p_false = "< 1e-6"
            conclusion = "Definitive ballistic match to questioned firearm (K >= 6 CMC, P_false < 10^-6)."
        elif cmc_count >= 3:
            verdict = "INCONCLUSIVE_BORDERLINE"
            p_false = "0.01 - 0.05"
            conclusion = "Inconclusive / Borderline striation similarity (3 <= K <= 5 CMC)."
        else:
            verdict = "ELIMINATION_NO_MATCH"
            p_false = "> 0.50"
            conclusion = "Elimination / Non-match (K < 3 CMC)."

        shield_statement = (
            "IMPORTANT (3D CMC Ballistic Striation Legal Shield - AFTE Criteria): Identification is established "
            "when K >= 6 congruent matching cells satisfy cross-correlation (CCF >= 0.55), translation (+/-15 um), "
            "and rotation (+/-1.0 deg) tolerances, providing statistical error bounds of P_false < 10^-6."
        )

        return {
            "total_cells_evaluated": len(cells),
            "cmc_count": cmc_count,
            "identification_verdict": verdict,
            "false_match_probability": p_false,
            "ballistic_conclusion": conclusion,
            "evaluated_cells": evaluated_cells,
            "prosecutors_fallacy_shield": shield_statement,
        }
