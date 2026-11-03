"""Footer contact actions retain native destinations and accessible tooltips."""

import os
from pathlib import Path

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import expect, sync_playwright

from apps.contacts.models import PublicContact


class FooterContactTests(StaticLiveServerTestCase):
    def test_contact_buttons_tooltips_and_navigation(self):
        contact, _ = PublicContact.objects.get_or_create(pk=1)
        contact.email = "portfolio-contact@example.com"
        contact.phone = "+49123456789"
        contact.whatsapp = "+49123456789"
        contact.telegram = "portfolio_contact"
        contact.linkedin = "https://www.linkedin.com/in/portfolio-contact/"
        contact.github = "https://github.com/portfolio-contact"
        contact.save()
        with sync_playwright() as playwright, playwright.chromium.launch() as browser:
            page = browser.new_page()
            page.route("https://fonts.googleapis.com/**", lambda route: route.abort())
            page.route("https://fonts.gstatic.com/**", lambda route: route.abort())
            page.goto(self.live_server_url)
            footer = page.locator(".site-footer")
            expect(footer.locator(".footer-contact-action")).to_have_count(6)
            for kind, destination in (
                ("email", "mailto:portfolio-contact@example.com"),
                ("phone", "tel:+49123456789"),
                ("whatsapp", "https://wa.me/49123456789"),
                ("telegram", "https://t.me/portfolio_contact"),
                ("linkedin", contact.linkedin),
                ("github", contact.github),
            ):
                link = footer.locator(f'[aria-describedby="footer-contact-{kind}"]')
                expect(link).to_have_attribute("href", destination)
                expect(link).to_have_attribute("hx-boost", "false")
                if kind not in ("email", "phone"):
                    expect(link).to_have_attribute("target", "_blank")
                    expect(link).to_have_attribute("rel", "noopener noreferrer")
            email = footer.get_by_role("link", name="Email", exact=True)
            tooltip = page.locator("#footer-contact-email")
            email.scroll_into_view_if_needed()
            page.mouse.move(0, 0)
            expect(tooltip).not_to_be_visible()
            email.hover()
            expect(tooltip).to_be_visible()
            tooltip.hover()
            expect(tooltip).to_be_visible()
            page.keyboard.press("Escape")
            expect(tooltip).not_to_be_visible()
            page.mouse.move(0, 0)
            email.focus()
            expect(tooltip).to_be_visible()
            page.keyboard.press("Escape")
            expect(tooltip).not_to_be_visible()
            expect(email).to_be_focused()

            for width in (320, 390, 768, 1440):
                page.set_viewport_size({"width": width, "height": 900})
                for theme in ("light", "dark"):
                    page.locator("html").evaluate(
                        "(root, theme) => root.dataset.theme = theme", theme
                    )
                    email.blur()
                    email.focus()
                    expect(tooltip).to_be_visible()
                    box = tooltip.bounding_box()
                    self.assertGreaterEqual(box["x"], 0)
                    self.assertLessEqual(box["x"] + box["width"], width)
                    self.assertGreaterEqual(email.bounding_box()["height"], 44)
                    self.assertLessEqual(
                        page.evaluate("document.documentElement.scrollWidth"), width
                    )
                    if os.environ.get("CONTACT_SCREENSHOT_DIR"):
                        output = Path(os.environ["CONTACT_SCREENSHOT_DIR"])
                        output.mkdir(parents=True, exist_ok=True)
                        footer.screenshot(
                            path=str(output / f"footer-{theme}-{width}.png")
                        )

            footer.get_by_role("link", name="Projects", exact=True).click()
            page.wait_for_url("**/projects/")
            expect(
                page.get_by_role("heading", name="Projects.", exact=True)
            ).to_be_visible()
            page.wait_for_function(
                "!document.querySelector('.htmx-settling, .htmx-swapping, .htmx-request')"
            )
            page.keyboard.press("Tab")
            email = page.locator(".site-footer").get_by_role(
                "link", name="Email", exact=True
            )
            email.focus()
            expect(page.locator("#footer-contact-email")).to_be_visible()
            page.keyboard.press("Escape")
            expect(page.locator("#footer-contact-email")).not_to_be_visible()
            page.get_by_role("button", name="বাংলা ব্যবহার করুন").click()
            expect(
                page.locator(".site-footer").get_by_role(
                    "link", name="কল করুন", exact=True
                )
            ).to_be_visible()

    def test_missing_contacts_do_not_render_empty_actions(self):
        contact, _ = PublicContact.objects.get_or_create(pk=1)
        contact.email = contact.phone = contact.whatsapp = contact.telegram = ""
        contact.linkedin = contact.github = ""
        contact.save()
        response = self.client.get("/")
        self.assertNotContains(response, 'class="footer-contact-action"')
        self.assertNotContains(response, 'href="tel:')
