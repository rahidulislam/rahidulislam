from django.test import TestCase
from django.urls import reverse

from .models import (
    Category, Contact, EngineeringChallenge, Experience, ExperienceBullet,
    PersonalInfo, Project, ProjectImage, ProjectMetric, Skill,
)
from .portfolio_content import fallback_experiences, fallback_projects


class PortfolioViewTests(TestCase):
    def test_seo_endpoints_and_metadata(self):
        self.assertContains(self.client.get('/robots.txt'), 'Sitemap:')
        sitemap = self.client.get('/sitemap.xml')
        self.assertEqual(sitemap['Content-Type'], 'application/xml')
        self.assertContains(self.client.get(reverse('home:home')), 'rel="canonical"')
        self.assertContains(self.client.get(reverse('home:home')), 'application/ld+json')

    def test_native_responsive_navigation_is_loaded_without_bootstrap(self):
        response = self.client.get(reverse("home:home"))
        self.assertContains(response, "css/portfolio.css?v=20260917-6")
        self.assertContains(response, "js/portfolio.js?v=20260917-4")
        self.assertContains(response, 'class="site-header"')
        self.assertContains(response, 'class="menu-toggle"')
        self.assertContains(response, 'aria-controls="site-nav"')
        self.assertNotContains(response, "bootstrap")
        self.assertNotContains(response, "data-bs-")

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
        database_names = {name.casefold() for name in Project.objects.values_list("name", flat=True)}
        expected_fallbacks = [item for item in fallback_projects if item["name"].casefold() not in database_names]
        self.assertEqual(response.context["fallback_projects"], expected_fallbacks[:5])
        listing = self.client.get(reverse("home:projects"))
        self.assertEqual(listing.context["fallback_projects"], expected_fallbacks)
        self.assertTrue({"slug", "category", "description", "technical_notes", "tags", "short_desc", "visual_label"}.issubset(fallback_projects[0]))
        self.assertEqual(response.context["fallback_experiences"], fallback_experiences)
        self.assertTrue(response.context["backend_skills"])

    def test_database_content_is_preserved_and_all_projects_are_shown(self):
        category = Category.objects.create(name="Additional")
        project = Project.objects.create(
            category=category, name="Database project", short_desc="A project",
            client_name="Client", date="2024-01-01", is_featured=True,
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

    def test_homepage_can_show_five_selected_projects(self):
        Project.objects.all().delete()
        category = Category.objects.create(name="Selected work")
        names = ["TalentBridge", "Smart Document Vault", "HotelMotel", "TheProperty", "Homeopathic Management API"]
        for order, name in enumerate(names):
            Project.objects.create(
                category=category,
                name=name,
                short_desc=f"{name} case study",
                is_featured=True,
                order=order,
            )

        response = self.client.get(reverse("home:home"))
        self.assertEqual([project.name for project in response.context["projects"]], names)
        self.assertContains(response, "TheProperty")
        self.assertContains(response, "Homeopathic Management API")

    def test_detail_url_includes_profile_and_social_context(self):
        category = Category.objects.create(name="Web")
        project = Project.objects.create(
            category=category, name="Detail project", short_desc="A project",
            client_name="Client", date="2024-01-01",
        )
        response = self.client.get(reverse("home:case_study", args=[project.slug]))
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

    def test_contact_honeypot_and_rate_limit_are_generic(self):
        for _ in range(3):
            response = self.client.post(reverse("home:home"), {
                "name": "Visitor", "email": "visitor@example.com", "subject": "Hello",
                "message": "hello", "website": "https://spam.example",
            })
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "accept that message")
        self.assertEqual(Contact.objects.count(), 0)


