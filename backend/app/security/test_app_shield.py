"""
FORENZA Web Application Protection Test Suite (Dimension 7).

Validates:
- SQL Injection (SQLi) Detection
- NoSQL Injection & Prototype Pollution Detection
- Command Injection Metacharacter Rejection
- Cross-Site Scripting (XSS) Output Encoding
- Server-Side Request Forgery (SSRF) & Private Subnet Protection
- Path Traversal Directory Jail Enforcement
- HTTP Request Smuggling & Header CRLF Injection Detection
- Forensic File Upload Magic Byte Verification
"""

import tempfile
import pytest

from app.security.app_shield import ApplicationShield


class TestApplicationShieldComprehensive:
    def test_sqli_detection_patterns(self):
        """SQL injection kalıpları (UNION SELECT, OR 1=1, DROP TABLE, SLEEP) tespit edilmeli."""
        shield = ApplicationShield()

        # Malicious inputs
        assert shield.detect_sql_injection("admin' UNION SELECT * FROM users--")[0] is True
        assert shield.detect_sql_injection("1' OR '1'='1")[0] is True
        assert shield.detect_sql_injection("test; DROP TABLE cases;")[0] is True
        assert shield.detect_sql_injection("1' AND SLEEP(5)--")[0] is True

        # Benign forensic inputs
        assert shield.detect_sql_injection("NIST SRM 2391d Comp A")[0] is False
        assert shield.detect_sql_injection("STR Locus D8S1179 allele 13,14")[0] is False

    def test_nosql_injection_and_prototype_pollution(self):
        """NoSQL operatör enjeksiyonları ($gt, $where, $ne) ve prototype pollution yakalanmalı."""
        shield = ApplicationShield()

        # NoSQL injection payloads
        assert shield.detect_nosql_injection({"username": "admin", "password": {"$ne": None}})[0] is True
        assert shield.detect_nosql_injection({"$where": "this.password.length > 5"})[0] is True
        assert shield.detect_nosql_injection({"filter": {"age": {"$gt": 0}}})[0] is True

        # Prototype pollution payloads
        assert shield.detect_nosql_injection({"__proto__": {"isAdmin": True}})[0] is True
        assert shield.detect_nosql_injection({"constructor": {"prototype": {"polluted": True}}})[0] is True

        # Benign forensic payload
        assert shield.detect_nosql_injection({"case_id": "CASE-2026-001", "loci": ["TH01", "vWA"]})[0] is False

    def test_command_injection_detection(self):
        """Shell komut enjeksiyon metakarakterleri (| ; & ` $ > <) yakalanmalı."""
        shield = ApplicationShield()

        assert shield.detect_command_injection("sample.fsa; cat /etc/passwd")[0] is True
        assert shield.detect_command_injection("sample.fsa | rm -rf /")[0] is True
        assert shield.detect_command_injection("$(whoami)")[0] is True
        assert shield.detect_command_injection("sample.fsa && nc -e /bin/sh")[0] is True

        # Benign filename
        assert shield.detect_command_injection("sample_run_01_green.fsa")[0] is False

    def test_xss_sanitization_and_html_encoding(self):
        """XSS ve zararlı HTML etiketleri bağlamsal olarak güvenli karakterlere dönüştürülmeli."""
        shield = ApplicationShield()

        raw_script = "<script>alert('XSS')</script>"
        clean_script = shield.sanitize_untrusted_text(raw_script)
        assert "<script>" not in clean_script
        assert "&lt;script&gt;" in clean_script

        raw_img = '<img src=x onerror="alert(1)">'
        clean_img = shield.sanitize_untrusted_text(raw_img)
        assert "<img" not in clean_img
        assert "&quot;" in clean_img

    def test_ssrf_and_dns_rebinding_shield(self):
        """SSRF koruması yerel ve özel ağ IP'lerini kesinlikle reddetmeli."""
        shield = ApplicationShield()

        # Prohibited schemes
        assert shield.is_safe_external_url("file:///etc/passwd")[0] is False
        assert shield.is_safe_external_url("gopher://127.0.0.1:6379")[0] is False

        # Prohibited internal IPs & cloud metadata
        assert shield.is_safe_external_url("http://127.0.0.1:8000/api")[0] is False
        assert shield.is_safe_external_url("http://localhost:3000")[0] is False
        assert shield.is_safe_external_url("http://169.254.169.254/latest/meta-data/")[0] is False
        assert shield.is_safe_external_url("http://10.0.0.1/internal/health")[0] is False
        assert shield.is_safe_external_url("http://192.168.1.1/admin")[0] is False

    def test_path_traversal_jail_verification(self):
        """Dizin kaçış (Path traversal) girişimleri engellenmeli ve base_dir dışına çıkılmamalı."""
        shield = ApplicationShield()

        with tempfile.TemporaryDirectory() as base_dir:
            # Traversal attempts
            assert shield.safe_resolve_path(base_dir, "../../etc/passwd")[0] is False
            assert shield.safe_resolve_path(base_dir, "..\\..\\windows\\system32")[0] is False
            assert shield.safe_resolve_path(base_dir, "/etc/shadow")[0] is False

            # Valid relative path inside jail
            ok, target = shield.safe_resolve_path(base_dir, "uploads/case_01.fsa")
            assert ok is True
            assert target is not None
            assert target.startswith(base_dir)

    def test_request_smuggling_header_detection(self):
        """HTTP Request Smuggling (TE.CL / CL.TE) ve CRLF başlık enjeksiyonu yakalanmalı."""
        shield = ApplicationShield()

        # Conflicting headers
        bad_headers = {
            "Host": "api.forenza.org",
            "Transfer-Encoding": "chunked",
            "Content-Length": "120",
        }
        assert shield.detect_request_smuggling_headers(bad_headers)[0] is True

        # CRLF injection in value
        crlf_headers = {
            "Host": "api.forenza.org",
            "X-User-Role": "Analyst\r\nSet-Cookie: admin=true",
        }
        assert shield.detect_request_smuggling_headers(crlf_headers)[0] is True

        # Benign headers
        clean_headers = {
            "Host": "api.forenza.org",
            "Content-Type": "application/json",
            "Authorization": "Bearer fat_123",
        }
        assert shield.detect_request_smuggling_headers(clean_headers)[0] is False

    def test_forensic_file_upload_validation(self):
        """Adli dosya yükleme doğrulaması magic byte ve uzantı kontrolü yapmalı."""
        shield = ApplicationShield()

        # Valid ABIF .fsa file
        valid_fsa_bytes = b"ABIF\x00\x01\x00\x02" + (b"\x00" * 100)
        assert shield.validate_file_upload("sample_run.fsa", valid_fsa_bytes)[0] is True

        # Valid VCF file
        valid_vcf_bytes = b"##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\n"
        assert shield.validate_file_upload("variants.vcf", valid_vcf_bytes)[0] is True

        # Executable disguised as .fsa (Magic byte mismatch)
        fake_fsa_bytes = b"MZ\x90\x00\x03\x00\x00\x00" + (b"\x00" * 100)  # Windows PE binary
        assert shield.validate_file_upload("trojan.fsa", fake_fsa_bytes)[0] is False

        # Prohibited file extension
        assert shield.validate_file_upload("script.php", b"<?php phpinfo(); ?>")[0] is False
        assert shield.validate_file_upload("exploit.exe", b"MZ...")[0] is False
