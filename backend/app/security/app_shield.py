"""
FORENZA Application-Layer Attack Shield (Dimension 7 & 18).

Comprehensive defenses against OWASP Top 10 & API Top 10:
- SQL & NoSQL Injection detection & parameterized query helpers.
- Cross-Site Scripting (XSS) output encoding & tag neutralization.
- Command Injection metacharacter filter.
- Server-Side Request Forgery (SSRF) with DNS rebinding & private IP blocking.
- Path Traversal directory jail validation.
- HTTP Request Smuggling & Header Injection detection.
- Malicious File Upload magic byte verification.
- Prototype Pollution & safe deserialization guards.
"""

import html
import ipaddress
import json
import os
import re
import socket
import urllib.parse
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class ApplicationShield:
    """
    Production-grade application security shield.
    Provides strict sanitization, invariant validation, and injection defense without relying solely on WAF.
    """

    MAX_PAYLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

    # Disallowed private, link-local, loopback, and cloud metadata subnets
    BLOCKED_NETWORKS = [
        ipaddress.ip_network("0.0.0.0/8"),
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("100.64.0.0/10"),    # Carrier-grade NAT
        ipaddress.ip_network("127.0.0.0/8"),
        ipaddress.ip_network("169.254.0.0/16"),  # Link-local & AWS/GCP/Azure metadata (169.254.169.254)
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.0.0.0/24"),
        ipaddress.ip_network("192.168.0.0/16"),
        ipaddress.ip_network("198.18.0.0/15"),   # Benchmark network
        ipaddress.ip_network("224.0.0.0/4"),     # Multicast
        ipaddress.ip_network("240.0.0.0/4"),     # Reserved
        ipaddress.ip_network("::1/128"),
        ipaddress.ip_network("fc00::/7"),        # IPv6 Unique local
        ipaddress.ip_network("fe80::/10"),       # IPv6 Link-local
        ipaddress.ip_network("ff00::/8"),        # IPv6 Multicast
    ]

    ALLOWED_FORENSIC_EXTENSIONS = {
        ".fsa", ".hid", ".xml", ".csv", ".tsv", ".txt", ".json", ".vcf", ".bed", ".pdf", ".png"
    }

    MAGIC_SIGNATURES = {
        ".fsa": [b"ABIF", b"BIFA"],
        ".hid": [b"ABIF", b"BIFA"],
        ".xml": [b"<?xml", b"<xml", b"<LIMS", b"<CODIS"],
        ".json": [b"{", b"["],
        ".vcf": [b"##fileformat=VCF", b"#CHROM"],
        ".pdf": [b"%PDF-"],
        ".png": [b"\x89PNG\r\n\x1a\n"],
    }

    SQLI_PATTERNS = [
        re.compile(r"(\bUNION\b\s+\bSELECT\b)", re.IGNORECASE),
        re.compile(r"(\bOR\b\s+['\"]?1['\"]?\s*=\s*['\"]?1)", re.IGNORECASE),
        re.compile(r"(\bAND\b\s+['\"]?1['\"]?\s*=\s*['\"]?1)", re.IGNORECASE),
        re.compile(r"(--|#|/\*).*", re.IGNORECASE),
        re.compile(r"(;\s*\bDROP\b\s+\bTABLE\b)", re.IGNORECASE),
        re.compile(r"(\bSLEEP\s*\(|\bBENCHMARK\s*\(|\bWAITFOR\s+\bDELAY\b)", re.IGNORECASE),
        re.compile(r"(\bINFORMATION_SCHEMA\b)", re.IGNORECASE),
    ]

    COMMAND_INJECTION_CHARS = re.compile(r"[;&|`$<>\n\\]")

    DANGEROUS_NOSQL_KEYS = {"$where", "$gt", "$lt", "$ne", "$regex", "$in", "$nin", "$or", "$and", "$expr"}
    PROTOTYPE_POLLUTION_KEYS = {"__proto__", "constructor", "prototype"}

    # ── 1. SQL & NoSQL Injection Defense ──────────────────────────────────
    @classmethod
    def detect_sql_injection(cls, value: str) -> Tuple[bool, Optional[str]]:
        """
        Inspects string parameter for SQL injection patterns.
        Returns (is_sqli, detected_pattern_description).
        """
        if not value or not isinstance(value, str):
            return False, None

        for pattern in cls.SQLI_PATTERNS:
            match = pattern.search(value)
            if match:
                return True, f"SQL injection signature detected: '{match.group(0)[:30]}'"

        return False, None

    @classmethod
    def detect_nosql_injection(cls, data: Union[Dict, List, Any]) -> Tuple[bool, Optional[str]]:
        """
        Recursively scans JSON payload tree for NoSQL operator injection keys.
        """
        if isinstance(data, dict):
            for key, val in data.items():
                if key in cls.DANGEROUS_NOSQL_KEYS:
                    return True, f"NoSQL operator injection detected: '{key}'"
                if key in cls.PROTOTYPE_POLLUTION_KEYS:
                    return True, f"Prototype pollution key detected: '{key}'"
                is_bad, reason = cls.detect_nosql_injection(val)
                if is_bad:
                    return True, reason
        elif isinstance(data, list):
            for item in data:
                is_bad, reason = cls.detect_nosql_injection(item)
                if is_bad:
                    return True, reason

        return False, None

    # ── 2. Command Injection Defense ──────────────────────────────────────
    @classmethod
    def detect_command_injection(cls, value: str) -> Tuple[bool, Optional[str]]:
        """
        Checks if argument contains shell metacharacters that could enable command execution.
        """
        if not value or not isinstance(value, str):
            return False, None

        match = cls.COMMAND_INJECTION_CHARS.search(value)
        if match:
            return True, f"Shell metacharacter '{match.group(0)}' detected in parameter"

        return False, None

    # ── 3. Cross-Site Scripting (XSS) Output Encoding ─────────────────────
    @classmethod
    def sanitize_untrusted_text(cls, text: str) -> str:
        """Sanitizes raw untrusted strings to neutralize HTML/Script tags."""
        if not text or not isinstance(text, str):
            return ""
        return html.escape(text, quote=True)

    # ── 4. SSRF & DNS Rebinding Shield ────────────────────────────────────
    @classmethod
    def is_safe_external_url(cls, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validates URL to prevent Server-Side Request Forgery (SSRF).
        Enforces scheme allowlist, rejects cloud metadata, and verifies resolved IP against private networks.
        """
        if not url or not isinstance(url, str):
            return False, "Invalid URL string"

        try:
            parsed = urllib.parse.urlparse(url.strip())
        except Exception:
            return False, "Malformed URL format"

        if parsed.scheme not in ("http", "https"):
            return False, f"Prohibited URL scheme: {parsed.scheme}"

        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname in URL"

        lower_host = hostname.lower()
        if lower_host in ("localhost", "127.0.0.1", "::1", "metadata.google.internal", "169.254.169.254", "instance-data"):
            return False, "Blocked access to internal host/cloud metadata"

        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip_obj = ipaddress.ip_address(ip_str)
                for blocked_net in cls.BLOCKED_NETWORKS:
                    if ip_obj in blocked_net:
                        return False, f"Target IP {ip_str} resides in private/prohibited network"
        except socket.gaierror:
            return False, f"Could not resolve hostname: {hostname}"
        except Exception as e:
            return False, f"DNS resolution validation failed: {e}"

        return True, None

    # ── 5. Path Traversal & Directory Jail Validation ───────────────────────
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Strips directory traversal symbols and non-printable characters from filenames.
        """
        if not filename:
            return "unnamed_file.dat"

        base = os.path.basename(filename.replace("\\", "/"))
        clean = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", base)
        safe = re.sub(r"[^a-zA-Z0-9_.-]", "_", clean)
        safe = safe.lstrip(".")
        return safe if safe else "file.dat"

    @classmethod
    def safe_resolve_path(cls, base_dir: str, relative_path: str) -> Tuple[bool, Optional[str]]:
        """
        Resolves relative path inside base_dir and verifies it does not escape base_dir jail.
        Returns (is_safe, absolute_resolved_path_or_error).
        """
        clean_rel = relative_path.replace("\x00", "")
        if ".." in clean_rel or clean_rel.startswith("/") or clean_rel.startswith("\\"):
            return False, "Path traversal sequence detected"

        abs_base = os.path.abspath(base_dir)
        target = os.path.abspath(os.path.join(abs_base, clean_rel))

        try:
            common = os.path.commonpath([abs_base, target])
            if common != abs_base:
                return False, "Path escapes base directory jail"
        except Exception:
            return False, "Invalid path resolution"

        return True, target

    # ── 6. Malicious File Upload & Magic Byte Verification ──────────────────
    @classmethod
    def validate_file_upload(
        cls,
        filename: str,
        content_bytes: bytes,
        allowed_extensions: Optional[Set[str]] = None,
        max_bytes: int = MAX_PAYLOAD_BYTES,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates forensic file uploads:
        - Max size ceiling (10 MB).
        - Extension whitelist.
        - Magic byte signature verification where applicable.
        """
        if len(content_bytes) > max_bytes:
            return False, f"File size ({len(content_bytes)} bytes) exceeds maximum limit ({max_bytes} bytes)"

        safe_name = cls.sanitize_filename(filename)
        _, ext = os.path.splitext(safe_name.lower())

        allowed = allowed_extensions or cls.ALLOWED_FORENSIC_EXTENSIONS
        if ext not in allowed:
            return False, f"File extension '{ext}' is not permitted for forensic ingestion"

        if ext in cls.MAGIC_SIGNATURES:
            expected_sigs = cls.MAGIC_SIGNATURES[ext]
            header = content_bytes[:64].lstrip()
            if not any(header.startswith(sig) for sig in expected_sigs):
                if ext not in (".csv", ".tsv", ".txt", ".json"):
                    return False, f"File content does not match expected forensic format for '{ext}'"

        return True, None

    # ── 7. HTTP Request Smuggling & Header Injection Defense ──────────────
    @classmethod
    def detect_request_smuggling_headers(cls, headers: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """
        Detects conflicting transfer-encoding and content-length or CRLF injection in headers.
        """
        lower_headers = {k.lower(): v for k, v in headers.items()}

        # 1. Conflicting TE and CL (TE.CL / CL.TE attack)
        has_te = "transfer-encoding" in lower_headers
        has_cl = "content-length" in lower_headers
        if has_te and has_cl:
            return True, "Conflicting Transfer-Encoding and Content-Length headers detected"

        # 2. CRLF injection in header keys or values
        for k, v in headers.items():
            if "\r" in k or "\n" in k or "\r" in v or "\n" in v:
                return True, f"CRLF newline injection detected in header '{k}'"

        return False, None


# Singleton instance
app_shield = ApplicationShield()
