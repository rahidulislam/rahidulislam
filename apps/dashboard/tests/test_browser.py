"""Exercise complete owner workflows with the real static assets and CSRF."""

import re

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from apps.analytics.models import DailyPage, DailyTraffic, PageView
from apps.articles.models import Article
from apps.contacts.models import Contact
from apps.profiles.models import Skill


class DashboardBrowserTests(StaticLiveServerTestCase):
    def setUp(self):
        get_user_model().objects.create_superuser(
            "browser-owner", "owner@example.com", "browser-test-password"
        )
        self.message = Contact.objects.create(
            name="A visitor",
            email="browser@example.com",
            subject="A project enquiry",
            message="Let's talk about your Django work.",
        )

    def login(self, page):
        page.goto(self.live_server_url + reverse("dashboard:login"))
        page.get_by_label("Username").fill("browser-owner")
        page.get_by_label("Password").fill("browser-test-password")
        page.get_by_role("button", name="Sign in →").click()
        expect(page.get_by_role("heading", name="Overview", exact=True)).to_be_visible()

    def test_desktop_management_preview_errors_and_inbox(self):
        with sync_playwright() as playwright, playwright.chromium.launch() as browser:
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            self.login(page)
            page.screenshot(path="/tmp/portfolio-dashboard-desktop.png", full_page=True)
            page.evaluate("window.workspaceMarker = 'kept'")
            page.get_by_role("link", name="Skills", exact=True).click()
            expect(
                page.get_by_role("heading", name="Skills", exact=True).first
            ).to_be_visible()
            self.assertEqual(page.evaluate("window.workspaceMarker"), "kept")
            page.get_by_role("link", name="+ Add record").click()
            page.locator("form[data-editor]").evaluate("form => form.noValidate = true")
            page.get_by_label("Name:", exact=True).fill("Browser skill")
            page.get_by_label("Value:", exact=True).fill("101")
            page.get_by_role("button", name="Save changes").click()
            expect(page.get_by_role("alert")).to_contain_text("Please correct")
            expect(page.get_by_label("Name:", exact=True)).to_have_value(
                "Browser skill"
            )
            page.get_by_label("Value:", exact=True).fill("88")
            page.get_by_role("button", name="Save changes").click()
            expect(
                page.locator(".notice.success").filter(has_text="saved")
            ).to_be_visible()
            page.goto(
                self.live_server_url + reverse("dashboard:add", args=["articles"])
            )
            page.get_by_label("Title:", exact=True).fill("Unsaved article")
            page.get_by_label("Body:", exact=True).fill(
                "# Preview heading\n<script>bad()</script>"
            )
            page.get_by_role("button", name="Preview English Markdown").click()
            expect(page.locator("#markdown-preview h1")).to_have_text("Preview heading")
            expect(page.get_by_label("Title:", exact=True)).to_have_value(
                "Unsaved article"
            )
            page.once("dialog", lambda dialog: dialog.dismiss())
            page.get_by_role("link", name="Visitor analytics", exact=True).click()
            expect(page.get_by_label("Title:", exact=True)).to_have_value(
                "Unsaved article"
            )
            # Save the draft and then navigate without an unsaved-change prompt.
            page.get_by_label("Slug:", exact=True).fill("browser-unsaved-article")
            page.get_by_label("Topic:", exact=True).fill("Engineering")
            page.get_by_label("Summary:", exact=True).fill("Browser preview regression")
            page.get_by_role("button", name="Save changes").click()
            expect(
                page.locator(".notice.success").filter(has_text="saved")
            ).to_be_visible()
            page.get_by_role("link", name="Inbox", exact=True).click()
            page.get_by_role("link").filter(has_text="A project enquiry").click()
            page.get_by_role("button", name="Mark replied").click()
            expect(
                page.get_by_role("status").filter(has_text="marked replied")
            ).to_be_visible()
            self.assertEqual(errors, [])
        self.assertTrue(Skill.objects.filter(name="Browser skill", value=88).exists())
        self.assertTrue(
            Article.objects.filter(title="Unsaved article", is_published=False).exists()
        )
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, "replied")

    def test_mobile_navigation_analytics_and_keyboard(self):
        from django.utils import timezone

        DailyTraffic.objects.create(date=timezone.localdate(), views=12, visitors=5)
        with sync_playwright() as playwright, playwright.chromium.launch() as browser:
            page = browser.new_page(viewport={"width": 390, "height": 844})
            self.login(page)
            expect(page.locator("details.navigation")).not_to_have_attribute("open", "")
            page.get_by_text("Workspace navigation", exact=True).click()
            page.get_by_role("link", name="Visitor analytics", exact=True).click()
            expect(
                page.get_by_role("heading", name="Visitor analytics")
            ).to_be_visible()
            expect(
                page.get_by_text("Estimated visitor-days", exact=True)
            ).to_be_visible()
            self.assertLessEqual(
                page.evaluate("document.documentElement.scrollWidth"), 390
            )
            page.screenshot(path="/tmp/portfolio-dashboard-mobile.png", full_page=True)
            page.keyboard.press("Tab")
            self.assertTrue(page.evaluate("document.activeElement !== document.body"))
            page.get_by_label("Period").select_option("custom")
            page.get_by_role("button", name="Update report").click()
            expect(
                page.get_by_text("Choose both dates for a custom range.")
            ).to_be_visible()

    def test_no_javascript_management(self):
        with sync_playwright() as playwright, playwright.chromium.launch() as browser:
            page = browser.new_page(java_script_enabled=False)
            self.login(page)
            page.get_by_role("link", name="Skills", exact=True).click()
            page.get_by_role("link", name="+ Add record").click()
            page.get_by_label("Name:", exact=True).fill("Native skill")
            page.get_by_label("Value:", exact=True).fill("75")
            page.get_by_role("button", name="Save changes").click()
            expect(
                page.locator(".notice.success").filter(has_text="saved")
            ).to_be_visible()
        self.assertTrue(Skill.objects.filter(name="Native skill").exists())

    def test_public_htmx_does_not_double_count(self):
        with sync_playwright() as playwright, playwright.chromium.launch() as browser:
            page = browser.new_page(
                user_agent="Portfolio navigation regression",
                viewport={"width": 1280, "height": 900},
            )
            page.route("https://fonts.googleapis.com/**", lambda route: route.abort())
            page.route("https://fonts.gstatic.com/**", lambda route: route.abort())
            page.goto(self.live_server_url + reverse("home:articles"))
            expect(page.locator("#page-shell")).to_be_visible()
            page.locator("#site-nav a").filter(has_text="Projects").click()
            expect(page).to_have_url(self.live_server_url + reverse("home:projects"))
        self.assertEqual(PageView.objects.count(), 2)
        self.assertEqual(DailyTraffic.objects.get().visitors, 1)
        self.assertEqual(DailyPage.objects.get(path=reverse("home:projects")).views, 1)
        self.assertEqual(DailyPage.objects.get(path=reverse("home:articles")).views, 1)

    def test_branding_upload_and_htmx_icon_refresh(self):
        from tempfile import TemporaryDirectory

        from django.test import override_settings

        from apps.portfolio.tests.test_branding import image_upload

        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            with (
                sync_playwright() as playwright,
                playwright.chromium.launch() as browser,
            ):
                owner = browser.new_page(viewport={"width": 1440, "height": 1000})
                visitor = browser.new_page(viewport={"width": 390, "height": 844})
                for page in (owner, visitor):
                    page.route(
                        "https://fonts.googleapis.com/**", lambda route: route.abort()
                    )
                    page.route(
                        "https://fonts.gstatic.com/**", lambda route: route.abort()
                    )
                visitor.goto(self.live_server_url + reverse("home:articles"))
                expect(visitor.locator('link[rel="icon"]')).to_have_attribute(
                    "href", "/static/img/favicon.svg?v=20261029"
                )
                self.login(owner)
                owner.goto(
                    self.live_server_url
                    + reverse("dashboard:add", args=["site-branding"])
                )
                owner.get_by_label("Brand name:", exact=True).fill("Readable brand")
                for field, name, size in [
                    ("logo", "logo.png", (120, 40)),
                    ("logo_dark", "dark.png", (120, 40)),
                    ("site_icon", "icon.png", (64, 64)),
                ]:
                    upload = image_upload(name, size)
                    owner.locator(f"#id_{field}").set_input_files(
                        {"name": name, "mimeType": "image/png", "buffer": upload.read()}
                    )
                owner.get_by_role("button", name="Save changes").click()
                expect(owner.locator(".notice.success")).to_contain_text("saved")
                visitor.locator(".menu-toggle").click()
                visitor.locator("#site-nav a").filter(has_text="Projects").click()
                expect(visitor.locator('link[rel="icon"]')).to_have_attribute(
                    "href",
                    re.compile(r"/media/branding/icons/icon.*\.png\?v="),
                )
                expect(
                    visitor.locator(".site-footer .brand-logo-light")
                ).to_be_visible()
                expect(
                    visitor.locator(".site-footer .brand-logo-light")
                ).to_have_attribute("alt", "Readable brand")
                visitor.locator("html").evaluate(
                    "element => element.dataset.theme = 'dark'"
                )
                expect(visitor.locator(".site-footer .brand-logo-dark")).to_be_visible()
                expect(
                    visitor.locator(".site-footer .brand-logo-light")
                ).not_to_be_visible()
                self.assertLessEqual(
                    visitor.evaluate("document.documentElement.scrollWidth"), 390
                )
