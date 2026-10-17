# Backend refactor verification — 17 October 2026

## Completed locally

- `python scripts/check_backend.py`: passed. Runs `python -m ruff check .`, `python -m black --check .`, `python manage.py check`, `python manage.py makemigrations --check --dry-run`, and `python manage.py test --noinput`.
- Full suite: **78 tests passed**, including fresh database installation, publication/access rules, existing public routes and admin aliases, both authentication backend session paths, contact timing/rollback/failure/retry, structured profile metadata, and forward/reverse app ownership migrations.
- Migration drift: **no changes detected**. Django framework checks: **no issues**.
- `git diff --check`: passed.
- Disposable upgrade of a SQLite backup of the existing local database: **all rows in all 19 domain tables preserved**; Django checks passed afterward. The original database was not modified.
- Migration regression also verifies all domain model data/PKs, relationships, content-type identities, permission identities and grants, and admin-log references. No table CREATE/ALTER/DROP occurs during ownership moves. Reverse migration preserves the same data.
- Historical home migrations 0001–0043 remain unchanged. New migrations are formatted and linted.
- SQLite matches the production engine in settings and deployment templates. No other database engine was tested.

## Repository delivery

- Branch: `codex/refactor-backend-structure`, created in an isolated managed worktree from fetched `origin/dev`.
- The existing footer feature was carried into the refactor. The original main checkout and unrelated user changes were preserved.
- `AGENTS.md` contains the supplied Engineering and Delivery Standards plus project-specific architecture guidance.
- CI runs the backend gate for PRs and pushes to dev, staging, and main, with promotion-source validation for release PRs.
- With explicit user approval, GitHub ruleset **Backend delivery standards** (ID `25285282`) was created and verified active. It requires PRs and the GitHub Actions **Backend quality gate** on dev/staging/main, requires resolved review threads, and prevents force pushes/deletion. Staging is currently absent; no release branch was created and no promotion was performed.
- PR CI status must be inspected on the pushed head. This local record is not a claim that remote CI passed or that the PR was merged.

## Scope and operational limits

There is no REST API schema, TypeScript application, frontend build, or new external integration to validate in this backend refactor. Tests use an in-memory email backend and mocked transport failure; no real email was sent. No production deployment or production database migration was performed. Deployment and rollback require matching code and migration state; follow `ARCHITECTURE.md`.
