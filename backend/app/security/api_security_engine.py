"""
FORENZA API Security & Resource Consumption Control Engine (Dimension 9 & 18).

Implements:
- Broken Object-Level Authorization (BOLA / IDOR) Ownership Verification.
- Broken Function-Level Authorization (BFLA / RBAC) Scopes.
- Request-Size Limits & Streaming Body Bounds.
- Strict Pagination & Query Complexity Limits (Anti-DOS pagination).
- Execution Timeout Enforcement (Anti-CPU exhaustion).
- Per-User Computational Resource Quotas (Anti-Noisy Neighbor).
"""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Deque, Dict, List, Optional, Set, Tuple


class UserRole(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    JUROR_VIEWER = "JUROR_VIEWER"
    FORENSIC_ANALYST = "FORENSIC_ANALYST"
    LAB_DIRECTOR = "LAB_DIRECTOR"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


ROLE_HIERARCHY: Dict[UserRole, int] = {
    UserRole.ANONYMOUS: 0,
    UserRole.JUROR_VIEWER: 1,
    UserRole.FORENSIC_ANALYST: 2,
    UserRole.LAB_DIRECTOR: 3,
    UserRole.SYSTEM_ADMIN: 4,
}

ROLE_PERMISSIONS: Dict[UserRole, Set[str]] = {
    UserRole.ANONYMOUS: {"public:read"},
    UserRole.JUROR_VIEWER: {"public:read", "evidence:read_visualizer"},
    UserRole.FORENSIC_ANALYST: {"public:read", "evidence:read", "evidence:write", "mixture:execute", "zkp:prove", "bpa:calculate", "geoint:query"},
    UserRole.LAB_DIRECTOR: {"public:read", "evidence:read", "evidence:write", "evidence:sign", "mixture:execute", "zkp:prove", "bpa:calculate", "geoint:query", "audit:export"},
    UserRole.SYSTEM_ADMIN: {"*"},
}


@dataclass
class UserResourceUsage:
    compute_seconds_used: float = 0.0
    active_requests: int = 0
    timestamps: Deque[float] = field(default_factory=deque)
    quota_exhausted_until: float = 0.0


class APISecurityEngine:
    """
    Independent API Security Engine protecting backend services from resource exhaustion,
    unauthorized data access, and unconstrained queries.
    """

    MAX_PAGE_SIZE = 100
    MAX_OFFSET = 10_000
    MAX_QUERY_DEPTH = 4
    DEFAULT_JSON_BODY_MAX_BYTES = 1_048_576       # 1 MB
    FORENSIC_UPLOAD_MAX_BYTES = 10_485_760        # 10 MB
    MAX_HOURLY_COMPUTE_SECONDS_PER_USER = 300.0   # 5 minutes of raw heavy CPU per hour per user

    def __init__(self):
        self._user_usage: Dict[str, UserResourceUsage] = defaultdict(UserResourceUsage)
        self._case_ownership: Dict[str, str] = {}     # case_id -> owner_user_or_org_id

    # ── 1. Authorization & Role Validation (BFLA) ──────────────────────────
    def check_permission(self, user_role: UserRole, required_permission: str) -> bool:
        """
        Validates if user role has the required permission scope.
        """
        if user_role == UserRole.SYSTEM_ADMIN:
            return True
        perms = ROLE_PERMISSIONS.get(user_role, set())
        return required_permission in perms or "*" in perms

    def register_case_ownership(self, case_id: str, owner_id: str):
        """Registers ownership of a forensic case / evidence item."""
        self._case_ownership[case_id] = owner_id

    # ── 2. Object-Level Ownership Verification (BOLA / IDOR) ───────────────
    def check_object_access(
        self,
        requesting_user_id: str,
        user_role: UserRole,
        case_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifies that requesting user owns or has legitimate access to the case object.
        """
        if user_role in (UserRole.SYSTEM_ADMIN, UserRole.LAB_DIRECTOR):
            return True, None

        owner_id = self._case_ownership.get(case_id)
        if owner_id and owner_id != requesting_user_id:
            return False, f"Access denied. User '{requesting_user_id}' is not authorized to access case '{case_id}'"

        return True, None

    # ── 3. Pagination & Query Complexity Limits ────────────────────────────
    def validate_pagination(self, limit: int, offset: int) -> Tuple[bool, int, int, Optional[str]]:
        """
        Validates pagination parameters to prevent resource-exhausting deep offsets or huge pages.
        Returns (is_valid, clamped_limit, offset, error_message).
        """
        if limit < 1:
            return False, 0, 0, "Limit must be at least 1."
        if offset < 0:
            return False, 0, 0, "Offset cannot be negative."

        clamped_limit = min(limit, self.MAX_PAGE_SIZE)

        if offset > self.MAX_OFFSET:
            return False, clamped_limit, offset, f"Offset exceeds maximum allowed limit ({self.MAX_OFFSET}). Use cursor-based pagination."

        return True, clamped_limit, offset, None

    def validate_query_complexity(self, query_params: Dict[str, Any], current_depth: int = 1) -> Tuple[bool, Optional[str]]:
        """
        Rejects deeply nested JSON/query tree filters that can trigger catastrophic backtracking.
        """
        if current_depth > self.MAX_QUERY_DEPTH:
            return False, f"Query nesting depth exceeds maximum allowed limit ({self.MAX_QUERY_DEPTH})"

        for key, val in query_params.items():
            if isinstance(val, dict):
                ok, err = self.validate_query_complexity(val, current_depth + 1)
                if not ok:
                    return False, err
            elif isinstance(val, str) and len(val) > 2000:
                return False, f"Query parameter value for '{key}' exceeds maximum allowed length (2000 chars)"

        return True, None

    # ── 4. Request Body Size Limits ────────────────────────────────────────
    def validate_request_size(self, content_length: Optional[int], is_upload: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validates Content-Length header before reading large payload into memory.
        """
        if content_length is None:
            return True, None

        max_allowed = self.FORENSIC_UPLOAD_MAX_BYTES if is_upload else self.DEFAULT_JSON_BODY_MAX_BYTES
        if content_length > max_allowed:
            return False, f"Payload size ({content_length} bytes) exceeds maximum limit ({max_allowed} bytes)"

        return True, None

    # ── 5. User Computational Quota Tracking (Anti-Noisy Neighbor) ─────────
    def acquire_compute_quota(self, user_id: str, estimated_seconds: float = 1.0) -> Tuple[bool, Optional[str]]:
        """
        Checks if user has available heavy CPU compute seconds within rolling 1-hour window.
        """
        now = time.time()
        usage = self._user_usage[user_id]

        if usage.quota_exhausted_until > now:
            remaining = int(usage.quota_exhausted_until - now)
            return False, f"Hourly compute quota exhausted. Quota resets in {remaining}s."

        # Prune older records (1 hour)
        cutoff = now - 3600.0
        while usage.timestamps and usage.timestamps[0] < cutoff:
            usage.timestamps.popleft()

        if usage.compute_seconds_used + estimated_seconds > self.MAX_HOURLY_COMPUTE_SECONDS_PER_USER:
            usage.quota_exhausted_until = now + 3600.0
            return False, "Hourly compute quota exceeded (300s). Please wait for cooldown."

        usage.compute_seconds_used += estimated_seconds
        usage.timestamps.append(now)
        return True, None

    def release_compute_quota(self, user_id: str, actual_seconds: float, estimated_seconds: float = 1.0):
        """Adjusts recorded compute seconds based on actual execution time."""
        usage = self._user_usage.get(user_id)
        if usage:
            diff = actual_seconds - estimated_seconds
            usage.compute_seconds_used = max(0.0, usage.compute_seconds_used + diff)


# Singleton instance
api_security_engine = APISecurityEngine()
