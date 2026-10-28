# Md. Rahidul Islam

**Mid Level Python Developer at TalentBridge**

Remote, Germany · June 2026–Present · Based in Bangladesh

I build REST APIs and Django applications for recruitment, document management, and hotel operations. My work focuses on data models, authentication, access control, and business workflows.

[Email](mailto:rahidulislam247@gmail.com) · [LinkedIn](https://www.linkedin.com/in/rahidulislam2023/) · [CV (PDF)](output/pdf/Rahidul_Islam_Python_Developer_CV.pdf)

[PythonAnywhere deployment guide](docs/deploy-pythonanywhere.md)

[AWS Lightsail deployment guide](docs/deploy-aws-lightsail.md)

## Selected work

| Project | Technical focus |
| --- | --- |
| [TalentBridge](https://github.com/rahidulislam/talentbridge) | Recruitment backend for candidates, employers, vacancies, shortlisting, and interviews. Python, Django REST Framework, PostgreSQL, Redis, and Celery. |
| [Smart Document Vault](https://github.com/rahidulislam/dms_saas) | Document-management API with workspace isolation, JWT authentication, document versions, and file scan states. Python and Django REST Framework. |
| [HotelMotel](https://github.com/rahidulislam/hotelmotel_saas) | Hotel operations backend covering rooms, guests, bookings, housekeeping, billing, and role-based access control. Python and Django. |
| [TheProperty](https://github.com/rahidulislam/realestate_property) | Multi-role marketplace with reviewed listings, buyer engagement, seller and agent workspaces, private identity documents, and production operations. Python, Django, and PostgreSQL. |
| [Homeopathic Management API](https://github.com/rahidulislam/homeopathic_ms) | Role-aware clinic backend for appointments, medical histories, prescriptions, medicine inventory, and billing. Python, Django REST Framework, and JWT. |
| [Ilmora — Madrasha Management](https://madrasha-backend.vercel.app/) | Completed bilingual React/TypeScript frontend with 58 management routes for admissions, students, attendance, fees, funds and administration. Browser-persisted demo with a future Django API adapter. |
| [Developer portfolio](https://github.com/rahidulislam/rahidulislam) | Django website with project case studies, admin-managed content, contact forms, and a downloadable CV. |

## Core skills

- **Backend:** Python, Django, Django REST Framework, REST APIs, JWT authentication
- **Data:** PostgreSQL, SQLite, Django ORM
- **Background tasks:** Celery, Redis
- **Web and tooling:** HTML, CSS, JavaScript, Git, GitHub

## Education

**Diploma in Computer Technology**

Noakhali Ideal Polytechnic Institute, Bangladesh · 2011–2015

## Opportunities

Interested in mid-level Python and Django roles with teams in Germany. For opportunities or questions about my work, contact [rahidulislam247@gmail.com](mailto:rahidulislam247@gmail.com).

## Backend development

Engineering standards live in [AGENTS.md](AGENTS.md). See [backend architecture and migration guidance](docs/ARCHITECTURE.md) for domain ownership, compatibility, deployment, and rollback. Install `requirements-dev.txt`, run `python -m playwright install --only-shell chromium` for browser tests (use `--with-deps` on a fresh Linux machine), and run `python scripts/check_backend.py` before submitting a PR to `dev`.

### Progressive navigation

Public links and forms use locally vendored HTMX 2.0.11 to replace `#page-shell`
without reloading the document. Page titles, canonical/social metadata, mobile
navigation, theme controls, and lightboxes are refreshed after navigation.
Downloads, lightbox links, and the language switch retain native behavior.
Contact forms retain Django validation and CSRF protection; submit buttons are
disabled while a submission is pending. JavaScript-free navigation still works.

HTMX history storage is disabled to avoid saving contact values and CSRF tokens
to localStorage. Back/forward navigation therefore reloads from the server.
The vendored library and Zero-Clause BSD license are in `static/vendor/htmx/`.
Run `python manage.py test apps.portfolio.tests.test_htmx_navigation` after
installing the development requirements and Playwright Chromium.

### Automatic Git delivery

Task completion includes checks, a meaningful commit, push, and GitHub PR creation
or reuse. The repository-local script requires Python and authenticated `gh`:

```bash
# Start before implementation, from a clean checkout
python scripts/git-deliver.py --start feature-task-name

# After implementation: use exact files belonging to this task
python scripts/git-deliver.py --files path/to/changed-file --message "fix: describe the actual change"
```

`.git-deliver.json` targets `dev` and runs the backend quality gate, including
delivery-script integration tests. Use the development Python environment.
See [the Bengali setup and reuse guide](docs/GIT_DELIVERY.bn.md) for installation,
other projects, and the difference between automatic delivery and merge approval.
The `Automatic Git delivery` section in `AGENTS.md` authorizes routine task
commits, pushes, and PR creation; merging still needs explicit authorization.
