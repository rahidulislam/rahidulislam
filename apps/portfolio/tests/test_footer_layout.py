"""Browser coverage for header/footer navigation isolation across breakpoints."""

import os
from pathlib import Path

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import expect, sync_playwright

from apps.articles.models import Article


class FooterLayoutTests(StaticLiveServerTestCase):
    def test_footer_stays_in_flow_and_header_menu_still_works(self) -> None:
        article = Article.objects.create(
            title="Responsive footer regression",
            slug="footer-layout-regression",
            summary="A published article for layout verification.",
            body="## Engineering notes\n\n"
            + "A readable paragraph about reliable software.\n\n" * 20,
            topic="Django",
            is_published=True,
        )
        paths = (f"/articles/{article.slug}/", "/articles/", "/", "/projects/")
        playwright = sync_playwright().start()
        self.addCleanup(playwright.stop)
        browser = playwright.chromium.launch()
        self.addCleanup(browser.close)
        page = browser.new_page()
        # Make the test deterministic and independent of external font hosts.
        page.route("https://fonts.googleapis.com/**", lambda route: route.abort())
        page.route("https://fonts.gstatic.com/**", lambda route: route.abort())
        for width in (390, 320, 760, 768, 1024):
            page.set_viewport_size({"width": width, "height": 844})
            for path in paths:
                with self.subTest(width=width, path=path):
                    response = page.goto(
                        self.live_server_url + path, wait_until="networkidle"
                    )
                    self.assertEqual(response.status, 200)
                    footer = page.locator(".site-footer")
                    navigation = page.get_by_role(
                        "navigation", name="Footer navigation"
                    )
                    expect(navigation).to_be_visible()
                    position = navigation.evaluate(
                        "element => getComputedStyle(element).position"
                    )
                    if (
                        os.environ.get("FOOTER_SCREENSHOT_DIR")
                        and width == 390
                        and path == paths[0]
                    ):
                        output = Path(os.environ["FOOTER_SCREENSHOT_DIR"])
                        output.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(output / "article-top.png"))
                        footer.screenshot(path=str(output / "article-footer.png"))
                    self.assertEqual(
                        position,
                        "static",
                        "Footer navigation must stay in document flow",
                    )
                    footer_box = footer.bounding_box()
                    nav_box = navigation.bounding_box()
                    self.assertGreaterEqual(nav_box["y"], footer_box["y"])
                    self.assertLessEqual(
                        nav_box["y"] + nav_box["height"],
                        footer_box["y"] + footer_box["height"] + 1,
                    )
                    self.assertGreaterEqual(nav_box["x"], footer_box["x"])
                    self.assertLessEqual(
                        nav_box["x"] + nav_box["width"],
                        footer_box["x"] + footer_box["width"] + 1,
                    )
                    self.assertLessEqual(
                        page.evaluate("document.documentElement.scrollWidth"), width
                    )
                    if width <= 768:
                        page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
                        toggle = page.get_by_role("button", name="Toggle navigation")
                        toggle.click()
                        expect(toggle).to_have_attribute("aria-expanded", "true")
                        expect(
                            page.get_by_role("navigation", name="Main navigation")
                        ).to_be_visible()
                        self.assertEqual(
                            navigation.evaluate(
                                "element => getComputedStyle(element).position"
                            ),
                            "static",
                        )
                        page.keyboard.press("Escape")
                        expect(toggle).to_have_attribute("aria-expanded", "false")
        page.close()
