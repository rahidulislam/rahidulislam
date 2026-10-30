from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import DatabaseError, IntegrityError, transaction
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import DailyPage, DailyReferrer, DailyTraffic, DailyVisitor, PageView
from .selectors import traffic_report
from .services import purge_details, record_navigation, referrer_domain, visitor_key


class AnalyticsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.today = timezone.localdate()

    def request(self, **kwargs):
        return self.factory.get(
            "/articles/", REMOTE_ADDR="192.0.2.10", HTTP_USER_AGENT="Browser", **kwargs
        )

    def test_cookie_free_navigation_counts_daily_uniques_and_safe_referrer(self):
        for _ in range(2):
            record_navigation(
                self.request(HTTP_REFERER="https://example.org/private?token=secret")
            )
        day = DailyTraffic.objects.get(date=self.today)
        self.assertEqual((day.views, day.visitors), (2, 1))
        self.assertEqual(DailyVisitor.objects.count(), 1)
        self.assertEqual(DailyPage.objects.get().views, 2)
        self.assertEqual(DailyReferrer.objects.get().domain, "example.org")
        self.assertEqual(
            PageView.objects.get(pk=PageView.objects.first().pk).referrer, "example.org"
        )
        payload = str(list(PageView.objects.values())) + str(
            list(DailyVisitor.objects.values())
        )
        for secret in ["192.0.2.10", "Browser", "token=secret", "/private"]:
            self.assertNotIn(secret, payload)
        self.assertEqual(len(DailyVisitor.objects.get().key), 64)

    def test_rotating_key_and_untrusted_proxy(self):
        request = self.request(HTTP_X_FORWARDED_FOR="203.0.113.5")
        self.assertEqual(
            visitor_key(request, "2026-01-01"),
            visitor_key(self.request(), "2026-01-01"),
        )
        self.assertNotEqual(
            visitor_key(request, "2026-01-01"), visitor_key(request, "2026-01-02")
        )
        with override_settings(ANALYTICS_TRUSTED_PROXIES=["192.0.2.10"]):
            self.assertNotEqual(
                visitor_key(request, "2026-01-01"),
                visitor_key(self.request(), "2026-01-01"),
            )
            # Stop at the nearest untrusted hop, not a spoofed leftmost address.
            request.META["HTTP_X_FORWARDED_FOR"] = "spoofed, 203.0.113.5"
            key = visitor_key(request, "2026-01-01")
            request.META["HTTP_X_FORWARDED_FOR"] = "another-spoof, 203.0.113.5"
            self.assertEqual(key, visitor_key(request, "2026-01-01"))

    def test_referrer_validation(self):
        for value in [
            "javascript:alert(1)",
            "https://[invalid",
            "https://testserver/private",
            "",
        ]:
            with self.subTest(value=value):
                self.assertEqual(referrer_domain(self.request(HTTP_REFERER=value)), "")

    def test_uniqueness_constraint(self):
        DailyVisitor.objects.create(date=self.today, key="same")
        with self.assertRaises(IntegrityError), transaction.atomic():
            DailyVisitor.objects.create(date=self.today, key="same")

    def test_event_and_aggregates_rollback_together(self):
        with (
            patch(
                "apps.analytics.services.PageView.objects.create",
                side_effect=DatabaseError("failed"),
            ),
            self.assertRaises(DatabaseError),
        ):
            record_navigation(self.request())
        self.assertFalse(DailyTraffic.objects.exists())
        self.assertFalse(DailyVisitor.objects.exists())
        self.assertFalse(DailyPage.objects.exists())

    def test_public_and_htmx_navigation_once_without_response_cookies(self):
        response = self.client.get(reverse("home:articles"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("analytics", str(response.cookies))
        self.client.get(
            reverse("home:articles"), HTTP_HX_REQUEST="true", HTTP_HX_BOOSTED="true"
        )
        self.assertEqual(DailyTraffic.objects.get().views, 2)
        self.client.get(reverse("home:articles"), HTTP_HX_REQUEST="true")
        self.assertEqual(DailyTraffic.objects.get().views, 2)

    def test_excluded_requests(self):
        url = reverse("home:articles")
        for path, options in [
            (url, {"HTTP_USER_AGENT": "Googlebot"}),
            (url + "?preview=1", {}),
            ("/admin/login/", {}),
            ("/dashboard/login/", {}),
            ("/missing-page/", {}),
            ("/sitemap.xml", {}),
        ]:
            self.client.get(path, **options)
        self.client.head(url)
        owner = get_user_model().objects.create_superuser(
            "owner", "owner@example.com", "test-password"
        )
        self.client.force_login(owner)
        self.client.get(url)
        self.assertFalse(DailyTraffic.objects.exists())

    def test_tracking_failure_does_not_fail_page_or_log_event_parameters(self):
        with (
            patch(
                "apps.analytics.middleware.record_navigation",
                side_effect=DatabaseError("secret-ip"),
            ),
            self.assertLogs("apps.analytics.middleware", level="WARNING") as logs,
        ):
            response = self.client.get(reverse("home:articles"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("secret-ip", str(logs.output))

    def test_retention_boundary_keeps_aggregates(self):
        record_navigation(self.request())
        cutoff = self.today - timedelta(days=90)
        old = PageView.objects.create(path="/old/")
        PageView.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=91)
        )
        DailyVisitor.objects.create(date=cutoff - timedelta(days=1), key="old")
        DailyVisitor.objects.create(date=cutoff, key="boundary")
        self.assertEqual(purge_details(), (1, 1))
        self.assertTrue(DailyVisitor.objects.filter(key="boundary").exists())
        self.assertEqual(DailyTraffic.objects.get().views, 1)
        call_command("purge_analytics", verbosity=0)
        self.assertEqual(PageView.objects.count(), 1)

    def test_report_no_data_historical_and_missing_days(self):
        self.assertFalse(traffic_report(start=self.today, end=self.today)["has_data"])
        DailyTraffic.objects.create(
            date=self.today - timedelta(days=2), views=3, visitors=2
        )
        report = traffic_report(start=self.today - timedelta(days=3), end=self.today)
        self.assertEqual([day["views"] for day in report["days"]], [3, 0, 0])
        self.assertEqual(report["visitor_days"], 2)
        self.assertFalse(
            traffic_report(
                start=self.today - timedelta(days=10),
                end=self.today - timedelta(days=3),
            )["has_data"]
        )
