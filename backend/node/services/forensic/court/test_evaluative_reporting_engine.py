"""
FORENZA Module 29 — Test Suite.

Golden Benchmark Test Vectors:
  VECTOR_P6_03     : LR = 3.5e7 → Verbal Tier 6 (Turkish phrase verified)
  VECTOR_29_ENFSI_A: Neutral / Inconclusive (LR = 1.0 → Tier 0)
  VECTOR_29_ENFSI_B: All boundary transitions Tiers 1–6
  VECTOR_29_ENFSI_C: Defense symmetric inversion (LR < 1.0 → H_d support)
  VECTOR_29_ENFSI_D: Bilingual concordance (EN & TR for same LR)
  VECTOR_29_ENFSI_E: Daubert FRE 702 4-pillar & Frye compliance audit
  VECTOR_29_ENFSI_F: Domain validation (LR ≤ 0 raises ValueError)
  VECTOR_29_ENFSI_G: FastAPI REST endpoint integration (/evaluative-report, /daubert-compliance)
"""

import math
import pytest
import httpx
from fastapi.testclient import TestClient

from backend.node.services.forensic.court.evaluative_reporting_engine import (
    DynamicEvaluativeReportingEngine,
)
from backend.app.main import app

engine = DynamicEvaluativeReportingEngine()
client = TestClient(app)

HP = "The DNA evidence originates from the named suspect."
HD = "The DNA evidence originates from an unknown unrelated person."


# ── VECTOR_P6_03 ─────────────────────────────────────────────────────────────

class TestVectorP603:
    """
    Ground-truth: LR = 3.5e7 → Tier 6, log10 ≈ 7.5441.
    Turkish: "Bulgular, iddia hipotezi (H_p) lehine aşırı güçlü destek sağlamaktadır."
    (Research §6 Artifact D)
    """

    def test_enfsi_tier_6_ground_truth(self):
        lr = 3.5e7
        res = engine.generate_evaluative_report(lr, HP, HD, language="tr")

        assert res["verbal_tier"] == 6
        assert abs(res["log10_likelihood_ratio"] - math.log10(lr)) < 1e-3
        assert res["supported_proposition"] == "H_p"
        assert res["is_prosecution_supported"] is True
        assert "aşırı güçlü destek" in res["evaluative_statement"]
        assert "iddia hipotezi (H_p)" in res["evaluative_statement"]
        assert res["reporting_standard"] == "ENFSI-2017-EVAL-V1"

    def test_vector_p6_03_log10_value(self):
        lr = 3.5e7
        res = engine.generate_evaluative_report(lr, HP, HD)
        # log10(3.5e7) = log10(3.5) + 7 ≈ 7.5441
        assert abs(res["log10_likelihood_ratio"] - 7.5441) < 1e-3


# ── VECTOR_29_ENFSI_A — Neutral Inconclusive (Tier 0) ────────────────────────

class TestVector29EnfsiA:
    """LR = 1.0 → Tier 0 (Neutral, no support for either proposition)."""

    def test_neutral_tier_zero(self):
        res = engine.generate_evaluative_report(1.0, HP, HD, language="tr")
        assert res["verbal_tier"] == 0
        assert res["log10_likelihood_ratio"] == 0.0
        assert "nötr" in res["evaluative_statement"].lower()

    def test_neutral_english(self):
        res = engine.generate_evaluative_report(1.0, HP, HD, language="en")
        assert res["verbal_tier"] == 0
        assert "neutral" in res["evaluative_statement"].lower()


# ── VECTOR_29_ENFSI_B — Step-Function Boundary Transitions (Tiers 1–6) ───────

