from unittest.mock import patch

from django.core.cache import cache
from django.db import OperationalError
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from apps.contacts.models import Contact
from core.client_ip import client_ip

VALID = {
    "name": "Visitor",
    "email": "visitor@example.com",
    "subject": "Hello",
    "message": "hello",
}


class ClientIpTests(SimpleTestCase):
    def request(self, peer, forwarded=None):
        extra = {"HTTP_X_FORWARDED_FOR": forwarded} if forwarded else {}
        return RequestFactory().get("/", REMOTE_ADDR=peer, **extra)

    def test_untrusted_peer_ignores_forwarded_header(self):
        with override_settings(TRUSTED_PROXIES=[]):
            self.assertEqual(
                client_ip(self.request("192.0.2.1", "203.0.113.9")), "192.0.2.1"
            )

    def test_unix_socket_proxy_uses_nearest_untrusted_hop(self):
        with override_settings(TRUSTED_PROXIES=[""]):
            self.assertEqual(
                client_ip(self.request("", "spoofed, 198.51.100.4, 203.0.113.9")),
                "203.0.113.9",
            )
            # A missing header falls back to the peer rather than inventing one.
            self.assertEqual(client_ip(self.request("")), "")


@override_settings(
    TRUSTED_PROXIES=[""],
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class ContactRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()

    def post(self, ip, data=VALID):
        return self.client.post(
            reverse("home:contact"), data, REMOTE_ADDR="", HTTP_X_FORWARDED_FOR=ip
        )

    def test_limit_is_per_visitor_behind_local_proxy(self):
        for _ in range(3):
            self.assertEqual(self.post("203.0.113.1").status_code, 302)
        self.assertContains(self.post("203.0.113.1"), "accept that message")
        # Another visitor behind the same proxy is unaffected.
        self.assertEqual(self.post("203.0.113.2").status_code, 302)
        self.assertEqual(Contact.objects.count(), 4)

    def test_invalid_submissions_do_not_use_the_budget(self):
        for _ in range(5):
            self.assertContains(
                self.post("203.0.113.3", {**VALID, "email": "invalid"}),
                "Enter a valid email address",
            )
        self.assertEqual(self.post("203.0.113.3").status_code, 302)

    def test_cache_failure_keeps_the_form_working(self):
        with (
            patch("apps.contacts.services.cache.add", side_effect=OperationalError),
            self.assertLogs("apps.contacts.services", "WARNING"),
        ):
            self.assertEqual(self.post("203.0.113.4").status_code, 302)
        self.assertEqual(Contact.objects.count(), 1)
