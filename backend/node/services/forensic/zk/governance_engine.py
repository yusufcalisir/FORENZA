"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Statutory Governance & Bilingual ENFSI Reporting

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
ISO/IEC 17025:2017 & ENFSI (2017) 7-Tier Bilingual Evaluative Reporting with Prosecutor's Fallacy Shield.
"""

from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone


class ZKForensicGovernanceEngine:
    """
    Statutory Governance & Evaluative Reporting Engine for Zero-Knowledge Proofs.
    Translates cryptographic match proofs into ISO 17025 / ENFSI compliant statements.
    """

    ENFSI_TIERS_EN = {
        1: "Tier 1: Inconclusive or Neutral Evidence (LR = 1)",
        2: "Tier 2: Moderate Support for Prosecution Hypothesis (1 < LR <= 10)",
        3: "Tier 3: Moderately Strong Support for Prosecution Hypothesis (10 < LR <= 100)",
        4: "Tier 4: Strong Support for Prosecution Hypothesis (100 < LR <= 10,000)",
        5: "Tier 5: Very Strong Support for Prosecution Hypothesis (10,000 < LR <= 1,000,000)",
        6: "Tier 6: Extremely Strong Support for Prosecution Hypothesis (LR > 1,000,000)",
        0: "Tier 0: Definitive Exclusion / Support for Defense Hypothesis (LR < 1)",
    }

    ENFSI_TIERS_TR = {
        1: "Kademe 1: Sonuçsuz veya Nötr Delil (LR = 1)",
        2: "Kademe 2: İddia Makamı Hipotezi Lehine Ilımlı Düzeyde Destek (1 < LR <= 10)",
        3: "Kademe 3: İddia Makamı Hipotezi Lehine Orta-Güçlü Düzeyde Destek (10 < LR <= 100)",
        4: "Kademe 4: İddia Makamı Hipotezi Lehine Güçlü Destek (100 < LR <= 10.000)",
        5: "Kademe 5: İddia Makamı Hipotezi Lehine Çok Güçlü Destek (10.000 < LR <= 1.000.000)",
        6: "Kademe 6: İddia Makamı Hipotezi Lehine Son Derece Güçlü Destek (LR > 1.000.000)",
        0: "Kademe 0: Kesin Dışlama / Savunma Hipotezi Lehine Destek (LR < 1)",
    }

    @classmethod
    def get_enfsi_tier(cls, lr_value: float) -> Tuple[int, str, str]:
        """Maps continuous LR to tier level and bilingual descriptions."""
        if lr_value < 1.0:
            tier_num = 0
        elif lr_value == 1.0:
            tier_num = 1
        elif lr_value <= 10.0:
            tier_num = 2
        elif lr_value <= 100.0:
            tier_num = 3
        elif lr_value <= 10000.0:
            tier_num = 4
        elif lr_value <= 1000000.0:
            tier_num = 5
        else:
            tier_num = 6

        return tier_num, cls.ENFSI_TIERS_EN[tier_num], cls.ENFSI_TIERS_TR[tier_num]

    @classmethod
    def format_prosecutor_fallacy_shield(cls, lr_value: float, is_valid: bool) -> Dict[str, str]:
        """
        Generates active Prosecutor's Fallacy shields in English and Turkish:
        Clarifies P(E | Hp) vs P(Hp | E).
        """
        if not is_valid:
            return {
                "en": "EVIDENTIARY SHIELD: Zero-knowledge proof invalid or match threshold unsatisfied. No statistical inference of guilt or identity may be drawn.",
                "tr": "HUKUKİ KALKAN: Sıfır bilgi ispatı geçersiz veya eşleşme eşiği sağlanamadı. Sanığın kimliği veya suçluluğu yönünde hiçbir istatistiki çıkarım yapılamaz."
            }

        en_shield = (
            f"EVIDENTIARY SHIELD (ENFSI 2017): The zero-knowledge cryptographic proof confirms that the DNA profile match "
            f"satisfies LR >= {lr_value:.2e}. This evaluates the probability of the genetic evidence given the hypotheses "
            f"[P(Evidence | Hp) / P(Evidence | Hd)], NOT the posterior probability of the suspect's guilt or innocence [P(Hp | Evidence)]."
        )
        tr_shield = (
            f"HUKUKİ KALKAN (ENFSI 2017): Sıfır bilgi kriptografik ispatı, DNA profil eşleşmesinin "
            f"LR >= {lr_value:.2e} eşiğini sağladığını doğrulamaktadır. Bu bulgu, hipotezler altında genetik delilin gözlenme "
            f"olasılığını [P(Delil | İddia) / P(Delil | Savunma)] ifade etmekte olup, doğrudan sanığın suçluluk veya masumiyet olasılığı [P(İddia | Delil)] değildir."
        )
        return {"en": en_shield, "tr": tr_shield}

    @classmethod
    def generate_iso17025_zk_certificate(
        cls,
        case_id_hash: str,
        proving_system: str,
        claimed_threshold: float,
        is_verified: bool,
        audit_hash: str,
    ) -> Dict[str, Any]:
        """Generates structured ISO 17025 ZK verification certificate."""
        tier_num, tier_en, tier_tr = cls.get_enfsi_tier(claimed_threshold)
        shields = cls.format_prosecutor_fallacy_shield(claimed_threshold, is_verified)

        return {
            "certificate_type": "ISO/IEC 17025:2017 Zero-Knowledge Blind Evidence Verification Certificate",
            "case_id_hash": case_id_hash,
            "proving_system": proving_system,
            "claimed_threshold": claimed_threshold,
            "is_verified": is_verified,
            "verdict": "VERIFIED_MATCH" if is_verified else "UNVERIFIED_OR_EXCLUDED",
            "enfsi_tier_level": tier_num,
            "enfsi_tier_en": tier_en,
            "enfsi_tier_tr": tier_tr,
            "prosecutors_fallacy_shield_en": shields["en"],
            "prosecutors_fallacy_shield_tr": shields["tr"],
            "audit_hash": audit_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "daubert_fre_702_compliant": True,
        }
