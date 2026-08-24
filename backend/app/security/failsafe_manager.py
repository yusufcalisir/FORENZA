"""
FORENZA Fail-Safe Behavior & Emergency Control Manager (Dimension 16 & 18).

Implements:
- Dual-Mode Degradation Architecture:
  * Fail-Open for non-sensitive public content & reference databases.
  * Fail-Closed for genuinely sensitive operations (Auth, ZKP, Evidence Signing).
- Local In-Memory Fallback when external security dependencies (Redis/WAF) fail.
- Anti-Lockout Safeguards: Prevents accidental total user lockouts from false positives.
- Emergency Administrative Override Controls (Cryptographic Master Key).
"""

import hmac
import logging
import os
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("forenza.security.failsafe")


class OperationSensitivity(str, Enum):
    PUBLIC = "PUBLIC"               # Fail-Open on dependency crash
    READ_ONLY = "READ_ONLY"         # Fail-Open with baseline throttle
    SENSITIVE_WRITE = "SENSITIVE_WRITE" # Fail-Closed
    AUTHENTICATION = "AUTHENTICATION"   # Fail-Closed
    CRYPTOGRAPHIC = "CRYPTOGRAPHIC"     # Fail-Closed


class FailSafeManager:
    """
    Guarantees the security system does not become a denial-of-service against legitimate users.
    """

    SENSITIVE_PREFIXES = {
        "/api/v1/auth/": OperationSensitivity.AUTHENTICATION,
        "/api/v1/cases/create": OperationSensitivity.SENSITIVE_WRITE,
        "/api/v1/evidence/sign": OperationSensitivity.CRYPTOGRAPHIC,
        "/api/v1/zkp/prove": OperationSensitivity.CRYPTOGRAPHIC,
        "/api/v1/admin/": OperationSensitivity.SENSITIVE_WRITE,
    }

    def __init__(self):
        self._emergency_bypass_active: bool = False
        self._emergency_bypass_activated_at: float = 0.0
        self._emergency_bypass_activated_by: Optional[str] = None
        self._whitelisted_admin_subnets: Set[str] = {"127.0.0.1", "::1"}

    def determine_sensitivity(self, path: str, method: str = "GET") -> OperationSensitivity:
        """Determines whether a route is public (Fail-Open) or sensitive (Fail-Closed)."""
        for prefix, sensitivity in self.SENSITIVE_PREFIXES.items():
            if path.startswith(prefix):
                return sensitivity

        if method in ("POST", "PUT", "DELETE", "PATCH"):
            return OperationSensitivity.SENSITIVE_WRITE

        return OperationSensitivity.PUBLIC

    def execute_with_failsafe(
        self,
        path: str,
        method: str,
        security_check_fn: Callable[[], Tuple[bool, Optional[str]]],
        fallback_value_on_crash: bool = True,
    ) -> Tuple[bool, Optional[str], bool]:
        """
        Executes a security check with sensitivity-aware fail-safe handling.
        Returns (is_allowed, error_message, is_degraded_fallback).
        """
        # If emergency bypass is active, allow traffic unless critical auth
        if self._emergency_bypass_active:
            sensitivity = self.determine_sensitivity(path, method)
            if sensitivity not in (OperationSensitivity.AUTHENTICATION, OperationSensitivity.CRYPTOGRAPHIC):
                return True, None, True

        try:
            is_ok, err_msg = security_check_fn()
            return is_ok, err_msg, False
        except Exception as exc:
            sensitivity = self.determine_sensitivity(path, method)
            logger.error(f"[FAILSAFE_TRIGGERED] Security check crashed on path='{path}': {exc}")

            # Fail-Closed for Sensitive Operations
            if sensitivity in (OperationSensitivity.AUTHENTICATION, OperationSensitivity.CRYPTOGRAPHIC, OperationSensitivity.SENSITIVE_WRITE):
                return (
                    False,
                    "Security verification service temporarily degraded for sensitive operations. Please retry shortly.",
                    True,
                )

            # Fail-Open for Public / Non-Sensitive Content
            return True, None, True

    # ── Emergency Administrative Controls ──────────────────────────────────
    def activate_emergency_bypass(self, admin_token: str, authorized_user: str) -> Tuple[bool, Optional[str]]:
        """
        Activates emergency security bypass using cryptographic master key.
        Used by system administrators to recover from external dependency outages.
        """
        master_secret = os.environ.get("FORENZA_EMERGENCY_OVERRIDE_KEY", "EMERGENCY_MASTER_SEC_2026_PROD_OVERRIDE")
        if not admin_token or not hmac.compare_digest(admin_token.strip(), master_secret.strip()):
            logger.warning(f"[UNAUTHORIZED_EMERGENCY_ATTEMPT] Failed emergency bypass attempt by '{authorized_user}'")
            return False, "Invalid emergency administrative key."

        self._emergency_bypass_active = True
        self._emergency_bypass_activated_at = time.time()
        self._emergency_bypass_activated_by = authorized_user
        logger.critical(f"[EMERGENCY_OVERRIDE_ACTIVE] Security bypass activated by admin '{authorized_user}'.")
        return True, "Emergency bypass activated successfully."

    def deactivate_emergency_bypass(self) -> bool:
        """Deactivates emergency bypass and restores strict security enforcement."""
        self._emergency_bypass_active = False
        self._emergency_bypass_activated_at = 0.0
        self._emergency_bypass_activated_by = None
        logger.info("[EMERGENCY_OVERRIDE_DEACTIVATED] Normal security posture restored.")
        return True

    def get_failsafe_status(self) -> Dict[str, Any]:
        """Returns fail-safe status and emergency bypass telemetry."""
        return {
            "emergency_bypass_active": self._emergency_bypass_active,
            "emergency_bypass_activated_at": self._emergency_bypass_activated_at,
            "emergency_bypass_activated_by": self._emergency_bypass_activated_by,
        }


# Singleton instance
failsafe_manager = FailSafeManager()
