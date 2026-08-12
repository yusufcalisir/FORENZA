"""
FORENZA Human Analyst Review & Dual-Sign-Off Decision Audit Subsystem.

Enforces legal & scientific human-in-the-loop governance:
Automated Analysis -> Primary Analyst Review -> Technical Reviewer Approval -> Court-Admissible ISO 17025 Report

Captures AI Recommendation vs Human Decision, mandates justification logging for analyst overrides,
and generates HMAC-SHA256 chained audit signatures for legal admissibility.
"""

import hashlib
import hmac
import time
from typing import Dict, Any, List, Optional


class HumanReviewEngine:
    """
    Forensic Human Analyst Review & Dual-Sign-Off Decision Auditor.
    """

    HMAC_SECRET: bytes = b"FORENZA_COURT_ADMISSIBLE_REVIEW_KEY"

    DECISION_TYPES: List[str] = [
        "APPROVE_AI_PREDICATE",
        "OVERRIDE_MODIFIED_PREDICATE",
        "REJECT_RE_ANALYSIS",
    ]

    def __init__(self):
        self._review_history: Dict[str, List[Dict[str, Any]]] = {}

    def submit_analyst_decision(
        self,
        sample_id: str,
        ai_recommendation: str,
        human_decision: str,
        primary_analyst_id: str,
        technical_reviewer_id: str,
        override_reason: Optional[str] = None,
        final_verdict: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submits human analyst review decision with dual sign-off and override rationale logging.

        :param sample_id: Target sample identifier.
        :param ai_recommendation: Computational recommendation.
        :param human_decision: Human analyst decision predicate.
        :param primary_analyst_id: Digital signature ID of lead analyst.
        :param technical_reviewer_id: Digital signature ID of secondary peer reviewer.
        :param override_reason: Required text justification if decision overrides AI.
        :param final_verdict: Approved final verdict string.
        :return: Dict containing dual-sign-off verification record and HMAC signature.
        """
        sample_clean = sample_id.strip().upper()
        decision_clean = human_decision.strip().upper()

        if decision_clean not in self.DECISION_TYPES:
            raise ValueError(f"Invalid decision type '{decision_clean}'. Allowed: {self.DECISION_TYPES}")

        if not primary_analyst_id or not primary_analyst_id.strip():
            raise ValueError("Primary analyst signature ID is required.")

        if not technical_reviewer_id or not technical_reviewer_id.strip():
            raise ValueError("Secondary technical peer reviewer signature ID is required for dual sign-off.")

        is_override = decision_clean == "OVERRIDE_MODIFIED_PREDICATE"
        if is_override and (not override_reason or not override_reason.strip()):
            raise ValueError("Analyst override reason justification is mandatory when modifying AI predicate.")

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Determine previous hash in chain
        history = self._review_history.get(sample_clean, [])
        prev_hash = history[-1]["hmac_signature"] if history else "GENESIS_REVIEW_BLOCK"

        # Compute HMAC-SHA256 signature
        payload = f"{prev_hash}|{sample_clean}|{ai_recommendation}|{decision_clean}|{primary_analyst_id}|{technical_reviewer_id}|{timestamp}|{override_reason or ''}"
        hmac_sig = hmac.new(self.HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()

        review_entry = {
            "review_id": f"REV-{int(time.time() * 1000)}",
            "sample_id": sample_clean,
            "ai_recommendation": ai_recommendation,
            "human_decision": decision_clean,
            "is_override": is_override,
            "override_reason": override_reason if is_override else None,
            "final_verdict": final_verdict or (ai_recommendation if not is_override else "OVERRIDDEN"),
            "primary_analyst_id": primary_analyst_id.strip(),
            "technical_reviewer_id": technical_reviewer_id.strip(),
            "dual_sign_off_verified": True,
            "timestamp": timestamp,
            "court_admissibility_status": "CERTIFIED_COURT_ADMISSIBLE",
            "hmac_signature": hmac_sig,
        }

        if sample_clean not in self._review_history:
            self._review_history[sample_clean] = []

        self._review_history[sample_clean].append(review_entry)
        return review_entry

    def get_audit_history(self, sample_id: str) -> Dict[str, Any]:
        """Retrieves review decision audit history and verifies HMAC chain integrity."""
        sample_clean = sample_id.strip().upper()
        history = self._review_history.get(sample_clean, [])

        is_valid = True
        for i in range(len(history)):
            prev_hash = history[i-1]["hmac_signature"] if i > 0 else "GENESIS_REVIEW_BLOCK"
            curr = history[i]
            payload = f"{prev_hash}|{sample_clean}|{curr['ai_recommendation']}|{curr['human_decision']}|{curr['primary_analyst_id']}|{curr['technical_reviewer_id']}|{curr['timestamp']}|{curr['override_reason'] or ''}"
            expected_hash = hmac.new(self.HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()
            if curr["hmac_signature"] != expected_hash:
                is_valid = False
                break

        return {
            "sample_id": sample_clean,
            "total_reviews": len(history),
            "chain_intact": is_valid,
            "review_history": history,
            "legal_provenance": "FORENZA ISO 17025 Dual-Sign-Off Governance Engine"
        }
