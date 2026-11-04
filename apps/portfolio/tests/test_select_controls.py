"""Dropdowns follow each page's palette without changing native form contracts."""

import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import expect, sync_playwright


class SelectControlTests(StaticLiveServerTestCase):
    def test_public_and_workspace_pickers_follow_theme_and_submit_values(self):
        owner = get_user_model().objects.create_superuser(
            "select-owner", "owner@example.com", "test-password"
        )
        self.client.force_login(owner)
        session_cookie = self.client.cookies["sessionid"].value
        with sync_playwright() as playwright, playwright.chromium.launch() as browser:
            page = browser.new_page()
            page.route("https://fonts.googleapis.com/**", lambda route: route.abort())
            page.route("https://fonts.gstatic.com/**", lambda route: route.abort())
            for width in (390, 1440):
                page.set_viewport_size({"width": width, "height": 900})
                for theme in ("light", "dark"):
                    for path, selector in (
                        ("/projects/", "#project-type"),
                        ("/articles/", "#article-topic"),
                    ):
                        page.goto(self.live_server_url + path)
                        page.locator("html").evaluate(
                            "(root, theme) => root.dataset.theme = theme", theme
                        )
                        control = page.locator(selector)
                        palette = control.evaluate("""select => ({
                                button: getComputedStyle(select).backgroundColor,
                                picker: getComputedStyle(select, '::picker(select)').backgroundColor,
                                surface: getComputedStyle(document.documentElement).getPropertyValue('--surface').trim(),
                                appearance: getComputedStyle(select).appearance
                            })""")
                        expected = (
                            "rgb(255, 255, 255)"
                            if theme == "light"
                            else "rgb(16, 31, 51)"
                        )
                        self.assertEqual(palette["button"], expected)
                        self.assertEqual(palette["picker"], expected)
                        self.assertEqual(palette["appearance"], "base-select")
                        control.click()
                        self.assertTrue(
                            control.evaluate("select => select.matches(':open')")
                        )
                        if os.environ.get("SELECT_SCREENSHOT_DIR"):
                            output = Path(os.environ["SELECT_SCREENSHOT_DIR"])
                            output.mkdir(parents=True, exist_ok=True)
                            page.screenshot(
                                path=str(output / f"{selector[1:]}-{theme}-{width}.png")
                            )
                        page.keyboard.press("Escape")
                        expect(control).to_be_focused()
                        self.assertLessEqual(
                            page.evaluate("document.documentElement.scrollWidth"), width
                        )
            page.goto(self.live_server_url + "/projects/")
            control = page.locator("#project-type")
            control.click()
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
            expect(control).to_have_value("backend")
            page.get_by_role("button", name="Apply filters").click()
            expect(page.locator("#project-type")).to_have_value("backend")
            page.wait_for_url("**/projects/?*type=backend*")

            page.context.add_cookies(
                [
                    {
                        "name": "sessionid",
                        "value": session_cookie,
                        "url": self.live_server_url,
                    }
                ]
            )
            page.goto(self.live_server_url + "/dashboard/inbox/")
            control = page.locator("#status")
            expect(control).to_have_css("appearance", "base-select")
            control.click()
            self.assertTrue(control.evaluate("select => select.matches(':open')"))
            page.keyboard.press("Escape")
            expect(control).to_be_focused()
            page.emulate_media(forced_colors="active")
            expect(control).to_have_css("appearance", "auto")
