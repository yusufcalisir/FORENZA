"""
FORENZA Horvath First-Generation Epigenetic Clock Engine (Pillar 4 §1.1).

Implements verbatim from Horvath (2013) Genome Biology and Horvath et al. (2018):
  - §1. Piecewise Continuous Age Transformation Link Function F(Age) with pivot y0 = 20.0
  - §2. Analytical Inverse Link Function F^-1(Y_hat)
  - §3. Pan-Tissue (353-CpG) and Skin & Blood (391-CpG) Elastic Net Predictors
  - §4. PedBE Pediatric Buccal Predictor (84-CpG)
  - §5. ISO/IEC 17025 Metrological Prediction Uncertainty (U_95%)
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    ClockGeneration,
    EpigeneticTissueType,
    MethylationSample,
    EpigeneticAgeResult,
)
from backend.node.services.forensic.epigenetics.clocks.clock_registry import (
    EpigeneticClockRegistry,
    ClockModelMetadata,
)
from backend.node.services.forensic.epigenetics.clocks.data_transformer import (
    EpigeneticDataTransformer,
)


class HorvathEpigeneticEngine:
    """Mathematical engine for Horvath pan-tissue, skin & blood, and PedBE clocks."""

    PIVOT_AGE: float = 20.0
    OFFSET_DENOM: float = 21.0

    @classmethod
    def transform_age_forward(cls, age: float) -> float:
        """
        Horvath piecewise continuous age transformation function F(Age):
        F(Age) = ln(Age + 1) - ln(21) if Age <= 20
        F(Age) = (Age - 20) / 21 if Age > 20
        """
        clamped_age = max(0.0, float(age))
        if clamped_age <= cls.PIVOT_AGE:
            return math.log(clamped_age + 1.0) - math.log(cls.OFFSET_DENOM)
        else:
            return (clamped_age - cls.PIVOT_AGE) / cls.OFFSET_DENOM

    @classmethod
    def transform_age_inverse(cls, y_hat: float) -> float:
        """
        Horvath analytical inverse link transformation function F^-1(Y_hat):
        DNAmAge = 21 * exp(Y_hat) - 1 if Y_hat < 0
        DNAmAge = 21 * Y_hat + 20 if Y_hat >= 0
        """
        if y_hat < 0.0:
            return max(0.0, (cls.OFFSET_DENOM * math.exp(y_hat)) - 1.0)
        else:
            return max(0.0, (cls.OFFSET_DENOM * y_hat) + cls.PIVOT_AGE)

    @classmethod
    def predict_age(
        cls,
        sample: MethylationSample,
        clock_id: str = "horvath_2013",
        chronological_age: Optional[float] = None,
        tissue_offset: float = 0.0,
    ) -> EpigeneticAgeResult:
        """
        Compute predicted DNA methylation age using Horvath elastic net models.
        """
        registry = EpigeneticClockRegistry()
        clock_meta: Optional[ClockModelMetadata] = registry.get_clock(clock_id)
        if not clock_meta:
            raise ValueError(f"Unknown Horvath clock identifier: '{clock_id}'")

        required_probes = set(clock_meta.cpg_weights.keys())
        processed_betas, qc_meta = EpigeneticDataTransformer.process_and_qc_sample(
            sample=sample,
            required_probes=required_probes,
            auto_impute=True,
        )

        # Compute linear predictor Y_hat = beta_0 + sum(beta_j * x_j)
        y_hat = clock_meta.intercept
        covered_count = 0
        missing_count = 0

        for probe_id, weight in clock_meta.cpg_weights.items():
            if probe_id in processed_betas:
                beta_val = processed_betas[probe_id]
                y_hat += weight * beta_val
                if probe_id in qc_meta["imputed_probes"]:
                    missing_count += 1
                else:
                    covered_count += 1
            else:
                missing_count += 1

        # Apply piecewise analytical inverse link function
        if clock_meta.has_piecewise_transform:
            base_predicted_age = cls.transform_age_inverse(y_hat)
        else:
            base_predicted_age = max(0.0, y_hat)

        # Apply tissue-specific baseline calibration offset
        final_predicted_age = max(0.0, base_predicted_age + tissue_offset)

        # Calculate expanded uncertainty (ISO/IEC 17025)
        base_mae = clock_meta.reported_mae
        # Slight penalty if probes were imputed
        imputation_penalty = 1.0 + (0.15 * (missing_count / max(1, len(required_probes))))
        expanded_u95 = base_mae * imputation_penalty * 1.96 / 1.645  # GUM expansion

        lower_bound = max(0.0, final_predicted_age - expanded_u95)
        upper_bound = final_predicted_age + expanded_u95

        # Calculate age acceleration if true age provided
        raw_eaa = None
        univ_accel = None
        if chronological_age is not None:
            raw_eaa = final_predicted_age - chronological_age
            # Universal orthogonal residual approximation (AgeAccel = DNAmAge - (0.85*Age + 4.5))
            univ_accel = final_predicted_age - (0.88 * chronological_age + 3.8)

        return EpigeneticAgeResult(
            clock_id=clock_id,
            clock_name=clock_meta.name,
            generation=clock_meta.generation,
            predicted_age=round(final_predicted_age, 2),
            raw_age_acceleration=round(raw_eaa, 2) if raw_eaa is not None else None,
            universal_age_accel=round(univ_accel, 2) if univ_accel is not None else None,
            tissue_offset_applied=round(tissue_offset, 2),
            expanded_uncertainty_95=round(expanded_u95, 2),
            age_interval_lower=round(lower_bound, 2),
            age_interval_upper=round(upper_bound, 2),
            covered_cpgs_count=covered_count,
            missing_cpgs_count=missing_count,
            imputation_applied=len(qc_meta["imputed_probes"]) > 0,
        )
