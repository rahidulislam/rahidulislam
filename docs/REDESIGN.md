# Portfolio redesign

The old Bootstrap portfolio put generic freelance services, percentage skill bars, age/birthday, and client counters before technical work. The new presentation puts Python/Django positioning, recent project evidence, experience, skills, and contact in a linear page.

## Content and Germany positioning

- User-confirmed: Bangladesh; current role mid-level Python developer; beginner English and no German. No language level, relocation promise, visa eligibility, or right-to-work claim is published.
- Selected projects: TalentBridge, Smart Document Vault, HotelMotel, and this portfolio. See PROJECT_EVIDENCE.md for repository sources. These summaries establish code scope, not production usage or sole authorship.
- Previous employers and dates come from the original README; the open-ended 2023 role is labeled “Started Sep 2023” until an end date is confirmed.
- Germany is the stated target market, not a claimed current location. Current Django role listings were checked at https://www.arbeitsagentur.de/jobsuche/suche?angebotsart=1&suchbereich=jobs&was=Django&wo=Deutschland . No numerical hiring-market claims are made.

## Running locally

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

For this session dependencies were installed in `/tmp/portfolio-venv`. The preview is running on port 8000.

## Editing content

- Update profile, social links, work experience, education, additional projects, and skills in Django admin. Existing records remain intact.
- Featured repository case studies are in `home/portfolio_content.py`; they remain visible alongside admin-managed projects.
- Main style: `static/css/portfolio.css`; interactions: `static/js/portfolio.js`. Original vendor assets are preserved but no longer loaded.
- Print this portfolio uses browser print with a dedicated stylesheet. No pretend downloadable CV is shown.
- Contact requests are saved to the existing Contact model and can be read in admin. Email notifications are not configured.

## Validation and remaining setup

Django tests cover homepage defaults and database records, project detail links, valid/invalid contact persistence, all curated case-study routes, and missing-case 404 behavior. Browser review covers desktop, 390px mobile, navigation, and contact layout.

Before public deployment: confirm latest employer dates, add your preferred contact email and portrait in admin, and add approved public demo/source links and project screenshots. The repository still has its pre-existing development settings (DEBUG on, fixed development secret, old dependency pins); production configuration and dependency upgrades require a separate tested deployment pass. The redesign has not been deployed.

## Navy/Amber public theme (October 2026)

All public HTML pages share the theme in `static/css/color-scheme.css`, loaded
last after the structural portfolio styles. Dark surfaces use `#081321` and
`#101f33`, with `#f5b942` for actions. Light surfaces use `#f7f8fa` and white;
inline amber text uses a darker shade for contrast. Existing accent variable
names are retained as compatibility aliases for article and case-study styles.
The engineering illustration stays navy in both themes. Brand imagery and
semantic success/error colors retain their own meaning.

The theme switch preserves the `portfolio-theme` preference, follows the system
when no preference exists, and reapplies after HTMX navigation. Public layout
changes do not alter admin, generated resume/PDF styles, routes or contact data.
Edit source assets in `static/`; deployment collects generated static files.

Validation: `npm ci --ignore-scripts && npm run check` and
`python scripts/check_backend.py`. The theme browser regression covers stored
preferences, HTMX navigation and overflow at 320, 390, 768 and 1440 pixels in both
themes. Set `THEME_SCREENSHOT_DIR` to an external output directory when running
`python manage.py test apps.portfolio.tests.test_public_theme` to capture pages.
