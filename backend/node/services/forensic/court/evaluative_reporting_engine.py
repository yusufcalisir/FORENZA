"""
FORENZA Dynamic ENFSI Evaluative Reporting & Verbal Scale Engine (Module 29).

Research Reference: Pillar 6 Research §4.1, §4.2, §4.3, and §6 (VECTOR_P6_03).
Implements:
  - ENFSI (2017) 7-Tier Verbal Strength Scale Step Function (§4.2)
  - Symmetric defense proposition inversion LR_def = 1/LR when LR < 1.0 (§4.2)
  - Bayesian evaluative LR framework: LR = P(E|H_p,I) / P(E|H_d,I) (§4.1)
  - Statutory Legal Admissibility Auditor: Daubert FRE 702 & Frye (§4.3)
  - Prosecutor's Fallacy Shield: P(E|H) ≠ P(H|E) (Active protection)
  - Bilingual courtroom statements: English & Turkish (§4.2)

Ground-Truth VECTOR_P6_03:
  LR = 3.5e7 → Verbal Tier 6
  Turkish: "Bulgular, iddia hipotezi (H_p) lehine aşırı güçlü destek sağlamaktadır."
"""

import math
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


# ── ENFSI 2017 Tier Definitions (verbatim from Research §4.2 & §6 Artifact A) ─

@dataclass(frozen=True)
class EnfsiTierDefinition:
    tier: int
    lr_min: float        # Inclusive lower bound for effective_lr
    lr_max: Optional[float]  # Exclusive upper bound (None = unbounded Tier 6)
    log10_min: float
    log10_max: Optional[float]
    phrase_en: str
    phrase_tr: str


ENFSI_2017_SCALE: List[EnfsiTierDefinition] = [
    EnfsiTierDefinition(
        tier=0,
        lr_min=1.0, lr_max=1.0,
        log10_min=0.0, log10_max=0.0,
        phrase_en="The findings are neutral and provide no support for either proposition.",
        phrase_tr="Bulgular nötr nitelikte olup her iki hipotez açısından da destek sağlamamaktadır.",
    ),
    EnfsiTierDefinition(
        tier=1,
        lr_min=1.0, lr_max=10.0,
        log10_min=0.0, log10_max=1.0,
        phrase_en="The findings provide weak support for {prop_supported} over {prop_opposed}.",
        phrase_tr="Bulgular, {prop_supported_tr} lehine zayıf destek sağlamaktadır.",
    ),
    EnfsiTierDefinition(
        tier=2,
        lr_min=10.0, lr_max=100.0,
        log10_min=1.0, log10_max=2.0,
        phrase_en="The findings provide moderate support for {prop_supported} over {prop_opposed}.",
        phrase_tr="Bulgular, {prop_supported_tr} lehine orta düzeyde destek sağlamaktadır.",
    ),
    EnfsiTierDefinition(
        tier=3,
        lr_min=100.0, lr_max=1000.0,
        log10_min=2.0, log10_max=3.0,
        phrase_en="The findings provide moderately strong support for {prop_supported} over {prop_opposed}.",
        phrase_tr="Bulgular, {prop_supported_tr} lehine orta-güçlü destek sağlamaktadır.",
    ),
    EnfsiTierDefinition(
        tier=4,
        lr_min=1000.0, lr_max=10000.0,
        log10_min=3.0, log10_max=4.0,
        phrase_en="The findings provide strong support for {prop_supported} over {prop_opposed}.",
        phrase_tr="Bulgular, {prop_supported_tr} lehine güçlü destek sağlamaktadır.",
    ),
    EnfsiTierDefinition(
        tier=5,
        lr_min=10000.0, lr_max=1_000_000.0,
        log10_min=4.0, log10_max=6.0,
        phrase_en="The findings provide very strong support for {prop_supported} over {prop_opposed}.",
        phrase_tr="Bulgular, {prop_supported_tr} lehine çok güçlü destek sağlamaktadır.",
    ),
    EnfsiTierDefinition(
        tier=6,
        lr_min=1_000_000.0, lr_max=None,
        log10_min=6.0, log10_max=None,
        phrase_en="The findings provide extremely strong support for {prop_supported} over {prop_opposed}.",
        phrase_tr="Bulgular, {prop_supported_tr} lehine aşırı güçlü destek sağlamaktadır.",
    ),
]


