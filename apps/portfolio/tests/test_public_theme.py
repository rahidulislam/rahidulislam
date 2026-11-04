"""Public theme behavior and responsive styling contracts."""

import os
from pathlib import Path

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import expect, sync_playwright

from apps.articles.models import Article


class PublicThemeTests(StaticLiveServerTestCase):
    def test_theme_persists_across_navigation_and_mobile_layouts(self) -> None:
        article = Article.objects.create(
            title="Theme reading regression",
            slug="theme-reading-regression",
            summary="A readable public article.",
            body="## Theme checks\n\nReadable text and accessible controls.",
            topic="Django",
            is_published=True,
        )
        paths = (
            "/",
            "/projects/",
            "/articles/",
            "/contact/",
            "/work/talentbridge/",
            "/experience/talentbridge/",
            f"/articles/{article.slug}/",
        )
        playwright = sync_playwright().start()
        self.addCleanup(playwright.stop)
        browser = playwright.chromium.launch()
        self.addCleanup(browser.close)
        page = browser.new_page(color_scheme="light")
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.route("https://fonts.googleapis.com/**", lambda route: route.abort())
        page.route("https://fonts.gstatic.com/**", lambda route: route.abort())
        page.goto(self.live_server_url)
        expect(page.locator("html")).to_have_attribute("data-theme", "light")
        toggle = page.locator(".theme-toggle")
        toggle.click()
        expect(page.locator("html")).to_have_attribute("data-theme", "dark")
        expect(toggle).to_have_attribute("aria-pressed", "true")
        expect(page.locator("body")).to_have_css("background-color", "rgb(8, 19, 33)")
        page.get_by_role("navigation", name="Main navigation").get_by_role(
            "link", name="Projects", exact=True
        ).click()
        expect(page.locator("#project-search")).to_be_visible()
        expect(page.locator("html")).to_have_attribute("data-theme", "dark")
        page.reload()
        expect(page.locator("html")).to_have_attribute("data-theme", "dark")
        for theme in ("light", "dark"):
            if page.locator("html").get_attribute("data-theme") != theme:
                page.locator(".theme-toggle").click()
            for width in (320, 390, 768, 1440):
                page.set_viewport_size({"width": width, "height": 900})
                for path in paths:
                    with self.subTest(theme=theme, width=width, path=path):
                        response = page.goto(self.live_server_url + path)
                        self.assertEqual(response.status, 200)
                        self.assertLessEqual(
                            page.evaluate("document.documentElement.scrollWidth"),
                            width,
                        )
                        expect(page.locator("html")).to_have_attribute(
                            "data-theme", theme
                        )
                        if os.environ.get("THEME_SCREENSHOT_DIR"):
                            output = Path(os.environ["THEME_SCREENSHOT_DIR"])
                            output.mkdir(parents=True, exist_ok=True)
                            label = path.strip("/").replace("/", "-") or "home"
                            page.screenshot(
                                path=str(output / f"{label}-{theme}-{width}.png"),
                                full_page=path != "/",
                            )
        self.assertEqual(errors, [])
        page.close()

    def test_navigation_controls_and_links_fit_small_screens(self) -> None:
        with sync_playwright() as playwright, playwright.chromium.launch() as browser:
            page = browser.new_page()
            for width in (320, 390, 768, 820, 1024):
                page.set_viewport_size({"width": width, "height": 900})
                page.goto(self.live_server_url)
                controls = page.locator(".header-actions").bounding_box()
                brand = page.locator(".site-header .wordmark").bounding_box()
                self.assertLessEqual(brand["x"] + brand["width"], width)
                if width <= 600:
                    self.assertGreaterEqual(controls["y"], brand["y"] + brand["height"])
                toggle = page.locator(".menu-toggle")
                toggle.click()
                nav = page.locator("#site-nav")
                expect(nav).to_be_visible()
                header = page.locator(".site-header").bounding_box()
                self.assertGreaterEqual(nav.bounding_box()["y"], header["height"] - 1)
                links = nav.locator("a")
                for index in range(links.count()):
                    box = links.nth(index).bounding_box()
                    self.assertGreaterEqual(box["height"], 44)
                    self.assertLessEqual(box["x"] + box["width"], width)
                page.keyboard.press("Escape")
                expect(toggle).to_have_attribute("aria-expanded", "false")
                expect(nav).to_have_attribute("inert", "")
