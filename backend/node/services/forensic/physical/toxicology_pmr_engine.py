r"""
FORENZA Forensic Toxicology, Pharmacokinetics & Post-Mortem Drug Redistribution (PMR) Engine — Module 25.

Implements verbatim from Pillar 5 Research §5 & §6:
  - §5.1 Physicochemical Determinants of PMR and C_heart / C_femoral (C/P) Ratios
  - §5.2 Elimination Kinetics and Antemortem Back-Extrapolation (Zero-Order Widmark & First-Order Half-Life)
  - SOFT / TIAFT Evaluative Post-Mortem Toxicology Guidelines
"""

import math
from typing import Dict, Any, List, Optional


# ── Xenobiotic Reference Database (Research §5.1 & §6 Artifact A) ─────────────

XENOBIOTIC_DATABASE: Dict[str, Dict[str, Any]] = {
    "Ethanol": {
        "vd_l_kg": 0.6,
        "log_p": -0.31,
        "pka": None,
        "cp_ratio_mean": 1.00,
        "cp_ratio_std": 0.10,
        "pmr_risk": "Low / Minimal",
        "elimination_type": "Zero-Order",
        "beta_60_g_l_h": 0.15,
        "half_life_hours": None,
        "guideline": "Uniform distribution; evaluate post-mortem microbial neo-formation in putrefaction.",
    },
    "Acetaminophen": {
        "vd_l_kg": 0.9,
        "log_p": 0.46,
        "pka": 9.5,
        "cp_ratio_mean": 1.05,
        "cp_ratio_std": 0.12,
        "pmr_risk": "Low",
        "elimination_type": "First-Order",
        "beta_60_g_l_h": None,
        "half_life_hours": 2.5,
        "guideline": "C_heart ≈ C_femoral; minimal diffusion artifact.",
    },
    "Morphine": {
        "vd_l_kg": 3.5,
        "log_p": 0.89,
        "pka": 8.0,
        "cp_ratio_mean": 1.80,
        "cp_ratio_std": 0.40,
        "pmr_risk": "Moderate",
        "elimination_type": "First-Order",
        "beta_60_g_l_h": None,
        "half_life_hours": 3.0,
        "guideline": "Moderate redistribution from liver/lung depots; peripheral femoral blood required.",
    },
    "Methamphetamine": {
        "vd_l_kg": 4.0,
        "log_p": 2.07,
        "pka": 9.9,
        "cp_ratio_mean": 2.10,
        "cp_ratio_std": 0.50,
        "pmr_risk": "High",
        "elimination_type": "First-Order",
        "beta_60_g_l_h": None,
        "half_life_hours": 10.0,
        "guideline": "Significant pulmonary/myocardial tissue release; cardiac blood drastically overestimates toxicity.",
    },
    "Fentanyl": {
        "vd_l_kg": 5.0,
        "log_p": 4.05,
        "pka": 8.4,
        "cp_ratio_mean": 2.80,
        "cp_ratio_std": 0.70,
        "pmr_risk": "High / Severe",
        "elimination_type": "First-Order",
        "beta_60_g_l_h": None,
        "half_life_hours": 7.0,
        "guideline": "Pronounced post-mortem lung-to-heart diffusion; femoral venous blood mandatory.",
    },
    "Amitriptyline": {
        "vd_l_kg": 20.0,
        "log_p": 4.92,
        "pka": 9.4,
        "cp_ratio_mean": 4.50,
        "cp_ratio_std": 1.20,
        "pmr_risk": "Very High",
        "elimination_type": "First-Order",
        "beta_60_g_l_h": None,
        "half_life_hours": 21.0,
        "guideline": "Massive myocardial release; cardiac blood up to 500% elevated above antemortem systemic level.",
    },
}


