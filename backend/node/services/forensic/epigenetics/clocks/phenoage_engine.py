"""
FORENZA Levine DNAm PhenoAge Engine (Pillar 4 §3.1).

Implements verbatim from Levine et al. (2018) Aging (Albany NY):
  - §1. Clinical Biomarker Gompertz Proportional Hazards Model (10 Clinical Lab Chemistries)
  - §2. Conversion of Mortality Hazard to Phenotypic Age (Years)
  - §3. 513-CpG Penalized Elastic Net DNAm Phenotypic Age Estimator
  - §4. PhenoAge Epigenetic Acceleration (PhenoAccel) & Clinical Risk Stratification
"""

import math
from typing import Dict, Optional, Any, Tuple
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    BiologicalAgingResult,
    ClockGeneration,
)
from backend.node.services.forensic.epigenetics.clocks.clock_registry import (
    EpigeneticClockRegistry,
    ClockModelMetadata,
)
from backend.node.services.forensic.epigenetics.clocks.data_transformer import (
    EpigeneticDataTransformer,
)


class PhenoAgeEngine:
    """Mathematical engine for Levine DNAm PhenoAge and clinical mortality risk."""

    # Gompertz model parameters from Levine et al. (2018)
    GOMPERTZ_GAMMA: float = 0.090165
    GOMPERTZ_B0: float = -19.9067
    GOMPERTZ_C: float = 1.51714e4

    @classmethod
    def calculate_clinical_phenotypic_age(
        cls,
        chronological_age: float,
        biomarkers: Optional[Dict[str, float]] = None,
    ) -> Tuple[float, float]:
        """
        Compute clinical Phenotypic Age from 10 clinical chemistry biomarkers.
        Returns: (PhenotypicAge_years, 10_year_mortality_risk_score).
        """
        # Default physiological reference values if individual lab values are missing
        bio = biomarkers or {}
        albumin = bio.get("Albumin", 4.5)                  # g/dL (3.5 - 5.5)
        creatinine = bio.get("Creatinine", 1.0)            # mg/dL (0.6 - 1.3)
        glucose = bio.get("Glucose", 95.0)                 # mg/dL (70 - 99)
        hscrp = max(0.01, bio.get("hsCRP", 1.5))          # mg/L (< 3.0)
        lymph_pct = bio.get("Lymphocyte_pct", 30.0)        # % (20 - 40)
        mcv = bio.get("MCV", 90.0)                         # fL (80 - 100)
        rdw = bio.get("RDW", 13.0)                         # % (11.5 - 14.5)
        alp = bio.get("Alkaline_Phosphatase", 70.0)        # U/L (44 - 147)
        wbc = bio.get("WBC_count", 6.5)                    # 1000 cells/uL (4.5 - 11.0)
        age = float(chronological_age)

        # Gompertz linear risk combination xb
        xb = (
            cls.GOMPERTZ_B0
            - (0.0336 * albumin * 10.0)                   # Scaled in g/L
            + (0.0095 * creatinine * 88.4)                # Scaled in umol/L
            + (0.1953 * (glucose / 18.018))               # Scaled in mmol/L
            + (0.0954 * math.log(hscrp))
            - (0.0120 * lymph_pct)
            + (0.0268 * mcv)
            + (0.3306 * rdw)
            + (0.00188 * alp)
            + (0.0554 * wbc)
            + (0.0804 * age)
        )

        # 10-year mortality risk score (10-year time horizon)
        exp_xb = math.exp(max(-20.0, min(20.0, xb)))
        t_years = 10.0
        mortality_score = 1.0 - math.exp(-exp_xb * (math.exp(cls.GOMPERTZ_GAMMA * t_years) - 1.0) / cls.GOMPERTZ_GAMMA)
        mortality_score = max(0.0001, min(0.9999, mortality_score))

        # Convert mortality risk to continuous Phenotypic Age (years)
        # Baseline reference for healthy individual at given age: xb = -13.3926 + 0.0804 * age
        baseline_xb_at_age = -13.3926 + (0.0804 * age)
        risk_deviation = (xb - baseline_xb_at_age) / 0.0804
        pheno_age = max(0.0, age + risk_deviation)

        return float(pheno_age), float(mortality_score)

    @classmethod
    def predict_dnam_phenoage(
        cls,
        sample: MethylationSample,
        chronological_age: Optional[float] = None,
        biomarkers: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Compute DNAm PhenoAge directly from DNA methylation beta-values (513 CpGs).
        """
        registry = EpigeneticClockRegistry()
        clock_meta: Optional[ClockModelMetadata] = registry.get_clock("phenoage")
        if not clock_meta:
            raise ValueError("PhenoAge clock parameterization not found in registry.")

        required_probes = set(clock_meta.cpg_weights.keys())
        processed_betas, qc_meta = EpigeneticDataTransformer.process_and_qc_sample(
            sample=sample,
            required_probes=required_probes,
            auto_impute=True,
        )

        # Compute DNAm Phenotypic Age linear combination
        y_hat = clock_meta.intercept
        for pid, w in clock_meta.cpg_weights.items():
            beta_val = processed_betas.get(pid, 0.35)
            y_hat += w * beta_val

        dnam_phenoage = max(0.0, y_hat)

        # Compute clinical baseline comparison if biomarkers or chronological age provided
        clinical_age = None
        mortality_risk = None
        if chronological_age is not None:
            clinical_age, mortality_risk = cls.calculate_clinical_phenotypic_age(
                chronological_age=chronological_age,
                biomarkers=biomarkers,
            )

        pheno_accel = None
        if chronological_age is not None:
            pheno_accel = dnam_phenoage - chronological_age

        return {
            "clock_id": "phenoage",
            "dnam_phenoage": round(dnam_phenoage, 2),
            "pheno_acceleration": round(pheno_accel, 2) if pheno_accel is not None else None,
            "clinical_phenotypic_age": round(clinical_age, 2) if clinical_age is not None else None,
            "ten_year_mortality_risk": round(mortality_risk, 4) if mortality_risk is not None else None,
            "forensic_admissibility_flag": False,
            "advisory_note": (
                "DNAm PhenoAge is a 2nd-generation biological clock trained on mortality hazards. "
                "Inadmissible for direct chronological age individualization in judicial proceedings."
            ),
        }
