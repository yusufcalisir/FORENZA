"""
Unit & Integration Tests for FORENZA Interpol DVI Mass Disaster Engine — Module 09.

Tests verbatim from Pillar 2 Research §4:
  - §4.1 Multi-Omic Joint Likelihood Ratio (LR_Joint) Formulation
  - §4.2 Interpol DVI Standing Committee 4-Tier Decision Boundaries
  - §4.1 N x M Ante-Mortem (AM) vs Post-Mortem (PM) Reconciliation Matrix & Missing Persons Ranking

Golden Benchmark Vectors:
  VECTOR_P2_03     — Severely Degraded PM Skeletal Sample:
                     Autosomal LR = 5.2e3, Y-STR p_upper = 0.0002 (LR_Y = 5000), mtDNA p_upper = 0.0001 (LR_mtDNA = 10000)
                     Combined DVI LR = 2.6e11, log10(LR) = 11.41497 -> DEFINITIVE IDENTIFICATION (LR >= 10^6)
  VECTOR_09_DVI_A  — Multi-omic product rule mathematical exactness & log-space preservation
  VECTOR_09_DVI_B  — Lineage data availability indicator flags (delta_y, delta_m, delta_s)
  VECTOR_09_DVI_C  — Interpol 4-tier threshold boundaries & exact classification
  VECTOR_09_DVI_D  — Judicial action criteria and secondary corroboration flags
  VECTOR_09_DVI_E  — N x M disaster cross-reconciliation matrix counts
  VECTOR_09_DVI_F  — Missing persons candidate ranking & posterior odds
  VECTOR_09_DVI_G  — Prosecutor's Fallacy Shield in DVI reporting
  VECTOR_09_DVI_H  — API integration across all endpoints
"""

import math
from typing import Any, Dict, List, Optional
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from node.services.forensic.dvi.dvi_engine import (
    DviEngine,
    InterpolDecisionTier,
    INTERPOL_TIER_RULES,
)
from app.api.dvi_routes import router as dvi_router

_app = FastAPI()
_app.include_router(dvi_router, prefix="/api/v1")
client = TestClient(_app)

engine = DviEngine()


# ── VECTOR_P2_03 — Golden Ground-Truth Benchmark ──────────────────────────────

class TestVectorP203:
    """
    VECTOR_P2_03 Golden Ground-Truth Benchmark (Research §6 Artifact D).
    Severely degraded PM skeletal sample.
    Autosomal LR = 5.2e3, Y-STR p_upper = 0.0002, mtDNA p_upper = 0.0001.
    Expected: Combined DVI LR = 2.6e11, log10(LR) = 11.41497, DEFINITIVE IDENTIFICATION.
    """

    def test_vector_p2_03_analytical_multiplication(self):
        lr_auto = 5200.0
        p_y = 0.0002
        p_m = 0.0001

        lr_y = 1.0 / p_y    # 5000.0
        lr_m = 1.0 / p_m    # 10000.0

        joint_lr = lr_auto * lr_y * lr_m  # 5200 * 5000 * 10000 = 2.6e11
        log10_joint = math.log10(joint_lr)

        assert lr_y == 5000.0
        assert lr_m == 10000.0
        assert joint_lr == pytest.approx(2.6e11, rel=1e-6)
        assert log10_joint == pytest.approx(11.4149733, abs=1e-4)

    def test_vector_p2_03_engine_evaluation(self):
        joint_lr, log10_joint, comp = engine.compute_multi_omic_joint_lr(
            autosomal_lr=5200.0,
            ystr_p_upper=0.0002,
            mtdna_p_upper=0.0001,
            has_ystr=True,
            has_mtdna=True,
        )

        tier, action = engine.classify_interpol_decision_tier(joint_lr)

        assert joint_lr == pytest.approx(2.6e11, rel=1e-5)
        assert log10_joint == pytest.approx(11.41497, abs=1e-4)
        assert tier == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION
        assert comp.ystr_lr == 5000.0
        assert comp.mtdna_lr == 10000.0
        assert comp.has_ystr is True
        assert comp.has_mtdna is True
        assert "standalone legal identification" in action


# ── VECTOR_09_DVI_A — Multi-Omic Product Rule & Log-Space Exactness ───────────

class TestVector09DVIA:
    """Verifies product rule and log-space addition."""

    def test_product_rule_log_space_invariant(self):
        lr_auto = 12500.0
        p_y = 0.001
        p_m = 0.0005
        snp_lr = 45.0

        joint_lr, log10_joint, comp = engine.compute_multi_omic_joint_lr(
            autosomal_lr=lr_auto,
            ystr_p_upper=p_y,
            mtdna_p_upper=p_m,
            snp_lr=snp_lr,
            has_ystr=True,
            has_mtdna=True,
            has_snp=True,
        )

        sum_logs = (
            math.log10(lr_auto)
            + math.log10(1.0 / p_y)
            + math.log10(1.0 / p_m)
            + math.log10(snp_lr)
        )

        assert abs(log10_joint - sum_logs) < 1e-6
        assert joint_lr == pytest.approx(lr_auto * (1.0 / p_y) * (1.0 / p_m) * snp_lr, rel=1e-6)


