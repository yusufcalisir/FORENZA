"""
FORENZA Enterprise Security Headers & CSP Manager (Dimension 13 & 18).

Provides compatible, hardened security headers preventing:
- Clickjacking & UI Redressing (frame-ancestors 'none', X-Frame-Options: DENY).
- MIME-Sniffing (X-Content-Type-Options: nosniff).
- Protocol Downgrades (Strict-Transport-Security preload).
- Data Leakage via Referrers (Referrer-Policy: strict-origin-when-cross-origin).
- Hardware/Device API Abuse (Permissions-Policy).
- XSS via Content-Security-Policy (Tailored for Next.js, Three.js 3D Canvas, and WebCrypto Workers).
"""

from typing import Dict, Optional


class SecurityHeadersManager:
    """
    Manages and validates HTTP security headers across all API and frontend endpoints.
    """

    DEFAULT_CSP_DIRECTIVES = {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-eval'", "'unsafe-inline'"],  # Next.js hydration & WebCrypto PoW
        "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        "font-src": ["'self'", "https://fonts.gstatic.com", "data:"],
        "img-src": ["'self'", "data:", "blob:", "https:"],
        "connect-src": [
            "'self'",
            "http://localhost:*",
            "http://127.0.0.1:*",
            "https://*.onrender.com",
            "https://*.vercel.app",
            "ws://localhost:*",
            "wss://*.onrender.com",
        ],
        "worker-src": ["'self'", "blob:"],  # Three.js 3D BPA & WebCrypto worker threads
        "frame-ancestors": ["'none'"],       # Strict Anti-Clickjacking
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
    }

    def build_csp_header(self, custom_directives: Optional[Dict[str, list]] = None) -> str:
        """
        Builds a RFC-compliant, semicolon-delimited Content-Security-Policy string.
        """
        directives = custom_directives or self.DEFAULT_CSP_DIRECTIVES
        parts = []
        for directive, sources in directives.items():
            sources_str = " ".join(sources)
            parts.append(f"{directive} {sources_str}")
        return "; ".join(parts) + ";"

    def get_enterprise_security_headers(self, is_html: bool = False) -> Dict[str, str]:
        """
        Returns a complete dictionary of enterprise security headers.
        """
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=(self)",
            "X-XSS-Protection": "1; mode=block",
        }

        if is_html:
            headers["Content-Security-Policy"] = self.build_csp_header()

        return headers

    def validate_header_compliance(self, response_headers: Dict[str, str]) -> Dict[str, bool]:
        """
        Audits whether a given response contains all required security headers.
        """
        lower_headers = {k.lower(): v for k, v in response_headers.items()}
        return {
            "has_nosniff": lower_headers.get("x-content-type-options") == "nosniff",
            "has_frame_deny": lower_headers.get("x-frame-options") in ("DENY", "SAMEORIGIN"),
            "has_hsts": "max-age" in lower_headers.get("strict-transport-security", ""),
            "has_referrer_policy": bool(lower_headers.get("referrer-policy")),
            "has_permissions_policy": bool(lower_headers.get("permissions-policy")),
        }


# Singleton instance
headers_guard = SecurityHeadersManager()
