from django.test import TestCase
from django.urls import reverse

from .models import (
    Category, Contact, EngineeringChallenge, Experience, ExperienceBullet,
    PersonalInfo, Project, ProjectImage, ProjectMetric, Skill,
)
from .portfolio_content import fallback_experiences, fallback_projects


from django.test import override_settings

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PortfolioViewTests(TestCase):
    def test_seo_endpoints_and_metadata(self):
        self.assertContains(self.client.get('/robots.txt'), 'Sitemap:')
        sitemap = self.client.get('/sitemap.xml')
        self.assertEqual(sitemap['Content-Type'], 'application/xml')
        self.assertContains(self.client.get(reverse('home:home')), 'rel="canonical"')
        self.assertContains(self.client.get(reverse('home:home')), 'application/ld+json')

    def test_native_responsive_navigation_is_loaded_without_bootstrap(self):
        response = self.client.get(reverse("home:home"))
        self.assertContains(response, "css/portfolio.css?v=20261008-features")
        self.assertContains(response, "js/portfolio.js?v=20261008-features")
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
        self.assertEqual(response.context["fallback_projects"], [item for item in expected_fallbacks if item["name"] in {"TalentBridge", "Smart Document Vault", "Ilmora — Madrasha Management"}])
        listing = self.client.get(reverse("home:projects"))
        self.assertEqual(listing.context["fallback_projects"], expected_fallbacks)
        self.assertTrue({"slug", "category", "description", "technical_notes", "tags", "short_desc", "visual_label"}.issubset(fallback_projects[0]))
        self.assertEqual(response.context["fallback_experiences"], fallback_experiences)
        self.assertTrue(response.context["backend_skills"])

    def test_database_content_is_preserved_in_project_library(self):
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
        listing = self.client.get(reverse("home:projects"))
        self.assertIn(project, listing.context["projects"])
        self.assertEqual([skill.name for skill in response.context["backend_skills"]], ["Python"])
        self.assertEqual(response.context["experiences"].count(), 1)

    def test_homepage_shows_only_three_selected_projects(self):
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
        selected_names = [project["name"] for project in response.context["fallback_projects"]]
        selected_names += [project.name for project in response.context["projects"]]
        self.assertCountEqual(selected_names, ["TalentBridge", "Smart Document Vault", "Ilmora — Madrasha Management"])
        self.assertNotContains(response, "TheProperty")
        self.assertNotContains(response, "Homeopathic Management API")

    def test_v3_homepage_positioning_and_structure(self):
        response = self.client.get(reverse("home:home"))
        self.assertContains(response, "Python &amp; Django engineer building secure business systems")
        self.assertContains(response, "Open to relocation to Germany and remote opportunities")
        self.assertContains(response, "View case studies")
        self.assertNotContains(response, "How I build backend systems")
        self.assertNotContains(response, 'class="filters"')
        self.assertContains(response, "02 / Experience")
        self.assertContains(response, "03 / What I work with")

    def test_v3_social_metadata_uses_branded_card(self):
        response = self.client.get(reverse("home:home"))
        self.assertContains(response, "og-portfolio-v3.png")
        self.assertContains(response, 'name="twitter:card" content="summary_large_image"')
        self.assertContains(response, '"@type":"WebSite"')
        self.assertNotContains(response, "img/me.jpg")

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
        self.assertNotContains(response, 'New project')
        self.assertContains(self.client.get(reverse('home:projects')), 'New project')


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

    def test_project_without_live_url_uses_non_link_and_hides_repository(self):
        project = Project.objects.create(
            category=self.category, name='Private source project', short_desc='Summary',
            repository_url='https://example.com/private-source',
        )
        response = self.client.get(reverse('home:case_study', args=[project.slug]))
        self.assertContains(response, 'aria-disabled="true">Live preview unavailable</span>')
        self.assertNotContains(response, 'href="#"')
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


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class MadrashaAndContactTests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def test_ilmora_is_seeded_and_has_live_case_study(self):
        project = Project.objects.get(slug='ilmora-madrasha-management')
        self.assertEqual(project.url, 'https://madrasha-backend.vercel.app/')
        self.assertContains(self.client.get(reverse('home:home')), project.name)
        self.assertContains(self.client.get(reverse('home:projects')), project.name)
        response = self.client.get(reverse('home:case_study', args=[project.slug]))
        self.assertContains(response, project.url)
        self.assertContains(response, '58 management routes')
        self.assertContains(response, 'browser-local data')

    def test_contact_route_saves_and_redirects(self):
        response = self.client.post(reverse('home:contact'), {
            'name': 'Visitor', 'email': 'visitor@example.com',
            'subject': 'Role', 'message': 'Let us connect.',
        })
        self.assertRedirects(response, '/#contact')
        self.assertEqual(Contact.objects.count(), 1)

    def test_contact_errors_keep_page_context_and_ip_protection(self):
        response = self.client.get(reverse('home:contact'))
        self.assertContains(response, 'class="site-header"')
        response = self.client.post(reverse('home:contact'), {
            'name': 'Visitor', 'email': 'invalid', 'subject': 'Hello', 'message': 'Hello',
        }, REMOTE_ADDR='192.0.2.7')
        self.assertContains(response, 'class="site-header"')
        self.assertEqual(response.context['form'].request_ip, '192.0.2.7')
        self.assertContains(response, 'Enter a valid email address')
        self.assertEqual(Contact.objects.count(), 0)
        response = self.client.post(reverse('home:contact'), {
            'name': 'Bot', 'email': 'bot@example.com', 'subject': 'Spam',
            'message': 'Spam', 'website': 'https://spam.example',
        })
        self.assertContains(response, 'accept that message')
        self.assertEqual(Contact.objects.count(), 0)