# ── VECTOR_09_DVI_B — Data Availability Indicator Flags (delta_y, delta_m) ───

class TestVector09DVIB:
    """Verifies that missing data flags correctly set multipliers to 1.0."""

    def test_missing_ystr_flag_sets_multiplier_one(self):
        joint_lr, _, comp = engine.compute_multi_omic_joint_lr(
            autosomal_lr=1000.0,
            ystr_p_upper=0.0002,
            has_ystr=False,    # Female victim or no male reference
        )
        assert joint_lr == 1000.0
        assert comp.has_ystr is False
        assert comp.ystr_lr == 1.0

    def test_missing_mtdna_flag_sets_multiplier_one(self):
        joint_lr, _, comp = engine.compute_multi_omic_joint_lr(
            autosomal_lr=1000.0,
            mtdna_p_upper=0.0001,
            has_mtdna=False,
        )
        assert joint_lr == 1000.0
        assert comp.has_mtdna is False
        assert comp.mtdna_lr == 1.0


# ── VECTOR_09_DVI_C — Interpol 4-Tier Decision Boundaries ─────────────────────

class TestVector09DVIC:
    """Verifies statutory Interpol decision tier boundaries."""

    def test_definitive_identification_boundary(self):
        # LR = 10^6 exactly
        tier, _ = engine.classify_interpol_decision_tier(1.0e6)
        assert tier == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION

        # LR = 10^7
        tier_high, _ = engine.classify_interpol_decision_tier(1.0e7)
        assert tier_high == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION

    def test_probable_match_boundary(self):
        # LR = 10^4
        tier, _ = engine.classify_interpol_decision_tier(1.0e4)
        assert tier == InterpolDecisionTier.PROBABLE_MATCH

        # LR = 9.99e5
        tier_sub, _ = engine.classify_interpol_decision_tier(9.99e5)
        assert tier_sub == InterpolDecisionTier.PROBABLE_MATCH

    def test_inconclusive_boundary(self):
        # LR = 100
        tier, _ = engine.classify_interpol_decision_tier(100.0)
        assert tier == InterpolDecisionTier.INCONCLUSIVE

        # LR = 0.50
        tier_low, _ = engine.classify_interpol_decision_tier(0.50)
        assert tier_low == InterpolDecisionTier.INCONCLUSIVE

    def test_exclusion_boundary(self):
        # LR = 0.01 (10^-2)
        tier, _ = engine.classify_interpol_decision_tier(0.01)
        assert tier == InterpolDecisionTier.EXCLUSION

        # LR = 0.0001
        tier_excl, _ = engine.classify_interpol_decision_tier(0.0001)
        assert tier_excl == InterpolDecisionTier.EXCLUSION


# ── VECTOR_09_DVI_D — Judicial Action Criteria Mappings ───────────────────────

class TestVector09DVID:
    """Verifies action criteria and corroboration requirements."""

    def test_tier_metadata_rules(self):
        def_meta = INTERPOL_TIER_RULES[InterpolDecisionTier.DEFINITIVE_IDENTIFICATION]
        assert def_meta.is_court_admissible_standalone is True
        assert def_meta.requires_secondary_corroboration is False

        prob_meta = INTERPOL_TIER_RULES[InterpolDecisionTier.PROBABLE_MATCH]
        assert prob_meta.is_court_admissible_standalone is False
        assert prob_meta.requires_secondary_corroboration is True

        incon_meta = INTERPOL_TIER_RULES[InterpolDecisionTier.INCONCLUSIVE]
        assert incon_meta.requires_secondary_corroboration is True

        excl_meta = INTERPOL_TIER_RULES[InterpolDecisionTier.EXCLUSION]
        assert excl_meta.is_court_admissible_standalone is True


# ── VECTOR_09_DVI_E — N x M Disaster Cross-Reconciliation Matrix ──────────────

