"""
FORENZA Forensic Evidence Operating System
Pillar 1 — Module 1.4: Low-Template DNA (LTDNA) Stochastic Modeling Engine
Sub-Item 1.4.2: Reference Datasets & Casework Dilution Series Unit Test Suite

Tests:
  1. TestLCNSerialDilutionDatasets: 6 Dilution Tiers (15-1000 pg), Monotonicity & Size Decay.
  2. TestSubstrateRecoveryMatrix: 4 Substrate Efficiencies, 50 pg Deposition, Warnings.
  3. TestGoldenTouchCaseworkVectors: VECTOR_03 & VECTOR_TERM_06 24-Locus Touch Profiles.
  4. TestNISTSRM2391dProfileIntegrity: 24-Locus Concordance & Certified Standards.
"""

import math
import pytest
from typing import Dict, List, Tuple

from backend.node.services.forensic.ltdna.ltdna_reference_datasets import (
    LTDNAReferenceDatasetRegistry,
    LCNDilutionTier,
    SubstrateRecoverySpec,
    SubstrateRecoveryResult,
    TouchBenchmarkVector,
    NIST_SRM2391D_COMP_A_PROFILE,
    STR_AMPLICON_MEAN_BP,
)
from backend.node.services.forensic.ltdna.ltdna_mathematical_formulation import (
    LTDNAMathematicalFormulation,
)


# ===========================================================================
# 1. Peter Gill / LCN Standard Serial Dilution Dataset Tests
# ===========================================================================

