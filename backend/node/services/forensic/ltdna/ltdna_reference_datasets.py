"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.4: Low-Template DNA (LTDNA) Stochastic Modeling Engine
Sub-Item 1.4.2: Reference Datasets & Casework Dilution Series

Derives exclusively and verbatim from:
  - Pillar 1 Research Specification (research/pillar_1_probabilistic_genotyping_research.md §4, §6, Artifact D)
  - DNA SNP Terminal Research (research/dna_snp_terminal_research.md §6.1, §6.2)
  - NIST SRM 2391d Certified Reference Standard (research/certified_reference_standards_gold_vectors_research.md)
  - Gill et al. (2000, 2001) LCN DNA Serial Dilution Standards
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

try:
    from .ltdna_mathematical_formulation import (
        LTDNAMathematicalFormulation,
        DROPOUT_BETA0_MASS,
        DROPOUT_BETA1_MASS,
        DROPOUT_BETA0_RFU,
        DROPOUT_BETA1_RFU,
        DROPIN_LAMBDA_POISSON,
        ANALYTICAL_THRESHOLD_RFU,
        STOCHASTIC_THRESHOLD_RFU,
        HB_FLAG_THRESHOLD,
    )
except ImportError:
    from backend.node.services.forensic.ltdna.ltdna_mathematical_formulation import (
        LTDNAMathematicalFormulation,
        DROPOUT_BETA0_MASS,
        DROPOUT_BETA1_MASS,
        DROPOUT_BETA0_RFU,
        DROPOUT_BETA1_RFU,
        DROPIN_LAMBDA_POISSON,
        ANALYTICAL_THRESHOLD_RFU,
        STOCHASTIC_THRESHOLD_RFU,
        HB_FLAG_THRESHOLD,
    )


# ===========================================================================
# 1. Reference Data Structures
# ===========================================================================

@dataclass(frozen=True)
class LCNDilutionTier:
    """Standardized LCN Serial Dilution Tier Profile."""
    tier_id: str
    nominal_mass_pg: float
    equivalent_cells: float
    expected_p_dropout: float
    expected_hb: float
    stochastic_zone: str
    operational_designation: str
    locus_peak_heights: Dict[str, Dict[float, float]]
    dropout_loci: List[str]


@dataclass(frozen=True)
class SubstrateRecoverySpec:
    """Forensic Substrate Material Recovery Efficiency Specification."""
    substrate_id: str
    name: str
    description: str
    recovery_efficiency: float
    porosity_type: str           # 'NON_POROUS', 'POROUS', 'SEMI_POROUS'
    touch_swab_protocol: str


@dataclass(frozen=True)
class SubstrateRecoveryResult:
    """Substrate recovery calculation and resulting stochastic properties."""
    substrate_id: str
    initial_mass_pg: float
    recovery_efficiency: float
    recovered_mass_pg: float
    dropout_probability: float
    stochastic_warning: bool
    interpretation: str


@dataclass(frozen=True)
class TouchBenchmarkVector:
    """Golden Benchmark Touch Casework Profile."""
    vector_id: str
    title: str
    description: str
    nominal_template_pg: float
    substrate_id: str
    suspect_genotypes: Dict[str, Tuple[float, float]]
    observed_epg_peaks: Dict[str, Dict[float, float]]
    masked_dropout_loci: List[str]
    expected_stochastic_flags: List[str]
    target_log10_lr: Optional[float]
    tolerance_log10_lr: Optional[float]


# ===========================================================================
# 2. Standard 24-Locus Reference Genotypes (NIST SRM 2391d Component A)
# ===========================================================================

NIST_SRM2391D_COMP_A_PROFILE: Dict[str, Tuple[float, float]] = {
    "D3S1358": (15.0, 16.0),
    "vWA": (16.0, 17.0),
    "FGA": (21.0, 22.0),
    "D8S1179": (13.0, 14.0),
    "D21S11": (28.0, 30.0),
    "D18S51": (12.0, 15.0),
    "D5S818": (11.0, 12.0),
    "D13S317": (11.0, 13.0),
    "D7S820": (9.0, 10.0),
    "TH01": (6.0, 9.3),
    "TPOX": (8.0, 11.0),
    "CSF1PO": (10.0, 11.0),
    "D1S1656": (15.0, 17.3),
    "D2S1338": (17.0, 20.0),
    "D10S1248": (13.0, 14.0),
    "D12S391": (18.0, 21.0),
    "D19S433": (13.0, 14.0),
    "D22S1045": (15.0, 16.0),
    "D2S441": (11.0, 12.0),
    "D6S1043": (11.0, 12.0),
    "SE33": (27.2, 28.2),
    "Penta_D": (9.0, 12.0),
    "Penta_E": (7.0, 14.0),
    "Amelogenin": (1.0, 2.0),  # X, Y
}