class TestVector29EnfsiB:
    """Verifies each tier boundary exactly (Research §4.2 step-function thresholds)."""

    @pytest.mark.parametrize("lr, expected_tier", [
        (2.0, 1),          # Tier 1: 1 < LR ≤ 10
        (10.0, 1),         # Tier 1 upper boundary (inclusive)
        (10.01, 2),        # Tier 2 lower boundary
        (100.0, 2),        # Tier 2 upper boundary (inclusive)
        (100.01, 3),       # Tier 3 lower boundary
        (1000.0, 3),       # Tier 3 upper boundary (inclusive)
        (1000.01, 4),      # Tier 4 lower boundary
        (10000.0, 4),      # Tier 4 upper boundary (inclusive)
        (10000.01, 5),     # Tier 5 lower boundary
        (1_000_000.0, 5),  # Tier 5 upper boundary (inclusive)
        (1_000_001.0, 6),  # Tier 6 lower boundary
        (3.5e7, 6),        # VECTOR_P6_03 ground truth
    ])
    def test_tier_boundaries(self, lr, expected_tier):
        res = engine.generate_evaluative_report(lr, HP, HD)
        assert res["verbal_tier"] == expected_tier, (
            f"LR={lr}: expected Tier {expected_tier}, got Tier {res['verbal_tier']}"
        )


# ── VECTOR_29_ENFSI_C — Defense Symmetric Inversion (LR < 1.0 → H_d) ────────

class TestVector29EnfsiC:
    """Symmetric LR < 1.0 → effective_lr = 1/LR evaluated for H_d (Research §4.2)."""

    def test_defense_tier_4_lr_0001(self):
        # LR = 0.0001 → effective_lr = 10000 → Tier 4 for H_d
        res = engine.generate_evaluative_report(0.0001, HP, HD, language="tr")
        assert res["is_prosecution_supported"] is False
        assert res["supported_proposition"] == "H_d"
        assert res["verbal_tier"] == 4
        assert abs(res["effective_lr"] - 10000.0) < 1e-3
        assert "savunma hipotezi (H_d)" in res["evaluative_statement"]

    def test_defense_tier_1(self):
        # LR = 0.5 → effective_lr = 2.0 → Tier 1 for H_d
        res = engine.generate_evaluative_report(0.5, HP, HD, language="en")
        assert res["is_prosecution_supported"] is False
        assert res["verbal_tier"] == 1
        assert "H_d" in res["phrase_en"]

    def test_log10_negative_for_defense(self):
        # log10(0.0001) = -4.0
        res = engine.generate_evaluative_report(0.0001, HP, HD)
        assert abs(res["log10_likelihood_ratio"] - (-4.0)) < 1e-6


# ── VECTOR_29_ENFSI_D — Bilingual Concordance ────────────────────────────────

class TestVector29EnfsiD:
    """Ensures EN and TR statements are concordant for the same LR/tier (Research §4.2 table)."""

    @pytest.mark.parametrize("lr, tier, kw_en, kw_tr", [
        (5.0,     1, "weak",             "zayıf"),
        (50.0,    2, "moderate",         "orta düzeyde"),
        (500.0,   3, "moderately strong","orta-güçlü"),
        (5000.0,  4, "strong",           "güçlü"),
        (50000.0, 5, "very strong",      "çok güçlü"),
        (5e7,     6, "extremely strong", "aşırı güçlü"),
    ])
    def test_bilingual_concordance(self, lr, tier, kw_en, kw_tr):
        res_en = engine.generate_evaluative_report(lr, HP, HD, language="en")
        res_tr = engine.generate_evaluative_report(lr, HP, HD, language="tr")

        assert res_en["verbal_tier"] == tier
        assert res_tr["verbal_tier"] == tier
        assert kw_en.lower() in res_en["evaluative_statement"].lower()
        assert kw_tr.lower() in res_tr["evaluative_statement"].lower()

    def test_phrases_differ_by_language(self):
        res_en = engine.generate_evaluative_report(3.5e7, HP, HD, language="en")
        res_tr = engine.generate_evaluative_report(3.5e7, HP, HD, language="tr")
        assert res_en["evaluative_statement"] != res_tr["evaluative_statement"]
        assert res_en["phrase_en"] == res_en["evaluative_statement"]
        assert res_tr["phrase_tr"] == res_tr["evaluative_statement"]


