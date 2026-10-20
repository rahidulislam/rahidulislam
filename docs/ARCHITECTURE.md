# Backend architecture

## Domains and ownership

| App | Owns |
| --- | --- |
| `apps.profiles` | PersonalInfo, SocialMedia, Skill, Interest, Education, Experience, ExperienceBullet; profile defaults and merging |
| `apps.projects` | Category, Project, ProjectImage, ProjectVideo, EngineeringChallenge, ProjectMetric; curated catalog, case studies, imports |
| `apps.articles` | Article; publication queries, safe Markdown rendering, editor admin |
| `apps.contacts` | Contact, PublicContact; enquiry validation, persistence, notification delivery and retry |
| `apps.portfolio` | InformationCounter, Service, Testimonial; homepage composition and SEO endpoints |
| `apps.resumes` | CV composition and PDF export; no database models |
| `core` | Localization HTTP utility, legacy admin URL and permission adapters |
| `rahidulislam` | Settings, root URLs, ASGI and WSGI |
| `home` | Frozen historical migrations, compatibility imports, public URL namespace and existing regression suite |

## Responsibilities and dependencies

Views handle HTTP, permissions, form errors, response status, and redirects. Forms validate untrusted input and retain existing localized messages. Selectors own reusable ORM reads and publication filters. Services own writes, transactions, and integration coordination. Models retain validation, relationships, slug generation, and persistent invariants. Admin CRUD continues to use Django's ModelAdmin lifecycle; custom business actions call services.

Presentation modules compose existing dictionaries for templates and PDF export. Their flexible dictionary shape is retained for template compatibility; new operation boundaries use explicit types and the immutable `EnquiryInput` dataclass. Selectors return model instances or typed querysets. This refactor does not introduce REST endpoints or an API schema.

Dependencies flow from portfolio/resume composition toward profiles and projects. Project case-study presentation consumes narrow profile selectors for shared identity. Contacts and articles do not depend on homepage composition. The `/contact/` handler uses the portfolio homepage view because GET and invalid POST must render the full homepage. Contact business rules remain in contacts. Domain code must never import `home` modules.

Use focused functions and the Django ORM. Avoid repository wrappers, generic service base classes, speculative interfaces, and empty service modules for read-only apps. Add services when a real operation needs one. New code imports the owning app, not a compatibility shim.

## Decisions and compatibility

- Keep `home:*` public URL names, paths, redirects, template paths, filenames, form fields, localized messages, publication filtering, and source-backed fallback behavior.
- Split broad profile/project loading: project listing does not load experience, education, or skills. Homepage and CV intentionally compose multiple domains.
- Keep the existing physical `home_*` tables. Domain initial migrations are state-only; `home.0046` removes legacy model state without executing table deletions.
- Transfer each existing ContentType row to its domain label in place. Its PK, permission PKs and grants, generic object references, and admin history remain stable. Each domain migration transfers ownership before post-migrate can create duplicate content types. Conflicting destination content types stop migration for investigation.
- Preserve `/admin/home/<model>/...` bookmarks and `admin:home_*` names with narrow URL aliases. New admin screens are grouped by domain. `core.auth.LegacyPermissionBackend` accepts legacy `home.<codename>` permission checks and normal new-domain checks without granting additional access. The original ModelBackend remains configured so existing authenticated sessions remain valid.
- Keep `home.models.validate_video_size` importable because a historical migration serializes that path. Do not delete historical migrations or shims until a separately reviewed migration-squashing plan removes those dependencies.
- Enquiries validate and persist atomically. Notifications run through `transaction.on_commit`, outside the write transaction. SMTP/network failure marks the saved enquiry failed; retry is an explicit admin operation. Unexpected programming/database failures propagate. Delivery remains synchronous after commit; no queue or dependency upgrade is introduced.
- Black and Ruff share root `pyproject.toml` configuration. Historical migrations 0001–0043 are frozen and excluded from formatting/lint; new migrations are checked. Ruff owns import ordering, replacing the separate isort runner.

## Verification

Install `requirements-dev.txt` and the Chromium browser used by the responsive regression tests, then run:

```sh
python -m playwright install --only-shell chromium
python scripts/check_backend.py
```

This runs Ruff, Black, Django checks, migration-drift checks, and the complete test suite. CI runs the same command on PRs and pushes to dev, staging, and main, including promotion PRs. SQLite is the configured production engine and is used in CI; change CI alongside settings if the production engine changes. There is no REST schema or TypeScript build to validate in this Django-template backend change.

Regression coverage includes real Chromium layout checks for mobile footer placement and header-menu behavior across article detail/list, homepage, and project pages at 320, 390, 760, 768, and 1024px, plus publication rules, localized forms, CV output, legacy redirects/admin paths, staff permissions, focused project queries, service validation, notification failure/retry, after-commit timing and rollback, and migration forward/reverse preservation of all domain tables, primary keys, relationships, permissions, and admin history. Migration tests reject table DDL during ownership moves. Test databases are migrated from scratch by Django.

Required GitHub check: **Backend quality gate**, bound to the GitHub Actions integration. The user-approved **Backend delivery standards** ruleset (ID `25285282`) is active for dev, staging, and main. It requires pull requests, resolved review threads, and the up-to-date backend check, and blocks force pushes and branch deletion. The staging branch does not yet exist; the rule will apply when it is created through the release workflow. Repository protection is external state and must be inspected again if policies change.

## Deployment and rollback

1. Back up the database using SQLite's backup API or stop writers before a file copy. Preserve uploaded media independently.
2. Enter a maintenance window and stop old application workers before migrating; old and new app labels should not serve traffic concurrently during ownership transfer.
3. Install unchanged runtime requirements, run `python manage.py migrate --noinput`, `python manage.py check`, and `python manage.py collectstatic --noinput`.
4. Start workers with the new code. Verify homepage, project/article visibility, CV download, footer contact links, staff permissions, and an enquiry delivery/retry.
5. Edit footer channels at **Admin → Contacts → Public contact details**. Empty fields are hidden. Telegram takes a username without `@`; phone and WhatsApp use international numbers.

For a code rollback, keep the refactored code installed while running:

```sh
python manage.py migrate articles zero
python manage.py migrate contacts zero
python manage.py migrate portfolio zero
python manage.py migrate profiles zero
python manage.py migrate projects zero
python manage.py migrate home 0045_seed_public_contact
```

Unapply every domain initial migration: targeting only `home.0045` does not unapply independent domain initials. This reverses domain ownership and content types while retaining physical tables and records. Then deploy the prior code (including the footer migrations if retained), run checks, and restart workers. Do not delete tables, remove migration records, fake migrations, or run `remove_stale_contenttypes` as a shortcut. Review destination conflicts and newly added domain migrations before rolling back a later release. The data-preserving ownership migration itself needs no database restore; keep the backup for operational recovery.
