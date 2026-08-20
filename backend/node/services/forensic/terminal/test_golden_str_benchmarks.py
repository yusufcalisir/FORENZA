"""
Unit tests for FORENZA Golden Benchmark STR Profiles (STR-A, STR-B, STR-C)
Verbatim validation of NIST 1036 Population Genetics, Capillary Electrophoresis Binning,
Micro-Variants, and Log-Likelihood Biocomputational Metrics.
Derived from: research/str_24_locus_microvariants_research.md (Section 5)
"""

import pytest
import math
from backend.node.services.forensic.terminal.nist_1036_popgen_engine import (
    Nist1036PopGenEngine,
    NistPopulationEnum,
)
from backend.node.services.forensic.terminal.str_locus_registry_engine import (
    StrLocusRegistryEngine,
    STR_LOCUS_24_MASTER_REGISTRY,
)
from backend.node.services.forensic.terminal.casework_presets import (
    GOLDEN_CASEWORK_PRESETS,
)


class TestGoldenStrBenchmarks:
    """Test suite executing Golden Benchmark Profiles STR-A, STR-B, and STR-C."""

    def test_benchmark_str_a_european(self):
        """
        Benchmark Profile STR-A (European Reference):
        - Population: Caucasian (2N=722), theta=0.01
        - Key Micro-Variants: TH01 9.3/9.3, D1S1656 14/17.3, SE33 26.2/28.2
        - Calculated Product: RMP = 9.3677e-25, Log10(LR) = 24.0284
        """
        profile = {
            "D3S1358": ("15", "16"),
            "vWA": ("16", "17"),
            "FGA": ("21", "23"),
            "D8S1179": ("13", "14"),
            "D21S11": ("29", "30"),
            "D18S51": ("12", "15"),
            "D5S818": ("11", "12"),
            "D13S317": ("11", "12"),
            "D7S820": ("10", "11"),
            "D16S539": ("11", "12"),
            "CSF1PO": ("10", "11"),
            "TH01": ("9.3", "9.3"),
            "TPOX": ("8", "11"),
            "D1S1656": ("14", "17.3"),
            "D2S441": ("11", "12"),
            "D2S1338": ("19", "23"),
            "D10S1248": ("13", "14"),
            "D12S391": ("18", "19"),
            "D19S433": ("13", "14"),
            "D22S1045": ("15", "16"),
            "SE33": ("26.2", "28.2"),
            "Penta D": ("9", "11"),
            "Penta E": ("12", "13"),
            "Amelogenin": ("X", "Y"),
        }

        res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
            profile=profile,
            population="Caucasian",
            theta=0.01,
        )

        assert pytest.approx(res["combined_log10_lr"], abs=1e-4) == 24.0284
        assert pytest.approx(res["combined_rmp"], rel=1e-4) == 9.3677e-25
        assert "Extremely Strong Support" in res["enfsi_verbal_scale"]

        # Micro-variant verification
        mv_th01 = StrLocusRegistryEngine.get_microvariant_details("TH01", "9.3")
        assert mv_th01 is not None and mv_th01.delta_bp == 3
        mv_d1s = StrLocusRegistryEngine.get_microvariant_details("D1S1656", "17.3")
        assert mv_d1s is not None and mv_d1s.delta_bp == 3
        mv_se33 = StrLocusRegistryEngine.get_microvariant_details("SE33", "26.2")
        assert mv_se33 is not None and mv_se33.delta_bp == 2

    def test_benchmark_str_b_african_american(self):
        """
        Benchmark Profile STR-B (African American Reference):
        - Population: African American (2N=684), theta=0.01
        - Key Micro-Variants: D21S11 29/31.2, FGA 22/25, D19S433 12/14.2
        - Calculated Product: RMP = 6.9141e-28, Log10(LR) = 27.1603
        """
        profile = {
            "D3S1358": ("16", "17"),
            "vWA": ("15", "18"),
            "FGA": ("22", "25"),
            "D8S1179": ("14", "15"),
            "D21S11": ("29", "31.2"),
            "D18S51": ("15", "17"),
            "D5S818": ("12", "13"),
            "D13S317": ("12", "13"),
            "D7S820": ("8", "10"),
            "D16S539": ("9", "11"),
            "CSF1PO": ("10", "12"),
            "TH01": ("7", "9"),
            "TPOX": ("8", "9"),
            "D1S1656": ("15", "16"),
            "D2S441": ("10", "11"),
            "D2S1338": ("17", "19"),
            "D10S1248": ("14", "15"),
            "D12S391": ("17", "21"),
            "D19S433": ("12", "14.2"),
            "D22S1045": ("11", "16"),
            "SE33": ("18", "22.2"),
            "Penta D": ("11", "12"),
            "Penta E": ("7", "12"),
            "Amelogenin": ("X", "Y"),
        }

        res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
            profile=profile,
            population="African American",
            theta=0.01,
        )

        assert pytest.approx(res["combined_log10_lr"], abs=1e-4) == 27.1603
        assert pytest.approx(res["combined_rmp"], rel=1e-4) == 6.9141e-28
        assert "Extremely Strong Support" in res["enfsi_verbal_scale"]

        # Micro-variant verification
        mv_d21 = StrLocusRegistryEngine.get_microvariant_details("D21S11", "31.2")
        assert mv_d21 is not None and mv_d21.delta_bp == 2
        mv_d19 = StrLocusRegistryEngine.get_microvariant_details("D19S433", "14.2")
        assert mv_d19 is not None and mv_d19.delta_bp == 2

    def test_benchmark_str_c_hispanic_amel_y_null(self):
        """
        Benchmark Profile STR-C (Hispanic Amelogenin Y-Null Deletion Reference):
        - Population: Hispanic (2N=472), theta=0.01
        - Key Markers: Amelogenin (X, X), DYS391 (11), TH01 (6, 9.3), D2S441 (11.3, 14)
        - Calculated Product: RMP = 4.9150e-30, Log10(LR) = 29.3085
        """
        profile = {
            "D3S1358": ("15", "17"),
            "vWA": ("17", "18"),
            "FGA": ("20", "24"),
            "D8S1179": ("12", "13"),
            "D21S11": ("28", "30"),
            "D18S51": ("13", "13"),
            "D5S818": ("10", "11"),
            "D13S317": ("11", "13"),
            "D7S820": ("9", "10"),
            "D16S539": ("12", "13"),
            "CSF1PO": ("11", "12"),
            "TH01": ("6", "9.3"),
            "TPOX": ("8", "8"),
            "D1S1656": ("12", "15"),
            "D2S441": ("11.3", "14"),
            "D2S1338": ("20", "25"),
            "D10S1248": ("12", "13"),
            "D12S391": ("18", "20"),
            "D19S433": ("13", "15"),
            "D22S1045": ("15", "17"),
            "SE33": ("19", "27.2"),
            "Penta D": ("9", "10"),
            "Penta E": ("11", "14"),
            "Amelogenin": ("X", "X"),
        }

        res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
            profile=profile,
            population="Hispanic",
            theta=0.01,
        )

        assert pytest.approx(res["combined_log10_lr"], abs=1e-4) == 29.3085
        assert pytest.approx(res["combined_rmp"], rel=1e-4) == 4.9150e-30
        assert "Extremely Strong Support" in res["enfsi_verbal_scale"]

        # Micro-variant verification
        mv_d2s = StrLocusRegistryEngine.get_microvariant_details("D2S441", "11.3")
        assert mv_d2s is not None and mv_d2s.delta_bp == 3

    def test_casework_preset_synchronization(self):
        """Verify casework presets dictionary contains the 3 Golden STR benchmarks."""
        assert "VECTOR_TERM_01" in GOLDEN_CASEWORK_PRESETS
        assert "VECTOR_TERM_02" in GOLDEN_CASEWORK_PRESETS
        assert "VECTOR_TERM_03" in GOLDEN_CASEWORK_PRESETS

        p1 = GOLDEN_CASEWORK_PRESETS["VECTOR_TERM_01"]
        assert p1.str_profile["TH01"]["allele1"] == "9.3"
        assert p1.str_profile["TH01"]["allele2"] == "9.3"

        p2 = GOLDEN_CASEWORK_PRESETS["VECTOR_TERM_02"]
        assert p2.str_profile["D21S11"]["allele2"] == "31.2"

        p3 = GOLDEN_CASEWORK_PRESETS["VECTOR_TERM_03"]
        assert p3.supplementary_markers["DYS391"] == "11"
        assert p3.str_profile["Amelogenin"]["allele1"] == "X"
        assert p3.str_profile["Amelogenin"]["allele2"] == "X"
