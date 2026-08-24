"""
FORENZA Caching & DDoS Resilience Test Suite (Dimension 12).

Validates:
- Strict Private Data Cache Isolation (Zero Web Cache Deception)
- Public Forensic Reference Dataset Aggressive Caching (stale-while-revalidate)
- Strong ETag Generation & Conditional 304 Evaluation
- SingleFlight Request Coalescing (Thundering Herd / Cache Stampede Prevention)
"""

import asyncio
import pytest

from app.security.cache_shield import CacheShield


class TestCacheShield:
    def test_private_authenticated_endpoints_never_cached(self):
        """Kimlik doğrulanmış veya oturum içeren istekler KESİNLİKLE önbelleğe alınmamalıdır (no-store)."""
        shield = CacheShield()

        # Authenticated case endpoint
        headers_auth = shield.determine_cache_headers(
            path="/api/v1/cases/CASE-2026-001",
            method="GET",
            has_auth_header=True,
        )
        assert "no-store" in headers_auth["Cache-Control"]
        assert "private" in headers_auth["Cache-Control"]
        assert "Authorization" in headers_auth["Vary"]

        # Session cookie present
        headers_cookie = shield.determine_cache_headers(
            path="/api/v1/evidence/item-88",
            method="GET",
            has_session_cookie=True,
        )
        assert "no-store" in headers_cookie["Cache-Control"]

        # POST / mutation methods
        headers_post = shield.determine_cache_headers(
            path="/api/v1/mixture/execute",
            method="POST",
        )
        assert "no-store" in headers_post["Cache-Control"]

    def test_public_reference_matrix_aggressive_caching(self):
        """Kamuya açık adli referans veri setleri CDN düzeyinde agresif ve güvenli önbelleğe alınmalıdır."""
        shield = CacheShield()

        headers = shield.determine_cache_headers(
            path="/api/v1/forensic/population/matrices",
            method="GET",
            has_auth_header=False,
            has_session_cookie=False,
        )

        cc = headers["Cache-Control"]
        assert "public" in cc
        assert "max-age=3600" in cc
        assert "s-maxage=86400" in cc
        assert "stale-while-revalidate" in cc

    def test_etag_generation_and_matching(self):
        """ETag üretimi ve 304 Not Modified eşleşmesi doğrulanmalıdır."""
        shield = CacheShield()
        payload = b'{"locus": "TH01", "frequencies": [0.12, 0.34]}'

        etag = shield.generate_etag(payload)
        assert etag.startswith('"') and etag.endswith('"')

        # Matching ETag
        assert shield.is_matching_etag(etag, etag) is True
        assert shield.is_matching_etag(f'W/{etag}', etag) is True

        # Non-matching ETag
        assert shield.is_matching_etag('"different_hash"', etag) is False

    @pytest.mark.asyncio
    async def test_singleflight_request_coalescing_stampede_protection(self):
        """Aynı anda gelen 20 eşzamanlı istek için ağır hesaplama yalnızca 1 KEZ çalışmalı (Thundering Herd koruması)."""
        shield = CacheShield()
        execution_count = 0

        async def expensive_computation():
            nonlocal execution_count
            execution_count += 1
            await asyncio.sleep(0.05)  # Simulate expensive DB/compute
            return {"status": "computed", "data": [1, 2, 3]}

        # Spawn 20 concurrent requests for the exact same cache key
        cache_key = "ref:nist_1036_caucasian_matrix"
        tasks = [
            shield.coalesce_request(cache_key, expensive_computation)
            for _ in range(20)
        ]

        results = await asyncio.gather(*tasks)

        # Computation executed exactly once
        assert execution_count == 1

        # All 20 callers received the identical valid result
        assert len(results) == 20
        for res in results:
            assert res == {"status": "computed", "data": [1, 2, 3]}
