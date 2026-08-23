"""
FORENZA Machine Learning STR Calling Certified Reference Standards & Golden Vectors.
Source: Barash et al. (2023) FSIG • PROVEDIt Mixture Benchmark • ISFG DNA Commission (2016).
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class MLSTRGoldenVector:
    vector_id: str
    name: str
    locus: str
    challenge_type: str
    raw_peak_descriptions: List[str]
    expected_classification_labels: List[str]
    expected_action_taken: str
    mcmc_speedup_factor: float
    description: str
    iso17025_conformance_note: str


GOLDEN_VECTORS_MLSTR: Dict[str, MLSTRGoldenVector] = {
    "VECTOR_MLSTR_01": MLSTRGoldenVector(
        vector_id="VECTOR_MLSTR_01",
        name="Severe Back-Stutter Discrimination & Subtraction",
        locus="D21S11",
        challenge_type="High-Ratio Reverse Stutter (SR = 18.5%)",
        raw_peak_descriptions=[
            "Peak_30 (2400 RFU, Major Allele)",
            "Peak_29 (444 RFU, SR=18.5% at -4 bp position)"
        ],
        expected_classification_labels=["CLASS_TRUE_ALLELE", "CLASS_BACK_STUTTER"],
        expected_action_taken="SUBTRACT_STUTTER_SIGNAL",
        mcmc_speedup_factor=1.45,
        description="Correctly discriminates severe back-stutter from genuine minor contributor peak in D21S11.",
        iso17025_conformance_note="ISO/IEC 17025 zero false positive donor inclusion under SWGDAM 2020."
    ),
    "VECTOR_MLSTR_02": MLSTRGoldenVector(
        vector_id="VECTOR_MLSTR_02",
        name="Split -A / +A Non-Template Adenylation Recombination",
        locus="TH01",
        challenge_type="Incomplete Polymerase Terminal Transferase (+1 bp peak)",
        raw_peak_descriptions=[
            "Peak_9.3 (1800 RFU, Major Allele)",
            "Peak_PlusA (360 RFU, at +1 bp position)"
        ],
        expected_classification_labels=["CLASS_TRUE_ALLELE", "CLASS_PLUS_A_ARTIFACT"],
        expected_action_taken="RECOMBINE_PLUS_A_INTO_PARENT_PEAK",
        mcmc_speedup_factor=1.30,
        description="Recombines split +A peak into parent 9.3 allele, conserving total signal area.",
        iso17025_conformance_note="ISO/IEC 17025 signal conservation and elimination of spurious split calls."
    ),
    "VECTOR_MLSTR_03": MLSTRGoldenVector(
        vector_id="VECTOR_MLSTR_03",
        name="High-RFU Spectral Pull-Up Elimination",
        locus="vWA",
        challenge_type="Secondary Dye Bleedthrough (h > 6000 RFU in Blue Channel)",
        raw_peak_descriptions=[
            "Major_Blue_Peak (6200 RFU in 6-FAM dye)",
            "PullUp_Yellow_Peak (480 RFU in NED dye co-eluting at identical retention time)"
        ],
        expected_classification_labels=["CLASS_TRUE_ALLELE", "CLASS_SPECTRAL_PULL_UP"],
        expected_action_taken="CULL_SPECTRAL_PULL_UP_BLEEDTHROUGH",
        mcmc_speedup_factor=1.60,
        description="Identifies and culls spectral pull-up bleedthrough caused by CCD sensor saturation.",
        iso17025_conformance_note="ISO/IEC 17025 optical artifact rejection without false profile alteration."
    ),
    "VECTOR_MLSTR_04": MLSTRGoldenVector(
        vector_id="VECTOR_MLSTR_04",
        name="PROVEDIt 3-Person Mixture Pre-Filtering & Search Space Reduction",
        locus="D3S1358",
        challenge_type="Complex 3-Person Mixture with 2 Stutters and 1 Noise Peak",
        raw_peak_descriptions=[
            "Allele_15 (1400 RFU, Contributor A)",
            "Allele_16 (950 RFU, Contributor B)",
            "Allele_17 (600 RFU, Contributor C)",
            "Stutter_14 (120 RFU, Back-Stutter of 15)",
            "Noise_Peak (32 RFU, Sub-AT baseline noise)"
        ],
        expected_classification_labels=[
            "CLASS_TRUE_ALLELE",
            "CLASS_TRUE_ALLELE",
            "CLASS_TRUE_ALLELE",
            "CLASS_BACK_STUTTER",
            "CLASS_BASE_NOISE_DROP_IN"
        ],
        expected_action_taken="OPTIMIZE_MCMC_SEARCH_SPACE",
        mcmc_speedup_factor=2.10,
        description="Filters stutters and sub-AT noise, reducing MCMC permutation state space from 32 to 8 candidate genotypes.",
        iso17025_conformance_note="ISO/IEC 17025 MCMC acceleration with Gelman-Rubin R̂ < 1.02 guaranteed."
    ),
}
