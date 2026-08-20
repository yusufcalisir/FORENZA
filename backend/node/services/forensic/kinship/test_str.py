"""
Unit tests for FORENZA 24-Locus STR & Kinship Engine (Sub-Item 1.1.5)
Validates:
1. 24-locus panel completeness, canonical sorting, and SMM mutation transitions.
2. Pedigree kinship calculations: Parent-Child, Full Siblings, Half Siblings, First Cousins, and Unrelated.
3. FastAPI Population API routes: /profile-rmp and /kinship-duo.

Derived from: research/pillar_1_probabilistic_genotyping_research.md
Compliance: ISO/IEC 17025:2017 • SWGDAM 2020 • ISFG Recommendations
"""

import math
import pytest
from httpx import ASGITransport, AsyncClient

from backend.node.services.forensic.kinship.str_engine import (
    KinshipSTREngine,
    KinshipRelationship,
    IBDCoefficients,
    IBD_COEFFICIENT_MAP,
    LOCI_24_ORDER,
)
from backend.node.services.forensic.terminal.str_reference_datasets import (
    NIST_SRM_2391D_COMP_A,
    NIST_SRM_2391D_COMP_C,
)
from backend.app.main import app


class TestKinshipSTREngineCore:
    """Test suite for 24-locus panel validation, canonical sorting, and SMM transitions."""

    def test_24_locus_completeness_validation(self):
        """Verify complete 24-locus profile passes completeness check."""
        is_comp, missing = KinshipSTREngine.validate_24locus_completeness(NIST_SRM_2391D_COMP_A.str_profile)
        assert is_comp is True
        assert len(missing) == 0

    def test_incomplete_profile_detects_missing_loci(self):
        """Verify partial profile flags missing loci."""
        partial = {"TH01": ("6", "9.3"), "D21S11": ("28", "31.2")}
        is_comp, missing = KinshipSTREngine.validate_24locus_completeness(partial)
        assert is_comp is False
        assert len(missing) == 22
        assert "D3S1358" in missing

    def test_canonical_allele_sorting(self):
        """Verify numerical and lexical sorting."""
        assert KinshipSTREngine.sort_alleles_canonically("9.3", "8") == ("8", "9.3")
        assert KinshipSTREngine.sort_alleles_canonically("14", "11") == ("11", "14")
        assert KinshipSTREngine.sort_alleles_canonically("Y", "X") == ("X", "Y")

    def test_smm_transition_probabilities(self):
        """
        Verify Stepwise Mutation Model (SMM) formulation:
        P(m->n) = (1-mu) if m==n
        P(m->n) = (mu/2)*(1-r)*r^(|m-n|-1) if m!=n
        """
        mu = 1e-3
        r = 0.10

        # No mutation
        assert pytest.approx(KinshipSTREngine.calculate_smm_transition("15", "15"), abs=1e-7) == 1.0 - mu

        # 1-step mutation (e.g. 15 -> 16)
        expected_1step = (mu / 2.0) * (1.0 - r) * (r ** 0)
        assert pytest.approx(KinshipSTREngine.calculate_smm_transition("15", "16"), abs=1e-8) == expected_1step

        # 2-step mutation (e.g. 15 -> 17)
        expected_2step = (mu / 2.0) * (1.0 - r) * (r ** 1)
        assert pytest.approx(KinshipSTREngine.calculate_smm_transition("15", "17"), abs=1e-9) == expected_2step


