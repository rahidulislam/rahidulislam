# Portfolio feature delivery

Requested scope: screenshot lightbox and desktop/mobile media, project search and Backend/Frontend/Full-stack/technology filters, engineering articles, experience details, real demo video, public architecture diagrams, English/Bangla preference, contact admin with read status/search and real email notifications, consent-controlled testimonials.

Verification must cover public routes and draft visibility, combined filters and empty/reset states, keyboard/lightbox focus, language preference and navigation, contact persistence and delivery failure, admin permission boundaries, media requests and browser layouts at desktop/mobile widths. Do not invent client feedback or production metrics.

Existing Ilmora screenshots are retained. New changes use codex/portfolio-features, based on the screenshot feature branch; the pending screenshot PR must be accounted for before integration. Local and remote main/dev start at 280a394.

## Implemented features

- `/projects/`: server-rendered combined query, work-type and technology filters; query values survive reload, with reset and empty state. Both managed and fallback projects participate, and hidden managed records suppress defaults. Work type and technology overrides are editable in Project admin.
- `/articles/` and `/articles/<slug>/`: three bilingual, source-grounded articles seeded idempotently. Admin supports drafts and publication, body text is escaped, and draft details return 404.
- `/experience/` and company detail routes: use the same live profile provider as the homepage and CV. No invented responsibilities or client outcomes.
- Captioned screenshot gallery: six real Ilmora images including mobile, attendance and fees; native dialog with Escape, arrow keys, previous/next controls and focus restoration. Original links still work without JavaScript. Public architecture diagrams cover all seven known projects.
- 72-second Ilmora demo walkthrough: actual deployed browser-local demo, WebM with native controls and a poster. No live institutional records or fake metrics.
- `/language/`: CSRF-protected POST, same-host redirects only, persistent English/Bangla cookie. Navigation, core UI, headings and seeded article content are translated. Technology names and owner-managed copy without a translation retain their original text.
- Contact admin: search, status/delivery filters, unread/read/replied state, mark actions and failed-notification retry. Saving the enquiry precedes the email attempt. Default console mail backend is for development; production requires authenticated SMTP settings.
- Testimonials: existing records are hidden until both `consent_to_publish` and `is_published` are checked. No fabricated feedback is seeded.

## Deployment

1. Run `python manage.py migrate` (0039 creates fields/Article; 0040 adds published articles without overwriting existing slugs).
2. Run `python manage.py collectstatic --noinput`; serve bundled screenshots, SVG diagrams, JS/CSS and WebM video through the static host. Ensure `.webm` uses `video/webm`.
3. Set SMTP environment variables from `.env.example` with an authenticated sender. `CONTACT_NOTIFICATION_EMAIL` is the recipient. Send a controlled enquiry and verify receipt before relying on production mail; local tests use an in-memory backend. `sent` means the configured mail backend accepted the message, not a guarantee of inbox delivery. Failed enquiries remain available for retry in admin.
4. Review articles and testimonials in Django admin. Obtain feedback owner's permission before setting consent/publication flags.

## Validation evidence

Fresh SQLite migrations succeeded. Browser flow at 1440px and 390px verified combined filters and reset, six decoded gallery images, keyboard lightbox/focus restoration, video playback, persistent Bangla article navigation, experience content, contact persistence and no horizontal overflow or JavaScript errors. Local browser contact row was `unread` / `sent` using the in-memory mail backend. SMTP production credentials were not assumed or inspected.

Rendered review screenshots live in `output/screenshots/`; product media lives in `static/img/projects/`, `static/img/architecture/` and `static/video/`.

## Reproduce the browser checks

Use a temporary local database and in-memory mail backend (never a production database):

```bash
DJANGO_DATABASE_PATH=/tmp/portfolio-review.sqlite3 venv/bin/python manage.py migrate
DJANGO_DATABASE_PATH=/tmp/portfolio-review.sqlite3 DJANGO_EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend venv/bin/python manage.py runserver 127.0.0.1:8097 --noreload
# In another terminal, with Playwright and its Chromium installed:
node scripts/verify_portfolio.cjs
```

`PLAYWRIGHT_MODULE` can point to an existing Playwright installation; `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` can select an installed Chromium. `PORTFOLIO_TEST_URL` defaults to the local URL above and rejects non-local hosts. The browser check creates one test enquiry. Backend validation is `venv/bin/python manage.py test home --noinput` (54 tests), followed by `manage.py check`, `manage.py makemigrations --check --dry-run` and `git diff --check`.