class TestVector09DVIE:
    """Verifies matrix dimensions and count calculations."""

    def test_reconciliation_matrix_counts(self):
        pm_remains = [
            {
                "pm_id": "PM-001",
                "autosomal_lr_map": {"AM-FAM-1": 5200.0, "AM-FAM-2": 0.001},
                "ystr_p_upper": 0.0002,
                "mtdna_p_upper": 0.0001,
            },
            {
                "pm_id": "PM-002",
                "autosomal_lr_map": {"AM-FAM-1": 0.005, "AM-FAM-2": 25000.0},
                "ystr_p_upper": 0.0005,
                "mtdna_p_upper": 0.0002,
            },
        ]

        am_families = [
            {"am_id": "AM-FAM-1", "has_male_reference": True, "has_maternal_reference": True},
            {"am_id": "AM-FAM-2", "has_male_reference": True, "has_maternal_reference": False},
        ]

        report = engine.reconcile_dvi_matrix(
            disaster_event_id="CRASH-101",
            pm_remains=pm_remains,
            am_families=am_families,
        )

        assert report.total_pm_remains == 2
        assert report.total_am_families == 2
        assert len(report.reconciliation_matrix) == 4  # 2 x 2
        assert report.definitive_identifications_count >= 1
        assert "CRASH-101" in report.interpol_summary
        assert len(report.prosecutors_fallacy_shield) > 50


# ── VECTOR_09_DVI_F — Missing Persons Candidate Ranking ───────────────────────

class TestVector09DVIF:
    """Verifies candidate prioritization and posterior odds ranking."""

    def test_missing_person_ranking_order(self):
        candidates = [
            {"am_family_id": "AM-A", "autosomal_lr": 10.0, "has_ystr": False, "has_mtdna": False},
            {"am_family_id": "AM-B", "autosomal_lr": 1.0e7, "has_ystr": False, "has_mtdna": False},
            {"am_family_id": "AM-C", "autosomal_lr": 5000.0, "ystr_p_upper": 0.001, "has_ystr": True},
        ]

        ranked = engine.rank_missing_person_candidates(
            pm_profile_id="PM-01",
            candidate_evaluations=candidates,
        )

        assert len(ranked) == 3
        # Top rank should be AM-B (1.0e7)
        assert ranked[0].am_family_id == "AM-B"
        assert ranked[0].decision_tier == InterpolDecisionTier.DEFINITIVE_IDENTIFICATION
        # Second rank should be AM-C (5000 * 1000 = 5.0e6)
        assert ranked[1].am_family_id == "AM-C"
        assert ranked[1].joint_lr == 5.0e6
        # Third rank should be AM-A (10.0)
        assert ranked[2].am_family_id == "AM-A"
        assert ranked[2].decision_tier == InterpolDecisionTier.INCONCLUSIVE


# ── VECTOR_09_DVI_G — Prosecutor's Fallacy Shield in DVI Reporting ────────────

class TestVector09DVIG:
    """Verifies that prosecutor's fallacy shield is included in DVI outputs."""

    def test_shield_content(self):
        report = engine.reconcile_dvi_matrix(
            disaster_event_id="TEST-EVENT",
            pm_remains=[{"pm_id": "PM-1"}],
            am_families=[{"am_id": "AM-1"}],
        )
        assert "Interpol DVI" in report.prosecutors_fallacy_shield
        assert "product rule" in report.prosecutors_fallacy_shield


# ── VECTOR_09_DVI_H — API Integration Tests ───────────────────────────────────

class TestVector09DVIH:
    """API integration tests across all Module 09 endpoints."""

    def test_api_decision_tiers(self):
        resp = client.get("/api/v1/forensic/dvi/decision-tiers")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["tiers"]) == 4
        tier_names = {t["tier_name"] for t in data["tiers"]}
        assert "DEFINITIVE_IDENTIFICATION" in tier_names
        assert "PROBABLE_MATCH" in tier_names
        assert "INCONCLUSIVE" in tier_names
        assert "EXCLUSION" in tier_names

    def test_api_joint_lr_vector_p2_03(self):
        payload = {
            "autosomal_lr": 5200.0,
            "ystr_p_upper": 0.0002,
            "mtdna_p_upper": 0.0001,
            "has_ystr": True,
            "has_mtdna": True,
        }
        resp = client.post("/api/v1/forensic/dvi/joint-lr", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["joint_lr"] == pytest.approx(2.6e11, rel=1e-4)
        assert data["log10_joint_lr"] == pytest.approx(11.41497, abs=1e-4)
        assert data["decision_tier"] == "DEFINITIVE_IDENTIFICATION"
        assert data["is_definitive_identification"] is True

    def test_api_reconcile_matrix(self):
        payload = {
            "disaster_event_id": "DVI-EVENT-99",
            "pm_remains": [
                {
                    "pm_id": "PM-A",
                    "autosomal_lr_map": {"AM-1": 5200.0},
                    "ystr_p_upper": 0.0002,
                    "mtdna_p_upper": 0.0001,
                }
            ],
            "am_families": [
                {"am_id": "AM-1", "has_male_reference": True, "has_maternal_reference": True}
            ],
            "threshold_lr": 1000000.0,
        }
        resp = client.post("/api/v1/forensic/dvi/reconcile-matrix", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["definitive_identifications_count"] == 1
        assert len(data["reconciliation_matrix"]) == 1
        assert data["reconciliation_matrix"][0]["is_positive_identification"] is True