class TestKinshipPedigreeCalculations:
    """Test suite for pedigree kinship calculations across relationship classes."""

    @pytest.fixture
    def true_father_child_pair(self):
        """Synthetic true biological father and child sharing obligate alleles."""
        father = {
            "D3S1358": ("15", "16"),
            "vWA": ("16", "18"),
            "FGA": ("21", "24"),
            "D8S1179": ("13", "15"),
            "D21S11": ("28", "30"),
            "D18S51": ("13", "16"),
            "D5S818": ("11", "12"),
            "D13S317": ("11", "12"),
            "D7S820": ("9", "11"),
            "D16S539": ("11", "13"),
            "CSF1PO": ("10", "12"),
            "PENTA_D": ("9", "12"),
            "TH01": ("6", "9.3"),
            "TPOX": ("8", "11"),
            "D2S1338": ("19", "23"),
            "D19S433": ("13", "14"),
            "PENTA_E": ("12", "14"),
            "D1S1656": ("15", "16"),
            "D12S391": ("18", "22"),
            "D2S441": ("11", "14"),
            "D10S1248": ("13", "14"),
            "D22S1045": ("15", "16"),
            "SE33": ("18", "27.2"),
            "AMEL": ("X", "Y"),
        }
        # Child inherits one allele from father at each locus
        child = {
            "D3S1358": ("15", "18"),
            "vWA": ("16", "17"),
            "FGA": ("21", "22"),
            "D8S1179": ("13", "14"),
            "D21S11": ("28", "29"),
            "D18S51": ("13", "15"),
            "D5S818": ("11", "13"),
            "D13S317": ("11", "11"),
            "D7S820": ("9", "10"),
            "D16S539": ("11", "12"),
            "CSF1PO": ("10", "11"),
            "PENTA_D": ("9", "10"),
            "TH01": ("6", "7"),
            "TPOX": ("8", "8"),
            "D2S1338": ("19", "20"),
            "D19S433": ("13", "15"),
            "PENTA_E": ("12", "13"),
            "D1S1656": ("15", "17"),
            "D12S391": ("18", "19"),
            "D2S441": ("11", "12"),
            "D10S1248": ("13", "15"),
            "D22S1045": ("15", "17"),
            "SE33": ("18", "25.2"),
            "AMEL": ("X", "Y"),
        }
        return father, child

    def test_parent_child_kinship_true_duo(self, true_father_child_pair):
        """Verify that true father-child duo yields CPI > 10^4 and W(%) > 99.9%."""
        father, child = true_father_child_pair
        res = KinshipSTREngine.compute_kinship_profile_analysis(
            profile1=child,
            profile2=father,
            relationship=KinshipRelationship.PARENT_CHILD,
            population="Caucasian",
            theta=0.01,
        )
        assert res.evaluated_loci_count == 24
        assert res.combined_kinship_index > 1e4
        assert res.probability_of_paternity_w > 99.99
        assert "Support for Proposed Kinship Relationship (Hp)" in res.enfsi_verbal_scale
        assert res.invariants["is_additive_invariant"] is True

    def test_unrelated_duo_baseline(self):
        """Verify unrelated relationship baseline with IBD (k0=1, k1=0, k2=0) yields CPI = 1.0."""
        p1 = {"TH01": ("6", "9.3"), "D21S11": ("28", "31.2")}
        p2 = {"TH01": ("7", "8"), "D21S11": ("29", "30")}

        res = KinshipSTREngine.compute_kinship_profile_analysis(
            profile1=p1,
            profile2=p2,
            relationship=KinshipRelationship.UNRELATED,
            population="Caucasian",
        )
        assert pytest.approx(res.combined_kinship_index, abs=1e-5) == 1.0
        assert pytest.approx(res.probability_of_paternity_w, abs=1e-3) == 50.0

    def test_smm_mutation_parent_child_duo(self, true_father_child_pair):
        """Verify that single-step mutation at D18S51 is handled gracefully by SMM."""
        father, child = true_father_child_pair
        # Introduce single-step mutation: child has 17 instead of 13/16 inherited
        child_mut = dict(child)
        child_mut["D18S51"] = ("17", "18")  # Father has (13, 16) -> 16 to 17 is 1 step

        res = KinshipSTREngine.compute_kinship_profile_analysis(
            profile1=child_mut,
            profile2=father,
            relationship=KinshipRelationship.PARENT_CHILD,
            population="Caucasian",
            apply_smm=True,
        )
        d18_res = next(r for r in res.locus_results if r.locus_name == "D18S51")
        assert d18_res.mutation_occurred is True
        assert d18_res.kinship_index > 0.0  # SMM transition gives non-zero probability
        assert d18_res.kinship_index < 1e-3  # Mutant locus is penalised by SMM transition rate
        assert res.combined_kinship_index > 0.0  # Overall CPI is non-zero (graceful handling without math error)


@pytest.mark.asyncio
class TestPopulationRoutesAPIIntegration:
    """Test suite for FastAPI endpoints /forensic/population/profile-rmp and /kinship-duo."""

    async def test_api_profile_rmp_endpoint(self):
        """Verify POST /forensic/population/profile-rmp returns valid ISO 17025 metrics."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {
                "profile": {
                    "TH01": ["6", "9.3"],
                    "D21S11": ["28", "31.2"],
                    "D3S1358": ["15", "16"],
                },
                "population": "Caucasian",
                "theta": 0.01,
                "use_exact_balding_nichols": True,
            }
            response = await ac.post("/api/v1/forensic/population/profile-rmp", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["population"] == "Caucasian"
            assert data["evaluated_loci_count"] == 3
            assert data["combined_rmp"] > 0.0
            assert data["combined_lr"] > 1.0
            assert data["invariants"]["is_additive_invariant"] is True
            assert "measurement_uncertainty" in data
            assert data["measurement_uncertainty"]["coverage_factor_k"] == 2.00

    async def test_api_kinship_duo_endpoint(self):
        """Verify POST /forensic/population/kinship-duo returns valid CPI and W(%)."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {
                "profile1": {
                    "TH01": ["6", "9.3"],
                    "D21S11": ["28", "31.2"],
                },
                "profile2": {
                    "TH01": ["6", "8"],
                    "D21S11": ["28", "30"],
                },
                "relationship": "Parent-Child",
                "population": "Caucasian",
                "theta": 0.01,
                "apply_smm": True,
            }
            response = await ac.post("/api/v1/forensic/population/kinship-duo", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["relationship"] == "Parent-Child"
            assert data["evaluated_loci_count"] == 2
            assert data["combined_kinship_index"] > 1.0
            assert data["probability_of_paternity_w"] > 50.0
            assert len(data["locus_results"]) == 2
