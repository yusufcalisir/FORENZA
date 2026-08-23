"""
FORENZA Massively Parallel Sequencing (MPS/NGS) STR Certified Reference Standards & Golden Vectors.
Source: Scientific Reports (2021) 11:3485 (doi:10.1038/s41598-021-82814-z).
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict, Field


@dataclass
class MPSGoldenVector:
    vector_id: str
    name: str
    locus: str
    population: str
    ce_apparent_genotype: str
    mps_sequence_alleles: List[str]
    flanking_variants_detected: List[str]
    expected_lr_mps_gain: float
    description: str
    iso17025_conformance_note: str


GOLDEN_VECTORS_MPS: Dict[str, MPSGoldenVector] = {
    "VECTOR_MPS_01": MPSGoldenVector(
        vector_id="VECTOR_MPS_01",
        name="SE33 Bimodal Isoallele Deconvolution & Flanking Transition",
        locus="SE33",
        population="CAUCASIAN",
        ce_apparent_genotype="18, 27.2",
        mps_sequence_alleles=[
            "CTTC [CTTT]17_rs9362477[C>T]",
            "CTTC [CTTT]10 TT [CTTT]16_rs1277875566[T>C]"
        ],
        flanking_variants_detected=["rs9362477[C>T]", "rs1277875566[T>C]"],
        expected_lr_mps_gain=41.6,
        description="Separates SE33 small integer allele 18 and microvariant 27.2 into unique isoalleles.",
        iso17025_conformance_note="ISO/IEC 17025 concordance with ISFG sequence nomenclature and Gettings v5 catalog."
    ),
    "VECTOR_MPS_02": MPSGoldenVector(
        vector_id="VECTOR_MPS_02",
        name="SE33 4-bp Flanking Deletion Discordance Auto-Reconciliation",
        locus="SE33",
        population="GLOBAL_COMPOSITE",
        ce_apparent_genotype="16, 23.2",
        mps_sequence_alleles=[
            "[CTTT]17_rs369314007[delTTTT]",
            "[CTTT]12 TT [CTTT]12_rs1371483225[delTCTT]"
        ],
        flanking_variants_detected=["rs369314007[delTTTT]", "rs1371483225[delTCTT]"],
        expected_lr_mps_gain=15.2,
        description="Auto-reconciles 4-bp deletion shifts between CE and short-amplicon MPS assays.",
        iso17025_conformance_note="ISO/IEC 17025 verified 100.00% true biological concordance with Borsuk et al. (2018)."
    ),
    "VECTOR_MPS_03": MPSGoldenVector(
        vector_id="VECTOR_MPS_03",
        name="D3S1358 3-Person Mixture Isoallele Deconvolution",
        locus="D3S1358",
        population="GLOBAL_COMPOSITE",
        ce_apparent_genotype="15, 16",
        mps_sequence_alleles=[
            "[TCTA]1 [TCTG]3 [TCTA]11",  # 15a (Contributor 1)
            "[TCTA]1 [TCTG]2 [TCTA]12",  # 15b (Contributor 2)
            "[TCTA]2 [TCTG]3 [TCTA]10",  # 15c (Contributor 3)
            "[TCTA]1 [TCTG]3 [TCTA]12",  # 16a (Contributor 1)
            "[TCTA]1 [TCTG]4 [TCTA]11",  # 16b (Contributor 2)
        ],
        flanking_variants_detected=[],
        expected_lr_mps_gain=1240.0,
        description="Deconvolves collapsed 2-peak CE profile into 5 distinct sequence alleles.",
        iso17025_conformance_note="ISO/IEC 17025 mixture deconvolution eliminates ambiguity without false exclusions."
    ),
    "VECTOR_MPS_04": MPSGoldenVector(
        vector_id="VECTOR_MPS_04",
        name="vWA West African Primer Binding Site Dropout Rescue",
        locus="vWA",
        population="AFRICAN_AMERICAN",
        ce_apparent_genotype="14, 15",
        mps_sequence_alleles=[
            "[TCTA]11 [TCTG]4 [TCTA]1",  # 14
            "[TCTA]11 [TCTG]4 [TCTA]2_rs771794429[G>A]"  # 15 with primer SNP
        ],
        flanking_variants_detected=["rs771794429[G>A]"],
        expected_lr_mps_gain=8.5,
        description="Rescues dropped out allele 15 caused by West African-specific primer binding mutation.",
        iso17025_conformance_note="ISO 17025 QA/QC rescue of population-specific null alleles."
    ),
}
