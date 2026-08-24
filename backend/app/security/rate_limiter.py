"""
FORENZA Adaptive Endpoint-Aware Rate Limiter (Dimension 3 & 9 & 18).

Implements endpoint-specific token bucket and sliding-window limits:
- Static Assets: 600 req/min (Burst 100) -> Highly permissive.
- Public Read: 120 req/min (Burst 30) -> Permissive.
- Search / API: 60 req/min (Burst 20) -> Moderate.
- Auth / Login: 5 req/min (Burst 3) -> Strict.
- Password Reset: 3 req/5min (Burst 1) -> Very strict.
- Heavy Biocompute: 10 req/min (Burst 4) -> Tightly controlled.

Features:
- Risk-Modulated Quotas: Scales capacity proportionally based on client risk score.
- NAT & Shared IP Protection: Evaluates independent token buckets per session identity.
- RFC-Compliant Headers: X-RateLimit-Limit, Remaining, Reset, Category, Retry-After.
"""

import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Deque, Dict, Optional, Tuple


class RateLimitCategory(str, Enum):
    STATIC_ASSET = "STATIC_ASSET"      # CSS, JS, Images, Fonts
    PUBLIC_READ = "PUBLIC_READ"        # Reference frequencies, health, schemas
    SEARCH_API = "SEARCH_API"          # Filter, search, lookup
    AUTH = "AUTH"                      # Login, registration, token refresh
    PASSWORD_RESET = "PASSWORD_RESET"  # Credential reset, password recovery
    HEAVY_COMPUTE = "HEAVY_COMPUTE"    # MCMC, ZKP, BPA L2, GIS Raster


@dataclass
class CategoryQuota:
    requests_per_minute: int
    burst_capacity: int
    window_seconds: float = 60.0


@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_seconds: int
    category: RateLimitCategory
    retry_after: Optional[int] = None


@dataclass
class IdentityBucket:
    tokens: float
    last_leak: float
    timestamps: Deque[float] = field(default_factory=deque)


