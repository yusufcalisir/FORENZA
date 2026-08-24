"""
FORENZA Security Headers & CSP Test Suite (Dimension 13).

Validates:
- Enterprise Security Headers (nosniff, DENY, HSTS preload, Permissions-Policy)
- Content-Security-Policy Directives (Anti-Clickjacking frame-ancestors 'none', WebGL/Three.js worker-src)
- Header Compliance Auditor
"""

import pytest

from app.security.headers_guard import SecurityHeadersManager


class TestSecurityHeadersGuard:
    def test_enterprise_security_headers_present(self):
        """Tüm temel kurumsal güvenlik başlıkları eksiksiz üretilmeli."""
        manager = SecurityHeadersManager()
        headers = manager.get_enterprise_security_headers(is_html=True)

        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert "max-age=63072000" in headers["Strict-Transport-Security"]
        assert "preload" in headers["Strict-Transport-Security"]
        assert "camera=()" in headers["Permissions-Policy"]
        assert "Content-Security-Policy" in headers

    def test_csp_header_format_and_directives(self):
        """CSP başlığı Next.js ve Three.js Canvas uyumlu olmalı ve clickjacking'i engellemeli."""
        manager = SecurityHeadersManager()
        csp = manager.build_csp_header()

        # Anti-Clickjacking
        assert "frame-ancestors 'none'" in csp
        # WebGL / WebCrypto worker support
        assert "worker-src 'self' blob:" in csp
        # Google fonts support
        assert "https://fonts.googleapis.com" in csp
        # Base and form action restrictions
        assert "base-uri 'self'" in csp
        assert "form-action 'self'" in csp

    def test_header_compliance_auditing(self):
        """Başlık uyumluluk denetleyicisi eksik başlıkları tespit edebilmeli."""
        manager = SecurityHeadersManager()

        complete_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=()",
        }

        audit = manager.validate_header_compliance(complete_headers)
        assert audit["has_nosniff"] is True
        assert audit["has_frame_deny"] is True
        assert audit["has_hsts"] is True
        assert audit["has_referrer_policy"] is True
        assert audit["has_permissions_policy"] is True

        # Incomplete headers missing HSTS and X-Frame-Options
        bad_headers = {"X-Content-Type-Options": "nosniff"}
        bad_audit = manager.validate_header_compliance(bad_headers)
        assert bad_audit["has_nosniff"] is True
        assert bad_audit["has_frame_deny"] is False
        assert bad_audit["has_hsts"] is False