class IlmoraScreenshotTests(TestCase):
    def test_managed_and_fallback_case_study_render_screenshots(self):
        from pathlib import Path
        from django.conf import settings
        from .madrasha_content import MADRASHA_SCREENSHOTS
        for managed in (True, False):
            if not managed:
                Project.objects.filter(slug='ilmora-madrasha-management').delete()
            response = self.client.get('/work/ilmora-madrasha-management/')
            self.assertContains(response, 'Project screenshots')
            for screenshot in MADRASHA_SCREENSHOTS:
                self.assertContains(response, screenshot['image'])
                self.assertTrue((Path(settings.BASE_DIR) / 'static' / screenshot['image']).is_file())
        self.assertContains(self.client.get('/'), 'img/projects/ilmora-landing.jpg')



@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PortfolioFeatureTests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def test_catalog_filters_combine_and_work_without_javascript(self):
        response = self.client.get('/projects/', {'q': 'Ilmora', 'type': 'frontend', 'technology': 'React'})
        self.assertEqual([item['slug'] for item in response.context['project_cards']], ['ilmora-madrasha-management'])
        self.assertContains(response, 'value="Ilmora"')
        self.assertContains(response, 'type="search"')
        empty = self.client.get('/projects/', {'q': 'Ilmora', 'type': 'backend'})
        self.assertContains(empty, 'No projects match these filters.')
        self.assertEqual(empty.context['project_cards'], [])
        self.assertGreater(len(self.client.get('/projects/').context['project_cards']), 1)

    def test_catalog_respects_drafts_and_explicit_technology_tags(self):
        project = Project.objects.get(slug='ilmora-madrasha-management')
        project.is_published = False
        project.save()
        self.assertNotContains(self.client.get('/projects/'), project.name)
        project.is_published = True
        project.technologies = 'React\nZod'
        project.save()
        response = self.client.get('/projects/', {'technology': 'Zod'})
        self.assertEqual([card['name'] for card in response.context['project_cards']], [project.name])

    def test_articles_publish_safely_with_bilingual_content(self):
        from .models import Article
        self.assertEqual(self.client.get('/articles/').status_code, 200)
        article = Article.objects.filter(is_published=True).first()
        self.assertContains(self.client.get(f'/articles/{article.slug}/'), article.title)
        Article.objects.create(title='Private draft', slug='private-draft', summary='Secret', body='Private', topic='Django')
        self.assertNotContains(self.client.get('/articles/'), 'Private draft')
        self.assertEqual(self.client.get('/articles/private-draft/').status_code, 404)
        article.body = '<script>alert(1)</script>'
        article.save()
        self.assertNotContains(self.client.get(f'/articles/{article.slug}/'), '<script>alert(1)</script>')
        self.client.cookies['portfolio_language'] = 'bn'
        self.assertContains(self.client.get(f'/articles/{article.slug}/'), article.title_bn)
        self.assertContains(self.client.get(f'/articles/{article.slug}/'), article.body_bn.split('\n')[0])

    def test_language_persists_and_rejects_external_redirect(self):
        response = self.client.post('/language/', {'language': 'bn', 'next': '/projects/?type=frontend'})
        self.assertEqual(response['Location'], '/projects/?type=frontend')
        self.assertEqual(response.cookies['portfolio_language'].value, 'bn')
        self.assertContains(self.client.get('/projects/'), '<html lang="bn">')
        self.assertContains(self.client.get('/projects/'), 'প্রজেক্ট খুঁজুন')
        self.assertEqual(self.client.post('/language/', {'language': 'en', 'next': 'https://evil.example/'} )['Location'], '/')
        self.assertEqual(self.client.get('/language/').status_code, 405)
        self.client.cookies['portfolio_language'] = 'bn'
        response = self.client.post('/contact/', {'name': 'Visitor', 'email': 'invalid', 'subject': 'Hello', 'message': 'Hello'})
        self.assertContains(response, 'সঠিক ইমেইল ঠিকানা দিন।')

    def test_experience_detail_uses_shared_live_profile(self):
        self.assertContains(self.client.get('/experience/'), 'TalentBridge')
        self.assertContains(self.client.get('/experience/talentbridge/'), 'Responsibilities and contributions')
        self.assertEqual(self.client.get('/experience/missing/').status_code, 404)
        experience = Experience.objects.create(company='TalentBridge', designation='Updated engineer', start_year='2026', end_year='Present', description='Updated responsibilities', address='Remote')
        self.assertContains(self.client.get('/experience/talentbridge/'), 'Updated responsibilities')

    def test_contact_notification_delivered_after_persistence(self):
        from django.core import mail
        response = self.client.post('/contact/', {'name': 'Visitor', 'email': 'visitor@example.com', 'subject': 'Hello', 'message': 'Let us talk.'})
        self.assertEqual(response.status_code, 302)
        contact = Contact.objects.get(email='visitor@example.com')
        self.assertEqual(contact.status, 'unread')
        self.assertEqual(contact.notification_status, 'sent')
        self.assertEqual(mail.outbox[-1].reply_to, ['visitor@example.com'])
        self.assertIn('Let us talk.', mail.outbox[-1].body)

    def test_notification_failure_preserves_enquiry_and_can_be_retried(self):
        from unittest.mock import patch
        from .notifications import notify_contact
        with patch('home.notifications.EmailMessage.send', side_effect=OSError('Offline')):
            response = self.client.post('/contact/', {'name': 'Visitor', 'email': 'visitor@example.com', 'subject': 'Hello', 'message': 'Keep this message.'})
        self.assertEqual(response.status_code, 302)
        contact = Contact.objects.get()
        self.assertEqual(contact.notification_status, 'failed')
        self.assertEqual(contact.message, 'Keep this message.')
        self.assertEqual(notify_contact(contact), 'sent')
        contact.refresh_from_db()
        self.assertEqual(contact.notification_status, 'sent')

    def test_testimonials_require_publication_and_consent(self):
        from .models import Testimonial
        testimonial = Testimonial.objects.create(client_name='Example colleague', designation='Engineer', review='Private feedback', is_published=True)
        self.assertNotContains(self.client.get('/'), 'Private feedback')
        testimonial.consent_to_publish = True
        testimonial.save()
        self.assertContains(self.client.get('/'), 'Private feedback')
        testimonial.is_published = False
        testimonial.save()
        self.assertNotContains(self.client.get('/'), 'Private feedback')

    def test_enquiries_require_staff_authentication(self):
        from django.contrib.auth.models import User
        response = self.client.get('/admin/home/contact/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.create_user(username='visitor', password='test-password')
        self.client.force_login(user)
        self.assertEqual(self.client.get('/admin/home/contact/').status_code, 302)

    def test_case_study_has_architecture_video_and_lightbox(self):
        response = self.client.get('/work/ilmora-madrasha-management/')
        self.assertContains(response, 'data-lightbox')
        self.assertContains(response, '<dialog')
        self.assertContains(response, 'img/architecture/ilmora-madrasha-management.svg')
        self.assertContains(response, 'video/ilmora-demo.webm')


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PortfolioAdminFeatureTests(TestCase):
    def test_contact_admin_filters_search_status_and_retry(self):
        from django.contrib.auth.models import User
        from django.urls import reverse
        from django.core import mail
        user = User.objects.create_superuser('admin', 'admin@example.com', 'test-password')
        self.client.force_login(user)
        contact = Contact.objects.create(name='Inbox visitor', email='inbox@example.com', subject='Opportunity', message='Hello', notification_status='failed')
        url = reverse('admin:home_contact_changelist')
        self.assertContains(self.client.get(url, {'q': 'Opportunity', 'status__exact': 'unread'}), 'Inbox visitor')
        response = self.client.post(url, {'action': 'mark_read', '_selected_action': [contact.pk]})
        self.assertEqual(response.status_code, 302)
        contact.refresh_from_db()
        self.assertEqual(contact.status, 'read')
        self.client.post(url, {'action': 'retry_notifications', '_selected_action': [contact.pk]})
        contact.refresh_from_db()
        self.assertEqual(contact.notification_status, 'sent')
        self.assertEqual(len(mail.outbox), 1)
        self.client.post(url, {'action': 'retry_notifications', '_selected_action': [contact.pk]})
        self.assertEqual(len(mail.outbox), 1)
        self.client.post(url, {'action': 'mark_replied', '_selected_action': [contact.pk]})
        contact.refresh_from_db()
        self.assertEqual(contact.status, 'replied')

    def test_sitemap_includes_public_articles_and_experience_only(self):
        from .models import Article
        Article.objects.create(slug='draft-sitemap', title='Draft', summary='Hidden', body='Draft', topic='Private')
        response = self.client.get('/sitemap.xml')
        self.assertContains(response, '/articles/django-contact-storage-before-email/')
        self.assertContains(response, '/experience/talentbridge/')
        self.assertNotContains(response, 'draft-sitemap')


class ExperienceSlugTests(TestCase):
    def create_experience(self, company, designation='Engineer'):
        return Experience.objects.create(company=company, designation=designation, start_year='2026', end_year='Present', description='Public responsibilities', address='Dhaka')

    def test_non_ascii_company_has_persisted_route_in_all_public_consumers(self):
        experience = self.create_experience('বাংলা প্রতিষ্ঠান')
        experience.refresh_from_db()
        self.assertTrue(experience.slug)
        url = reverse('home:experience_detail', args=[experience.slug])
        self.assertContains(self.client.get('/experience/'), url)
        self.assertContains(self.client.get('/'), url)
        self.assertContains(self.client.get('/sitemap.xml'), url)
        self.assertContains(self.client.get(url), 'বাংলা প্রতিষ্ঠান')

    def test_empty_and_duplicate_slug_bases_have_distinct_working_routes(self):
        first = self.create_experience('বাংলা প্রতিষ্ঠান', 'First role')
        second = self.create_experience('বাংলা প্রতিষ্ঠান', 'Second role')
        punctuation = self.create_experience('!!!', 'Third role')
        self.assertEqual(len({first.slug, second.slug, punctuation.slug}), 3)
        for experience in (first, second, punctuation):
            response = self.client.get(reverse('home:experience_detail', args=[experience.slug]))
            self.assertEqual(response.context['experience']['role'], experience.designation)

    def test_company_rename_preserves_existing_url(self):
        experience = self.create_experience('Existing Company')
        self.assertEqual(experience.slug, 'existing-company')
        original_slug = experience.slug
        experience.company = 'নতুন কোম্পানি'
        experience.save(update_fields=['company'])
        experience.refresh_from_db()
        self.assertEqual(experience.slug, original_slug)
        self.assertContains(self.client.get(reverse('home:experience_detail', args=[original_slug])), 'নতুন কোম্পানি')

    def test_generated_slugs_do_not_shadow_source_backed_experience_urls(self):
        experience = self.create_experience('TalentBridge!')
        self.assertNotEqual(experience.slug, 'talentbridge')
        response = self.client.get('/experience/talentbridge/')
        self.assertEqual(response.context['experience']['company'], 'TalentBridge')
        self.assertEqual(self.client.get(reverse('home:experience_detail', args=[experience.slug])).status_code, 200)


from django.test import TransactionTestCase


class ExperienceSlugMigrationTests(TransactionTestCase):
    def test_existing_rows_receive_nonempty_unique_slugs(self):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor
        before = ('home', '0040_seed_engineering_articles')
        after = ('home', '0041_persist_experience_slugs')
        executor = MigrationExecutor(connection)
        executor.migrate([before])
        try:
            OldExperience = executor.loader.project_state([before]).apps.get_model('home', 'Experience')
            records = []
            for company in ('বাংলা প্রতিষ্ঠান', 'বাংলা প্রতিষ্ঠান', '!!!', 'TalentBridge!', 'TalentBridge'):
                records.append(OldExperience.objects.create(company=company, designation='Engineer', start_year='2026', end_year='Present', description='Migration fixture', address='Dhaka').pk)
            executor = MigrationExecutor(connection)
            executor.migrate([after])
            MigratedExperience = executor.loader.project_state([after]).apps.get_model('home', 'Experience')
            slugs = list(MigratedExperience.objects.filter(pk__in=records).values_list('slug', flat=True))
            self.assertTrue(all(slugs))
            self.assertEqual(len(set(slugs)), len(slugs))
            self.assertEqual(MigratedExperience.objects.get(pk=records[-1]).slug, 'talentbridge')
            self.assertNotEqual(MigratedExperience.objects.get(pk=records[-2]).slug, 'talentbridge')
        finally:
            MigrationExecutor(connection).migrate([after])
