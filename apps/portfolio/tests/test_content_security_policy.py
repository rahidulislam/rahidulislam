"""The enforced CSP must not block anything the site itself serves."""

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from playwright.sync_api import sync_playwright

PUBLIC_PATHS = (
    "/",
    "/projects/",
    "/articles/",
    "/experience/",
    "/privacy/",
    "/work/talentbridge/",
    "/articles/django-contact-storage-before-email/",
)
OWNER_PATHS = (
    "/dashboard/",
    "/dashboard/analytics/",
    "/dashboard/inbox/",
    "/admin/",
    "/admin/auth/user/",
    "/admin/articles/article/add/",
)


class PolicyHeaderTests(TestCase):
    def test_html_responses_send_a_nonce_based_policy(self):
        response = self.client.get("/")
        policy = response["Content-Security-Policy"]
        for directive in (
            "default-src 'self'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "base-uri 'none'",
        ):
            self.assertIn(directive, policy)
        nonce = policy.split("'nonce-")[1].split("'")[0]
        self.assertContains(response, f'nonce="{nonce}"', count=2)
        self.assertContains(response, f'"inlineStyleNonce":"{nonce}"')
        self.assertNotIn("unsafe-inline", policy.split("style-src-attr")[0])


class PolicyBrowserTests(StaticLiveServerTestCase):
    def test_pages_render_without_policy_violations(self):
        get_user_model().objects.create_superuser("csp-owner", password="csp-pass-1")
        with sync_playwright() as playwright, playwright.chromium.launch() as browser:
            page = browser.new_page()
            violations = []
            page.on(
                "console",
                lambda message: (
                    violations.append(f"{page.url}: {message.text}")
                    if "Content Security Policy" in message.text
                    else None
                ),
            )
            for path in PUBLIC_PATHS:
                page.goto(self.live_server_url + path)
            # Boosted navigation swaps content through htmx.
            page.goto(self.live_server_url + "/")
            page.locator(".site-header .wordmark").click()
            page.goto(self.live_server_url + "/dashboard/login/")
            page.get_by_label("Username").fill("csp-owner")
            page.get_by_label("Password").fill("csp-pass-1")
            page.get_by_role("button", name="Sign in").click()
            page.wait_for_url("**/dashboard/")
            for path in OWNER_PATHS:
                page.goto(self.live_server_url + path)
            self.assertEqual(violations, [])
