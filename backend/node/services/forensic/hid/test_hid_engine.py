"""
Unit & Integration Tests for FORENZA Ancient DNA & Degraded Forensic SNP / HID Engine — Module 10.

Tests verbatim from Pillar 2 Research §5:
  - §5.1 Post-Mortem Damage Kinetics (MapDamage / Briggs Model)
  - §5.1 Exponential Fragmentation Length Distribution & Amplicon Dropout Risk
  - §5.2 Low-Coverage Forensic SNP Genotype Likelihood (GL) with Deamination Compensation
  - §5.2 Multi-Locus Micro-Multiplex SNP Likelihood Ratio (LR_SNP)
  - §5.1 Skeletal Degradation Index (DI) & LCN Stochastic Threshold Audit
  - Multi-Modal Human Identification Remains Synthesis

Test Vectors:
  VECTOR_10_HID_A  — MapDamage deamination kinetics exactness, delta_1 = delta_0, asymptotic decay
  VECTOR_10_HID_B  — Exponential fragmentation length distribution, mean/median, CDF at 100 bp
  VECTOR_10_HID_C  — Low-coverage SNP Genotype Likelihood (GL) and damage compensation
  VECTOR_10_HID_D  — Terminal 5' deamination vs interior read base deamination contrast
  VECTOR_10_HID_E  — Multi-locus micro-multiplex SNP Likelihood Ratio product rule & log-space
  VECTOR_10_HID_F  — Skeletal degradation index (DI) audit & LCN stochastic thresholding
  VECTOR_10_HID_G  — Multi-modal remains candidate ranking synthesis
  VECTOR_10_HID_H  — API integration across all endpoints
"""

import math
from typing import Any, Dict, List, Optional
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.hid.adna_engine import AncientDNAEngine
from app.api.hid_routes import router as hid_router

_app = FastAPI()
_app.include_router(hid_router, prefix="/api/v1")
client = TestClient(_app)

engine = AncientDNAEngine()


# ── VECTOR_10_HID_A — MapDamage Deamination Kinetics ──────────────────────────

class TestVector10HIDA:
    """Verifies MapDamage / Briggs model deamination kinetics."""

    def test_terminal_position_one_equals_delta_0(self):
        delta_1 = engine.compute_mapdamage_deamination_rate(k=1, delta_0=0.25, decay_alpha=0.10)
        assert delta_1 == pytest.approx(0.25, rel=1e-6)

    def test_analytical_deamination_rate_at_position_ten(self):
        # delta_10 = 0.25 * exp(-0.10 * 9) = 0.25 * exp(-0.9)
        expected = 0.25 * math.exp(-0.90)  # ~0.10164
        computed = engine.compute_mapdamage_deamination_rate(k=10, delta_0=0.25, decay_alpha=0.10)
        assert computed == pytest.approx(expected, rel=1e-5)

    def test_asymptotic_decay_towards_zero(self):
        delta_50 = engine.compute_mapdamage_deamination_rate(k=50, delta_0=0.25, decay_alpha=0.10)
        assert delta_50 < 0.002
        delta_100 = engine.compute_mapdamage_deamination_rate(k=100, delta_0=0.25, decay_alpha=0.10)
        assert delta_100 < 1e-4

    def test_strictly_monotonic_decreasing(self):
        rates = [engine.compute_mapdamage_deamination_rate(k=k, delta_0=0.30) for k in range(1, 20)]
        for i in range(len(rates) - 1):
            assert rates[i] > rates[i + 1]


# ── VECTOR_10_HID_B — Exponential Fragmentation Length Distribution ───────────

class TestVector10HIDB:
    """Verifies exponential DNA fragment length distribution."""

    def test_fragmentation_mean_and_median(self):
        prof = engine.compute_fragmentation_distribution(lambda_param=0.025, l_min=30.0)
        # Mean = 1/0.025 + 30 = 40 + 30 = 70 bp
        assert prof.mean_length == pytest.approx(70.0, rel=1e-5)
        # Median = ln(2)/0.025 + 30 ~ 57.73 bp
        expected_median = (math.log(2.0) / 0.025) + 30.0
        assert prof.median_length == pytest.approx(expected_median, rel=1e-3)

    def test_cdf_at_100bp_str_dropout_threshold(self):
        prof = engine.compute_fragmentation_distribution(lambda_param=0.025, l_min=30.0)
        # CDF(100) = 1 - exp(-0.025 * 70) = 1 - exp(-1.75) ~ 0.8262
        expected_cdf = 1.0 - math.exp(-0.025 * 70.0)
        assert prof.cdf_at_100bp == pytest.approx(expected_cdf, rel=1e-3)
        assert prof.cdf_at_100bp > 0.80  # >80% fragments under 100 bp