class CaseStudyTests(TestCase):
    def test_every_fallback_case_study_is_complete_and_disclosure_safe(self):
        required = {
            'problem', 'contribution', 'architecture_summary',
            'technical_decisions', 'outcome', 'lessons', 'project_type',
            'project_role', 'collaboration', 'development_status',
            'contribution_areas', 'constraints', 'validation',
        }
        forbidden = (
            'X-Workspace-ID', 'BookingRoom', 'Prescription duration',
            'pending, confirmed', 'draft, review, published',
            'identity-document storage', 'invitation recovery',
        )
        for project in fallback_projects:
            self.assertTrue(required.issubset(project), project['name'])
            public_copy = ' '.join(str(project[key]) for key in required)
            for phrase in forbidden:
                self.assertNotIn(phrase, public_copy, project['name'])

    def test_all_case_studies_render_and_unknown_slug_is_404(self):
        from .portfolio_content import fallback_projects
        for project in fallback_projects:
            response = self.client.get(reverse('home:case_study', args=[project['slug']]))
            database_project = Project.objects.filter(name__iexact=project['name']).first()
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, project['name'])
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
                               client_name='Client', date='2026-06-01', is_featured=True)
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
        response = self.client.get(reverse('home:case_study', args=[project.slug]))
        for value in ['Detailed implementation', 'https://example.com/demo',
                      'Dashboard', 'Walkthrough', '<video', '/media/project/videos/demo.mp4']:
            self.assertContains(response, value)
        self.assertNotContains(response, 'https://example.com/source')
        self.assertNotContains(response, '>GitHub ↗<')
        self.assertContains(self.client.get(reverse('home:projects')), project.name)

    def test_project_without_live_url_uses_hash_and_hides_repository(self):
        project = Project.objects.create(
            category=self.category, name='Private source project', short_desc='Summary',
            repository_url='https://example.com/private-source',
        )
        response = self.client.get(reverse('home:case_study', args=[project.slug]))
        self.assertContains(response, 'href="#">Live project ↗</a>')
        self.assertNotContains(response, 'https://example.com/private-source')

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

    def test_import_dry_run_reports_without_writing(self):
        from django.core.management import call_command
        from io import StringIO

        Project.objects.filter(name='TalentBridge').delete()
        output = StringIO()
        call_command('import_portfolio_projects', dry_run=True, stdout=output)
        self.assertFalse(Project.objects.filter(name='TalentBridge').exists())
        self.assertIn('WOULD CREATE talentbridge', output.getvalue())
        self.assertIn('(dry run)', output.getvalue())

    def test_import_creates_full_case_study_and_explicit_update_overwrites(self):
        from django.core.management import call_command
        from io import StringIO

        Project.objects.filter(name='TalentBridge').delete()
        call_command('import_portfolio_projects', stdout=StringIO())
        project = Project.objects.get(slug='talentbridge')
        self.assertEqual(project.project_type, 'Recruitment platform backend')
        self.assertTrue(project.constraints)
        self.assertTrue(project.validation)
        self.assertEqual(project.engineering_challenges.count(), 2)
        self.assertTrue(all(item.trade_offs for item in project.engineering_challenges.all()))

        project.description = 'Admin-only edit'
        project.save(update_fields=['description'])
        call_command('import_portfolio_projects', update_existing=True, stdout=StringIO())
        project.refresh_from_db()
        expected = next(item for item in fallback_projects if item['slug'] == 'talentbridge')
        self.assertEqual(project.description, expected['description'])


