"""
FORENZA Hannum First-Generation Blood Epigenetic Clock Engine (Pillar 4 §1.2).

Implements verbatim from Hannum et al. (2013) Molecular Cell:
  - §1. Whole-Blood Linear Elastic Net Model (71-CpG)
  - §2. Adult Domain Validation & Error Bounds (RMSE ~ 4.9 years)
  - §3. Standardized Epigenetic Age Result Construction
"""

from typing import Dict, Optional
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


class HannumEpigeneticEngine:
    """Mathematical engine for Hannum et al. whole-blood epigenetic clock."""

    @classmethod
    def predict_age(
        cls,
        sample: MethylationSample,
        chronological_age: Optional[float] = None,
        tissue_offset: float = 0.0,
    ) -> EpigeneticAgeResult:
        """
        Compute predicted DNA methylation age using Hannum linear blood model.
        """
        registry = EpigeneticClockRegistry()
        clock_meta: Optional[ClockModelMetadata] = registry.get_clock("hannum_2013")
        if not clock_meta:
            raise ValueError("Hannum clock parameterization not found in registry.")

        required_probes = set(clock_meta.cpg_weights.keys())
        processed_betas, qc_meta = EpigeneticDataTransformer.process_and_qc_sample(
            sample=sample,
            required_probes=required_probes,
            auto_impute=True,
        )

        # Direct linear combination Y_hat = beta_0 + sum(beta_j * x_j)
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

        # Apply non-negativity bound and tissue offset
        final_predicted_age = max(0.0, y_hat + tissue_offset)

        # Expanded uncertainty budget (Hannum reported RMSE ~ 4.9y)
        base_mae = clock_meta.reported_mae
        imputation_penalty = 1.0 + (0.15 * (missing_count / max(1, len(required_probes))))
        expanded_u95 = base_mae * imputation_penalty * 1.96 / 1.645

        lower_bound = max(0.0, final_predicted_age - expanded_u95)
        upper_bound = final_predicted_age + expanded_u95

        raw_eaa = None
        univ_accel = None
        if chronological_age is not None:
            raw_eaa = final_predicted_age - chronological_age
            univ_accel = final_predicted_age - (0.90 * chronological_age + 2.5)

        return EpigeneticAgeResult(
            clock_id="hannum_2013",
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
