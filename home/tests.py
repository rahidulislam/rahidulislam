from django.test import TestCase
from django.urls import reverse

from .models import Category, Contact, Experience, PersonalInfo, Project, Skill
from .portfolio_content import fallback_experiences, fallback_projects


class PortfolioViewTests(TestCase):
    def test_theme_switch_is_icon_only_and_accessible(self):
        response = self.client.get(reverse("home:home"))
        self.assertContains(response, 'class="theme-toggle"')
        self.assertContains(response, 'aria-label="Enable dark mode"')
        self.assertContains(response, 'class="theme-moon"')
        self.assertContains(response, 'class="theme-sun"')
        self.assertNotContains(response, 'class="theme-label"')

    def test_empty_home_exposes_readme_fallbacks(self):
        response = self.client.get(reverse("home:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["fallback_projects"], fallback_projects[:3])
        listing = self.client.get(reverse("home:projects"))
        self.assertEqual(listing.context["fallback_projects"], fallback_projects)
        self.assertTrue({"slug", "category", "description", "technical_notes", "tags", "short_desc", "visual_label"}.issubset(fallback_projects[0]))
        self.assertEqual(response.context["fallback_experiences"], fallback_experiences)
        self.assertTrue(response.context["backend_skills"])

    def test_database_content_is_preserved_and_all_projects_are_shown(self):
        category = Category.objects.create(name="Additional")
        project = Project.objects.create(
            category=category, name="Database project", short_desc="A project",
            client_name="Client", date="2024-01-01",
        )
        Skill.objects.create(name="Python", value=90)
        Experience.objects.create(
            designation="Developer", company="Company", start_year="2024",
            end_year="2025", description="Work", address="Remote",
        )
        response = self.client.get(reverse("home:home"))
        self.assertIn(project, response.context["projects"])
        self.assertEqual([skill.name for skill in response.context["backend_skills"]], ["Python"])
        self.assertEqual(response.context["experiences"].count(), 1)

    def test_detail_url_includes_profile_and_social_context(self):
        category = Category.objects.create(name="Web")
        project = Project.objects.create(
            category=category, name="Detail project", short_desc="A project",
            client_name="Client", date="2024-01-01",
        )
        response = self.client.get(reverse("home:project_detail", args=[project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project"], project)
        self.assertIn("personal_info", response.context)
        self.assertIn("social_items", response.context)

    def test_valid_contact_is_saved_and_redirects_to_contact_anchor(self):
        response = self.client.post(reverse("home:home"), {
            "name": "Visitor", "email": "visitor@example.com",
            "subject": "Hello", "message": "I would like to connect.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/#contact")
        self.assertTrue(Contact.objects.filter(email="visitor@example.com").exists())

    def test_invalid_contact_is_not_saved(self):
        response = self.client.post(reverse("home:home"), {
            "name": "Visitor", "email": "not-an-email", "subject": "Hello", "message": "x",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)


class CaseStudyTests(TestCase):
    def test_all_case_studies_render_and_unknown_slug_is_404(self):
        from .portfolio_content import fallback_projects
        for project in fallback_projects:
            response = self.client.get(reverse('home:case_study', args=[project['slug']]))
            self.assertContains(response, project['name'])
            self.assertContains(response, project['description'])
        response = self.client.get(reverse('home:case_study', args=['missing-project']))
        self.assertEqual(response.status_code, 404)


class CVDownloadTests(TestCase):
    def test_pdf_download_and_links(self):
        response = self.client.get(reverse('home:download_cv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertIn('Rahidul_Islam_Python_Developer_CV.pdf', response['Content-Disposition'])
        self.assertTrue(b''.join(response.streaming_content).startswith(b'%PDF-'))
        self.assertContains(self.client.get(reverse('home:home')), reverse('home:download_cv'), count=2)

    def test_download_is_read_only(self):
        self.assertEqual(self.client.post(reverse('home:download_cv')).status_code, 405)


class LiveCVTests(TestCase):
    def test_admin_experience_updates_home_and_pdf_input_without_file_export(self):
        from unittest.mock import patch
        record = Experience.objects.create(
            designation='Python Engineer', company='TalentBridge', start_year='Jun 2026',
            end_year='Present', description='API work', address='Remote, Germany')
        for title in ['Python Engineer', 'Updated Python Engineer']:
            record.designation = title
            record.save()
            self.assertContains(self.client.get(reverse('home:home')), title)
            with patch('home.cv_pdf.build_cv', return_value=b'%PDF-test') as build:
                response = self.client.get(reverse('home:download_cv'))
                self.assertEqual(response['Cache-Control'], 'no-store')
                self.assertIn(title, [item['role'] for item in build.call_args.args[0]['experience']])
                response.close()

    def test_corrected_wege_dates_are_shared(self):
        from .portfolio_data import get_portfolio_data
        profile = get_portfolio_data()['cv_profile']
        wege = next(item for item in profile['experience'] if item['company'] == 'Wege LLC')
        self.assertEqual(wege['dates'], 'September 2023 - June 2024')
        self.assertContains(self.client.get(reverse('home:home')), wege['dates'])

    def test_admin_project_and_skill_are_shared(self):
        from .portfolio_data import get_portfolio_data
        category = Category.objects.create(name='API')
        Project.objects.create(category=category, name='New project', short_desc='Fresh content',
                               client_name='Client', date='2026-06-01')
        Skill.objects.create(name='New skill', value=50)
        data = get_portfolio_data()
        self.assertIn('New project', [item['name'] for item in data['cv_projects']])
        self.assertEqual(data['cv_profile']['skills'], ['New skill'])
        response = self.client.get(reverse('home:home'))
        self.assertContains(response, 'New skill')
        self.assertContains(response, 'New project')


class ManagedProjectTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Backend')

    def test_published_detail_renders_links_description_and_media(self):
        from .models import ProjectImage, ProjectVideo
        project = Project.objects.create(
            category=self.category, name='Managed project', short_desc='Summary',
            description='Detailed implementation', features='Authentication\nReporting',
            url='https://example.com/demo', repository_url='https://example.com/source')
        ProjectImage.objects.create(project=project, image='project/one.png', caption='Dashboard')
        ProjectVideo.objects.create(project=project, file='project/videos/demo.mp4', caption='Walkthrough')
        response = self.client.get(reverse('home:project_detail', args=[project.pk]))
        for value in ['Detailed implementation', 'https://example.com/demo', 'https://example.com/source',
                      'Dashboard', 'Walkthrough', '<video', '/media/project/videos/demo.mp4']:
            self.assertContains(response, value)
        self.assertContains(self.client.get(reverse('home:projects')), project.name)

    def test_drafts_are_private_in_listing_detail_and_cv(self):
        from .portfolio_data import get_portfolio_data
        project = Project.objects.create(category=self.category, name='TalentBridge',
                                         short_desc='Private draft', is_published=False)
        self.assertNotContains(self.client.get(reverse('home:projects')), 'Private draft')
        self.assertEqual(self.client.get(reverse('home:project_detail', args=[project.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('home:case_study', args=['talentbridge'])).status_code, 404)
        self.assertNotIn('TalentBridge', [p['name'] for p in get_portfolio_data()['cv_projects']])

    def test_video_validation_and_admin_inlines(self):
        from django.core.exceptions import ValidationError
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.contrib.auth import get_user_model
        from .models import ProjectVideo, validate_video_size
        project = Project.objects.create(category=self.category, name='Media project', short_desc='Summary')
        video = ProjectVideo(project=project, file=SimpleUploadedFile('invalid.html', b'bad'))
        with self.assertRaises(ValidationError):
            video.full_clean()
        class LargeFile:
            size = 51 * 1024 * 1024
        with self.assertRaises(ValidationError):
            validate_video_size(LargeFile())
        self.client.force_login(get_user_model().objects.create_superuser('admin-test', 'admin@example.com', 'test-password'))
        response = self.client.get(reverse('admin:home_project_change', args=[project.pk]))
        self.assertContains(response, 'project_image-TOTAL_FORMS')
        self.assertContains(response, 'videos-TOTAL_FORMS')
        self.assertContains(response, 'Featured image')

    def test_import_is_repeatable_and_preserves_admin_edits(self):
        from django.core.management import call_command
        from io import StringIO
        call_command('import_portfolio_projects', stdout=StringIO())
        project = Project.objects.get(name='TalentBridge')
        project.description = 'Edited in admin'
        project.save()
        total = Project.objects.count()
        call_command('import_portfolio_projects', stdout=StringIO())
        project.refresh_from_db()
        self.assertEqual(project.description, 'Edited in admin')
        self.assertEqual(Project.objects.count(), total)


class StructuredCaseStudyTests(TestCase):
    def test_seeded_project_uses_real_static_evidence_when_no_upload_exists(self):
        category = Category.objects.create(name="Recruitment")
        project = Project.objects.create(
            category=category,
            name="TalentBridge",
            short_desc="Recruitment API",
        )
        response = self.client.get(reverse("home:project_detail", args=[project.pk]))
        self.assertContains(response, "/static/img/projects/talentbridge-login.png")
        self.assertContains(response, "TalentBridge authentication interface")
        project.name = "HotelMotel"
        project.save(update_fields=["name"])
        response = self.client.get(reverse("home:project_detail", args=[project.pk]))
        self.assertContains(response, "/static/img/projects/hotelmotel-api.png")
        self.assertContains(response, "HotelMotel generated OpenAPI contract")

    def test_sections_render_safely_and_empty_sections_are_omitted(self):
        category = Category.objects.create(name="Backend")
        project = Project.objects.create(
            category=category, name="Case study", short_desc="API project",
            problem="Separate customer data.",
            technical_decisions="<script>alert(1)</script>",
            outcome="Workspace-scoped endpoints.",
        )
        response = self.client.get(reverse("home:project_detail", args=[project.pk]))
        self.assertContains(response, "The problem")
        self.assertContains(response, "Workspace-scoped endpoints.")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertNotContains(response, "<h2>My role</h2>")
        self.assertNotContains(response, "<h2>Lessons and next steps</h2>")
