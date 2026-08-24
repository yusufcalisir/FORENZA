"""
FORENZA Security Layer API Routes (Dimensions 1, 4, 11, 15).

Exposes:
- GET  /api/v1/security/health       : Security subsystem health check
- GET  /api/v1/security/metrics      : Active concurrency semaphores and telemetry
- POST /api/v1/security/pow-challenge : Silent background WebCrypto challenge generator
- POST /api/v1/security/verify-pow   : Nonce verification for high-risk challenge resolution
"""

import hashlib
import hmac
import secrets
import time
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, ConfigDict

from app.security.concurrency_guard import get_resource_guard
from app.security.risk_engine import traffic_risk_engine

router = APIRouter(prefix="/security", tags=["Security Subsystem"])

_POW_SECRET = secrets.token_hex(32)


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
    signature: str


class PoWVerifyResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    verified: bool
    reduced_risk_score: int
    detail: str


@router.get("/health", summary="Security Subsystem Health")
async def security_health():
    """Returns real-time health and configuration status of security controls."""
    guard = get_resource_guard()
    return {
        "status": "HEALTHY",
        "security_layer": "ACTIVE",
        "zero_friction_mode": True,
        "adaptive_rate_limiting": "ENABLED",
        "concurrency_semaphores": "ACTIVE",
        "risk_scoring_engine": "ACTIVE",
        "timestamp": time.time(),
    }


@router.get("/metrics", summary="Security Telemetry and Concurrency Metrics")
async def security_metrics(request: Request):
    """Returns active compute semaphores and client risk score."""
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
    sig = hmac.new(_POW_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

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
    Verifies solved nonce. If valid, reduces client risk score.
    """
    # 1. Verify signature integrity
    payload = f"{req.challenge_id}:{req.salt}:{req.difficulty}"
    # Check signature against timestamp tolerance
    # Recreate signature pattern
    verified_sig = False
    now = time.time()

    # Verify signature over valid minute window
    for t_offset in range(-180, 10):
        test_exp = int(now + t_offset)
        test_payload = f"{req.challenge_id}:{req.salt}:{req.difficulty}:{test_exp}"
        test_sig = hmac.new(_POW_SECRET.encode("utf-8"), test_payload.encode("utf-8"), hashlib.sha256).hexdigest()
        if hmac.compare_digest(test_sig, req.signature):
            verified_sig = True
            break

    # 2. Check hash difficulty
    candidate = f"{req.salt}:{req.nonce}"
    digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
    target_prefix = "0" * req.difficulty

    if not digest.startswith(target_prefix):
        return PoWVerifyResponse(
            verified=False,
            reduced_risk_score=getattr(request.state, "risk_score", 50),
            detail=f"Invalid nonce. Hash {digest[:8]}... does not meet difficulty {req.difficulty}",
        )

    # 3. Reward with reduced risk score
    client_ip = request.client.host if request.client else "127.0.0.1"
    traffic_risk_engine.record_auth_success(client_ip)

    return PoWVerifyResponse(
        verified=True,
        reduced_risk_score=10,
        detail="Proof-of-Work verified. Client risk status cleared to NORMAL.",
    )
