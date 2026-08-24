"""
FORENZA Unified Production Security Middleware (Dimensions 1, 2, 3, 4, 10, 12, 13, 14, 18).

Connects:
- Real Client IP Resolution (CF-Connecting-IP, X-Forwarded-For)
- Passive Traffic Risk Scoring (TrafficRiskEngine)
- Endpoint-Aware Token Bucket Rate Limiting (AdaptiveRateLimiter)
- Micro-Throttling & Silent Defense Execution
- Hardened Enterprise Security Headers & Cache Controls
- Structured ISO 27001 Security Logging (SecurityAuditLogger)
"""

import asyncio
import time
from typing import Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .audit_logger import security_logger
from .rate_limiter import adaptive_rate_limiter
from .risk_engine import RiskTier, traffic_risk_engine


class UnifiedSecurityMiddleware(BaseHTTPMiddleware):
    """
    Core defensive middleware operating with zero legitimate user friction.
    """

    PUBLIC_CACHE_PATHS = (
        "/api/v1/forensic/population",
        "/api/v1/forensic/mixture/models",
        "/api/v1/forensic/mixture/health",
        "/api/v1/security/health",
        "/openapi.json",
        "/docs",
    )

    def extract_client_ip(self, request: Request) -> str:
        """
        Extracts real client IP from Cloudflare or reverse proxy headers.
        """
        # 1. Cloudflare Connecting IP
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip and cf_ip.strip():
            return cf_ip.strip()

        # 2. X-Forwarded-For (leftmost client address)
        xff = request.headers.get("X-Forwarded-For")
        if xff and xff.strip():
            client_ip = xff.split(",")[0].strip()
            if client_ip:
                return client_ip

        # 3. Direct client host fallback
        if request.client and request.client.host:
            return request.client.host

        return "127.0.0.1"

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        correlation_id = request.headers.get("X-Correlation-ID") or security_logger.generate_correlation_id()
        request.state.correlation_id = correlation_id

        # 0. Allow CORS OPTIONS preflight without rate limit consumption
        if request.method == "OPTIONS":
            response = await call_next(request)
            self._apply_security_headers(response, request.url.path)
            response.headers["X-Correlation-ID"] = correlation_id
            return response

        client_ip = self.extract_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        session_id = request.cookies.get("forenza_session") or request.headers.get("X-Session-Token")
        path = request.url.path
        method = request.method

        # 1. Traffic Risk Assessment (Passive background scoring)
        risk = traffic_risk_engine.evaluate_request(
            ip=client_ip,
            path=path,
            method=method,
            user_agent=user_agent,
            session_id=session_id,
        )

        request.state.risk_score = risk.risk_score
        request.state.risk_tier = risk.risk_tier.value
        request.state.ip_hash = risk.ip_hash

        # 2. Check for Immediate Malicious Block (Tier 4: R >= 95)
        if risk.is_blocked:
            security_logger.log_event(
                event_type="TRAFFIC_BLOCKED_HIGH_RISK",
                path=path,
                method=method,
                ip_hash=risk.ip_hash,
                risk_score=risk.risk_score,
                risk_tier=risk.risk_tier.value,
                correlation_id=correlation_id,
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                details={"reasons": risk.reasons},
                duration_ms=(time.time() - start_time) * 1000,
            )
            resp = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Traffic anomaly detected. Temporary cooling period active.",
                    "correlation_id": correlation_id,
                },
                headers={"Retry-After": "60", "X-Correlation-ID": correlation_id},
            )
            self._apply_security_headers(resp, path)
            return resp

        # 3. Adaptive Rate Limiting Evaluation
        rl_res = adaptive_rate_limiter.check_rate_limit(
            client_key=risk.client_key,
            path=path,
            method=method,
        )

        if not rl_res.allowed:
            retry_seconds = rl_res.retry_after or 30
            security_logger.log_event(
                event_type="RATE_LIMIT_EXCEEDED",
                path=path,
                method=method,
                ip_hash=risk.ip_hash,
                risk_score=risk.risk_score,
                risk_tier=risk.risk_tier.value,
                correlation_id=correlation_id,
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                details={"category": rl_res.category.value, "limit": rl_res.limit},
                duration_ms=(time.time() - start_time) * 1000,
            )
            resp = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit quota reached for {rl_res.category.value}. Please retry in {retry_seconds}s.",
                    "correlation_id": correlation_id,
                    "retry_after_seconds": retry_seconds,
                },
                headers={
                    "Retry-After": str(retry_seconds),
                    "X-RateLimit-Limit": str(rl_res.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(rl_res.reset_seconds),
                    "X-Correlation-ID": correlation_id,
                },
            )
            self._apply_security_headers(resp, path)
            return resp

        # 4. Micro-Throttling Execution (Tier 2: 60 <= R < 80)
        if risk.delay_ms > 0:
            await asyncio.sleep(risk.delay_ms / 1000.0)

        # 5. Execute Downstream Handlers
        try:
            response = await call_next(request)
        except Exception as exc:
            traffic_risk_engine.record_error(client_ip, user_agent, session_id)
            security_logger.log_event(
                event_type="UNHANDLED_SERVER_EXCEPTION",
                path=path,
                method=method,
                ip_hash=risk.ip_hash,
                risk_score=risk.risk_score,
                risk_tier=risk.risk_tier.value,
                correlation_id=correlation_id,
                status_code=500,
                details={"error": str(exc)},
                duration_ms=(time.time() - start_time) * 1000,
            )
            raise exc

        # 6. Track 4xx/5xx Errors in Risk Engine
        if response.status_code >= 400:
            traffic_risk_engine.record_error(client_ip, user_agent, session_id)

        # 7. Apply Security, Rate-Limit and Telemetry Headers
        self._apply_security_headers(response, path)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-RateLimit-Limit"] = str(rl_res.limit)
        response.headers["X-RateLimit-Remaining"] = str(rl_res.remaining)
        response.headers["X-RateLimit-Reset"] = str(rl_res.reset_seconds)
        response.headers["X-Risk-Tier"] = risk.risk_tier.value

        # 8. Record Successful Audit Telemetry
        duration_ms = (time.time() - start_time) * 1000
        if risk.risk_score >= 30 or response.status_code >= 400:
            security_logger.log_event(
                event_type="HTTP_REQUEST_AUDIT",
                path=path,
                method=method,
                ip_hash=risk.ip_hash,
                risk_score=risk.risk_score,
                risk_tier=risk.risk_tier.value,
                correlation_id=correlation_id,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

        return response

    def _apply_security_headers(self, response: Response, path: str):
        """
        Applies hardened enterprise security and caching headers.
        """
        headers = response.headers
        headers["X-Content-Type-Options"] = "nosniff"
        headers["X-Frame-Options"] = "DENY"
        headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(self)"
        headers["X-XSS-Protection"] = "1; mode=block"

        # Caching header strategy (Dimension 12)
        if any(path.startswith(p) for p in self.PUBLIC_CACHE_PATHS):
            headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=86400"
        else:
            headers["Cache-Control"] = "no-store, max-age=0, private"
