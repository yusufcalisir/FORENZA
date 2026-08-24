"""
FORENZA API Security & Resource Protection Test Suite (Dimension 9).

Validates:
- Broken Function Level Authorization (BFLA / RBAC)
- Broken Object Level Authorization (BOLA / IDOR) Case Ownership
- Pagination Clamping & Deep Offset Rejection
- Query Tree Complexity & Deep Nesting Limits
- Request Body Size Bounds (1MB JSON / 10MB Forensic Upload)
- Per-User Heavy Compute Resource Quota Tracking (Anti-Noisy Neighbor)
"""

import pytest

from app.security.api_security_engine import APISecurityEngine, UserRole


class TestAPISecurityEngine:
    def test_bfla_role_based_permissions(self):
        """Rol bazlı fonksiyon yetkilendirmesi (BFLA) doğrulanmalı."""
        engine = APISecurityEngine()

        # Analyst can execute mixture but not export audit
        assert engine.check_permission(UserRole.FORENSIC_ANALYST, "mixture:execute") is True
        assert engine.check_permission(UserRole.FORENSIC_ANALYST, "audit:export") is False

        # Lab Director can export audit and sign evidence
        assert engine.check_permission(UserRole.LAB_DIRECTOR, "audit:export") is True
        assert engine.check_permission(UserRole.LAB_DIRECTOR, "evidence:sign") is True

        # Juror viewer has read-only visualizer access
        assert engine.check_permission(UserRole.JUROR_VIEWER, "evidence:read_visualizer") is True
        assert engine.check_permission(UserRole.JUROR_VIEWER, "evidence:write") is False

        # System Admin has universal wildcard
        assert engine.check_permission(UserRole.SYSTEM_ADMIN, "any:custom:scope") is True

    def test_bola_idor_object_ownership_enforcement(self):
        """Nesne seviyesi yetkilendirme (BOLA/IDOR) vaka sahipliğini denetlemeli."""
        engine = APISecurityEngine()
        case_id = "CASE-2026-DNA-088"
        owner_id = "usr_analyst_alice"
        attacker_id = "usr_analyst_bob"

        engine.register_case_ownership(case_id, owner_id)

        # Owner has access
        ok_owner, _ = engine.check_object_access(owner_id, UserRole.FORENSIC_ANALYST, case_id)
        assert ok_owner is True

        # Unrelated analyst is blocked
        ok_attacker, err = engine.check_object_access(attacker_id, UserRole.FORENSIC_ANALYST, case_id)
        assert ok_attacker is False
        assert "Access denied" in err

        # Admin has override access
        ok_admin, _ = engine.check_object_access("usr_admin", UserRole.SYSTEM_ADMIN, case_id)
        assert ok_admin is True

    def test_pagination_bounds_and_clamping(self):
        """Sayfalama sınırları aşırı büyük limitleri (max 100) kırpmalı ve derin ofsetleri reddetmeli."""
        engine = APISecurityEngine()

        # Excessive limit clamped to 100
        ok, limit, offset, _ = engine.validate_pagination(limit=5000, offset=0)
        assert ok is True
        assert limit == 100

        # Excessive offset (>10,000) rejected
        ok_deep, _, _, err_deep = engine.validate_pagination(limit=50, offset=25000)
        assert ok_deep is False
        assert "exceeds maximum" in err_deep

        # Negative offset rejected
        ok_neg, _, _, _ = engine.validate_pagination(limit=10, offset=-5)
        assert ok_neg is False

    def test_query_complexity_nesting_limits(self):
        """Aşırı derin sorgu ağaçları (Depth > 4) reddedilmeli."""
        engine = APISecurityEngine()

        # Safe query (Depth 2)
        safe_query = {"filter": {"locus": "TH01", "allele": "9.3"}}
        assert engine.validate_query_complexity(safe_query)[0] is True

        # Deeply nested malicious query (Depth 6)
        deep_query = {"a": {"b": {"c": {"d": {"e": {"f": "exploit"}}}}}}
        ok, err = engine.validate_query_complexity(deep_query)
        assert ok is False
        assert "depth exceeds" in err

    def test_request_body_size_limits(self):
        """JSON gövdesi için 1MB, adli yükleme için 10MB sınırı uygulanmalı."""
        engine = APISecurityEngine()

        # 500 KB JSON -> Allowed
        assert engine.validate_request_size(500_000, is_upload=False)[0] is True

        # 2 MB JSON -> Rejected (exceeds 1MB)
        ok_json, err_json = engine.validate_request_size(2_000_000, is_upload=False)
        assert ok_json is False
        assert "exceeds maximum limit" in err_json

        # 5 MB Forensic file upload -> Allowed (under 10MB)
        assert engine.validate_request_size(5_000_000, is_upload=True)[0] is True

        # 15 MB Forensic file upload -> Rejected (exceeds 10MB)
        assert engine.validate_request_size(15_000_000, is_upload=True)[0] is False

    def test_per_user_compute_seconds_quota(self):
        """Kullanıcı başına saatlik ağır hesaplama süresi kotası izlenmeli ve aşımda engellenmeli."""
        engine = APISecurityEngine()
        user_id = "usr_heavy_researcher"

        # Acquire 100 seconds -> passes
        ok1, _ = engine.acquire_compute_quota(user_id, estimated_seconds=100.0)
        assert ok1 is True

        # Acquire 150 seconds -> passes (total 250s <= 300s)
        ok2, _ = engine.acquire_compute_quota(user_id, estimated_seconds=150.0)
        assert ok2 is True

        # Acquire 100 more seconds -> exceeds 300s limit -> blocked
        ok3, err3 = engine.acquire_compute_quota(user_id, estimated_seconds=100.0)
        assert ok3 is False
        assert "quota exceeded" in err3.lower()
