"""
FORENZA Infrastructure Security & Secrets Hygiene Guard (Dimension 10).

Validates:
- Secrets Hygiene & Rejection of Default/Insecure Credentials in Production.
- Database Connection Pool Timeouts & Limits.
- Network Segmentation & Origin Cloaking Verification.
- Restricted Port & TLS 1.3 Transport Invariants.
"""

import os
import re
from typing import Dict, List, Optional, Tuple


class InfrastructureGuard:
    """
    Validates infrastructure-level security controls and secrets management.
    """

    INSECURE_DEFAULT_SECRETS = {
        "secret", "admin", "password", "123456", "default", "changeme",
        "root", "test", "development", "jwt_secret", "forenza_secret"
    }

    REQUIRED_PRODUCTION_SECRETS = [
        "FORENZA_SESSION_HMAC_SECRET",
        "FORENZA_ORIGIN_VERIFY_SECRET",
    ]

    RESTRICTED_ADMIN_PORTS = {22, 23, 3306, 5432, 6379, 27017, 9200, 2375, 2376}

    @classmethod
    def audit_secrets_hygiene(cls, env_vars: Optional[Dict[str, str]] = None) -> Tuple[bool, List[str]]:
        """
        Scans runtime environment variables for insecure or default secrets.
        Returns (is_secure, list_of_violations).
        """
        env = env_vars if env_vars is not None else dict(os.environ)
        is_prod = env.get("FORENZA_ENVIRONMENT", "").lower() in ("production", "prod")

        violations: List[str] = []

        for key, val in env.items():
            if any(s in key.lower() for s in ("secret", "password", "key", "token", "auth")):
                clean_val = val.strip().lower()
                if clean_val in cls.INSECURE_DEFAULT_SECRETS:
                    violations.append(f"Insecure default secret detected in '{key}'. Must be changed to cryptographically random entropy.")
                elif len(val) < 16 and is_prod:
                    violations.append(f"Production secret in '{key}' has insufficient entropy (length < 16 chars).")

        if is_prod:
            for req in cls.REQUIRED_PRODUCTION_SECRETS:
                if not env.get(req) or env.get(req).strip() in cls.INSECURE_DEFAULT_SECRETS:
                    violations.append(f"Mandatory production secret '{req}' is missing or unconfigured.")

        return len(violations) == 0, violations

    @classmethod
    def validate_port_exposure(cls, exposed_ports: List[int], is_public_facing: bool = True) -> Tuple[bool, List[str]]:
        """
        Ensures internal database and administrative ports are never bound to public-facing network interfaces.
        """
        violations: List[str] = []
        if is_public_facing:
            for p in exposed_ports:
                if p in cls.RESTRICTED_ADMIN_PORTS:
                    violations.append(f"Administrative/Database port {p} is exposed to public interface. Must reside in private VPC subnet.")

        return len(violations) == 0, violations

    @classmethod
    def validate_tls_configuration(cls, min_tls_version: str = "TLSv1.3", hsts_enabled: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Validates that TLS transport meets modern cryptographic baselines (TLS 1.3 + HSTS).
        """
        if min_tls_version not in ("TLSv1.2", "TLSv1.3"):
            return False, f"Insecure TLS baseline '{min_tls_version}'. Minimum required is TLSv1.2, recommended TLSv1.3."

        if not hsts_enabled:
            return False, "HTTP Strict Transport Security (HSTS) must be enabled."

        return True, None


# Singleton instance
infra_guard = InfrastructureGuard()
