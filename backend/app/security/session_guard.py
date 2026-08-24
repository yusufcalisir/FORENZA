"""
FORENZA Privacy-Conscious Session & Device Intelligence (Dimension 5).

Implements:
- Ephemeral, Non-Invasive Device Consistency Validation.
- Short-Lived Access Tokens (15 min) + Refresh Token Rotation (RTR).
- Automatic Token Family Reuse Detection (Anti-Token Theft).
- Ephemeral HMAC Session Binding (Zero permanent tracking of ordinary users).
- Session Risk Scoring based on behavioral anomalies and session hijacking signals.
"""

import hashlib
import hmac
import os
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class SessionAuthLevel(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED_BASIC = "AUTHENTICATED_BASIC"
    AUTHENTICATED_MFA = "AUTHENTICATED_MFA"


@dataclass
class SessionDeviceContext:
    user_agent_family: str
    accept_language_prefix: str
    ip_subnet: str


@dataclass
class RefreshTokenRecord:
    token_hash: str
    family_id: str
    user_id: str
    issued_at: float
    expires_at: float
    is_consumed: bool = False
    revoked: bool = False


@dataclass
class ActiveSessionRecord:
    session_id: str
    user_id: Optional[str]
    auth_level: SessionAuthLevel
    device_context_hash: str
    created_at: float
    last_active_at: float
    risk_score: int = 0
    anomaly_flags: List[str] = field(default_factory=list)
    refresh_token_family_id: Optional[str] = None


class SessionSecurityManager:
    """
    Privacy-first session and token manager.
    Protects user accounts without invasive canvas/audio fingerprinting or permanent surveillance.
    """

    ACCESS_TOKEN_TTL_SECONDS = 900.0        # 15 minutes
    REFRESH_TOKEN_TTL_SECONDS = 604800.0    # 7 days
    SESSION_INACTIVITY_TTL = 86400.0        # 24 hours

    def __init__(self, hmac_secret: Optional[str] = None):
        # Ephemeral secret for HMAC context binding, rotatable without persistent storage
        self._hmac_secret = (hmac_secret or os.getenv("FORENZA_SESSION_HMAC_SECRET") or secrets.token_hex(32)).encode("utf-8")
        self._sessions: Dict[str, ActiveSessionRecord] = {}
        self._refresh_tokens: Dict[str, RefreshTokenRecord] = {}
        self._token_families: Dict[str, Set[str]] = {}  # family_id -> set of token_hashes
        self._last_cleanup = time.time()

    def generate_device_context_hash(
        self,
        user_agent: str,
        accept_language: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> str:
        """
        Computes a non-invasive, coarse device context hash.
        Uses only high-level UA family and /24 subnet rather than persistent hardware fingerprints.
        """
        # Normalize coarse UA (e.g. Chrome 120 on Mac vs Firefox on Linux)
        clean_ua = (user_agent or "unknown").strip().split(" ")[0][:50]
        clean_lang = (accept_language or "en").strip().split(",")[0][:5]

        # Extract /24 IPv4 or /48 IPv6 subnet to accommodate mobile carrier IP hops
        subnet = "127.0.0"
        if client_ip:
            if "." in client_ip:
                parts = client_ip.split(".")
                subnet = ".".join(parts[:3]) if len(parts) >= 3 else client_ip
            elif ":" in client_ip:
                parts = client_ip.split(":")
                subnet = ":".join(parts[:3]) if len(parts) >= 3 else client_ip

        raw = f"{clean_ua}|{clean_lang}|{subnet}"
        return hmac.new(self._hmac_secret, raw.encode("utf-8"), hashlib.sha256).hexdigest()[:24]

    def create_session(
        self,
        user_id: Optional[str] = None,
        auth_level: SessionAuthLevel = SessionAuthLevel.ANONYMOUS,
        user_agent: str = "",
        accept_language: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> Tuple[str, str, str]:
        """
        Creates a new session and returns (session_id, access_token, refresh_token).
        """
        now = time.time()
        session_id = f"fsess_{secrets.token_urlsafe(32)}"
        family_id = f"fam_{secrets.token_urlsafe(16)}"
        context_hash = self.generate_device_context_hash(user_agent, accept_language, client_ip)

        session = ActiveSessionRecord(
            session_id=session_id,
            user_id=user_id,
            auth_level=auth_level,
            device_context_hash=context_hash,
            created_at=now,
            last_active_at=now,
            refresh_token_family_id=family_id if user_id else None,
        )
        self._sessions[session_id] = session

        # Generate tokens if authenticated
        access_token = ""
        refresh_token = ""
        if user_id:
            refresh_token = f"frt_{secrets.token_urlsafe(48)}"
            rt_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
            rt_record = RefreshTokenRecord(
                token_hash=rt_hash,
                family_id=family_id,
                user_id=user_id,
                issued_at=now,
                expires_at=now + self.REFRESH_TOKEN_TTL_SECONDS,
            )
            self._refresh_tokens[rt_hash] = rt_record
            if family_id not in self._token_families:
                self._token_families[family_id] = set()
            self._token_families[family_id].add(rt_hash)

            access_token = f"fat_{secrets.token_urlsafe(32)}"

        return session_id, access_token, refresh_token

    def validate_session_consistency(
        self,
        session_id: str,
        user_agent: str,
        accept_language: Optional[str] = None,
        client_ip: Optional[str] = None,
        now: Optional[float] = None,
    ) -> Tuple[bool, int, List[str]]:
        """
        Evaluates session consistency. Detects sudden context switching (hijacking attempts).
        Returns (is_valid, session_risk_score, anomaly_flags).
        """
        ts = now if now is not None else time.time()
        self._maybe_cleanup(ts)

        session = self._sessions.get(session_id)
        if not session:
            return False, 80, ["SESSION_NOT_FOUND"]

        # Check inactivity timeout
        if ts - session.last_active_at > self.SESSION_INACTIVITY_TTL:
            del self._sessions[session_id]
            return False, 70, ["SESSION_EXPIRED_INACTIVITY"]

        session.last_active_at = ts
        current_context = self.generate_device_context_hash(user_agent, accept_language, client_ip)

        anomalies: List[str] = []
        risk_increment = 0

        # Check context mismatch (potential token / cookie theft across networks)
        if current_context != session.device_context_hash:
            anomalies.append("DEVICE_CONTEXT_MISMATCH")
            risk_increment += 40

        session.risk_score = min(100, max(0, session.risk_score + risk_increment))
        session.anomaly_flags.extend(anomalies)

        return True, session.risk_score, anomalies

    def rotate_refresh_token(
        self,
        presented_refresh_token: str,
        user_agent: str = "",
        client_ip: Optional[str] = None,
        now: Optional[float] = None,
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Executes Refresh Token Rotation (RTR).
        Detects reuse attacks: If an already consumed token is reused, revokes the entire family!
        Returns (success, new_access_token, new_refresh_token, error_message).
        """
        ts = now if now is not None else time.time()
        rt_hash = hashlib.sha256(presented_refresh_token.encode("utf-8")).hexdigest()
        record = self._refresh_tokens.get(rt_hash)

        if not record:
            return False, None, None, "Invalid refresh token."

        # 1. Automatic Reuse Detection (Critical Security Feature)
        if record.is_consumed or record.revoked:
            # Token reuse detected! Attacker or victim is using an old token -> Revoke family
            family_id = record.family_id
            self._revoke_token_family(family_id)
            return False, None, None, "Token reuse detected. Entire session family revoked for security."

        # 2. Check expiration
        if record.expires_at < ts:
            return False, None, None, "Refresh token expired. Please log in again."

        # 3. Mark current token consumed
        record.is_consumed = True

        # 4. Issue new rotated pair
        new_refresh_token = f"frt_{secrets.token_urlsafe(48)}"
        new_rt_hash = hashlib.sha256(new_refresh_token.encode("utf-8")).hexdigest()
        new_record = RefreshTokenRecord(
            token_hash=new_rt_hash,
            family_id=record.family_id,
            user_id=record.user_id,
            issued_at=ts,
            expires_at=ts + self.REFRESH_TOKEN_TTL_SECONDS,
        )
        self._refresh_tokens[new_rt_hash] = new_record
        self._token_families[record.family_id].add(new_rt_hash)

        new_access_token = f"fat_{secrets.token_urlsafe(32)}"
        return True, new_access_token, new_refresh_token, None

    def _revoke_token_family(self, family_id: str):
        """Invalidates all refresh tokens and sessions belonging to a family."""
        token_hashes = self._token_families.get(family_id, set())
        for th in token_hashes:
            rec = self._refresh_tokens.get(th)
            if rec:
                rec.revoked = True

        # Invalidate associated sessions
        for sess in list(self._sessions.values()):
            if sess.refresh_token_family_id == family_id:
                del self._sessions[sess.session_id]

    def _maybe_cleanup(self, now: float):
        if now - self._last_cleanup < 300.0 and len(self._sessions) < 20000:
            return
        self._last_cleanup = now
        expired_sessions = [
            sid for sid, s in self._sessions.items()
            if now - s.last_active_at > self.SESSION_INACTIVITY_TTL
        ]
        for sid in expired_sessions:
            del self._sessions[sid]


# Singleton instance
session_manager = SessionSecurityManager()