# ── VECTOR_10_HID_C — Low-Coverage SNP Genotype Likelihood (GL) ───────────────

class TestVector10HIDC:
    """Verifies low-coverage SNP genotype likelihoods and damage compensation."""

    def test_deamination_c_to_t_read_damage_compensated(self):
        # 4 reads: 3 C reads and 1 T read at position k=2 (high deamination hazard)
        res = engine.compute_low_coverage_snp_likelihood(
            locus_id="rs12913832",
            read_bases=["C", "C", "T", "C"],
            read_positions=[1, 5, 2, 12],
            ref_allele="C",
            alt_allele="T",
            delta_0=0.25,
            sequencing_error_rate=0.01,
        )

        assert res.read_count == 4
        assert res.called_genotype == "AA"  # Homozygous Ref correctly called despite T read
        assert res.posterior_probabilities["AA"] > 0.70
        assert res.deamination_risk_flag is True
        assert res.is_damage_compensated is True


    def test_true_heterozygote_called_when_alt_reads_not_terminal(self):
        # Multiple Alt reads at deeper positions (k=15, 20) where deamination is minimal
        res = engine.compute_low_coverage_snp_likelihood(
            locus_id="rs1800407",
            read_bases=["C", "T", "T", "C"],
            read_positions=[15, 18, 20, 22],
            ref_allele="C",
            alt_allele="T",
            delta_0=0.25,
            sequencing_error_rate=0.01,
        )
        assert res.called_genotype == "AB"  # Heterozygous


# ── VECTOR_10_HID_D — Terminal 5' vs Interior Deamination Contrast ────────────

class TestVector10HIDD:
    """Contrasts terminal deamination vs interior read base behavior."""

    def test_terminal_reads_have_lower_alt_likelihood_penalty_under_ref(self):
        # T read at k=1 (terminal)
        res_k1 = engine.compute_low_coverage_snp_likelihood(
            locus_id="SNP-1",
            read_bases=["T"],
            read_positions=[1],
            ref_allele="C",
            alt_allele="T",
            delta_0=0.25,
        )
        # T read at k=25 (interior)
        res_k25 = engine.compute_low_coverage_snp_likelihood(
            locus_id="SNP-1",
            read_bases=["T"],
            read_positions=[25],
            ref_allele="C",
            alt_allele="T",
            delta_0=0.25,
        )

        # Under AA (Ref), terminal T read has higher likelihood (damage accounted for) than interior T read
        assert res_k1.raw_likelihoods["AA"] > res_k25.raw_likelihoods["AA"]


# ── VECTOR_10_HID_E — Multi-SNP Likelihood Ratio Product Rule ─────────────────

class TestVector10HIDE:
    """Verifies cumulative micro-multiplex SNP Likelihood Ratio product rule."""

    def test_multi_snp_product_rule_log_preservation(self):
        gl1 = engine.compute_low_coverage_snp_likelihood(
            locus_id="SNP-A",
            read_bases=["C", "C"],
            read_positions=[3, 8],
            ref_allele="C",
            alt_allele="T",
        )
        gl2 = engine.compute_low_coverage_snp_likelihood(
            locus_id="SNP-B",
            read_bases=["A", "G"],
            read_positions=[10, 14],
            ref_allele="A",
            alt_allele="G",
        )

        res = engine.compute_multi_snp_lr(
            snp_results=[gl1, gl2],
            suspect_genotypes={"SNP-A": "AA", "SNP-B": "AB"},
        )

        assert res.total_snps == 2
        assert res.cumulative_lr > 1.0
        sum_logs = math.log10(res.per_locus_lr["SNP-A"]) + math.log10(res.per_locus_lr["SNP-B"])
        assert abs(res.log10_cumulative_lr - sum_logs) < 1e-4
        assert len(res.prosecutors_fallacy_shield) > 50


# ── VECTOR_10_HID_F — Skeletal Degradation Index Audit ────────────────────────

