import pytest
from backend.node.services.forensic.review.human_review_engine import HumanReviewEngine


def test_approve_ai_predicate_success():
    engine = HumanReviewEngine()
    res = engine.submit_analyst_decision(
        sample_id="SAMPLE-101",
        ai_recommendation="INCLUSION (LR = 10^26)",
        human_decision="APPROVE_AI_PREDICATE",
        primary_analyst_id="ANALYST-01",
        technical_reviewer_id="PEER-REVIEWER-02"
    )
    assert res["dual_sign_off_verified"] is True
    assert res["court_admissibility_status"] == "CERTIFIED_COURT_ADMISSIBLE"
    assert res["is_override"] is False
    assert res["hmac_signature"] is not None


def test_override_ai_predicate_requires_reason():
    engine = HumanReviewEngine()
    with pytest.raises(ValueError, match="override reason justification is mandatory"):
        engine.submit_analyst_decision(
            sample_id="SAMPLE-102",
            ai_recommendation="INCLUSION (LR = 10^26)",
            human_decision="OVERRIDE_MODIFIED_PREDICATE",
            primary_analyst_id="ANALYST-01",
            technical_reviewer_id="PEER-02",
            override_reason=""
        )


def test_override_ai_predicate_with_reason_success():
    engine = HumanReviewEngine()
    res = engine.submit_analyst_decision(
        sample_id="SAMPLE-103",
        ai_recommendation="INCLUSION (LR = 10^26)",
        human_decision="OVERRIDE_MODIFIED_PREDICATE",
        primary_analyst_id="ANALYST-01",
        technical_reviewer_id="PEER-02",
        override_reason="Allele dropout at locus D18S51 due to tri-allelic primer binding mutation",
        final_verdict="INCONCLUSIVE"
    )
    assert res["is_override"] is True
    assert res["final_verdict"] == "INCONCLUSIVE"


def test_missing_technical_reviewer_raises_error():
    engine = HumanReviewEngine()
    with pytest.raises(ValueError, match="Secondary technical peer reviewer signature ID is required"):
        engine.submit_analyst_decision(
            sample_id="SAMPLE-104",
            ai_recommendation="QC_PASSED",
            human_decision="APPROVE_AI_PREDICATE",
            primary_analyst_id="ANALYST-01",
            technical_reviewer_id=""
        )


def test_audit_history_retrieval_and_hmac_verification():
    engine = HumanReviewEngine()
    engine.submit_analyst_decision(
        sample_id="SAMPLE-105",
        ai_recommendation="INCLUSION",
        human_decision="APPROVE_AI_PREDICATE",
        primary_analyst_id="ANALYST-01",
        technical_reviewer_id="PEER-02"
    )
    audit = engine.get_audit_history("SAMPLE-105")
    assert audit["total_reviews"] == 1
    assert audit["chain_intact"] is True


def test_audit_history_tampering_detected():
    engine = HumanReviewEngine()
    engine.submit_analyst_decision(
        sample_id="SAMPLE-TAMPER",
        ai_recommendation="INCLUSION",
        human_decision="APPROVE_AI_PREDICATE",
        primary_analyst_id="ANALYST-01",
        technical_reviewer_id="PEER-02"
    )
    # Tamper with record
    engine._review_history["SAMPLE-TAMPER"][0]["ai_recommendation"] = "TAMPERED"

    audit = engine.get_audit_history("SAMPLE-TAMPER")
    assert audit["chain_intact"] is False