# ── VECTOR_29_ENFSI_E — Daubert FRE 702 4-Pillar & Frye Audit ────────────────

class TestVector29EnfsiE:
    """Statutory legal admissibility engine audit (Research §4.3)."""

    def test_full_compliance_passes(self):
        result = engine.audit_daubert_frye_compliance(
            error_rate=1e-9,
            has_peer_reviewed_algorithms=True,
            swgdam_compliant=True,
            iso17025_compliant=True,
        )
        assert result.pillar_1_falsifiability is True
        assert result.pillar_2_error_rate is True    # 1e-9 ≤ 1e-6
        assert result.pillar_3_peer_review is True
        assert result.pillar_4_standards is True
        assert result.frye_general_acceptance is True
        assert result.overall_admissible is True
        assert result.error_rate_bound == 1e-6

    def test_excessive_error_rate_fails_pillar_2(self):
        result = engine.audit_daubert_frye_compliance(
            error_rate=5e-5,   # > 1e-6 → Pillar 2 fails
            has_peer_reviewed_algorithms=True,
            swgdam_compliant=True,
            iso17025_compliant=True,
        )
        assert result.pillar_2_error_rate is False
        assert result.overall_admissible is False

    def test_missing_standards_fails_pillar_4(self):
        result = engine.audit_daubert_frye_compliance(
            error_rate=1e-9,
            has_peer_reviewed_algorithms=True,
            swgdam_compliant=False,   # No SWGDAM → Pillar 4 fails
            iso17025_compliant=True,
        )
        assert result.pillar_4_standards is False
        assert result.overall_admissible is False

    def test_fallacy_shield_present(self):
        result = engine.audit_daubert_frye_compliance()
        assert "PROSECUTOR'S FALLACY SHIELD" in result.prosecutor_fallacy_shield
        assert "P(E|H_p)" in result.prosecutor_fallacy_shield


# ── VECTOR_29_ENFSI_F — Domain Validation ────────────────────────────────────

class TestVector29EnfsiF:
    """Non-positive LR raises ValueError (Research §6 Artifact C)."""

    @pytest.mark.parametrize("lr", [0.0, -1.0, -1e6])
    def test_non_positive_lr_raises(self, lr):
        with pytest.raises(ValueError, match="greater than 0"):
            engine.generate_evaluative_report(lr, HP, HD)


# ── VECTOR_29_ENFSI_G — FastAPI REST Integration ─────────────────────────────

class TestVector29EnfsiG:
    """End-to-end REST API verification for /evaluative-report and /daubert-compliance."""

    def test_api_evaluative_report_tier6(self):
        payload = {
            "likelihood_ratio": 3.5e7,
            "hp_proposition": HP,
            "hd_proposition": HD,
            "language": "tr",
        }
        resp = client.post("/api/v1/forensic/court/evaluative-report", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["verbal_tier"] == 6
        assert "aşırı güçlü" in data["evaluative_statement"]

    def test_api_evaluative_report_neutral(self):
        payload = {
            "likelihood_ratio": 1.0,
            "hp_proposition": HP,
            "hd_proposition": HD,
            "language": "en",
        }
        resp = client.post("/api/v1/forensic/court/evaluative-report", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["verbal_tier"] == 0

    def test_api_daubert_compliance_pass(self):
        payload = {
            "error_rate": 1e-9,
            "has_peer_reviewed_algorithms": True,
            "swgdam_compliant": True,
            "iso17025_compliant": True,
        }
        resp = client.post("/api/v1/forensic/court/daubert-compliance", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["overall_admissible"] is True

    def test_api_evaluative_invalid_lr_returns_400(self):
        payload = {
            "likelihood_ratio": -5.0,
            "hp_proposition": HP,
            "hd_proposition": HD,
        }
        resp = client.post("/api/v1/forensic/court/evaluative-report", json=payload)
        assert resp.status_code == 400