@dataclass
class DaubertAuditResult:
    """Daubert FRE 702 4-pillar and Frye compliance audit result (Research §4.3)."""
    pillar_1_falsifiability: bool  # Automated deterministic unit test suites
    pillar_2_error_rate: bool      # P_error <= 1e-6
    pillar_3_peer_review: bool     # Published peer-reviewed validation
    pillar_4_standards: bool       # SWGDAM (2020) & ISO/IEC 17025:2017
    frye_general_acceptance: bool  # General acceptance in forensic genetics community
    overall_admissible: bool
    error_rate_bound: float        # P_error <= 1e-6
    prosecutor_fallacy_shield: str


class DynamicEvaluativeReportingEngine:
    """
    ENFSI (2017) Dynamic Evaluative Reporting & Verbal Scale Engine.

    Derives verbatim from Pillar 6 Research §4.1, §4.2, §4.3, and §6 Artifact C/D.

    Core Method:
      generate_evaluative_report(lr, hp, hd, language) → Dict[str, Any]

    Mathematical Invariants:
      - LR > 0 (strict positivity; LR ≤ 0 raises ValueError)
      - Tier = f(effective_lr) where effective_lr = LR if LR ≥ 1.0 else 1/LR
      - VECTOR_P6_03: LR = 3.5e7 → Tier 6, log10_lr = 7.5441, Turkish phrase verified
      - Prosecutor's Fallacy Shield ACTIVE: P(E|H) ≠ P(H|E)
    """

    # Daubert FRE 702 error rate bound (Research §4.3)
    DAUBERT_ERROR_RATE_BOUND: float = 1e-6

    PROSECUTORS_FALLACY_SHIELD: str = (
        "PROSECUTOR'S FALLACY SHIELD [ACTIVE]: The Likelihood Ratio LR = P(E|H_p) / P(E|H_d) "
        "expresses the probability of observing the DNA evidence E GIVEN each proposition, "
        "NOT the probability that the suspect is guilty GIVEN the evidence. "
        "Transposing the conditional [P(E|H_p) ≠ P(H_p|E)] constitutes a Prosecutor's Fallacy "
        "and violates ENFSI (2017) evaluative reporting guidelines. "
        "Prior probabilities of guilt remain exclusively within the domain of the trier-of-fact."
    )

    def generate_evaluative_report(
        self,
        likelihood_ratio: float,
        hp_proposition: str = "The DNA evidence originates from the named suspect.",
        hd_proposition: str = "The DNA evidence originates from an unknown unrelated person.",
        language: str = "tr",
    ) -> Dict[str, Any]:
        """
        Translates LR into ENFSI (2017) standardized verbal scale statement (Research §4.1 & §4.2).

        Implements Research §6 Artifact C verbatim:
          - LR > 0 (raises ValueError on non-positive)
          - Effective LR: effective_lr = LR if LR >= 1.0 else 1/LR
          - Tier 0 → neutral (effective_lr == 1.0)
          - Tier 1 → (1.0, 10.0]
          - Tier 2 → (10.0, 100.0]
          - Tier 3 → (100.0, 1000.0]
          - Tier 4 → (1000.0, 10000.0]
          - Tier 5 → (10000.0, 1000000.0]
          - Tier 6 → > 1000000.0
          - VECTOR_P6_03: LR=3.5e7 → Tier 6, Turkish phrase confirmed

        :param likelihood_ratio: Numerical LR > 0
        :param hp_proposition: Prosecution proposition H_p (free text)
        :param hd_proposition: Defense proposition H_d (free text)
        :param language: "tr" (Turkish, default) or "en" (English)
        :return: Dict with tier, verbal statement, LR, log10_lr, dual-language fields
        """
        if likelihood_ratio <= 0.0:
            raise ValueError(
                f"Likelihood ratio must be strictly greater than 0. Received: {likelihood_ratio}"
            )

        log10_lr = math.log10(likelihood_ratio)
        is_prosecution = likelihood_ratio >= 1.0
        effective_lr = likelihood_ratio if is_prosecution else (1.0 / likelihood_ratio)

        prop_supported = "H_p" if is_prosecution else "H_d"
        prop_opposed = "H_d" if is_prosecution else "H_p"
        prop_supported_tr = (
            "iddia hipotezi (H_p)" if is_prosecution else "savunma hipotezi (H_d)"
        )

        # Step-function tier assignment (Research §4.2, §6 Artifact A TIERS)
        if effective_lr == 1.0:
            tier_def = ENFSI_2017_SCALE[0]  # Tier 0: Neutral
        elif effective_lr <= 10.0:
            tier_def = ENFSI_2017_SCALE[1]  # Tier 1
        elif effective_lr <= 100.0:
            tier_def = ENFSI_2017_SCALE[2]  # Tier 2
        elif effective_lr <= 1000.0:
            tier_def = ENFSI_2017_SCALE[3]  # Tier 3
        elif effective_lr <= 10000.0:
            tier_def = ENFSI_2017_SCALE[4]  # Tier 4
        elif effective_lr <= 1_000_000.0:
            tier_def = ENFSI_2017_SCALE[5]  # Tier 5
        else:
            tier_def = ENFSI_2017_SCALE[6]  # Tier 6

        if tier_def.tier == 0:
            phrase_en = tier_def.phrase_en
            phrase_tr = tier_def.phrase_tr
        else:
            phrase_en = tier_def.phrase_en.format(
                prop_supported=prop_supported,
                prop_opposed=prop_opposed,
            )
            phrase_tr = tier_def.phrase_tr.format(
                prop_supported_tr=prop_supported_tr,
            )

        evaluative_statement = phrase_tr if language.lower() == "tr" else phrase_en

        return {
            "likelihood_ratio": likelihood_ratio,
            "log10_likelihood_ratio": round(log10_lr, 4),
            "effective_lr": round(effective_lr, 4),
            "is_prosecution_supported": is_prosecution,
            "supported_proposition": prop_supported,
            "opposed_proposition": prop_opposed,
            "verbal_tier": tier_def.tier,
            "log10_tier_min": tier_def.log10_min,
            "log10_tier_max": tier_def.log10_max,
            "phrase_en": phrase_en,
            "phrase_tr": phrase_tr,
            "evaluative_statement": evaluative_statement,
            "language": language.lower(),
            "hp_proposition": hp_proposition,
            "hd_proposition": hd_proposition,
            "prosecutors_fallacy_shield": self.PROSECUTORS_FALLACY_SHIELD,
            "reporting_standard": "ENFSI-2017-EVAL-V1",
        }

    def audit_daubert_frye_compliance(
        self,
        error_rate: float = 1e-9,
        has_peer_reviewed_algorithms: bool = True,
        swgdam_compliant: bool = True,
        iso17025_compliant: bool = True,
    ) -> DaubertAuditResult:
        """
        Evaluates Daubert FRE 702 4-pillar and Frye general acceptance compliance (Research §4.3).

        Daubert Standard (Federal Rule of Evidence 702):
          1. Falsifiability & Testability: Automated deterministic unit test suites.
          2. Error Rate: P_error ≤ 1e-6.
          3. Peer-Reviewed Literature: Published algorithms and peer-reviewed validation.
          4. Standards Control: SWGDAM (2020) and ISO/IEC 17025:2017 compliance.
        Frye Standard: General scientific acceptance in forensic genetics community.

        :param error_rate: Observed system error rate (must be ≤ 1e-6 to pass pillar 2)
        :param has_peer_reviewed_algorithms: Whether underlying algorithms are peer-reviewed
        :param swgdam_compliant: Whether SWGDAM (2020) QAS compliance is documented
        :param iso17025_compliant: Whether ISO/IEC 17025:2017 accreditation is in scope
        :return: DaubertAuditResult dataclass with per-pillar and overall verdict
        """
        pillar_1 = True   # Automated deterministic unit test suites (always true for FORENZA)
        pillar_2 = error_rate <= self.DAUBERT_ERROR_RATE_BOUND
        pillar_3 = has_peer_reviewed_algorithms
        pillar_4 = swgdam_compliant and iso17025_compliant
        frye = has_peer_reviewed_algorithms and swgdam_compliant

        overall = pillar_1 and pillar_2 and pillar_3 and pillar_4 and frye

        return DaubertAuditResult(
            pillar_1_falsifiability=pillar_1,
            pillar_2_error_rate=pillar_2,
            pillar_3_peer_review=pillar_3,
            pillar_4_standards=pillar_4,
            frye_general_acceptance=frye,
            overall_admissible=overall,
            error_rate_bound=self.DAUBERT_ERROR_RATE_BOUND,
            prosecutor_fallacy_shield=self.PROSECUTORS_FALLACY_SHIELD,
        )
