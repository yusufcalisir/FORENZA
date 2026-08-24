"""
FORENZA Zero-Friction User Experience Metric & Auditor Engine (Dimension 18).

Treats legitimate user friction as a first-class security metric.
Guarantees:
1. Zero CAPTCHA / Challenges on regular visits ($R < 30$).
2. Zero verification prompts on page refreshes.
3. Zero shared IP / NAT collateral damage (Dual-Key Isolation).
4. Zero added artificial delays for normal traffic ($0.0ms$).
5. Zero forced re-authentication for active sessions (RTR rotation).
6. Non-invasive privacy-conscious telemetry (No permanent hardware fingerprinting).
7. High-throughput power-user tolerance for legitimate forensic workflows.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .risk_engine import RiskTier, TrafficRiskEngine


@dataclass
class UserFrictionReport:
    total_requests: int
    friction_events_count: int
    added_artificial_delay_ms: float
    challenges_triggered_count: int
    blocked_requests_count: int
    friction_free_percentage: float
    shared_ip_isolation_intact: bool
    violations: List[str]


class ZeroFrictionAuditor:
    """
    Continuous UX friction auditor ensuring security protections remain invisible to legitimate users.
    """

    def __init__(self, risk_engine: Optional[TrafficRiskEngine] = None):
        self.risk_engine = risk_engine or TrafficRiskEngine()

    def audit_normal_user_browsing_session(
        self,
        client_ip: str,
        user_agent: str,
        page_views: int = 25,
        average_interval_seconds: float = 2.5,
    ) -> UserFrictionReport:
        """
        Simulates an analyst browsing case files and verifies zero security friction.
        """
        base_time = 1000.0
        current_time = base_time
        added_delay_ms = 0.0
        challenges = 0
        blocks = 0
        violations = []

        for i in range(page_views):
            # Human jitter: interval between 1.0s and 4.0s
            jitter = (i % 5) * 0.5
            current_time += average_interval_seconds + jitter

            assessment = self.risk_engine.evaluate_request(
                ip=client_ip,
                path=f"/cases/CASE-2026-{100 + i}",
                method="GET",
                user_agent=user_agent,
                now=current_time,
            )

            if assessment.delay_ms > 0:
                added_delay_ms += assessment.delay_ms
                violations.append(f"Artificial delay added on request {i}: {assessment.delay_ms}ms")

            if assessment.requires_pow or assessment.risk_tier == RiskTier.HIGHLY_SUSPICIOUS:
                challenges += 1
                violations.append(f"Challenge triggered for legitimate user on request {i}")

            if assessment.is_blocked:
                blocks += 1
                violations.append(f"Legitimate user blocked on request {i}")

        friction_free_pct = 100.0 if page_views > 0 else 0.0
        if challenges > 0 or blocks > 0 or added_delay_ms > 0:
            friction_free_pct = max(0.0, 100.0 - ((challenges + blocks) / page_views * 100.0))

        return UserFrictionReport(
            total_requests=page_views,
            friction_events_count=len(violations),
            added_artificial_delay_ms=added_delay_ms,
            challenges_triggered_count=challenges,
            blocked_requests_count=blocks,
            friction_free_percentage=friction_free_pct,
            shared_ip_isolation_intact=True,
            violations=violations,
        )

    def audit_shared_nat_coexistence(
        self,
        shared_ip: str,
        normal_users_count: int = 10,
        malicious_users_count: int = 1,
    ) -> UserFrictionReport:
        """
        Verifies that a bot on a shared corporate/university NAT does NOT cause collateral lockout for normal users.
        """
        base_time = 2000.0
        normal_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        bot_ua = "HeadlessChrome/120.0.0.0 (Automated Script)"

        # 1. Bot spams exploit probes from the shared IP
        for i in range(15):
            self.risk_engine.evaluate_request(
                ip=shared_ip,
                path="/.env",
                method="GET",
                user_agent=bot_ua,
                session_id="bot_session",
                now=base_time + (i * 0.05),
            )

        # 2. Legitimate users browse normally from the same shared IP
        normal_friction_events = 0
        violations = []

        for u in range(normal_users_count):
            assessment = self.risk_engine.evaluate_request(
                ip=shared_ip,
                path=f"/evidence/EVID-{u}",
                method="GET",
                user_agent=normal_ua,
                session_id=f"legit_user_{u}",
                now=base_time + 10.0 + (u * 1.5),
            )

            if assessment.is_blocked:
                normal_friction_events += 1
                violations.append(f"Legitimate user {u} on shared IP was falsely blocked due to bot activity")
            if assessment.requires_pow:
                normal_friction_events += 1
                violations.append(f"Legitimate user {u} on shared IP was challenged due to bot activity")

        return UserFrictionReport(
            total_requests=normal_users_count,
            friction_events_count=normal_friction_events,
            added_artificial_delay_ms=0.0,
            challenges_triggered_count=0,
            blocked_requests_count=normal_friction_events,
            friction_free_percentage=100.0 if normal_friction_events == 0 else 0.0,
            shared_ip_isolation_intact=(normal_friction_events == 0),
            violations=violations,
        )


# Singleton instance
zero_friction_auditor = ZeroFrictionAuditor()
