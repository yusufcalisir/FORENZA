"""
FORENZA Security Layer API Routes (Dimensions 1, 4, 11, 15, 18).

Exposes:
- GET  /api/v1/security/health       : Sanitized security subsystem health check
- GET  /api/v1/security/metrics      : Protected telemetry and concurrency metrics (Admin Only)
- POST /api/v1/security/pow-challenge : Silent background WebCrypto challenge generator
- POST /api/v1/security/verify-pow   : Constant-time O(1) Nonce verification with anti-replay
"""

import hashlib
import hmac
import os
import secrets
import time
from collections import deque
from typing import Deque, Dict, Optional, Set

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from app.security.concurrency_guard import get_resource_guard
from app.security.risk_engine import traffic_risk_engine

router = APIRouter(prefix="/security", tags=["Security Subsystem"])

# Derived master key for multi-worker signature consistency
_POW_SECRET = os.getenv("FORENZA_SECRET_KEY", "FORENZA_PRODUCTION_POW_MASTER_SECRET_2026").encode("utf-8")
_ADMIN_KEY = os.getenv("FORENZA_ADMIN_KEY", "FORENZA_ADMIN_METRICS_KEY_2026")

# Anti-replay ring buffer for consumed PoW challenges (stores challenge_id with expiry)
_CONSUMED_CHALLENGES: Dict[str, float] = {}


def _cleanup_consumed_challenges(now: float):
    expired = [cid for cid, exp in _CONSUMED_CHALLENGES.items() if exp < now]
    for cid in expired:
        _CONSUMED_CHALLENGES.pop(cid, None)


class PoWChallengeRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    difficulty: int = Field(default=4, ge=2, le=6, description="Leading zero hex nibbles required")


class PoWChallengeResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    challenge_id: str
    salt: str
    difficulty: int
    expires_at: float
    signature: str


class PoWVerifyRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    challenge_id: str
    salt: str
    nonce: str
    difficulty: int
    expires_at: float
    signature: str


class PoWVerifyResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    verified: bool
    reduced_risk_score: int
    detail: str


@router.get("/health", summary="Security Subsystem Health")
async def security_health():
    """Returns minimal sanitized liveness status without leaking internal telemetry."""
    return {
        "status": "HEALTHY",
        "service": "forenza-security-layer",
        "version": "2.0.0",
        "timestamp": int(time.time()),
    }


@router.get("/metrics", summary="Security Telemetry and Concurrency Metrics")
async def security_metrics(
    request: Request,
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
):
    """
    Returns active compute semaphores and telemetry metrics.
    Restricted to authorized administrators to prevent reconnaissance.
    """
    # Verify admin key
    if not x_admin_key or not hmac.compare_digest(x_admin_key.strip(), _ADMIN_KEY.strip()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative authorization required to access security telemetry metrics.",
        )

    guard = get_resource_guard()
    telemetry = guard.get_active_telemetry()
    return {
        "compute_semaphores": telemetry,
        "client_risk_score": getattr(request.state, "risk_score", 0),
        "client_risk_tier": getattr(request.state, "risk_tier", "NORMAL"),
        "correlation_id": getattr(request.state, "correlation_id", "none"),
        "timestamp": time.time(),
    }


@router.post("/pow-challenge", response_model=PoWChallengeResponse, summary="Generate Silent PoW Challenge")
async def create_pow_challenge(req: PoWChallengeRequest):
    """
    Generates a cryptographic Proof-of-Work challenge for high-risk traffic mitigation.
    Solved client-side via WebCrypto SHA-256 without user interaction.
    """
    challenge_id = f"pow_{secrets.token_hex(8)}"
    salt = secrets.token_hex(16)
    expires_at = time.time() + 180.0  # 3 minutes

    payload = f"{challenge_id}:{salt}:{req.difficulty}:{int(expires_at)}"
    sig = hmac.new(_POW_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    return PoWChallengeResponse(
        challenge_id=challenge_id,
        salt=salt,
        difficulty=req.difficulty,
        expires_at=expires_at,
        signature=sig,
    )


@router.post("/verify-pow", response_model=PoWVerifyResponse, summary="Verify Solved PoW Challenge")
async def verify_pow_challenge(req: PoWVerifyRequest, request: Request):
    """
    Constant-time O(1) PoW nonce verification with anti-replay protection.
    If valid, reduces client risk score.
    """
    now = time.time()
    _cleanup_consumed_challenges(now)

    # 1. Expiration check
    if now > req.expires_at:
        return PoWVerifyResponse(
            verified=False,
            reduced_risk_score=getattr(request.state, "risk_score", 70),
            detail="PoW challenge has expired. Request a new challenge.",
        )

    # 2. Anti-Replay check
    if req.challenge_id in _CONSUMED_CHALLENGES:
        return PoWVerifyResponse(
            verified=False,
            reduced_risk_score=getattr(request.state, "risk_score", 85),
            detail="PoW challenge has already been consumed (Anti-Replay violation).",
        )

    # 3. Constant-time O(1) HMAC signature verification
    expected_payload = f"{req.challenge_id}:{req.salt}:{req.difficulty}:{int(req.expires_at)}"
    expected_sig = hmac.new(_POW_SECRET, expected_payload.encode("utf-8"), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_sig, req.signature):
        return PoWVerifyResponse(
            verified=False,
            reduced_risk_score=getattr(request.state, "risk_score", 80),
            detail="Invalid challenge signature or tampered parameters.",
        )

    # 4. Hash difficulty check
    candidate = f"{req.salt}:{req.nonce}"
    digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
    target_prefix = "0" * req.difficulty

    if not digest.startswith(target_prefix):
        return PoWVerifyResponse(
            verified=False,
            reduced_risk_score=getattr(request.state, "risk_score", 60),
            detail=f"Invalid nonce. Hash {digest[:8]}... does not satisfy difficulty {req.difficulty}",
        )

    # 5. Mark challenge as consumed
    _CONSUMED_CHALLENGES[req.challenge_id] = req.expires_at

    # 6. Apply reputation recovery bonus in risk engine (-35 risk score)
    client_key = getattr(request.state, "client_key", None)
    if client_key:
        traffic_risk_engine.apply_pow_recovery_bonus(client_key)

    return PoWVerifyResponse(
        verified=True,
        reduced_risk_score=max(0, getattr(request.state, "risk_score", 30) - 35),
        detail="PoW challenge verified successfully. Client reputation restored.",
    )
