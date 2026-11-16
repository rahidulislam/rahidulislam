from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import OperationalError
from django.test import TestCase, override_settings
from django.urls import reverse

from core.login_throttle import ACCOUNT_FAILURE_LIMIT, ADDRESS_FAILURE_LIMIT

PASSWORD = "strong-test-password"


@override_settings(TRUSTED_PROXIES=[""])
class LoginThrottleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_superuser("owner", password=PASSWORD)

    def setUp(self):
        cache.clear()

    def attempt(self, url, password, ip="203.0.113.1", username="owner"):
        return self.client.post(
            url,
            {"username": username, "password": password},
            REMOTE_ADDR="",
            HTTP_X_FORWARDED_FOR=ip,
        )

    def test_dashboard_and_admin_lock_after_repeated_failures(self):
        for url in (reverse("dashboard:login"), reverse("admin:login")):
            with self.subTest(url=url):
                cache.clear()
                for _ in range(ACCOUNT_FAILURE_LIMIT):
                    self.assertEqual(self.attempt(url, "wrong").status_code, 200)
                # Even the right password is refused while the account is throttled.
                response = self.attempt(url, PASSWORD)
                self.assertContains(response, "Too many failed sign-in attempts")
                self.assertNotIn("_auth_user_id", self.client.session)
                # A different visitor behind the same proxy can still sign in.
                self.assertEqual(
                    self.attempt(url, PASSWORD, ip="203.0.113.2").status_code, 302
                )
                self.client.logout()

    def test_success_resets_the_account_counter(self):
        url = reverse("dashboard:login")
        for _ in range(ACCOUNT_FAILURE_LIMIT - 1):
            self.attempt(url, "wrong")
        self.assertEqual(self.attempt(url, PASSWORD).status_code, 302)
        self.client.logout()
        for _ in range(ACCOUNT_FAILURE_LIMIT - 1):
            self.attempt(url, "wrong")
        self.assertEqual(self.attempt(url, PASSWORD).status_code, 302)

    def test_address_limit_stops_spraying_many_usernames(self):
        url = reverse("dashboard:login")
        for number in range(ADDRESS_FAILURE_LIMIT):
            self.attempt(url, "wrong", username=f"guess{number}")
        self.assertContains(
            self.attempt(url, PASSWORD), "Too many failed sign-in attempts"
        )

    def test_cache_outage_does_not_block_sign_in(self):
        with (
            patch("core.login_throttle.cache.get", side_effect=OperationalError),
            patch("core.login_throttle.cache.delete", side_effect=OperationalError),
            self.assertLogs("core.login_throttle", "WARNING"),
        ):
            response = self.attempt(reverse("dashboard:login"), PASSWORD)
        self.assertEqual(response.status_code, 302)
