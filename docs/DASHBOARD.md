# Portfolio workspace

The owner workspace is served at `/dashboard/`. Sign in with an existing **active superuser**. Staff accounts and public users cannot access content, inbox, preview or analytics endpoints. `/admin/` and all public URL names remain available. Dashboard responses use `private, no-store` and `noindex, nofollow`; HTMX history storage is disabled.

## Install and operate

1. Install the existing Python requirements. No new production Python dependencies are required.
2. Back up the database, then run `python manage.py migrate`. The additive analytics migration creates new tables without moving existing content.
3. Run `python manage.py collectstatic --noinput` for the deployment's existing static serving setup. Dashboard assets and the already vendored HTMX library are included.
4. Visit `/dashboard/login/`. If there is no owner account, run `python manage.py createsuperuser` on the deployment host. Never put passwords into source code or command arguments.
5. Schedule `python manage.py purge_analytics` **daily**, using the deployment's virtualenv and environment. For example, add `15 2 * * * cd /absolute/path/to/project && /absolute/path/to/venv/bin/python manage.py purge_analytics` to the host's cron, or use a PythonAnywhere daily scheduled task with the same command. Configure this explicitly on the deployment host; installing code does not install a scheduler.

Roll out the migration before serving the new code. If application code is rolled back, retain the analytics tables so traffic history is not destroyed. No deployment or production migration is performed by this PR.

## Content and inbox

The sidebar exposes allowlisted domain models through dedicated ModelForms. Projects include separate related-content screens for images, videos, engineering challenges and metrics; open them from the saved project's editor. Experience details work the same way. Existing model validation, slug generation, publication and testimonial consent behavior are preserved. Public contact details remain a single editable record and cannot be deleted through the workspace.

Forms retain entered text after validation errors. Native browser navigation and saving work without JavaScript. HTMX enhances navigation; JavaScript additionally provides unsaved-change confirmation and safe Markdown previews of either language without saving. A selected upload must be reselected after a validation response, as browsers do not repopulate file inputs.

Every successful dashboard content write/deletion and inbox status change writes a standard Django admin `LogEntry` in the same database transaction. Audit messages contain changed field names, not submitted field values. Newly stored uploads are removed if that transaction fails. Existing media files are retained on replacement/deletion, matching Django's storage lifecycle and avoiding accidental removal of shared assets.

Opening an enquiry does not change its status. Use **Mark read** or **Mark replied** explicitly. **Retry failed notification** records a retry request and attempts the existing owner notification email; failures remain visible and retryable. It does not send a reply to the visitor. Configure SMTP using the existing deployment environment variables.

CV preview/download use the current live CV generator. Source-backed defaults in `cv_profile.json`, project catalogs and existing presentation fallbacks keep their current behavior; they are not editable files in the dashboard. Database content remains the editable override source used by the public site. Deleting an override can reveal a source-backed default again.

## Analytics definitions and privacy

- A page view is a successful anonymous `GET` of a resolved public HTML page. Redirects, errors, assets, downloads, management pages, known bot/preview agents, signed-in users and requests carrying `preview` are excluded. Counts are estimates; bot detection is deliberately a small heuristic rather than an external service.
- Middleware records each qualifying response once. Boosted HTMX navigation and history restoration count once; non-navigation HTMX fragments do not count. Refreshes are new page views. No browser beacon is used, so JavaScript is not required and duplicate browser/server events cannot occur.
- Estimated daily visitors use an HMAC of the connection IP and a bounded user-agent value, with a date-specific salt and Django's secret. Only the resulting daily hash is stored. No cross-day visitor ID, cookie, raw IP or full user agent is stored. Shared networks/devices, changing user agents and IPs affect accuracy. A range's **visitor-days** is the sum of daily estimates, not a count of unique people across that range.
- Query strings are dropped. Only the referrer's domain is retained, without userinfo, path or query. Internal/missing/invalid referrers appear as **Direct / internal / unknown**. No geolocation or returning-visitor claims are made.
- Dates use Django's existing `TIME_ZONE` (UTC). Reports offer 7/30/90 days and custom inclusive ranges up to 366 days. The first recorded visit establishes the available history; earlier dates display **No data**, not invented historical metrics. Missing days after tracking begins are zero-filled.
- `PageView` details and `DailyVisitor` hashes expire after 90 days when the daily purge command runs. Anonymous per-day page/referrer/traffic aggregates remain. The retention cutoff keeps the boundary day and purges strictly older dates.
- `ANALYTICS_TRUSTED_PROXIES` is empty by default. Only set it to comma-separated, exact IP addresses of proxies you control. The right-to-left forwarded chain stops at the first untrusted hop. Never trust arbitrary client-supplied forwarding headers. With no trusted proxy configuration, the socket peer is used and proxy traffic may be undercounted.
- Analytics writes are atomic. Database failures log a generic warning without event parameters and do not interrupt the public page. Investigate repeated warnings, run migrations, check database permissions, and check that the daily retention task succeeds. This synchronous, database-backed approach fits the portfolio's current traffic and SQLite deployment.

## Development and verification

Use a supported Node.js 24 environment and the existing Python virtualenv:

```bash
npm ci --ignore-scripts
npm run check
python scripts/check_dashboard_assets.py
python scripts/check_backend.py
```

`npm run check` runs ESLint without accepted warnings and strict TypeScript checking of the dashboard's JavaScript. There is no frontend bundler: assets are served directly; `check_dashboard_assets.py` verifies production collection into a temporary directory without touching tracked `staticfiles/`. Backend tests include Playwright desktop/mobile, JavaScript-free CRUD, Markdown preview, validation, unsaved edits, inbox updates, analytics navigation/privacy/retention, access control, CSRF, audit rollback and upload cleanup. Install Playwright Chromium as described in the main README before running the suite.

CI runs these frontend/asset checks within **Backend quality gate**, followed by the existing backend checks and browser suites. SQLite remains the configured production engine and CI database. Require the existing Backend quality gate status on protected branches; no separate unchecked frontend status is introduced.

## Site branding

Open **Site content → Site branding**, add the settings once, and save. **Brand name** supplies the accessible logo text and the text fallback. Upload **Logo for light backgrounds** for the public header/footer; optionally upload a light-coloured **Logo for dark backgrounds** for dark mode. Without a dark variant the regular logo keeps a white backing for contrast. With no regular logo, the site uses the brand text and the default mark. Upload tightly cropped PNG, JPEG or WebP images up to 2 MiB; SVG uploads are not accepted.

**Site icon** changes the browser tab icon on public pages and the dashboard. Use a square image at least 32 × 32 pixels (256 × 256 PNG recommended). Save, then reload the public page; boosted public navigation also refreshes the icon metadata. Browsers can cache favicons, so refresh the tab if needed. Use each field's **Clear** checkbox and save to restore text/default icon fallbacks. The settings are a database-constrained singleton and cannot be deleted from the dashboard or admin. Deploy the new portfolio migration before serving templates using these settings.