# Standard amplicon base-pair lengths for size-dependent degradation
STR_AMPLICON_MEAN_BP: Dict[str, float] = {
    "D3S1358": 125.0,
    "vWA": 175.0,
    "FGA": 260.0,
    "D8S1179": 140.0,
    "D21S11": 215.0,
    "D18S51": 290.0,
    "D5S818": 155.0,
    "D13S317": 220.0,
    "D7S820": 240.0,
    "TH01": 180.0,
    "TPOX": 230.0,
    "CSF1PO": 310.0,
    "D1S1656": 145.0,
    "D2S1338": 330.0,
    "D10S1248": 105.0,
    "D12S391": 235.0,
    "D19S433": 120.0,
    "D22S1045": 110.0,
    "D2S441": 100.0,
    "D6S1043": 160.0,
    "SE33": 360.0,
    "Penta_D": 375.0,
    "Penta_E": 410.0,
    "Amelogenin": 108.0,
}


# ===========================================================================
# 3. LTDNAReferenceDatasetRegistry
# ===========================================================================

class LTDNAReferenceDatasetRegistry:
    """
    Forensic Reference Dataset Registry & Ingestion Engine for Low-Template DNA (LTDNA).
    """

    # -----------------------------------------------------------------------
    # Substrate Recovery Casework Matrix
    # -----------------------------------------------------------------------
    SUBSTRATE_RECOVERY_MATRIX: Dict[str, SubstrateRecoverySpec] = {
        "SMOOTH_NON_POROUS": SubstrateRecoverySpec(
            substrate_id="SMOOTH_NON_POROUS",
            name="Smooth Non-Porous Surface",
            description="Glass slides, stainless steel cutlery/blades, polished hard plastic",
            recovery_efficiency=0.60,
            porosity_type="NON_POROUS",
            touch_swab_protocol="Double-swab method (wet/dry sterile flocked swab)",
        ),
        "TEXTURED_NON_POROUS": SubstrateRecoverySpec(
            substrate_id="TEXTURED_NON_POROUS",
            name="Textured Non-Porous Surface",
            description="Textured polymer firearm grips, vehicle steering wheels, molded plastics",
            recovery_efficiency=0.40,
            porosity_type="SEMI_POROUS",
            touch_swab_protocol="Flocked swab with 0.1% SDS / TE buffer extraction",
        ),
        "POROUS_FABRIC": SubstrateRecoverySpec(
            substrate_id="POROUS_FABRIC",
            name="Porous Garment & Fabric",
            description="Cotton collars/cuffs, denim jeans waistband, synthetic fabric",
            recovery_efficiency=0.20,
            porosity_type="POROUS",
            touch_swab_protocol="Substrate cutting or adhesive tape-lifting extraction",
        ),
        "ROUGH_WOOD": SubstrateRecoverySpec(
            substrate_id="ROUGH_WOOD",
            name="Rough Wood & Mineral Surface",
            description="Unfinished wood handle/club, brick surface, coarse stone/concrete",
            recovery_efficiency=0.15,
            porosity_type="POROUS",
            touch_swab_protocol="Differential scraping with micro-vacuum or flocked swab",
        ),
    }

    # -----------------------------------------------------------------------
    # Peter Gill / LCN Standard Serial Dilution Dataset (6 Dilution Tiers)
    # -----------------------------------------------------------------------
    LCN_SERIAL_DILUTION_SERIES: Dict[str, LCNDilutionTier] = {
        "LCN_DILUTION_1000PG": LCNDilutionTier(
            tier_id="LCN_DILUTION_1000PG",
            nominal_mass_pg=1000.0,
            equivalent_cells=150.0,
            expected_p_dropout=0.000001,
            expected_hb=0.92,
            stochastic_zone="PRISTINE_STANDARD",
            operational_designation="High-Template Positive Control (1.0 ng)",
            locus_peak_heights={
                locus: {
                    a1: 850.0 - (STR_AMPLICON_MEAN_BP.get(locus, 200.0) * 0.4),
                    a2: 820.0 - (STR_AMPLICON_MEAN_BP.get(locus, 200.0) * 0.4),
                } if a1 != a2 else {
                    a1: 1600.0 - (STR_AMPLICON_MEAN_BP.get(locus, 200.0) * 0.8)
                }
                for locus, (a1, a2) in NIST_SRM2391D_COMP_A_PROFILE.items()
            },
            dropout_loci=[],
        ),
        "LCN_DILUTION_500PG": LCNDilutionTier(
            tier_id="LCN_DILUTION_500PG",
            nominal_mass_pg=500.0,
            equivalent_cells=75.0,
            expected_p_dropout=0.000001,
            expected_hb=0.88,
            stochastic_zone="STANDARD_CASEWORK",
            operational_designation="Standard High Quality Profile (0.5 ng)",
            locus_peak_heights={
                locus: {
                    a1: 450.0 - (STR_AMPLICON_MEAN_BP.get(locus, 200.0) * 0.25),
                    a2: 420.0 - (STR_AMPLICON_MEAN_BP.get(locus, 200.0) * 0.25),
                } if a1 != a2 else {
                    a1: 850.0 - (STR_AMPLICON_MEAN_BP.get(locus, 200.0) * 0.5)
                }
                for locus, (a1, a2) in NIST_SRM2391D_COMP_A_PROFILE.items()
            },
            dropout_loci=[],
        ),
        "LCN_DILUTION_100PG": LCNDilutionTier(
            tier_id="LCN_DILUTION_100PG",
            nominal_mass_pg=100.0,
            equivalent_cells=15.0,
            expected_p_dropout=0.008163,
            expected_hb=0.74,
            stochastic_zone="STOCHASTIC_BOUNDARY",
            operational_designation="SWGDAM Low-Template Transition Boundary (100 pg)",
            locus_peak_heights={
                locus: {
                    a1: max(60.0, 160.0 - (STR_AMPLICON_MEAN_BP.get(locus, 200.0) * 0.20)),
                    a2: max(55.0, 130.0 - (STR_AMPLICON_MEAN_BP.get(locus, 200.0) * 0.20)),
                } if a1 != a2 else {
                    a1: max(100.0, 280.0 - (STR_AMPLICON_MEAN_BP.get(locus, 200.0) * 0.40))
                }
                for locus, (a1, a2) in NIST_SRM2391D_COMP_A_PROFILE.items()
            },
            dropout_loci=[],
        ),
        "LCN_DILUTION_60PG": LCNDilutionTier(
            tier_id="LCN_DILUTION_60PG",
            nominal_mass_pg=60.0,
            equivalent_cells=9.0,
            expected_p_dropout=0.167982,
            expected_hb=0.62,
            stochastic_zone="LOW_TEMPLATE_ZONE",
            operational_designation="Sub-stochastic Low-Template Casework (60 pg)",
            locus_peak_heights={
                "D3S1358": {15.0: 110.0, 16.0: 95.0},
                "vWA": {16.0: 85.0, 17.0: 70.0},
                "FGA": {21.0: 75.0},  # allele 22 dropped
                "D8S1179": {13.0: 100.0, 14.0: 80.0},
                "D21S11": {28.0: 70.0},  # allele 30 dropped
                "D18S51": {12.0: 65.0},  # allele 15 dropped
                "D5S818": {11.0: 90.0, 12.0: 75.0},
                "D13S317": {11.0: 85.0, 13.0: 65.0},
                "D7S820": {9.0: 70.0, 10.0: 55.0},
                "TH01": {6.0: 95.0, 9.3: 85.0},
                "TPOX": {8.0: 80.0, 11.0: 65.0},
                "CSF1PO": {10.0: 60.0},  # allele 11 dropped
                "D1S1656": {15.0: 105.0, 17.3: 90.0},
                "D2S1338": {17.0: 55.0},  # allele 20 dropped
                "D10S1248": {13.0: 115.0, 14.0: 100.0},
                "D12S391": {18.0: 75.0, 21.0: 60.0},
                "D19S433": {13.0: 110.0, 14.0: 95.0},
                "D22S1045": {15.0: 120.0, 16.0: 105.0},
                "D2S441": {11.0: 125.0, 12.0: 110.0},
                "D6S1043": {11.0: 90.0, 12.0: 75.0},
                "SE33": {27.2: 55.0},  # allele 28.2 dropped
                "Penta_D": {9.0: 55.0},  # allele 12 dropped
                "Penta_E": {},  # both dropped
                "Amelogenin": {1.0: 110.0, 2.0: 90.0},
            },
            dropout_loci=["FGA", "D21S11", "D18S51", "CSF1PO", "D2S1338", "SE33", "Penta_D", "Penta_E"],
        ),
        "LCN_DILUTION_30PG": LCNDilutionTier(
            tier_id="LCN_DILUTION_30PG",
            nominal_mass_pg=30.0,
            equivalent_cells=4.5,
            expected_p_dropout=0.689974,
            expected_hb=0.48,
            stochastic_zone="SEVERE_LTDNA_ZONE",
            operational_designation="Touch DNA Casework Swab (30 pg)",
            locus_peak_heights={
                "D3S1358": {15.0: 80.0},
                "vWA": {16.0: 75.0},
                "FGA": {},
                "D8S1179": {13.0: 70.0},
                "D21S11": {},
                "D18S51": {},
                "D5S818": {11.0: 65.0},
                "D13S317": {11.0: 60.0},
                "D7S820": {},
                "TH01": {6.0: 80.0, 9.3: 55.0},
                "TPOX": {8.0: 60.0},
                "CSF1PO": {},
                "D1S1656": {15.0: 75.0},
                "D2S1338": {},
                "D10S1248": {13.0: 85.0, 14.0: 55.0},
                "D12S391": {},
                "D19S433": {13.0: 80.0},
                "D22S1045": {15.0: 90.0, 16.0: 60.0},
                "D2S441": {11.0: 95.0, 12.0: 65.0},
                "D6S1043": {11.0: 65.0},
                "SE33": {},
                "Penta_D": {},
                "Penta_E": {},
                "Amelogenin": {1.0: 85.0},
            },
            dropout_loci=[
                "D3S1358", "vWA", "FGA", "D8S1179", "D21S11", "D18S51",
                "D5S818", "D13S317", "D7S820", "TPOX", "CSF1PO", "D1S1656",
                "D2S1338", "D12S391", "D19S433", "D6S1043", "SE33",
                "Penta_D", "Penta_E", "Amelogenin"
            ],
        ),
        "LCN_DILUTION_15PG": LCNDilutionTier(
            tier_id="LCN_DILUTION_15PG",
            nominal_mass_pg=15.0,
            equivalent_cells=2.2,
            expected_p_dropout=0.880797,
            expected_hb=0.35,
            stochastic_zone="SINGLE_CELL_ULTRALOW",
            operational_designation="Extreme Single-Cell / Trace LTDNA (15 pg)",
            locus_peak_heights={
                "D3S1358": {15.0: 55.0},
                "vWA": {},
                "FGA": {},
                "D8S1179": {},
                "D21S11": {},
                "D18S51": {},
                "D5S818": {},
                "D13S317": {},
                "D7S820": {},
                "TH01": {6.0: 60.0},
                "TPOX": {},
                "CSF1PO": {},
                "D1S1656": {},
                "D2S1338": {},
                "D10S1248": {13.0: 65.0},
                "D12S391": {},
                "D19S433": {13.0: 55.0},
                "D22S1045": {15.0: 70.0},
                "D2S441": {11.0: 75.0},
                "D6S1043": {},
                "SE33": {},
                "Penta_D": {},
                "Penta_E": {},
                "Amelogenin": {1.0: 60.0},
            },
            dropout_loci=[
                "D3S1358", "vWA", "FGA", "D8S1179", "D21S11", "D18S51",
                "D5S818", "D13S317", "D7S820", "TH01", "TPOX", "CSF1PO",
                "D1S1656", "D2S1338", "D10S1248", "D12S391", "D19S433",
                "D22S1045", "D2S441", "D6S1043", "SE33", "Penta_D", "Penta_E", "Amelogenin"
            ],
        ),
    }

    # -----------------------------------------------------------------------
    # Golden Benchmark Casework Vectors
    # -----------------------------------------------------------------------
    GOLDEN_BENCHMARK_VECTORS: Dict[str, TouchBenchmarkVector] = {
        "VECTOR_03": TouchBenchmarkVector(
            vector_id="VECTOR_03",
            title="LTDNA Single-Locus Allele Dropout (vWA Locus)",
            description=(
                "Pillar 1 Research Artifact D benchmark: vWA locus, suspect (16, 17), "
                "observed peak 16@80RFU, allele 17 dropped out, P(D) stochastic penalty active."
            ),
            nominal_template_pg=45.0,
            substrate_id="SMOOTH_NON_POROUS",
            suspect_genotypes={"vWA": (16.0, 17.0)},
            observed_epg_peaks={"vWA": {16.0: 80.0}},
            masked_dropout_loci=["vWA"],
            expected_stochastic_flags=["High Dropout Risk: P(D)=62.25%", "Allelic Dropout Observed (1 alleles)"],
            target_log10_lr=0.5604,
            tolerance_log10_lr=0.20,
        ),
        "VECTOR_TERM_06": TouchBenchmarkVector(
            vector_id="VECTOR_TERM_06",
            title="Full 24-Locus Low-Template Touch DNA Mixture",
            description=(
                "DNA SNP Terminal Research §6.2: Low-Template Touch DNA (Sample TOUCH_LTDNA), "
                "template mass ≈ 31.2 pg (< 62.5 pg), P(D) = 0.35, lambda = 0.08, Hb = 0.45. "
                "Contains dropout masks ([0]) at D3S1358, D21S11, D5S818, D13S317."
            ),
            nominal_template_pg=31.25,
            substrate_id="TEXTURED_NON_POROUS",
            suspect_genotypes={
                "D3S1358": (15.0, 16.0),
                "vWA": (16.0, 18.0),
                "FGA": (22.0, 24.0),
                "D8S1179": (12.0, 14.0),
                "D21S11": (29.0, 31.2),
                "D18S51": (13.0, 17.0),
                "D5S818": (11.0, 12.0),
                "D13S317": (11.0, 13.0),
                "D7S820": (8.0, 10.0),
                "TH01": (7.0, 9.3),
                "TPOX": (8.0, 11.0),
                "CSF1PO": (10.0, 12.0),
                "D1S1656": (12.0, 17.3),
                "D2S1338": (18.0, 23.0),
                "D10S1248": (13.0, 15.0),
                "D12S391": (17.0, 22.0),
                "D19S433": (12.0, 14.0),
                "D22S1045": (14.0, 16.0),
                "D2S441": (10.0, 11.0),
                "D6S1043": (11.0, 18.0),
                "SE33": (19.0, 28.2),
                "Penta_D": (9.0, 11.0),
                "Penta_E": (8.0, 13.0),
                "Amelogenin": (1.0, 2.0),
            },
            observed_epg_peaks={
                "D3S1358": {15.0: 75.0},        # allele 16 dropped
                "vWA": {16.0: 110.0, 18.0: 50.0}, # imbalanced Hb=50/110=0.455
                "FGA": {22.0: 85.0, 24.0: 70.0},
                "D8S1179": {12.0: 90.0, 14.0: 80.0},
                "D21S11": {29.0: 65.0},        # allele 31.2 dropped
                "D18S51": {13.0: 70.0, 17.0: 60.0},
                "D5S818": {11.0: 60.0},         # allele 12 dropped
                "D13S317": {11.0: 85.0, 13.0: 75.0},
                "D7S820": {8.0: 70.0, 10.0: 65.0},
                "TH01": {7.0: 100.0, 9.3: 90.0},
                "TPOX": {8.0: 80.0, 11.0: 70.0},
                "CSF1PO": {10.0: 75.0, 12.0: 65.0},
                "D1S1656": {12.0: 95.0, 17.3: 85.0},
                "D2S1338": {18.0: 65.0},        # allele 23 dropped
                "D10S1248": {13.0: 110.0, 15.0: 95.0},
                "D12S391": {17.0: 70.0, 22.0: 55.0},
                "D19S433": {12.0: 105.0, 14.0: 90.0},
                "D22S1045": {14.0: 115.0, 16.0: 100.0},
                "D2S441": {10.0: 120.0, 11.0: 105.0},
                "D6S1043": {11.0: 85.0, 18.0: 70.0},
                "SE33": {19.0: 55.0},           # allele 28.2 dropped
                "Penta_D": {9.0: 60.0},         # allele 11 dropped
                "Penta_E": {},                  # both dropped
                "Amelogenin": {1.0: 95.0, 2.0: 80.0},
            },
            masked_dropout_loci=["D3S1358", "D21S11", "D5S818", "D2S1338", "SE33", "Penta_D", "Penta_E"],
            expected_stochastic_flags=[
                "H_b < 0.60 Imbalance",
                "Sub-stochastic Peak Heights (< 150 RFU)",
                "Stochastic Boundary Flag Triggered"
            ],
            target_log10_lr=None,
            tolerance_log10_lr=None,
        ),
    }

    # -----------------------------------------------------------------------
    # Helper & Query Methods
    # -----------------------------------------------------------------------

    @classmethod
    def get_dilution_tier(cls, tier_id: str) -> LCNDilutionTier:
        """Retrieve an LCN serial dilution tier by ID."""
        tier = cls.LCN_SERIAL_DILUTION_SERIES.get(tier_id.upper())
        if tier is None:
            valid_ids = list(cls.LCN_SERIAL_DILUTION_SERIES.keys())
            raise KeyError(f"Dilution tier '{tier_id}' not found. Valid IDs: {valid_ids}")
        return tier

    @classmethod
    def get_substrate_spec(cls, substrate_id: str) -> SubstrateRecoverySpec:
        """Retrieve a forensic substrate recovery specification by ID."""
        sub = cls.SUBSTRATE_RECOVERY_MATRIX.get(substrate_id.upper())
        if sub is None:
            valid_ids = list(cls.SUBSTRATE_RECOVERY_MATRIX.keys())
            raise KeyError(f"Substrate '{substrate_id}' not found. Valid IDs: {valid_ids}")
        return sub

    @classmethod
    def get_benchmark_vector(cls, vector_id: str) -> TouchBenchmarkVector:
        """Retrieve a golden benchmark casework vector by ID."""
        vec = cls.GOLDEN_BENCHMARK_VECTORS.get(vector_id.upper())
        if vec is None:
            valid_ids = list(cls.GOLDEN_BENCHMARK_VECTORS.keys())
            raise KeyError(f"Benchmark vector '{vector_id}' not found. Valid IDs: {valid_ids}")
        return vec

    @classmethod
    def simulate_substrate_recovery(
        cls,
        initial_mass_pg: float,
        substrate_id: str,
    ) -> SubstrateRecoveryResult:
        """
        Calculate recovered DNA mass from an initial touch deposition on a specific substrate.

        Uses research-calibrated logistic mass-based dropout model:
          Recovered Mass = Initial Mass * Recovery Efficiency (η)
          P(D) = 1 / (1 + exp(-(β₀ + β₁ · Recovered Mass)))
        """
        if initial_mass_pg <= 0.0:
            raise ValueError(f"Initial DNA mass must be strictly positive (got {initial_mass_pg})")

        spec = cls.get_substrate_spec(substrate_id)
        recovered_mass = initial_mass_pg * spec.recovery_efficiency
        d_res = LTDNAMathematicalFormulation.compute_dropout_probability_mass(recovered_mass)

        is_warning = recovered_mass < 100.0

        interp = (
            f"Deposition of {initial_mass_pg:.1f} pg on {spec.name} yields "
            f"{recovered_mass:.1f} pg ({spec.recovery_efficiency * 100:.0f}% recovery). "
            f"Expected Allelic Dropout P(D) = {d_res.dropout_probability:.2%}. "
            f"Status: {'LOW-TEMPLATE (LTDNA) STOCHASTIC REGIME' if is_warning else 'STANDARD TEMPLATE REGIME'}."
        )

        return SubstrateRecoveryResult(
            substrate_id=spec.substrate_id,
            initial_mass_pg=initial_mass_pg,
            recovery_efficiency=spec.recovery_efficiency,
            recovered_mass_pg=round(recovered_mass, 4),
            dropout_probability=d_res.dropout_probability,
            stochastic_warning=is_warning,
            interpretation=interp,
        )

    @classmethod
    def get_all_dilution_tiers(cls) -> List[LCNDilutionTier]:
        """Return all registered LCN dilution tier objects."""
        return list(cls.LCN_SERIAL_DILUTION_SERIES.values())

    @classmethod
    def get_all_substrates(cls) -> List[SubstrateRecoverySpec]:
        """Return all registered substrate recovery spec objects."""
        return list(cls.SUBSTRATE_RECOVERY_MATRIX.values())

    @classmethod
    def get_all_benchmark_vectors(cls) -> List[TouchBenchmarkVector]:
        """Return all registered golden benchmark vector objects."""
        return list(cls.GOLDEN_BENCHMARK_VECTORS.values())

    @classmethod
    def list_all_tiers(cls) -> List[str]:
        """List all available LCN serial dilution tier IDs."""
        return list(cls.LCN_SERIAL_DILUTION_SERIES.keys())

    @classmethod
    def list_all_substrates(cls) -> List[str]:
        """List all available substrate material IDs."""
        return list(cls.SUBSTRATE_RECOVERY_MATRIX.keys())

    @classmethod
    def list_all_benchmark_vectors(cls) -> List[str]:
        """List all available golden touch casework vector IDs."""
        return list(cls.GOLDEN_BENCHMARK_VECTORS.keys())