class StructuredCaseStudyTests(TestCase):
    def test_public_case_study_hides_internal_logic_and_unpublished_evidence(self):
        category = Category.objects.create(name='Recruitment')
        project = Project.objects.create(
            category=category, name='Private Logic Project', short_desc='Public summary',
            architecture_summary='Public architecture only.',
            project_type='Backend platform', project_role='Backend Developer',
            collaboration='Product team', development_status='Development',
            contribution_areas='API design\nValidation',
            constraints='Keep private rules private.',
            validation='Validation focused on public behavior.',
        )
        EngineeringChallenge.objects.create(
            project=project, title='Safe boundary', problem='Public context',
            approach='Public approach', solution='CONFIDENTIAL_POLICY_FORMULA',
            trade_offs='Public trade-off',
            verification='Verified by access-control tests.',
        )
        EngineeringChallenge.objects.create(
            project=project, title='Draft secret', solution='UNPUBLISHED_CHALLENGE',
            is_published=False,
        )
        ProjectMetric.objects.create(
            project=project, label='Private metric', value='9999', is_published=False,
        )

        response = self.client.get(reverse('home:case_study', args=[project.slug]))
        self.assertContains(response, 'Safe boundary')
        self.assertContains(response, 'Public approach')
        self.assertContains(response, 'Architecture overview')
        self.assertContains(response, 'Project facts')
        self.assertContains(response, 'Backend platform')
        self.assertContains(response, 'Constraints')
        self.assertContains(response, 'Validation')
        self.assertContains(response, 'Public trade-off')
        self.assertContains(response, 'CreativeWork')
        self.assertNotContains(response, 'CONFIDENTIAL_POLICY_FORMULA')
        self.assertNotContains(response, 'UNPUBLISHED_CHALLENGE')
        self.assertNotContains(response, 'Private metric')

    def test_legacy_project_url_redirects_to_canonical_slug(self):
        category = Category.objects.create(name='Backend')
        project = Project.objects.create(category=category, name='Canonical Project', short_desc='Summary')
        response = self.client.get(reverse('home:project_detail', args=[project.pk]))
        self.assertRedirects(
            response, reverse('home:case_study', args=[project.slug]),
            status_code=301, fetch_redirect_response=False,
        )

    def test_homeopathic_case_study_is_available_to_site_and_cv(self):
        from .portfolio_data import get_portfolio_data

        category = Category.objects.create(name="Clinic management")
        project = Project.objects.create(
            category=category,
            name="Homeopathic Management API",
            short_desc="Role-aware clinic API",
            problem="Coordinate clinic workflows.",
            contribution="Implemented appointments and clinical records.",
            repository_url="https://github.com/rahidulislam/homeopathic_ms",
        )
        detail = self.client.get(reverse("home:case_study", args=[project.slug]))
        self.assertContains(detail, "Coordinate clinic workflows.")
        self.assertContains(detail, "/static/img/projects/homeopathic-live.jpg")
        self.assertContains(detail, "CuraLink live homeopathic management landing page")
        self.assertContains(self.client.get(reverse("home:projects")), "Homeopathic Management API")
        self.assertIn("Homeopathic Management API", [item["name"] for item in get_portfolio_data()["cv_projects"]])

    def test_theproperty_case_study_is_available_to_site_and_cv(self):
        from .portfolio_data import get_portfolio_data

        category = Category.objects.create(name="Real estate marketplace")
        project = Project.objects.create(
            category=category,
            name="TheProperty",
            short_desc="Role-aware property marketplace",
            problem="Keep draft inventory private.",
            contribution="Implemented role workspaces.",
            repository_url="https://github.com/rahidulislam/realestate_property",
        )
        detail = self.client.get(reverse("home:case_study", args=[project.slug]))
        self.assertContains(detail, "Keep draft inventory private.")
        self.assertContains(detail, "/static/img/projects/theproperty-live.jpg")
        self.assertContains(self.client.get(reverse("home:projects")), "TheProperty")
        self.assertIn("TheProperty", [item["name"] for item in get_portfolio_data()["cv_projects"]])

    def test_seeded_project_uses_real_static_evidence_when_no_upload_exists(self):
        category = Category.objects.create(name="Recruitment")
        project = Project.objects.create(
            category=category,
            name="TalentBridge",
            short_desc="Recruitment API",
        )
        response = self.client.get(reverse("home:case_study", args=[project.slug]))
        self.assertContains(response, "/static/img/projects/talentbridge-login.png")
        self.assertContains(response, "TalentBridge authentication interface")
        project.name = "HotelMotel"
        project.save(update_fields=["name"])
        response = self.client.get(reverse("home:case_study", args=[project.slug]))
        self.assertContains(response, "/static/img/projects/hotelmotel-live.jpg")
        self.assertContains(response, "HotelMotel live landing page")

    def test_sections_render_safely_and_empty_sections_are_omitted(self):
        category = Category.objects.create(name="Backend")
        project = Project.objects.create(
            category=category, name="Case study", short_desc="API project",
            problem="Separate customer data.",
            technical_decisions="<script>alert(1)</script>",
            outcome="Workspace-scoped endpoints.",
        )
        response = self.client.get(reverse("home:case_study", args=[project.slug]))
        self.assertContains(response, "The problem")
        self.assertContains(response, "Workspace-scoped endpoints.")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertNotContains(response, "<h2>My role</h2>")
        self.assertNotContains(response, "<h2>Lessons and next steps</h2>")


class PortfolioModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Backend')

    def test_skill_group_and_order_are_stable(self):
        later = Skill.objects.create(name='Django', value=90, group='Backend', order=2)
        first = Skill.objects.create(name='Python', value=95, group='Backend', order=1)
        self.assertEqual(list(Skill.objects.all()), [first, later])

    def test_experience_bullets_are_ordered_and_available_in_admin(self):
        experience = Experience.objects.create(
            designation='Engineer', company='Example', start_year='2025', end_year='Present',
            description='Backend work', address='Remote',
        )
        second = ExperienceBullet.objects.create(experience=experience, text='Second responsibility', order=2)
        first = ExperienceBullet.objects.create(experience=experience, text='First responsibility', order=1)
        self.assertEqual(list(experience.bullets.all()), [first, second])

    def test_project_slug_is_unique_and_is_backfilled_on_save(self):
        first = Project.objects.create(category=self.category, name='Smart Document Vault', short_desc='Vault')
        second = Project.objects.create(category=self.category, name='Smart Document Vault', short_desc='Another vault')
        self.assertEqual(first.slug, 'smart-document-vault')
        self.assertEqual(second.slug, 'smart-document-vault-2')
        self.assertTrue(Project._meta.get_field('slug').null)
        self.assertTrue(Project._meta.get_field('slug').blank)

    def test_ordered_project_evidence_has_publication_controls_and_image_metadata(self):
        project = Project.objects.create(category=self.category, name='Evidence project', short_desc='Summary')
        private_metric = ProjectMetric.objects.create(
            project=project, label='Private measurement', value='12ms', is_published=False,
            source_url='https://example.com/measurement', order=2,
        )
        public_metric = ProjectMetric.objects.create(
            project=project, label='Public measurement', value='20ms', is_published=True,
            source_url='https://example.com/public-measurement', order=1,
        )
        challenge = EngineeringChallenge.objects.create(
            project=project, title='Tenant isolation', problem='Keep tenant data separate.',
            verification='Covered by isolation tests.', source_url='https://example.com/tests', order=1,
        )
        image = ProjectImage.objects.create(
            project=project, kind=ProjectImage.ARCHITECTURE,
            alt_text='Workspace boundary diagram', order=1,
        )
        self.assertEqual(list(project.metrics.all()), [public_metric, private_metric])
        self.assertTrue(challenge.is_published)
        self.assertFalse(private_metric.is_published)
        self.assertEqual(image.image_alt, 'Workspace boundary diagram')

    def test_admin_exposes_ordered_portfolio_children(self):
        from django.contrib.auth import get_user_model

        project = Project.objects.create(category=self.category, name='Admin project', short_desc='Summary')
        experience = Experience.objects.create(
            designation='Engineer', company='Example', start_year='2025', end_year='Present',
            description='Backend work', address='Remote',
        )
        user = get_user_model().objects.create_superuser(
            'portfolio-admin', 'portfolio-admin@example.com', 'test-password')
        self.client.force_login(user)
        project_response = self.client.get(reverse('admin:home_project_change', args=[project.pk]))
        experience_response = self.client.get(reverse('admin:home_experience_change', args=[experience.pk]))
        for prefix in ('project_image', 'videos', 'engineering_challenges', 'metrics'):
            self.assertContains(project_response, f'{prefix}-TOTAL_FORMS')
        self.assertContains(experience_response, 'bullets-TOTAL_FORMS')

    def test_project_case_study_facts_are_blank_safe_and_editable_in_admin(self):
        from django.contrib.auth import get_user_model

        project = Project.objects.create(
            category=self.category, name='Recruiter facts', short_desc='Summary')
        for field_name in (
            'project_type', 'project_role', 'collaboration', 'development_status',
            'contribution_areas', 'constraints', 'validation',
        ):
            field = Project._meta.get_field(field_name)
            self.assertTrue(field.blank)
            self.assertEqual(getattr(project, field_name), '')

        user = get_user_model().objects.create_superuser(
            'facts-admin', 'facts-admin@example.com', 'test-password')
        self.client.force_login(user)
        response = self.client.get(reverse('admin:home_project_change', args=[project.pk]))
        for label in (
            'Project type', 'Project role', 'Collaboration', 'Development status',
            'Contribution areas', 'Constraints', 'Validation',
        ):
            self.assertContains(response, label)