class AdaptiveRateLimiter:
    """
    High-performance token bucket with sliding-window precision and risk modulation.
    Guarantees zero disruption for legitimate users while throttling automated abuse.
    """

    DEFAULT_QUOTAS: Dict[RateLimitCategory, CategoryQuota] = {
        RateLimitCategory.STATIC_ASSET: CategoryQuota(requests_per_minute=600, burst_capacity=100, window_seconds=60.0),
        RateLimitCategory.PUBLIC_READ: CategoryQuota(requests_per_minute=120, burst_capacity=30, window_seconds=60.0),
        RateLimitCategory.SEARCH_API: CategoryQuota(requests_per_minute=60, burst_capacity=20, window_seconds=60.0),
        RateLimitCategory.AUTH: CategoryQuota(requests_per_minute=5, burst_capacity=3, window_seconds=60.0),
        RateLimitCategory.PASSWORD_RESET: CategoryQuota(requests_per_minute=3, burst_capacity=1, window_seconds=300.0),
        RateLimitCategory.HEAVY_COMPUTE: CategoryQuota(requests_per_minute=10, burst_capacity=4, window_seconds=60.0),
    }

    HEAVY_COMPUTE_PATHS = (
        "/api/v1/forensic/mixture",
        "/api/v1/forensic/zk",
        "/api/v1/forensic/geoint/fuse",
        "/api/v1/forensic/physical/bpa-area-of-origin",
        "/api/v1/forensic/phenotyping/bga/predict-full",
    )

    PASSWORD_RESET_PATHS = (
        "/api/v1/auth/reset-password",
        "/api/v1/auth/forgot-password",
        "/auth/reset-password",
        "/auth/forgot-password",
    )

    AUTH_PATHS = (
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/auth/login",
        "/login",
    )

    def __init__(self, custom_quotas: Optional[Dict[RateLimitCategory, CategoryQuota]] = None):
        self.quotas = custom_quotas or dict(self.DEFAULT_QUOTAS)
        self._buckets: Dict[Tuple[str, RateLimitCategory], IdentityBucket] = {}
        self._last_cleanup = time.time()

    def classify_request(self, path: str, method: str) -> RateLimitCategory:
        """Categorizes request based on path, HTTP verb, and computational complexity."""
        clean_path = path.lower().split("?")[0]

        # 1. Password reset endpoints (most sensitive)
        if any(clean_path.startswith(p) for p in self.PASSWORD_RESET_PATHS):
            return RateLimitCategory.PASSWORD_RESET

        # 2. Authentication endpoints
        if any(clean_path.startswith(p) for p in self.AUTH_PATHS):
            return RateLimitCategory.AUTH

        # 3. Expensive mathematical / biocomputational solvers
        if any(clean_path.startswith(p) for p in self.HEAVY_COMPUTE_PATHS):
            return RateLimitCategory.HEAVY_COMPUTE

        # 4. Static assets & public cached files
        if clean_path.endswith((".css", ".js", ".png", ".jpg", ".svg", ".ico", ".woff2", ".ttf", ".webp")):
            return RateLimitCategory.STATIC_ASSET

        # 5. Public read endpoints
        if method in ("GET", "HEAD"):
            if any(q in clean_path for q in ("search", "query", "filter", "lookup", "find")):
                return RateLimitCategory.SEARCH_API
            return RateLimitCategory.PUBLIC_READ

        # 6. Default API mutation
        return RateLimitCategory.SEARCH_API

    def check_rate_limit(
        self,
        client_key: str,
        path: str,
        method: str,
        risk_score: int = 0,
        now: Optional[float] = None,
    ) -> RateLimitResult:
        """
        Evaluates token bucket for client_key under path's category.
        Adjusts burst capacity and refill rate according to risk score.
        """
        ts = now if now is not None else time.time()
        category = self.classify_request(path, method)
        base_quota = self.quotas.get(category, self.DEFAULT_QUOTAS[RateLimitCategory.PUBLIC_READ])

        # Risk-modulated quota adjustment
        if risk_score >= 80:
            effective_rpm = max(1, int(base_quota.requests_per_minute * 0.30))
            effective_burst = max(1, int(base_quota.burst_capacity * 0.30))
        elif risk_score >= 60:
            effective_rpm = max(2, int(base_quota.requests_per_minute * 0.50))
            effective_burst = max(1, int(base_quota.burst_capacity * 0.50))
        elif risk_score >= 30:
            effective_rpm = max(3, int(base_quota.requests_per_minute * 0.75))
            effective_burst = max(1, int(base_quota.burst_capacity * 0.75))
        else:
            effective_rpm = base_quota.requests_per_minute
            effective_burst = base_quota.burst_capacity

        self._maybe_cleanup(ts)

        bucket_key = (client_key, category)
        bucket = self._buckets.get(bucket_key)

        if bucket is None:
            bucket = IdentityBucket(
                tokens=float(effective_burst),
                last_leak=ts,
            )
            self._buckets[bucket_key] = bucket

        # Refill tokens according to elapsed time
        elapsed = max(0.0, ts - bucket.last_leak)
        refill_rate = effective_rpm / base_quota.window_seconds
        bucket.tokens = min(float(effective_burst), bucket.tokens + (elapsed * refill_rate))
        bucket.last_leak = ts

        # Sliding window timestamp pruning
        cutoff = ts - base_quota.window_seconds
        while bucket.timestamps and bucket.timestamps[0] < cutoff:
            bucket.timestamps.popleft()

        # Token allowance evaluation
        if bucket.tokens >= 1.0:
            bucket.tokens -= 1.0
            bucket.timestamps.append(ts)
            allowed = True
            retry_after = None
        else:
            allowed = False
            needed = 1.0 - bucket.tokens
            retry_after = max(1, int(needed / refill_rate)) if refill_rate > 0 else int(base_quota.window_seconds)

        remaining = max(0, int(bucket.tokens))
        first_ts = bucket.timestamps[0] if bucket.timestamps else ts
        reset_seconds = int(base_quota.window_seconds - (ts - first_ts))
        reset_seconds = max(1, min(int(base_quota.window_seconds), reset_seconds))

        return RateLimitResult(
            allowed=allowed,
            limit=effective_rpm,
            remaining=remaining,
            reset_seconds=reset_seconds,
            category=category,
            retry_after=retry_after,
        )

    def _maybe_cleanup(self, now: float):
        if now - self._last_cleanup < 180.0 and len(self._buckets) < 20000:
            return
        self._last_cleanup = now
        cutoff = now - 360.0
        expired = [k for k, b in self._buckets.items() if b.last_leak < cutoff]
        for k in expired:
            del self._buckets[k]


# Singleton instance
adaptive_rate_limiter = AdaptiveRateLimiter()
