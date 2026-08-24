"""
FORENZA WAF Configuration & False-Positive Minimization Test Suite (Dimension 8).

Validates:
- Verified Search Engine & Spider Whitelisting (Zero friction for Googlebot/Bingbot)
- Critical Exploit Probe Blocking (.env, .git, etc/passwd)
- Remote Code Execution (RCE) Web Shell Detection
- Managed Challenge Action for Borderline Scripting
- Dynamic False-Positive Path Exception Registration
- WAF Telemetry Metrics & Continuous Tuning Statistics
"""

import pytest

from app.security.waf_tuner import WAFAction, WAFRuleEngine


class TestWAFConfiguration:
    def test_verified_search_engine_bot_whitelisting(self):
        """Googlebot ve Bingbot gibi doğrulanmış arama motoru örümcekleri kamu sayfalarında engellenmemeli."""
        engine = WAFRuleEngine()
        googlebot_ua = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

        res = engine.evaluate_request(
            path="/api/v1/forensic/population",
            method="GET",
            user_agent=googlebot_ua,
        )

        assert res.action == WAFAction.ALLOW
        assert res.is_whitelisted is True

    def test_critical_exploit_probe_blocked(self):
        """.env, .git veya /etc/passwd gibi hassas dosya taramaları kesinlikle BLOCK edilmeli."""
        engine = WAFRuleEngine()

        res_env = engine.evaluate_request(path="/.env", method="GET")
        assert res_env.action == WAFAction.BLOCK
        assert res_env.severity == "CRITICAL"
        assert res_env.matched_rule_id == "WAF_APP_01_PROBE_FILES"

        res_git = engine.evaluate_request(path="/.git/HEAD", method="GET")
        assert res_git.action == WAFAction.BLOCK

    def test_rce_web_shell_blocked(self):
        """Gövde içerisinde web shell ve eval kod çalıştırma desenleri BLOCK edilmeli."""
        engine = WAFRuleEngine()

        res_rce = engine.evaluate_request(
            path="/api/v1/forensic/upload",
            method="POST",
            body_text="<?php base64_decode('aGVsbG8='); passthru($_GET['cmd']); ?>",
        )
        assert res_rce.action == WAFAction.BLOCK
        assert res_rce.severity == "CRITICAL"
        assert res_rce.matched_rule_id == "WAF_APP_02_RCE_PATTERNS"

    def test_borderline_xss_triggers_managed_challenge(self):
        """Sınırda kalan şüpheli betik parametreleri meşru kullanıcıyı doğrudan engellemek yerine MANAGED_CHALLENGE tetiklemeli."""
        engine = WAFRuleEngine()

        res = engine.evaluate_request(
            path="/api/v1/forensic/search",
            method="GET",
            query_string="q=<script>alert(1)</script>",
        )
        assert res.action == WAFAction.MANAGED_CHALLENGE
        assert res.severity == "MEDIUM"

    def test_false_positive_tuning_and_exception_registration(self):
        """Yanlış alarm (false positive) bildirilen spesifik adli yollar kuraldan muaf tutulabilmeli."""
        engine = WAFRuleEngine()
        special_path = "/api/v1/forensic/search/scientific-query"

        # Initially triggers challenge on query
        res_initial = engine.evaluate_request(
            path=special_path,
            method="GET",
            query_string="q=<script>alert(1)</script>",
        )
        assert res_initial.action == WAFAction.MANAGED_CHALLENGE

        # Register false positive exception for this path
        engine.report_false_positive("WAF_APP_04_SUSPICIOUS_SCRIPT_TAGS", special_path)

        # Subsequent evaluation should be ALLOWed
        res_after = engine.evaluate_request(
            path=special_path,
            method="GET",
            query_string="q=<script>alert(1)</script>",
        )
        assert res_after.action == WAFAction.ALLOW

    def test_waf_telemetry_reporting(self):
        """WAF telemetrisi toplam istekleri, müdahaleleri ve false positive oranını doğru raporlamalı."""
        engine = WAFRuleEngine()

        engine.evaluate_request(path="/.env")
        engine.evaluate_request(path="/api/v1/forensic/population")
        engine.report_false_positive("WAF_APP_01_PROBE_FILES", "/test")

        telemetry = engine.get_waf_telemetry()
        assert telemetry["total_requests_evaluated"] == 2
        assert telemetry["total_waf_interventions"] >= 1
        assert telemetry["false_positive_reports"] == 1
        assert telemetry["false_positive_ratio"] > 0
