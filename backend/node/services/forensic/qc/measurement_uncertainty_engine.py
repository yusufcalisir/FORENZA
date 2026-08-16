r"""
FORENZA ISO/IEC 17025:2017 Measurement Uncertainty & Calibration Budget Engine — Module 28.

Implements verbatim from Pillar 6 Research §3 & §6:
  - §3.1 Combined and Expanded Measurement Uncertainty (GUM / JCGM 100:2008 & k=2.00 Coverage Factor)
  - §3.2 Quantitative Calibration Uncertainty Budget & Proficiency Testing z-Scores
  - ISO/IEC 17025:2017 Clause 7.6 & Federal Rules of Evidence (FRE 702) Metrological Safeguards
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class UncertaintyComponent:
    """Represents a single input quantity x_i in the GUM uncertainty budget."""
    name: str
    standard_uncertainty: float  # u_i (e.g. in ng/uL)
    probability_distribution: str = "NORMAL"  # "NORMAL", "RECTANGULAR", "TRIANGULAR"
    sensitivity_coefficient: float = 1.00     # c_i = df/dx_i
    description: Optional[str] = None


class ForensicMeasurementUncertaintyEngine:
    """
    FORENZA ISO/IEC 17025 Metrological Measurement Uncertainty Engine.

    Derives verbatim from Pillar 6 Research §3 & §6.
    """

    # Canonical 4-component calibration budget from Research §3.2 (VECTOR_P6_02 Ground Truth)
    CANONICAL_BUDGET: List[UncertaintyComponent] = [
        UncertaintyComponent(
            name="Micro-Pipette Volume (x1)",
            standard_uncertainty=0.013228756555322953,  # Rectangular variance contribution = 0.000175
            probability_distribution="RECTANGULAR",
            sensitivity_coefficient=1.00,
            description="ISO 8655 volumetric dispensing variance",
        ),
        UncertaintyComponent(
            name="Thermal Gradient (x2)",
            standard_uncertainty=0.015,
            probability_distribution="NORMAL",
            sensitivity_coefficient=1.00,
            description="Thermal cycler block temperature heterogeneity",
        ),
        UncertaintyComponent(
            name="qPCR Standard Curve (x3)",
            standard_uncertainty=0.030,
            probability_distribution="NORMAL",
            sensitivity_coefficient=1.00,
            description="Serial dilution standard curve regression variance",
        ),
        UncertaintyComponent(
            name="Master Mix Amplification (x4)",
            standard_uncertainty=0.040,
            probability_distribution="NORMAL",
            sensitivity_coefficient=1.00,
            description="Polymerase enzymatic amplification efficiency drift",
        ),
    ]


    def calculate_uncertainty_budget(
        self,
        nominal_concentration: float,
        components: Optional[List[UncertaintyComponent]] = None,
        correlations: Optional[Dict[str, float]] = None,
        coverage_factor: float = 2.00,
    ) -> Dict[str, Any]:
        """
        Calculates GUM combined and expanded measurement uncertainty (Research §3.1 & §3.2).

        Formula:
          u_c^2(y) = sum (c_i * u_i)^2 + 2 * sum_{i<j} c_i * c_j * r_ij * u_i * u_j
          U_95% = k * u_c(y) (k = 2.00 for 95.45% confidence)
          Interval = [y - U_95%, y + U_95%]
        """
        if nominal_concentration < 0.0:
            raise ValueError("Nominal concentration must be non-negative.")
        if coverage_factor <= 0.0:
            raise ValueError("Coverage factor k must be greater than zero.")

        budget_components = components if (components is not None and len(components) > 0) else self.CANONICAL_BUDGET

        # 1. Sum variance contributions
        variance_sum = 0.0
        component_details: List[Dict[str, Any]] = []

        for comp in budget_components:
            if comp.standard_uncertainty < 0.0:
                raise ValueError(f"Standard uncertainty for {comp.name} cannot be negative.")
            c_i = comp.sensitivity_coefficient
            u_i = comp.standard_uncertainty
            var_contrib = (c_i * u_i) ** 2
            variance_sum += var_contrib

        # 2. Add covariance terms if correlations are provided
        covariance_sum = 0.0
        if correlations:
            n = len(budget_components)
            for i in range(n):
                for j in range(i + 1, n):
                    pair_key = f"{budget_components[i].name}:{budget_components[j].name}"
                    alt_key = f"{budget_components[j].name}:{budget_components[i].name}"
                    r_ij = correlations.get(pair_key, correlations.get(alt_key, 0.0))
                    if r_ij != 0.0:
                        c_i = budget_components[i].sensitivity_coefficient
                        u_i = budget_components[i].standard_uncertainty
                        c_j = budget_components[j].sensitivity_coefficient
                        u_j = budget_components[j].standard_uncertainty
                        cov_term = 2.0 * c_i * c_j * r_ij * u_i * u_j
                        covariance_sum += cov_term

        total_variance = variance_sum + covariance_sum
        if total_variance < 0.0:
            raise ValueError("Negative total variance derived from covariance matrix.")

        combined_standard_uncertainty = math.sqrt(total_variance)
        expanded_uncertainty = coverage_factor * combined_standard_uncertainty

        # 3. Calculate percentage variance contributions
        for comp in budget_components:
            c_i = comp.sensitivity_coefficient
            u_i = comp.standard_uncertainty
            var_contrib = (c_i * u_i) ** 2
            pct_contrib = (var_contrib / total_variance * 100.0) if total_variance > 0.0 else 0.0
            component_details.append({
                "component_name": comp.name,
                "standard_uncertainty": u_i,
                "sensitivity_coefficient": c_i,
                "probability_distribution": comp.probability_distribution,
                "variance_contribution": round(var_contrib, 8),
                "percentage_contribution": round(pct_contrib, 2),
                "description": comp.description,
            })

        lower_bound = max(0.0, nominal_concentration - expanded_uncertainty)
        upper_bound = nominal_concentration + expanded_uncertainty

        shield_statement = (
            "IMPORTANT (ISO/IEC 17025:2017 Clause 7.6 & FRE 702 Metrological Uncertainty Shield): "
            "Quantitative forensic DNA estimates are reported with combined standard uncertainty (u_c) "
            "and expanded uncertainty at 95.45% confidence (k = 2.00). Deterministic calibration budgets "
            "ensure compliance with international forensic metrology standards."
        )

        return {
            "nominal_concentration": round(nominal_concentration, 5),
            "combined_standard_uncertainty": round(combined_standard_uncertainty, 5),
            "expanded_uncertainty": round(expanded_uncertainty, 5),
            "coverage_factor": coverage_factor,
            "confidence_level": "95.45%",
            "reported_interval": {
                "lower_bound": round(lower_bound, 5),
                "upper_bound": round(upper_bound, 5),
                "formatted_interval": f"{nominal_concentration:.3f} ± {expanded_uncertainty:.3f} ng/uL",
            },
            "total_variance": round(total_variance, 8),
            "component_count": len(budget_components),
            "components": component_details,
            "prosecutors_fallacy_shield": shield_statement,
        }

    def evaluate_proficiency_z_score(
        self,
        lab_measured_value: float,
        consensus_mean: float,
        consensus_std: float,
    ) -> Dict[str, Any]:
        """
        Evaluates Proficiency Testing Consensus z-Score (Research §3.2):
          z = (x_lab - mu_consensus) / sigma_consensus

        Classification Tiers:
          |z| <= 2.0: SATISFACTORY (Fully Calibrated)
          2.0 < |z| < 3.0: QUESTIONABLE (Warning State)
          |z| >= 3.0: UNSATISFACTORY (Non-Compliant Alert)
        """
        if consensus_std <= 0.0:
            raise ValueError("Consensus standard deviation must be strictly positive.")

        z_score = (lab_measured_value - consensus_mean) / consensus_std
        abs_z = abs(z_score)

        if abs_z <= 2.0:
            tier = "SATISFACTORY"
            verdict = "Satisfactory / Fully Calibrated (ISO/IEC 17025 Compliant)"
            is_compliant = True
        elif abs_z < 3.0:
            tier = "QUESTIONABLE"
            verdict = "Questionable / Warning State (Requires Internal Metrological Review)"
            is_compliant = False
        else:
            tier = "UNSATISFACTORY"
            verdict = "Unsatisfactory / Non-Compliant (Immediate Corrective Action Required)"
            is_compliant = False

        return {
            "lab_measured_value": round(lab_measured_value, 5),
            "consensus_mean": round(consensus_mean, 5),
            "consensus_std": round(consensus_std, 5),
            "z_score": round(z_score, 4),
            "absolute_z_score": round(abs_z, 4),
            "performance_tier": tier,
            "verdict": verdict,
            "is_compliant": is_compliant,
        }