class ForensicToxicologyPmrEngine:
    """
    FORENZA Post-Mortem Toxicokinetics & Drug Redistribution (PMR) Engine.

    Derives verbatim from Pillar 5 Research §5 & §6.
    """

    def evaluate_pmr_ratio(
        self,
        compound_name: str,
        c_heart: float,
        c_femoral: float,
        unit: str = "mg/L",
    ) -> Dict[str, Any]:
        """
        Calculates observed central-to-peripheral (C_heart / C_femoral) ratio
        and performs risk assessment against empirical literature benchmarks.
        """
        if c_heart < 0 or c_femoral <= 0:
            raise ValueError("c_heart must be non-negative and c_femoral must be strictly positive.")

        cp_observed = round(c_heart / c_femoral, 3)

        # Retrieve compound reference data (or generic fallback)
        info = XENOBIOTIC_DATABASE.get(compound_name)
        if not info:
            info = {
                "vd_l_kg": 3.0,
                "log_p": 1.5,
                "pka": None,
                "cp_ratio_mean": 1.50,
                "cp_ratio_std": 0.50,
                "pmr_risk": "Moderate",
                "elimination_type": "First-Order",
                "beta_60_g_l_h": None,
                "half_life_hours": 6.0,
                "guideline": "Uncataloged xenobiotic; exercise caution with central blood sampling.",
            }

        vd = info["vd_l_kg"]
        pmr_risk = info["pmr_risk"]

        # Determine overestimation alert
        is_overestimated = (cp_observed > 2.0 and vd > 3.0) or (cp_observed > 1.5 * info["cp_ratio_mean"])
        overestimation_pct = max(0.0, round(((c_heart - c_femoral) / c_femoral) * 100.0, 1))

        if is_overestimated:
            alert = (
                f"HIGH PMR OVERESTIMATION ALERT: Heart blood concentration ({c_heart} {unit}) is "
                f"{overestimation_pct}% higher than peripheral femoral blood ({c_femoral} {unit}). "
                f"Post-mortem diffusion from high Vd ({vd} L/kg) tissue depots overestimates antemortem systemic toxicity."
            )
        else:
            alert = f"Heart and femoral concentrations are consistent with low/expected PMR (C/P = {cp_observed})."

        shield_statement = (
            "IMPORTANT (SOFT / TIAFT Post-Mortem Toxicology Evaluative Shield): Post-mortem cardiac blood concentrations "
            "cannot be directly translated to antemortem intoxication levels due to post-mortem drug redistribution (PMR). "
            "Femoral venous blood is the legal gold standard for quantitative forensic back-extrapolation."
        )

        return {
            "compound_name": compound_name,
            "c_heart": c_heart,
            "c_femoral": c_femoral,
            "unit": unit,
            "cp_observed": cp_observed,
            "cp_literature_mean": info["cp_ratio_mean"],
            "vd_l_kg": vd,
            "pmr_risk_tier": pmr_risk,
            "is_cardiac_overestimated": is_overestimated,
            "overestimation_percentage": overestimation_pct,
            "clinical_guideline": info["guideline"],
            "alert_message": alert,
            "prosecutors_fallacy_shield": shield_statement,
        }

    def extrapolate_antemortem_concentration(
        self,
        compound_name: str,
        c_femoral: float,
        elapsed_hours: float,
        unit: str = "mg/L",
        custom_half_life_hours: Optional[float] = None,
        custom_beta_60: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Back-extrapolates antemortem concentration at time (t_death - elapsed_hours)
        using zero-order (Ethanol Widmark) or first-order elimination kinetics (Research §5.2).
        """
        if c_femoral <= 0:
            raise ValueError("Peripheral femoral concentration (c_femoral) must be strictly positive.")
        if elapsed_hours < 0:
            raise ValueError("Elapsed hours must be non-negative.")

        info = XENOBIOTIC_DATABASE.get(compound_name)
        elim_type = info["elimination_type"] if info else "First-Order"

        if elim_type == "Zero-Order" or compound_name.lower() == "ethanol":
            beta_60 = custom_beta_60 if custom_beta_60 is not None else (info.get("beta_60_g_l_h") or 0.15)
            # C_antemortem = C_femoral + beta_60 * elapsed_hours
            c_antemortem = c_femoral + (beta_60 * elapsed_hours)
            ke = None
            half_life = None
            kinetic_formula = f"Zero-Order Widmark: C_antemortem = C_femoral + ({beta_60} * {elapsed_hours}h)"
        else:
            half_life = custom_half_life_hours if custom_half_life_hours is not None else (
                info.get("half_life_hours") if info else 6.0
            )
            if half_life is None or half_life <= 0:
                half_life = 6.0
            ke = round(math.log(2.0) / half_life, 5)
            # C_antemortem = C_femoral * exp(ke * elapsed_hours)
            c_antemortem = c_femoral * math.exp(ke * elapsed_hours)
            beta_60 = None
            kinetic_formula = f"First-Order: C_antemortem = C_femoral * exp({ke} * {elapsed_hours}h)"

        return {
            "compound_name": compound_name,
            "c_femoral_postmortem": c_femoral,
            "elapsed_hours": elapsed_hours,
            "c_antemortem_extrapolated": round(c_antemortem, 4),
            "unit": unit,
            "elimination_type": elim_type,
            "elimination_rate_constant_ke_h": ke,
            "half_life_hours": half_life,
            "beta_60_g_l_h": beta_60,
            "kinetic_formula": kinetic_formula,
            "prosecutors_fallacy_shield": (
                "NOTE (SOFT / TIAFT Kinematic Extrapolation Shield): Antemortem back-extrapolation assumes linear "
                "or exponential clearance in an uncompromised circulatory system prior to somatic death. "
                "Post-mortem interval and agonal phase multi-organ failure can influence clearance rates."
            )
        }
