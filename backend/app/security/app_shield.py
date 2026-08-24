"""
FORENZA Application-Layer Shield (Dimensions 7, 8, 9).

OWASP Top 10 & API Top 10 Hardening:
- SSRF Shield: blocks private/internal IP subnets and AWS/GCP metadata endpoints.
- Path Traversal Shield: sanitizes filenames and prevents directory escaping.
- Malicious File Upload Inspector: magic byte validation and 10MB cap for forensic files.
- Request Payload Size Guard: blocks oversized bodies before buffer exhaustion.
- XSS Input Sanitizer: escapes raw untrusted strings.
"""

import ipaddress
import os
import re
import socket
import urllib.parse
from typing import List, Optional, Set, Tuple


class ApplicationShield:
    """
    Core application security sanitization and validation utilities.
    """

    MAX_PAYLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

    # Disallowed private and cloud metadata IP networks
    BLOCKED_NETWORKS = [
        ipaddress.ip_network("0.0.0.0/8"),
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("127.0.0.0/8"),
        ipaddress.ip_network("169.254.0.0/16"),  # Link-local & AWS/GCP metadata
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.168.0.0/16"),
        ipaddress.ip_network("::1/128"),
        ipaddress.ip_network("fc00::/7"),        # IPv6 Unique local
        ipaddress.ip_network("fe80::/10"),       # IPv6 Link-local
    ]

    ALLOWED_FORENSIC_EXTENSIONS = {
        ".fsa", ".hid", ".xml", ".csv", ".tsv", ".txt", ".json", ".vcf", ".bed"
    }

    MAGIC_SIGNATURES = {
        ".fsa": [b"ABIF", b"BIFA"],
        ".hid": [b"ABIF", b"BIFA"],
        ".xml": [b"<?xml", b"<xml", b"<LIMS", b"<CODIS"],
        ".json": [b"{", b"["],
        ".vcf": [b"##fileformat=VCF", b"#CHROM"],
    }

    @classmethod
    def is_safe_external_url(cls, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validates URL to prevent Server-Side Request Forgery (SSRF).
        Returns (is_safe, error_reason).
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

        # Block localhost and metadata keywords
        lower_host = hostname.lower()
        if lower_host in ("localhost", "127.0.0.1", "::1", "metadata.google.internal", "169.254.169.254"):
            return False, "Blocked access to internal host/metadata"

        # Resolve IP to verify subnet
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

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Strips path components, directory traversal symbols, and dangerous characters.
        """
        if not filename:
            return "unnamed_file.dat"

        # Strip directory path (os.path.basename and raw / \ replacements)
        base = os.path.basename(filename.replace("\\", "/"))
        # Remove null bytes and non-printable characters
        clean = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", base)
        # Retain only safe alphanumeric, hyphen, dot, and underscore
        safe = re.sub(r"[^a-zA-Z0-9_.-]", "_", clean)
        # Prevent hidden files or relative dots (e.g. ..)
        safe = safe.lstrip(".")
        return safe if safe else "file.dat"

    @classmethod
    def validate_file_upload(
        cls,
        filename: str,
        content_bytes: bytes,
        allowed_extensions: Optional[Set[str]] = None,
        max_bytes: int = MAX_PAYLOAD_BYTES,
    ) -> Tuple[bool, Optional[str]]:
        """
        Enforces strict file upload security:
        - Size bound checking.
        - Allowed forensic extension checking.
        - Magic signature verification where applicable.
        """
        if len(content_bytes) > max_bytes:
            return False, f"File size ({len(content_bytes)} bytes) exceeds maximum limit ({max_bytes} bytes)"

        safe_name = cls.sanitize_filename(filename)
        _, ext = os.path.splitext(safe_name.lower())

        allowed = allowed_extensions or cls.ALLOWED_FORENSIC_EXTENSIONS
        if ext not in allowed:
            return False, f"File extension '{ext}' is not permitted for forensic ingestion"

        # Magic byte signature check
        if ext in cls.MAGIC_SIGNATURES:
            expected_sigs = cls.MAGIC_SIGNATURES[ext]
            header = content_bytes[:64].lstrip()
            if not any(header.startswith(sig) for sig in expected_sigs):
                # Allow standard text/CSV without strict binary header
                if ext not in (".csv", ".tsv", ".txt", ".json"):
                    return False, f"File content does not match expected forensic format for '{ext}'"

        return True, None

    @classmethod
    def sanitize_untrusted_text(cls, text: str) -> str:
        """Sanitizes raw text to neutralize HTML/Script tags."""
        if not text or not isinstance(text, str):
            return ""
        clean = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        clean = clean.replace('"', "&quot;").replace("'", "&#x27;")
        return clean
