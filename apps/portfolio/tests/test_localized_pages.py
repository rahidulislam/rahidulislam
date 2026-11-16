from django.test import RequestFactory, TestCase
from django.urls import reverse

from core.views import error_500


class LocalizedPageTests(TestCase):
    def bangla(self):
        self.client.cookies["portfolio_language"] = "bn"

    def test_fallback_case_study_is_translated(self):
        url = reverse("home:case_study", args=["talentbridge"])
        self.assertContains(self.client.get(url), "Technical focus")
        self.bangla()
        response = self.client.get(url)
        self.assertContains(response, "প্রযুক্তিগত দিক")
        self.assertContains(response, "কাজটি নিয়ে কথা বলি।")
        self.assertNotContains(response, "Technical focus")

    def test_home_project_heading_and_404_are_translated(self):
        self.bangla()
        self.assertContains(
            self.client.get(reverse("home:home")), "নির্বাচিত প্রজেক্ট।"
        )
        missing = self.client.get("/no-such-page/")
        self.assertEqual(missing.status_code, 404)
        self.assertContains(missing, "পেজটি এখানে নেই।", status_code=404)

    def test_server_error_page_needs_no_database(self):
        request = RequestFactory().get("/")
        with self.assertNumQueries(0):
            response = error_500(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Something went wrong.", response.content)

    def test_honeypot_has_no_empty_label_and_is_hidden_from_assistive_tech(self):
        response = self.client.get(reverse("home:home"))
        self.assertNotContains(response, '<label for="id_website">')
        self.assertContains(
            response,
            '<div class="contact-trap-field" hidden aria-hidden="true">'
            '<input type="text" name="website"',
        )
