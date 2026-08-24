"""
FORENZA Caching, Request Coalescing & DDoS Resilience Engine (Dimension 12 & 18).

Implements:
- Strict Cache-Control Header Generation with Absolute Private Data Isolation (Anti-Web Cache Deception).
- Public Reference Dataset Aggressive Caching (stale-while-revalidate).
- Strong ETag & Conditional 304 Not Modified Handling.
- SingleFlight Request Coalescing (Anti-Thundering Herd / Cache Stampede Protection).
"""

import asyncio
import hashlib
import time
from typing import Any, Callable, Coroutine, Dict, Optional, Set, Tuple


class CacheShield:
    """
    Coordinates enterprise caching strategies and protects private data from accidental caching.
    """

    # Static / immutable forensic reference paths safe for aggressive CDN caching
    PUBLIC_CACHEABLE_PREFIXES = {
        "/api/v1/forensic/population/matrices",
        "/api/v1/forensic/snp/aims-reference",
        "/api/v1/forensic/mtdna/phylotree",
        "/api/v1/forensic/str/locus-registry",
        "/_next/static/",
        "/favicon.ico",
    }

    # Explicitly private prefixes that must NEVER be cached by CDN or shared proxies
    STRICT_PRIVATE_PREFIXES = {
        "/api/v1/auth/",
        "/api/v1/cases/",
        "/api/v1/evidence/",
        "/api/v1/mixture/execute",
        "/api/v1/zkp/prove",
        "/api/v1/session/",
    }

    def __init__(self):
        self._singleflight_locks: Dict[str, asyncio.Event] = {}
        self._singleflight_results: Dict[str, Any] = {}
        self._singleflight_in_progress: Set[str] = set()

    def determine_cache_headers(
        self,
        path: str,
        method: str = "GET",
        has_auth_header: bool = False,
        has_session_cookie: bool = False,
    ) -> Dict[str, str]:
        """
        Calculates secure Cache-Control and Vary headers based on path and authorization context.
        Guarantees zero private data caching.
        """
        # Any non-GET or authenticated/session request is STRICTLY private
        if method not in ("GET", "HEAD") or has_auth_header or has_session_cookie:
            return {
                "Cache-Control": "no-store, no-cache, must-revalidate, private",
                "Pragma": "no-cache",
                "Expires": "0",
                "Vary": "Authorization, Cookie, Accept-Encoding",
            }

        # Explicitly private endpoints
        if any(path.startswith(prefix) for prefix in self.STRICT_PRIVATE_PREFIXES):
            return {
                "Cache-Control": "no-store, no-cache, must-revalidate, private",
                "Pragma": "no-cache",
                "Expires": "0",
                "Vary": "Authorization, Cookie, Accept-Encoding",
            }

        # Safe public reference endpoints -> aggressive caching
        if any(path.startswith(prefix) for prefix in self.PUBLIC_CACHEABLE_PREFIXES):
            return {
                "Cache-Control": "public, max-age=3600, s-maxage=86400, stale-while-revalidate=604800",
                "Vary": "Accept-Encoding",
            }

        # Default standard public read endpoints -> short cache with revalidation
        return {
            "Cache-Control": "public, max-age=60, s-maxage=300, must-revalidate",
            "Vary": "Accept-Encoding",
        }

    def generate_etag(self, content_bytes: bytes) -> str:
        """Generates a strong SHA-256 ETag for response payload."""
        digest = hashlib.sha256(content_bytes).hexdigest()[:16]
        return f'"{digest}"'

    def is_matching_etag(self, client_etag: Optional[str], current_etag: str) -> bool:
        """Validates client If-None-Match header against current ETag."""
        if not client_etag:
            return False
        clean_client = client_etag.strip().strip("W/").strip('"')
        clean_current = current_etag.strip().strip("W/").strip('"')
        return clean_client == clean_current

    # ── Request Coalescing / SingleFlight Pattern ─────────────────────────
    async def coalesce_request(self, cache_key: str, compute_coroutine_fn: Callable[[], Coroutine[Any, Any, Any]]) -> Any:
        """
        Prevents cache stampedes (thundering herd problem).
        If 50 concurrent requests ask for the same cache_key, exactly 1 executes
        the computation and the other 49 await and share the single result.
        """
        if cache_key in self._singleflight_in_progress:
            # Another coroutine is already computing -> wait for the completion event
            event = self._singleflight_locks.get(cache_key)
            if event:
                await event.wait()
                return self._singleflight_results.get(cache_key)

        # First coroutine to arrive -> register lock event
        event = asyncio.Event()
        self._singleflight_locks[cache_key] = event
        self._singleflight_in_progress.add(cache_key)

        try:
            result = await compute_coroutine_fn()
            self._singleflight_results[cache_key] = result
            return result
        finally:
            event.set()
            self._singleflight_in_progress.discard(cache_key)
            self._singleflight_locks.pop(cache_key, None)


# Singleton instance
cache_shield = CacheShield()
