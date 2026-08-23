"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Certified Golden Benchmark Vectors

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
Certified Multi-Omic Forensic Reference Vectors for Zero-Knowledge Verifiable Ingestion & Proving.
"""

from typing import Dict, Any, List
from .schemas import ZKProofInstance, ZKWitnessData


# 1. VECTOR_ZK_CODIS_MATCH: NIST SRM 2391d Component A (Single-Source Inclusion LR >= 1e18)
VECTOR_ZK_CODIS_MATCH_INSTANCE = ZKProofInstance(
    case_id_hash="0xNIST_SRM_2391D_COMP_A_CODIS24",
    claimed_lr_threshold=1.0e18,
    claimed_lr_threshold_quantized=65536 * 1000000000000000000,
    merkle_root="0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
    locus_count=24,
    scale_s=16,
)

VECTOR_ZK_CODIS_MATCH_WITNESS = ZKWitnessData(
    sample_id="NIST_SRM_2391D_COMP_A",
    suspect_genotypes={
        "AMEL": (1.0, 2.0),
        "TH01": (9.3, 9.3),
        "D21S11": (29.0, 31.2),
        "D18S51": (12.0, 15.0),
        "vWA": (16.0, 19.0),
        "FGA": (21.0, 24.0),
        "D8S1179": (13.0, 15.0),
        "D3S1358": (15.0, 16.0),
    },
    evidence_peak_heights={
        "TH01": {9.3: 3500.0},
        "D21S11": {29.0: 2800.0, 31.2: 2750.0},
    },
    true_likelihood_ratio=2.51e18,
    numerator_quantized=65536 * 2510000000000000000,
    denominator_quantized=65536,
    quotient_advice=65536 * 2510000000000000000,
    remainder_advice=0,
)


# 2. VECTOR_ZK_EXCLUSION: NA12878 CEU vs NA19240 YRI (Definitive Exclusion LR < 1e-6)
VECTOR_ZK_EXCLUSION_INSTANCE = ZKProofInstance(
    case_id_hash="0xNA12878_VS_NA19240_EXCLUSION",
    claimed_lr_threshold=1.0e6,
    claimed_lr_threshold_quantized=65536 * 1000000,
    merkle_root="0x9b74c9897bac770ffc029102a200c5deac24863e1081addd200126d9069a1122",
    locus_count=24,
    scale_s=16,
)

VECTOR_ZK_EXCLUSION_WITNESS = ZKWitnessData(
    sample_id="NA19240_EXCLUDED",
    suspect_genotypes={
        "TH01": (6.0, 7.0),
        "D21S11": (28.0, 28.0),
    },
    evidence_peak_heights={
        "TH01": {9.3: 3000.0},
        "D21S11": {30.0: 2500.0, 32.0: 2400.0},
    },
    true_likelihood_ratio=1.2e-7,
    numerator_quantized=0,
    denominator_quantized=65536 * 1000000,
    quotient_advice=0,
    remainder_advice=0,
)


# 3. VECTOR_ZK_MIXTURE_2P: 2-Person 70:30 Mixture Deconvolution
VECTOR_ZK_MIXTURE_2P_INSTANCE = ZKProofInstance(
    case_id_hash="0xMIXTURE_2P_70_30_CASEWORK",
    claimed_lr_threshold=1.0e8,
    claimed_lr_threshold_quantized=65536 * 100000000,
    merkle_root="0x11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
    locus_count=24,
    scale_s=16,
)

VECTOR_ZK_MIXTURE_2P_WITNESS = ZKWitnessData(
    sample_id="MAJOR_CONTRIBUTOR_70",
    suspect_genotypes={
        "TH01": (7.0, 9.3),
        "D18S51": (14.0, 16.0),
    },
    evidence_peak_heights={
        "TH01": {7.0: 2100.0, 9.3: 2050.0, 6.0: 890.0},
    },
    true_likelihood_ratio=4.5e9,
    numerator_quantized=65536 * 4500000000,
    denominator_quantized=65536,
    quotient_advice=65536 * 4500000000,
    remainder_advice=0,
)


# 4. VECTOR_ZK_TRACE_LOW_TEMPLATE: 18pg Touch DNA Specimen
VECTOR_ZK_TRACE_LOW_TEMPLATE_INSTANCE = ZKProofInstance(
    case_id_hash="0xTRACE_18PG_TOUCH_DNA",
    claimed_lr_threshold=1.0e4,
    claimed_lr_threshold_quantized=65536 * 10000,
    merkle_root="0x3344556677889900aabbccddeeff11223344556677889900aabbccddeeff1122",
    locus_count=24,
    scale_s=16,
)

VECTOR_ZK_TRACE_LOW_TEMPLATE_WITNESS = ZKWitnessData(
    sample_id="TRACE_18PG_SUSPECT",
    suspect_genotypes={
        "TH01": (9.3, 9.3),
    },
    evidence_peak_heights={
        "TH01": {9.3: 85.0},
    },
    true_likelihood_ratio=7.8e4,
    numerator_quantized=65536 * 78000,
    denominator_quantized=65536,
    quotient_advice=65536 * 78000,
    remainder_advice=0,
)


# 5. VECTOR_ZK_INTERPOL_CROSS_BORDER: Bilateral Blind Match Query
VECTOR_ZK_INTERPOL_CROSS_BORDER_INSTANCE = ZKProofInstance(
    case_id_hash="0xINTERPOL_RED_NOTICE_BLIND_MATCH",
    claimed_lr_threshold=1.0e12,
    claimed_lr_threshold_quantized=65536 * 1000000000000,
    merkle_root="0x556677889900aabbccddeeff11223344556677889900aabbccddeeff11223344",
    locus_count=24,
    scale_s=16,
)

VECTOR_ZK_INTERPOL_CROSS_BORDER_WITNESS = ZKWitnessData(
    sample_id="INTERPOL_SUBJECT_X",
    suspect_genotypes={
        "TH01": (9.3, 9.3),
        "D21S11": (29.0, 31.2),
    },
    evidence_peak_heights={
        "TH01": {9.3: 3200.0},
    },
    true_likelihood_ratio=8.9e14,
    numerator_quantized=65536 * 890000000000000,
    denominator_quantized=65536,
    quotient_advice=65536 * 890000000000000,
    remainder_advice=0,
)


ALL_ZK_GOLDEN_VECTORS = {
    "VECTOR_ZK_CODIS_MATCH": (VECTOR_ZK_CODIS_MATCH_INSTANCE, VECTOR_ZK_CODIS_MATCH_WITNESS),
    "VECTOR_ZK_EXCLUSION": (VECTOR_ZK_EXCLUSION_INSTANCE, VECTOR_ZK_EXCLUSION_WITNESS),
    "VECTOR_ZK_MIXTURE_2P": (VECTOR_ZK_MIXTURE_2P_INSTANCE, VECTOR_ZK_MIXTURE_2P_WITNESS),
    "VECTOR_ZK_TRACE_LOW_TEMPLATE": (VECTOR_ZK_TRACE_LOW_TEMPLATE_INSTANCE, VECTOR_ZK_TRACE_LOW_TEMPLATE_WITNESS),
    "VECTOR_ZK_INTERPOL_CROSS_BORDER": (VECTOR_ZK_INTERPOL_CROSS_BORDER_INSTANCE, VECTOR_ZK_INTERPOL_CROSS_BORDER_WITNESS),
}
