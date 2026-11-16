from django.test import TestCase
from django.urls import reverse

from apps.projects.models import Project, ProjectVideo


class MediaAttributeTests(TestCase):
    def test_static_cover_and_social_card_use_real_image_size(self):
        project = Project.objects.get(slug="theproperty")
        width, height = project.get_image_size()
        self.assertGreater(width, 0)
        response = self.client.get(reverse("home:case_study", args=[project.slug]))
        self.assertContains(
            response,
            f'class="detail-cover" src="{project.get_image_url()}" '
            f'alt="{project.image_alt}" width="{width}" height="{height}" '
            'fetchpriority="high"',
        )
        self.assertContains(
            response, f'<meta property="og:image:width" content="{width}">'
        )
        self.assertContains(
            response, f'<meta property="og:image:height" content="{height}">'
        )

    def test_default_social_card_is_a_small_jpeg(self):
        response = self.client.get(reverse("home:home"))
        self.assertContains(response, "img/og-portfolio-v3.jpg")
        self.assertContains(response, '<meta property="og:image:width" content="1200">')
        self.assertContains(response, '<meta property="og:image:height" content="628">')

    def test_missing_upload_omits_size_instead_of_failing(self):
        project = Project.objects.get(slug="theproperty")
        project.image.name = "images/missing.png"
        with self.assertLogs("core.images", "WARNING"):
            self.assertIsNone(project.get_image_size())

    def test_video_source_declares_its_type(self):
        video = ProjectVideo(file="project/videos/demo.WEBM")
        self.assertEqual(video.content_type, "video/webm")

    def test_experience_links_its_published_case_study(self):
        response = self.client.get(
            reverse("home:experience_detail", args=["talentbridge"])
        )
        self.assertContains(response, 'href="/work/talentbridge/"')
        response = self.client.get(reverse("home:experience_detail", args=["wege-llc"]))
        self.assertNotContains(response, "Related work")