class TestLCNSerialDilutionDatasets:
    """Verifies Peter Gill / LCN serial dilution benchmark series across 6 template tiers."""

    def test_all_six_dilution_tiers_present(self):
        """Registry contains all 6 required LCN dilution tiers."""
        expected_tiers = [
            "LCN_DILUTION_1000PG",
            "LCN_DILUTION_500PG",
            "LCN_DILUTION_100PG",
            "LCN_DILUTION_60PG",
            "LCN_DILUTION_30PG",
            "LCN_DILUTION_15PG",
        ]
        available_tiers = LTDNAReferenceDatasetRegistry.list_all_tiers()
        for tier_id in expected_tiers:
            assert tier_id in available_tiers
            tier = LTDNAReferenceDatasetRegistry.get_dilution_tier(tier_id)
            assert isinstance(tier, LCNDilutionTier)
            assert tier.nominal_mass_pg > 0.0

    def test_dilution_cell_count_scaling(self):
        """Equivalent diploid cell counts scale linearly with template mass (6.6 pg/cell)."""
        masses = [1000.0, 500.0, 100.0, 60.0, 30.0, 15.0]
        for m in masses:
            tier_id = f"LCN_DILUTION_{int(m)}PG"
            tier = LTDNAReferenceDatasetRegistry.get_dilution_tier(tier_id)
            # 1 diploid human cell ≈ 6.6 pg genomic DNA
            expected_cells = m / 6.6
            assert abs(tier.equivalent_cells - expected_cells) < 2.0

    def test_dropout_probability_monotonic_increase_with_dilution(self):
        """Expected dropout probability increases monotonically as nominal mass decreases."""
        tier_ids = [
            "LCN_DILUTION_1000PG",
            "LCN_DILUTION_500PG",
            "LCN_DILUTION_100PG",
            "LCN_DILUTION_60PG",
            "LCN_DILUTION_30PG",
            "LCN_DILUTION_15PG",
        ]
        p_drops = [
            LTDNAReferenceDatasetRegistry.get_dilution_tier(t).expected_p_dropout
            for t in tier_ids
        ]
        for i in range(len(p_drops) - 1):
            assert p_drops[i] <= p_drops[i + 1], f"Dropout monotonicity failed: {tier_ids[i]} ({p_drops[i]}) > {tier_ids[i+1]} ({p_drops[i+1]})"

        # Check boundary values
        assert p_drops[0] < 0.0001        # 1000 pg pristine
        assert abs(p_drops[2] - 0.008163) < 1e-4  # 100 pg boundary
        assert abs(p_drops[3] - 0.167982) < 1e-4  # 60 pg casework
        assert abs(p_drops[4] - 0.689974) < 1e-4  # 30 pg touch
        assert abs(p_drops[5] - 0.880797) < 1e-4  # 15 pg single-cell

    def test_heterozygote_balance_degradation_with_dilution(self):
        """Expected heterozygote balance (H_b) decreases monotonically with lower mass."""
        tier_ids = [
            "LCN_DILUTION_1000PG",
            "LCN_DILUTION_500PG",
            "LCN_DILUTION_100PG",
            "LCN_DILUTION_60PG",
            "LCN_DILUTION_30PG",
            "LCN_DILUTION_15PG",
        ]
        hb_vals = [
            LTDNAReferenceDatasetRegistry.get_dilution_tier(t).expected_hb
            for t in tier_ids
        ]
        for i in range(len(hb_vals) - 1):
            assert hb_vals[i] > hb_vals[i + 1]

        assert hb_vals[0] >= 0.90  # 1000 pg pristine
        assert hb_vals[-1] <= 0.40 # 15 pg severe imbalance

    def test_dropout_loci_count_escalation(self):
        """Number of dropped loci escalates as template approaches single-cell range."""
        tier_1000 = LTDNAReferenceDatasetRegistry.get_dilution_tier("LCN_DILUTION_1000PG")
        tier_500 = LTDNAReferenceDatasetRegistry.get_dilution_tier("LCN_DILUTION_500PG")
        tier_60 = LTDNAReferenceDatasetRegistry.get_dilution_tier("LCN_DILUTION_60PG")
        tier_30 = LTDNAReferenceDatasetRegistry.get_dilution_tier("LCN_DILUTION_30PG")
        tier_15 = LTDNAReferenceDatasetRegistry.get_dilution_tier("LCN_DILUTION_15PG")

        assert len(tier_1000.dropout_loci) == 0
        assert len(tier_500.dropout_loci) == 0
        assert len(tier_60.dropout_loci) >= 5
        assert len(tier_30.dropout_loci) >= 15
        assert len(tier_15.dropout_loci) >= 20

    def test_amplicon_size_dependent_dropout_hierarchy(self):
        """Large amplicons (e.g. SE33 360 bp, Penta E 410 bp) drop out before short amplicons."""
        tier_60 = LTDNAReferenceDatasetRegistry.get_dilution_tier("LCN_DILUTION_60PG")
        # In 60 pg tier, large amplicons SE33, Penta_E, CSF1PO, D2S1338 drop out
        assert "SE33" in tier_60.dropout_loci
        assert "Penta_E" in tier_60.dropout_loci
        # Short amplicons D3S1358 (125 bp), D10S1248 (105 bp), D22S1045 (110 bp) survive
        assert "D3S1358" not in tier_60.dropout_loci
        assert "D10S1248" not in tier_60.dropout_loci
        assert "D22S1045" not in tier_60.dropout_loci

    def test_invalid_dilution_tier_key_error(self):
        """Querying a non-existent dilution tier ID raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            LTDNAReferenceDatasetRegistry.get_dilution_tier("LCN_DILUTION_9999PG")


# ===========================================================================
# 2. Substrate Recovery Casework Matrix Tests
# ===========================================================================

class TestSubstrateRecoveryMatrix:
    """Verifies substrate recovery efficiencies and empirical simulation calculations."""

    def test_all_four_substrates_registered(self):
        """Registry contains all 4 standard forensic substrate materials."""
        expected_subs = [
            "SMOOTH_NON_POROUS",
            "TEXTURED_NON_POROUS",
            "POROUS_FABRIC",
            "ROUGH_WOOD",
        ]
        available_subs = LTDNAReferenceDatasetRegistry.list_all_substrates()
        for sub_id in expected_subs:
            assert sub_id in available_subs
            spec = LTDNAReferenceDatasetRegistry.get_substrate_spec(sub_id)
            assert isinstance(spec, SubstrateRecoverySpec)
            assert spec.recovery_efficiency > 0.0

    def test_substrate_efficiency_hierarchy(self):
        """Smooth non-porous > Textured non-porous > Porous fabric > Rough wood."""
        eff_smooth = LTDNAReferenceDatasetRegistry.get_substrate_spec("SMOOTH_NON_POROUS").recovery_efficiency
        eff_textured = LTDNAReferenceDatasetRegistry.get_substrate_spec("TEXTURED_NON_POROUS").recovery_efficiency
        eff_fabric = LTDNAReferenceDatasetRegistry.get_substrate_spec("POROUS_FABRIC").recovery_efficiency
        eff_wood = LTDNAReferenceDatasetRegistry.get_substrate_spec("ROUGH_WOOD").recovery_efficiency

        assert eff_smooth == 0.60
        assert eff_textured == 0.40
        assert eff_fabric == 0.20
        assert eff_wood == 0.15
        assert eff_smooth > eff_textured > eff_fabric > eff_wood

    def test_simulate_substrate_recovery_50pg_deposition(self):
        """Simulating 50 pg touch deposition yields exact recovered mass and dropout."""
        # 1. Smooth Non-Porous (60%): 50 * 0.60 = 30.0 pg -> P(D) ≈ 68.9974%
        res_smooth = LTDNAReferenceDatasetRegistry.simulate_substrate_recovery(50.0, "SMOOTH_NON_POROUS")
        assert abs(res_smooth.recovered_mass_pg - 30.0) < 1e-4
        assert abs(res_smooth.dropout_probability - 0.689974) < 1e-4
        assert res_smooth.stochastic_warning

        # 2. Textured Non-Porous (40%): 50 * 0.40 = 20.0 pg -> logit = 3.20 - 1.60 = 1.60 -> P(D) ≈ 83.20%
        res_textured = LTDNAReferenceDatasetRegistry.simulate_substrate_recovery(50.0, "TEXTURED_NON_POROUS")
        assert abs(res_textured.recovered_mass_pg - 20.0) < 1e-4
        expected_p_20 = 1.0 / (1.0 + math.exp(-1.60))
        assert abs(res_textured.dropout_probability - expected_p_20) < 1e-4

        # 3. Porous Fabric (20%): 50 * 0.20 = 10.0 pg -> logit = 3.20 - 0.80 = 2.40 -> P(D) ≈ 91.68%
        res_fabric = LTDNAReferenceDatasetRegistry.simulate_substrate_recovery(50.0, "POROUS_FABRIC")
        assert abs(res_fabric.recovered_mass_pg - 10.0) < 1e-4
        expected_p_10 = 1.0 / (1.0 + math.exp(-2.40))
        assert abs(res_fabric.dropout_probability - expected_p_10) < 1e-4

        # 4. Rough Wood (15%): 50 * 0.15 = 7.5 pg -> logit = 3.20 - 0.60 = 2.60 -> P(D) ≈ 93.08%
        res_wood = LTDNAReferenceDatasetRegistry.simulate_substrate_recovery(50.0, "ROUGH_WOOD")
        assert abs(res_wood.recovered_mass_pg - 7.5) < 1e-4
        expected_p_75 = 1.0 / (1.0 + math.exp(-2.60))
        assert abs(res_wood.dropout_probability - expected_p_75) < 1e-4

    def test_high_mass_recovery_no_stochastic_warning(self):
        """Deposition of 500 pg on smooth glass yields 300 pg with zero stochastic warning."""
        res_high = LTDNAReferenceDatasetRegistry.simulate_substrate_recovery(500.0, "SMOOTH_NON_POROUS")
        assert res_high.recovered_mass_pg == 300.0
        assert res_high.dropout_probability < 0.0001
        assert not res_high.stochastic_warning
        assert "STANDARD TEMPLATE" in res_high.interpretation

    def test_invalid_substrate_inputs(self):
        """Non-positive initial mass or invalid substrate ID raises appropriate error."""
        with pytest.raises(ValueError, match="strictly positive"):
            LTDNAReferenceDatasetRegistry.simulate_substrate_recovery(0.0, "SMOOTH_NON_POROUS")
        with pytest.raises(KeyError, match="not found"):
            LTDNAReferenceDatasetRegistry.simulate_substrate_recovery(50.0, "UNKNOWN_SURFACE")


# ===========================================================================
# 3. Golden Benchmark Touch Casework Vector Tests
# ===========================================================================

class TestGoldenTouchCaseworkVectors:
    """Verifies golden benchmark touch DNA casework vectors (VECTOR_03 & VECTOR_TERM_06)."""

    def test_vector_03_benchmark_integrity(self):
        """VECTOR_03 benchmark vector contains single-locus vWA dropout casework data."""
        vec03 = LTDNAReferenceDatasetRegistry.get_benchmark_vector("VECTOR_03")
        assert vec03.vector_id == "VECTOR_03"
        assert "vWA" in vec03.suspect_genotypes
        assert vec03.suspect_genotypes["vWA"] == (16.0, 17.0)
        assert 16.0 in vec03.observed_epg_peaks["vWA"]
        assert 17.0 not in vec03.observed_epg_peaks["vWA"]
        assert vec03.observed_epg_peaks["vWA"][16.0] == 80.0
        assert "vWA" in vec03.masked_dropout_loci

    def test_vector_term_06_benchmark_integrity(self):
        """VECTOR_TERM_06 contains full 24-locus touch DNA profile with stochastic flags."""
        vec06 = LTDNAReferenceDatasetRegistry.get_benchmark_vector("VECTOR_TERM_06")
        assert vec06.vector_id == "VECTOR_TERM_06"
        assert len(vec06.suspect_genotypes) == 24
        assert len(vec06.observed_epg_peaks) == 24
        assert vec06.nominal_template_pg == 31.25

        # Check dropout loci (alleles masked or dropped)
        assert "D3S1358" in vec06.masked_dropout_loci
        assert "D21S11" in vec06.masked_dropout_loci
        assert "D5S818" in vec06.masked_dropout_loci
        assert "Penta_E" in vec06.masked_dropout_loci

        # Verify heterozygote peak imbalance at vWA (Hb = 50 / 110 = 0.455 < 0.60)
        vwa_peaks = vec06.observed_epg_peaks["vWA"]
        assert 16.0 in vwa_peaks and 18.0 in vwa_peaks
        hb_vwa = min(vwa_peaks.values()) / max(vwa_peaks.values())
        assert abs(hb_vwa - (50.0 / 110.0)) < 1e-4
        assert hb_vwa < 0.60


# ===========================================================================
# 4. NIST SRM 2391d Component A Profile Integrity Tests
# ===========================================================================

class TestNISTSRM2391dProfileIntegrity:
    """Verifies NIST SRM 2391d Component A certified standard reference profile."""

    def test_nist_profile_contains_all_24_loci(self):
        """NIST SRM 2391d Comp A profile contains all 24 Expanded CODIS loci."""
        expected_loci = [
            "D3S1358", "vWA", "FGA", "D8S1179", "D21S11", "D18S51",
            "D5S818", "D13S317", "D7S820", "TH01", "TPOX", "CSF1PO",
            "D1S1656", "D2S1338", "D10S1248", "D12S391", "D19S433",
            "D22S1045", "D2S441", "D6S1043", "SE33", "Penta_D", "Penta_E", "Amelogenin"
        ]
        for loc in expected_loci:
            assert loc in NIST_SRM2391D_COMP_A_PROFILE
            a1, a2 = NIST_SRM2391D_COMP_A_PROFILE[loc]
            assert a1 > 0.0 and a2 > 0.0

    def test_nist_certified_key_alleles(self):
        """Key diagnostic microvariant and certified alleles match NIST reference values."""
        assert NIST_SRM2391D_COMP_A_PROFILE["TH01"] == (6.0, 9.3)
        assert NIST_SRM2391D_COMP_A_PROFILE["D1S1656"] == (15.0, 17.3)
        assert NIST_SRM2391D_COMP_A_PROFILE["SE33"] == (27.2, 28.2)
        assert NIST_SRM2391D_COMP_A_PROFILE["Amelogenin"] == (1.0, 2.0)
