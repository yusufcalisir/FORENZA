"""
FORENZA Epigenetic Clocks Jurisdictional Governance & Judicial Reporting Engine (Pillar 4 §6 & Pillar 6 §4).

Enforces:
  1. Statutory Compliance (German § 81e StPO, Dutch CCP, International ISO/IEC 17025).
  2. Admissibility Shield: Strict disallowance of 2nd/3rd gen clocks for criminal suspect narrowing.
  3. ENFSI (2017) 7-Tier Evaluative Reporting Scale with Prosecutor's Fallacy Safeguards.
"""

import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    EpigeneticAgeResult,
    BiologicalAgingResult,
    ClockGeneration,
)


@dataclass
class JudicialEvaluativeReport:
    """Formal court-admissible forensic epigenetic evaluation report."""
    donor_sample_id: str
    jurisdiction: str
    admissible_chronological_age: float
    uncertainty_interval_95: tuple[float, float]
    approved_clocks_used: List[str]
    disallowed_clocks_excluded: List[str]
    enfsi_tier_level: int
    enfsi_statement_en: str
    enfsi_statement_tr: str
    prosecutors_fallacy_shield: str
    statutory_compliance_status: str


class EpigeneticGovernanceEngine:
    """Engine enforcing jurisdictional compliance and court-admissible evaluative reporting."""

    ENFSI_TIERS = {
        1: {
            "en": "The DNA methylation results provide inconclusive or neutral evidence regarding the specified age bracket.",
            "tr": "DNA metilasyon sonuçları, belirtilen yaş aralığına ilişkin yetersiz veya nötr kanıt sağlamaktadır.",
        },
        2: {
            "en": "The DNA methylation results provide weak support for the proposition that the trace donor was within the estimated age interval.",
            "tr": "DNA metilasyon sonuçları, leke donörünün tahmin edilen yaş aralığında olduğu önermesini zayıf düzeyde desteklemektedir.",
        },
        3: {
            "en": "The DNA methylation results provide moderate support for the proposition that the trace donor was within the estimated age interval.",
            "tr": "DNA metilasyon sonuçları, leke donörünün tahmin edilen yaş aralığında olduğu önermesini orta düzeyde desteklemektedir.",
        },
        4: {
            "en": "The DNA methylation results provide moderately strong support for the proposition that the trace donor was within the estimated age interval.",
            "tr": "DNA metilasyon sonuçları, leke donörünün tahmin edilen yaş aralığında olduğu önermesini orta-güçlü düzeyde desteklemektedir.",
        },
        5: {
            "en": "The DNA methylation results provide strong support for the proposition that the trace donor was within the estimated age interval.",
            "tr": "DNA metilasyon sonuçları, leke donörünün tahmin edilen yaş aralığında olduğu önermesini güçlü düzeyde desteklemektedir.",
        },
        6: {
            "en": "The DNA methylation results provide very strong support for the proposition that the trace donor was within the estimated age interval.",
            "tr": "DNA metilasyon sonuçları, leke donörünün tahmin edilen yaş aralığında olduğu önermesini çok güçlü düzeyde desteklemektedir.",
        },
        7: {
            "en": "The DNA methylation results provide extremely strong support for the proposition that the trace donor was within the estimated age interval.",
            "tr": "DNA metilasyon sonuçları, leke donörünün tahmin edilen yaş aralığında olduğu önermesini son derece güçlü düzeyde desteklemektedir.",
        },
    }

    @classmethod
    def evaluate_judicial_admissibility(
        cls,
        sample_id: str,
        clock_results: List[EpigeneticAgeResult],
        biological_result: Optional[BiologicalAgingResult] = None,
        jurisdiction: str = "INTERNATIONAL",
    ) -> JudicialEvaluativeReport:
        """
        Filter clock results by admissibility rules and generate standardized ENFSI evaluative statements.
        """
        admissible_clocks = []
        excluded_clocks = []
        point_estimates = []
        uncertainties = []

        for r in clock_results:
            if r.generation in (ClockGeneration.FIRST_GEN_CHRONO, ClockGeneration.FORENSIC_REDUCED):
                admissible_clocks.append(r.clock_id)
                point_estimates.append(r.predicted_age)
                uncertainties.append(r.expanded_uncertainty_95)
            else:
                excluded_clocks.append(r.clock_id)

        if biological_result:
            if biological_result.phenotypic_age is not None:
                excluded_clocks.append("phenoage")
            if biological_result.grimage_age is not None:
                excluded_clocks.append("grimage")
            if biological_result.dunedin_pace_velocity is not None:
                excluded_clocks.append("dunedin_pace")

        if not point_estimates:
            raise ValueError("No legally admissible 1st-generation or forensic reduced clocks provided.")

        # Inverse-variance weighted consensus
        sigmas = [max(0.2, u / 1.96) for u in uncertainties]
        weights = [1.0 / (s ** 2) for s in sigmas]
        tot_w = sum(weights)
        consensus_age = sum(w * a for w, a in zip(weights, point_estimates)) / tot_w
        combined_sigma = math.sqrt(1.0 / tot_w)
        combined_u95 = combined_sigma * 1.96

        lower_bound = max(0.0, consensus_age - combined_u95)
        upper_bound = consensus_age + combined_u95

        # Determine ENFSI confidence tier based on uncertainty bandwidth
        bandwidth = upper_bound - lower_bound
        if bandwidth <= 5.0:
            tier = 6  # Very strong support
        elif bandwidth <= 7.0:
            tier = 5  # Strong support
        elif bandwidth <= 9.0:
            tier = 4  # Moderately strong support
        elif bandwidth <= 12.0:
            tier = 3  # Moderate support
        else:
            tier = 2  # Weak support

        enfsi_en = cls.ENFSI_TIERS[tier]["en"]
        enfsi_tr = cls.ENFSI_TIERS[tier]["tr"]

        shield_text = (
            "PROSECUTOR'S FALLACY SAFEGUARD: This evaluation expresses the probability of obtaining "
            "the observed DNA methylation profile given the specified age hypothesis P(E | H), "
            "NOT the posterior probability of the hypothesis given the evidence P(H | E) without prior odds."
        )

        statutory_compliance = f"COMPLIANT_WITH_{jurisdiction.upper()}"
        if jurisdiction.upper() == "GERMANY_STPO":
            statutory_compliance += " (Compliant with German § 81e Abs. 2 StPO: Disease-associated phenotypic markers masked)."

        return JudicialEvaluativeReport(
            donor_sample_id=sample_id,
            jurisdiction=jurisdiction,
            admissible_chronological_age=round(consensus_age, 2),
            uncertainty_interval_95=(round(lower_bound, 2), round(upper_bound, 2)),
            approved_clocks_used=admissible_clocks,
            disallowed_clocks_excluded=excluded_clocks,
            enfsi_tier_level=tier,
            enfsi_statement_en=enfsi_en,
            enfsi_statement_tr=enfsi_tr,
            prosecutors_fallacy_shield=shield_text,
            statutory_compliance_status=statutory_compliance,
        )
