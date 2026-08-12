import pytest
from backend.node.services.forensic.court.expert_witness_engine import ExpertWitnessEngine


def test_expert_witness_testimony_generation():
    engine = ExpertWitnessEngine()
    res = engine.generate_testimony_brief(
        case_id="CASE-2026-COURT-01",
        sample_id="SAMPLE-DNA-101",
        log10_lr=26.0,
        enfsi_verbal_predicate="EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION"
    )

    assert res["operating_mode"] == "COURT_EXPERT_WITNESS_MODE"
    assert len(res["testimony_pillars"]) == 7
    assert res["prosecutors_fallacy_shield"] == "PROTECTED_TRANSPOSED_CONDITIONAL_SHIELD"
    assert res["testimony_hmac_hash"] is not None


def test_testimony_pillar_6_contains_fallacy_warning():
    engine = ExpertWitnessEngine()
    res = engine.generate_testimony_brief()
    pillar_6 = res["testimony_pillars"][5]
    assert "P(E|Hp)" in pillar_6["summary"]
    assert "Prosecutor's Fallacy" in pillar_6["details"]
    assert pillar_6["fallacy_protection_active"] is True


def test_testimony_pillar_5_contains_log10_lr():
    engine = ExpertWitnessEngine()
    res = engine.generate_testimony_brief(log10_lr=18.5)
    pillar_5 = res["testimony_pillars"][4]
    assert "10^18.5" in pillar_5["details"]


def test_all_7_pillars_have_title_summary_details():
    engine = ExpertWitnessEngine()
    res = engine.generate_testimony_brief()
    for pillar in res["testimony_pillars"]:
        assert "title" in pillar
        assert "summary" in pillar
        assert "details" in pillar


def test_court_admissibility_certified_flag():
    engine = ExpertWitnessEngine()
    res = engine.generate_testimony_brief()
    assert res["court_admissible"] is True


def test_hmac_testimony_hash_integrity():
    engine = ExpertWitnessEngine()
    res1 = engine.generate_testimony_brief(case_id="CASE-A")
    res2 = engine.generate_testimony_brief(case_id="CASE-B")
    assert res1["testimony_hmac_hash"] != res2["testimony_hmac_hash"]
