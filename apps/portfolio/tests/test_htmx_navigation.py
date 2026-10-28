"""Exercise progressive navigation and contact submission in a real browser."""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.cache import cache
from playwright.sync_api import expect, sync_playwright

from apps.contacts.models import Contact


class HtmxNavigationTests(StaticLiveServerTestCase):
    def test_navigation_theme_contact_and_history(self):
        cache.clear()
        with sync_playwright() as playwright, playwright.chromium.launch() as browser:
            page = browser.new_page(viewport={"width": 390, "height": 844})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("https://fonts.googleapis.com/**", lambda route: route.abort())
            page.route("https://fonts.gstatic.com/**", lambda route: route.abort())
            page.goto(self.live_server_url)
            page.evaluate("window.navigationMarker = 'preserved'")
            page.locator(".menu-toggle").click()
            page.locator("#site-nav a").filter(has_text="Projects").click()
            expect(page).to_have_url(self.live_server_url + "/projects/")
            expect(page.locator("#project-search")).to_be_visible()
            self.assertEqual(page.evaluate("window.navigationMarker"), "preserved")
            self.assertEqual(
                page.locator('link[rel="canonical"]').get_attribute("href"),
                self.live_server_url + "/projects/",
            )
            page.locator(".menu-toggle").click()
            expect(page.locator(".menu-toggle")).to_have_attribute(
                "aria-expanded", "true"
            )
            page.keyboard.press("Escape")
            before = page.locator("html").get_attribute("data-theme")
            page.locator(".theme-toggle").click()
            self.assertNotEqual(
                page.locator("html").get_attribute("data-theme"), before
            )
            page.locator(".site-header .wordmark").click()
            expect(page.locator("#id_name")).to_be_attached()
            page.locator(".contact-form").evaluate("form => form.noValidate = true")
            page.locator("#id_name").fill("Keep my name")
            page.locator('.contact-form button[type="submit"]').click()
            expect(page.locator(".form-errors")).to_be_visible()
            expect(page.locator("#id_name")).to_have_value("Keep my name")
            page.locator("#id_name").fill("HTMX browser test")
            page.locator("#id_email").fill("htmx@example.com")
            page.locator("#id_subject").fill("Progressive contact")
            page.locator("#id_message").fill("Submitted without a document reload.")
            page.locator('.contact-form button[type="submit"]').click()
            expect(
                page.get_by_text("Your message was saved. Thank you!")
            ).to_be_visible()
            self.assertEqual(page.evaluate("window.navigationMarker"), "preserved")
            page.route("**/projects/", lambda route: route.abort())
            page.locator(".menu-toggle").click()
            page.locator("#site-nav a").filter(has_text="Projects").click()
            expect(page.locator("#navigation-status")).to_contain_text("request failed")
            expect(page.locator("#id_name")).to_be_attached()
            page.unroute("**/projects/")
            page.locator(".site-header .wordmark").click()
            expect(page.locator("#id_name")).to_have_value("")
            page.go_back()
            expect(page.locator("#main")).to_be_visible()
            self.assertEqual(errors, [])

        self.assertEqual(Contact.objects.filter(email="htmx@example.com").count(), 1)

    def test_site_remains_usable_without_javascript(self):
        with sync_playwright() as playwright, playwright.chromium.launch() as browser:
            page = browser.new_page(java_script_enabled=False)
            page.goto(self.live_server_url)
            page.locator("#site-nav a").filter(has_text="Projects").click()
            expect(page).to_have_url(self.live_server_url + "/projects/")
            expect(page.locator("#project-search")).to_be_visible()