class TestVector10HIDF:
    """Verifies skeletal degradation index and LCN classification."""

    def test_severe_degradation_detected(self):
        audit = engine.audit_skeletal_degradation(
            profile_id="BONE-FRAGMENT-01",
            small_loci_rfu=1200.0,
            large_loci_rfu=350.0,
            dna_input_pg=80.0,
        )
        assert audit.degradation_index == pytest.approx(1200.0 / 350.0, rel=1e-3)
        assert audit.long_amplicon_dropout_risk == "SEVERE"
        assert audit.is_lcn_sample is True
        assert audit.recommended_technology == "MICRO_SNP_PANEL_40_70BP"
        assert "Severe degradation" in audit.stochastic_warning

    def test_low_degradation_standard_str(self):
        audit = engine.audit_skeletal_degradation(
            profile_id="PRISTINE-BONE-02",
            small_loci_rfu=1000.0,
            large_loci_rfu=900.0,
            dna_input_pg=500.0,
        )
        assert audit.long_amplicon_dropout_risk == "LOW"
        assert audit.is_lcn_sample is False
        assert audit.recommended_technology == "STANDARD_STR"
        assert audit.stochastic_warning is None


# ── VECTOR_10_HID_G — Multi-Modal Remains Candidate Ranking ───────────────────

class TestVector10HIDG:
    """Verifies multi-modal human identification synthesis."""

    def test_multi_modal_synthesis_identification(self):
        # Verified through API or internal engine
        prof_json = {
            "profile_id": "CAND-01",
            "loci": {"TH01": {"locus_name": "TH01", "allele1": 6.0, "allele2": 9.3}},
            "population_group": "Caucasian",
        }
        payload = {
            "remains_id": "REMAINS-SITE-10",
            "sample_type": "SKELETAL_BONE",
            "str_profile": prof_json,
            "ystr_markers": {"DYS19": 14.0},
            "mtdna_variants": ["16189T", "263G"],
            "candidate_db": [prof_json],
        }
        resp = client.post("/api/v1/forensic/hid/evaluate-remains", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["evaluated_candidates_count"] == 1
        assert len(data["top_candidate_hits"]) == 1
        assert data["top_candidate_hits"][0]["joint_lr"] > 1.0


# ── VECTOR_10_HID_H — API Integration Tests ───────────────────────────────────

class TestVector10HIDH:
    """API integration tests across all Module 10 endpoints."""

    def test_api_damage_kinetics(self):
        resp = client.post("/api/v1/forensic/hid/damage-kinetics", json={"delta_0": 0.25, "decay_alpha": 0.10, "max_position": 10})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["damage_curve"]) == 10
        assert data["damage_curve"]["1"] == 0.25

    def test_api_fragmentation_distribution(self):
        resp = client.post("/api/v1/forensic/hid/fragmentation-distribution", json={"lambda_param": 0.025, "l_min": 30.0})
        assert resp.status_code == 200
        data = resp.json()
        assert data["mean_length"] == 70.0
        assert data["cdf_at_100bp"] > 0.80

    def test_api_snp_genotype_likelihood(self):
        payload = {
            "locus_id": "rs12913832",
            "read_bases": ["C", "C", "T", "C"],
            "read_positions": [1, 5, 2, 12],
            "ref_allele": "C",
            "alt_allele": "T",
            "delta_0": 0.25,
        }
        resp = client.post("/api/v1/forensic/hid/snp-genotype-likelihood", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["called_genotype"] == "AA"
        assert data["is_damage_compensated"] is True

    def test_api_multi_snp_lr(self):
        payload = {
            "snp_observations": [
                {"locus_id": "SNP-1", "read_bases": ["C", "C"], "read_positions": [2, 5], "ref_allele": "C", "alt_allele": "T"},
                {"locus_id": "SNP-2", "read_bases": ["A", "G"], "read_positions": [12, 15], "ref_allele": "A", "alt_allele": "G"},
            ],
            "suspect_genotypes": {"SNP-1": "AA", "SNP-2": "AB"},
            "delta_0": 0.25,
            "sequencing_error_rate": 0.01,
        }
        resp = client.post("/api/v1/forensic/hid/multi-snp-lr", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_snps"] == 2
        assert data["cumulative_lr"] > 1.0

    def test_api_skeletal_audit(self):
        payload = {
            "profile_id": "BONE-99",
            "small_loci_rfu": 1200.0,
            "large_loci_rfu": 350.0,
            "dna_input_pg": 75.0,
        }
        resp = client.post("/api/v1/forensic/hid/skeletal-audit", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["long_amplicon_dropout_risk"] == "SEVERE"
        assert data["is_lcn_sample"] is True
        assert data["recommended_technology"] == "MICRO_SNP_PANEL_40_70BP"
