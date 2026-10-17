"""Exercise app ownership moves against existing tables, permissions, and admin history."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

DOMAINS = {
    "profiles": (
        "SocialMedia",
        "PersonalInfo",
        "Skill",
        "Interest",
        "Education",
        "Experience",
        "ExperienceBullet",
    ),
    "projects": (
        "Category",
        "Project",
        "ProjectImage",
        "EngineeringChallenge",
        "ProjectMetric",
        "ProjectVideo",
    ),
    "articles": ("Article",),
    "contacts": ("PublicContact", "Contact"),
    "portfolio": ("InformationCounter", "Testimonial", "Service"),
}


class DomainMigrationTests(TransactionTestCase):
    def migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        # Include independent auth/admin migrations already applied by the test runner.
        executor = MigrationExecutor(connection)
        return executor.loader.project_state(
            list(executor.loader.applied_migrations)
        ).apps

    def snapshot(self, apps, *, legacy):
        return {
            name: list(
                apps.get_model("home" if legacy else domain, name)
                .objects.order_by("pk")
                .values()
            )
            for domain, names in DOMAINS.items()
            for name in names
        }

    def test_existing_data_permissions_and_history_survive_forward_and_reverse(self):
        old_target = [(domain, None) for domain in DOMAINS] + [
            ("home", "0045_seed_public_contact")
        ]
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        old = self.migrate(old_target)
        try:
            category = old.get_model("home", "Category").objects.create(
                name="Migration category"
            )
            project = old.get_model("home", "Project").objects.create(
                category=category,
                name="Existing project",
                slug="existing-project",
                short_desc="Keep this",
            )
            old.get_model("home", "ProjectImage").objects.create(
                project=project, image="project/existing.png", caption="Keep image"
            )
            old.get_model("home", "ProjectVideo").objects.create(
                project=project, file="project/videos/existing.mp4"
            )
            old.get_model("home", "ProjectMetric").objects.create(
                project=project, label="Existing metric", value="42"
            )
            old.get_model("home", "EngineeringChallenge").objects.create(
                project=project, title="Existing challenge"
            )
            old.get_model("home", "PersonalInfo").objects.create(
                name="Existing owner",
                profession="Engineer",
                dob="1995-01-01",
                phone="+8801612061077",
                email="owner@example.com",
                age=31,
            )
            old.get_model("home", "SocialMedia").objects.create(
                name="GitHub", social_link="https://github.com/example"
            )
            old.get_model("home", "Skill").objects.create(name="Python", value=90)
            old.get_model("home", "Interest").objects.create(
                name="Reading", icon_name="book", icon_color="#ffffff"
            )
            old.get_model("home", "Education").objects.create(
                degree_name="BSc",
                start_year="2015",
                end_year="2019",
                description="Existing",
                institute="University",
                address="Dhaka",
            )
            exp = old.get_model("home", "Experience").objects.create(
                slug="existing-work",
                designation="Engineer",
                start_year="2020",
                end_year="Present",
                description="Existing",
                company="Example",
                address="Dhaka",
            )
            old.get_model("home", "ExperienceBullet").objects.create(
                experience=exp, text="Existing responsibility"
            )
            old.get_model("home", "InformationCounter").objects.create(
                happy_client=1, project=2, support=3, awards=4
            )
            old.get_model("home", "Service").objects.create(
                name="APIs", icon_name="code", description="Existing"
            )
            old.get_model("home", "Testimonial").objects.create(
                client_name="Colleague",
                designation="Engineer",
                review="Existing",
                consent_to_publish=True,
                is_published=True,
            )
            old.get_model("home", "Article").objects.create(
                title="Existing article",
                slug="existing-article",
                summary="Keep",
                body="Keep",
                topic="Django",
            )
            old.get_model("home", "Contact").objects.create(
                name="Visitor",
                email="visitor@example.com",
                subject="Existing",
                message="Keep private enquiry",
                notification_status="failed",
            )
            before = self.snapshot(old, legacy=True)
            ContentType = old.get_model("contenttypes", "ContentType")
            types = {}
            for names in DOMAINS.values():
                for name in names:
                    ct, _ = ContentType.objects.get_or_create(
                        app_label="home", model=name.lower()
                    )
                    types[name] = ct.pk
            ct = ContentType.objects.get(pk=types["Project"])
            Permission = old.get_model("auth", "Permission")
            perm, _ = Permission.objects.get_or_create(
                content_type=ct,
                codename="change_project",
                defaults={"name": "Can change project"},
            )
            group = old.get_model("auth", "Group").objects.create(
                name="Existing editors"
            )
            group.permissions.add(perm)
            user = old.get_model("auth", "User").objects.create(
                username="existing-editor", is_staff=True
            )
            user.groups.add(group)
            user.user_permissions.add(perm)
            log = old.get_model("admin", "LogEntry").objects.create(
                user=user,
                content_type=ct,
                object_id=str(project.pk),
                object_repr=project.name,
                action_flag=2,
                change_message="Existing history",
            )
            statements = []

            def record(execute, sql, params, many, context):
                statements.append(sql)
                return execute(sql, params, many, context)

            with connection.execute_wrapper(record):
                moved = self.migrate(latest)
            self.assertEqual(self.snapshot(moved, legacy=False), before)
            for domain, names in DOMAINS.items():
                for name in names:
                    self.assertEqual(
                        ContentType.objects.get(
                            app_label=domain, model=name.lower()
                        ).pk,
                        types[name],
                    )
            self.assertEqual(Permission.objects.get(pk=perm.pk).content_type_id, ct.pk)
            self.assertTrue(group.permissions.filter(pk=perm.pk).exists())
            self.assertTrue(user.user_permissions.filter(pk=perm.pk).exists())
            self.assertTrue(user.groups.filter(pk=group.pk).exists())
            self.assertEqual(
                old.get_model("admin", "LogEntry")
                .objects.get(pk=log.pk)
                .content_type_id,
                ct.pk,
            )
            ddl = [
                sql
                for sql in statements
                if sql.lstrip()
                .upper()
                .startswith(("DROP TABLE", "ALTER TABLE", "CREATE TABLE"))
            ]
            self.assertEqual(
                ddl, [], "Ownership migration must not rebuild or drop tables"
            )
            restored = self.migrate(old_target)
            self.assertEqual(self.snapshot(restored, legacy=True), before)
            self.assertEqual(ContentType.objects.get(pk=ct.pk).app_label, "home")
        finally:
            self.migrate(latest)
