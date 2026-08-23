"""
FORENZA Anti-Averaging Fallacy Guard & Multi-Clock Methodology Engine (Pillar 4 §3.4).

Intercepts and prevents statistically invalid arithmetic averaging of first-, second-,
and third-generation epigenetic clocks, enforcing legal and mathematical integrity.
"""

from typing import Dict, List, Any, Optional
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    EpigeneticAgeResult,
    ClockGeneration,
)


class AntiAveragingGuard:
    """Mathematical and legal shield against multi-generation clock averaging fallacies."""

    @classmethod
    def evaluate_multi_clock_consensus(
        cls,
        clock_results: List[EpigeneticAgeResult],
        pheno_result: Optional[Dict[str, Any]] = None,
        grim_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Synthesize multi-clock estimates into a methodologically sound consensus.
        Enforces separate reporting for chronological vs. biological clocks.
        """
        first_gen_results = [
            c for c in clock_results
            if c.generation in (ClockGeneration.FIRST_GEN_CHRONO, ClockGeneration.FORENSIC_REDUCED)
        ]

        if not first_gen_results:
            return {
                "consensus_chronological_age": None,
                "admissibility_status": "NO_VALID_CHRONOLOGICAL_CLOCK",
                "anti_averaging_warning": "No verified 1st-generation or forensic chronological clock was provided.",
            }

        # Valid inverse-variance weighted pooling across 1st-generation / forensic clocks ONLY
        weights = []
        ages = []
        for r in first_gen_results:
            sigma = max(0.5, r.expanded_uncertainty_95 / 1.96)
            var = sigma ** 2
            w = 1.0 / var
            weights.append(w)
            ages.append(r.predicted_age)

        total_w = sum(weights)
        consensus_age = sum(w * a for w, a in zip(weights, ages)) / total_w
        combined_sigma = (1.0 / total_w) ** 0.5
        combined_u95 = combined_sigma * 1.96

        response: Dict[str, Any] = {
            "consensus_chronological_age": round(consensus_age, 2),
            "consensus_uncertainty_95": round(combined_u95, 2),
            "age_range_95_lower": round(max(0.0, consensus_age - combined_u95), 2),
            "age_range_95_upper": round(consensus_age + combined_u95, 2),
            "chronological_clocks_included": [c.clock_id for c in first_gen_results],
            "anti_averaging_protection": {
                "status": "ENFORCED",
                "rule": "Second-generation (PhenoAge/GrimAge) and 3rd-generation (DunedinPACE) clocks excluded from chronological consensus.",
                "scientific_rationale": (
                    "First-generation clocks optimize for calendar time E[Y|X] = Age. "
                    "Second-generation clocks optimize for mortality hazard HR(t) = exp(X*beta). "
                    "Naive arithmetic averaging conflates calendar intervals with physiological morbidity risk, "
                    "producing an uncalibrated error distribution without legal ground truth."
                ),
            },
        }

        # Include biological aging discrepancy if available
        if pheno_result or grim_result:
            biological_summary = {}
            if pheno_result:
                biological_summary["phenoage"] = pheno_result.get("dnam_phenoage")
                biological_summary["pheno_acceleration"] = pheno_result.get("pheno_acceleration")
            if grim_result:
                biological_summary["grimage"] = grim_result.get("grimage_age")
                biological_summary["grimage_acceleration"] = grim_result.get("grimage_acceleration")
                biological_summary["mortality_hazard_ratio"] = grim_result.get("mortality_hazard_ratio")

            response["biological_healthspan_intelligence"] = biological_summary

        return response
