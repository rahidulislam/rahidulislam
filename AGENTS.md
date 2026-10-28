# Engineering and Delivery Standards

## 1. Professional code quality

- Write production-quality, maintainable code. Avoid beginner-level
  shortcuts, deprecated APIs, unsupported dependencies, and legacy patterns
  in new code.
- Follow established project conventions and supported framework patterns.
  Do not upgrade dependencies or rewrite working code without a clear need.
- Prefer clear names, cohesive modules, explicit contracts, and small,
  reviewable changes.
- Preserve existing behavior, public APIs, validation messages, permissions,
  data formats, and user data unless the task explicitly changes them.

## 2. SOLID principles

- Single responsibility: each function, class, component, and module should
  have one cohesive responsibility and reason to change.
- Open/closed: use composition and appropriate extension points to add
  behavior without repeatedly modifying unrelated logic.
- Liskov substitution: implementations and overrides must preserve their
  contracts, expected behavior, and guarantees.
- Interface segregation: expose focused interfaces; consumers should not
  depend on unrelated methods or large catch-all objects.
- Dependency inversion: business policies should depend on narrow
  interfaces rather than HTTP handlers, UI components, or vendor clients.
- Apply SOLID practically. Avoid unnecessary abstractions, interfaces,
  class hierarchies, and framework wrappers.

## 3. Architecture and maintainability

- Follow KISS, DRY, and YAGNI: keep solutions simple, centralize shared
  business knowledge, and avoid speculative features.
- Prefer composition over inheritance and high cohesion with low coupling.
- Separate presentation/transport, business rules, persistence, and
  external integrations.
- Keep views/controllers and UI components focused on their responsibilities.
- For Django projects, place business operations in services and reusable
  read queries in selectors. Enforce invariants in models and the database.
- Use explicit types and contracts at module and API boundaries.
- Avoid circular dependencies, hidden global state, and unexplained
  magic values.
- Document consequential architectural decisions and tradeoffs.

## 4. Security and data integrity

- Validate untrusted input at system boundaries.
- Enforce authorization on the server using least privilege and
  fail-closed behavior.
- Preserve tenant, organization, branch, and user isolation.
- Use parameterized queries and framework security protections.
- Never commit credentials or expose secrets in client bundles or logs.
- Keep related writes and audit records atomic.
- Preserve financial precision, concurrency controls, and idempotency.
- Make migrations reviewable and compatible with the deployment sequence.
  Obtain authorization before executing destructive data changes.

## 5. Errors, resources, and performance

- Handle specific errors at appropriate boundaries. Never silently hide
  failed operations or report success after a failed write.
- Log actionable diagnostics without exposing sensitive information.
- Clean up files, connections, subscriptions, timers, and requests.
- Handle cancellation and stale responses in asynchronous workflows.
- Avoid obvious N+1 queries, unbounded results, redundant requests, and
  unnecessary rendering.
- Measure before introducing complex optimizations or caching. Define
  cache invalidation when caching is needed.

## 6. Frontend standards

- Use ESLint for JavaScript/TypeScript and framework-specific rules.
  Required lint checks must pass without warnings.
- Use strict TypeScript where the project supports it; avoid unchecked
  casts and unjustified `any`.
- Keep rendering, reusable hooks, business logic, and API access separated.
- Follow React Hooks rules and correct effect dependency management.
- Preserve accessibility, semantic HTML, keyboard navigation, visible
  focus, responsive layouts, and localization.
- Provide explicit loading, empty, error, and success states.
- Preserve user-entered values and unsaved work during UI changes.

## 7. Backend standards

- Use Black for Python formatting and Ruff for lint/import checks.
  Keep formatter configuration consistent across local tools and CI.
- Follow supported framework conventions and keep HTTP handling separate
  from business operations.
- Enforce important data invariants with database constraints.
- Preserve API contracts, transaction boundaries, permissions, and
  audit behavior during refactoring.

## 8. Testing and PR quality gates

- Add focused regression tests for bug fixes and changed behavior.
- Test observable contracts rather than duplicating implementation details.
- Cover relevant success, failure, boundary, authorization, isolation,
  transaction, and concurrency scenarios.
- Keep tests deterministic. Mock external boundaries appropriately.
- Never weaken assertions, suppress valid lint findings, disable checks,
  or add unjustified skips to obtain passing results.
- Reject focused tests such as `.only` in CI.
- Run relevant checks before pushing and inspect CI on the latest PR commit.
- Every PR must run automated checks, including promotion PRs:
  - Frontend: ESLint, type checking, unit tests, production build,
    and relevant browser/integration tests.
  - Backend: Ruff, Black, framework checks, migration checks,
    unit/integration tests, and API/schema validation.
- Run database-specific tests against the production database engine in CI.
  Report locally skipped coverage honestly.
- Documentation-only changes may skip local application suites when
  executable configuration is unchanged; CI must still run.
- Never mark a PR ready to merge while required checks fail or remain pending.
- Configure GitHub branch protection/rulesets to require these checks.
- Report actual commands, results, skipped checks, and unresolved limitations.

## 9. Required Git and PR workflow

The promotion path is:

main <- staging <- dev <- isolated feature/fix branch

- `dev` integrates completed development work.
- `staging` validates release candidates.
- `main` contains production releases.
- Inspect repository instructions, Git status, and existing changes
  before editing.
- Start every feature, bug fix, refactor, or documentation task on a
  separate isolated branch from the latest remote `dev`.
- Use descriptive branch names such as:
  - `codex/feature-<name>`
  - `codex/fix-<name>`
  - `codex/refactor-<name>`
  - `codex/docs-<name>`
- Continue an existing branch only for follow-up work on the same task.
- Never implement directly on `dev`, `staging`, or `main`.
- Preserve unrelated user changes. Use an isolated worktree when needed.
- After completing a task:
  1. Review the final diff.
  2. Run relevant validation and fix task-caused failures.
  3. Stage only intended files.
  4. Create descriptive commits.
  5. Push the task branch.
  6. Create or update a PR targeting `dev`.
  7. Inspect checks and report the PR link and remaining issues.
- Promote releases only when requested:
  1. PR from `dev` to `staging`.
  2. Validate the release in staging.
  3. PR from `staging` to `main`.
- Never skip a promotion stage, force-push, rewrite published history,
  bypass protections, or merge without explicit user authorization.
- If a required branch, credential, permission, or tool is unavailable,
  preserve the work and report the exact blocker.
- A later explicit user instruction may override the default workflow
  for a specific task.

## 10. Documentation and handoff

- Keep setup instructions, architecture documentation, API contracts,
  and verification records consistent with delivered changes.
- PR descriptions should explain the problem, resulting behavior,
  validation performed, and material risks or limitations.
- Do not commit secrets, dependency directories, generated builds,
  temporary files, or unrelated artifacts.
- Clearly distinguish completed work from pending checks or external
  dependencies. Never claim unrun checks passed.

## Project architecture

- Domain apps live in `apps/`: profiles, projects, articles, contacts, portfolio, resumes.
- Keep HTTP handling in views, read queries in selectors, business writes in services, and external clients in integrations.
- Use typed boundaries and focused functions; avoid generic base services or ORM repository wrappers.
- `home` retains historical migrations and compatibility imports only. Do not add new business logic there.
- Preserve existing tables, records, URL names, localization, and admin access when moving models.
- Run `python scripts/check_backend.py` for the backend quality gate.

## Automatic Git delivery

For code or documentation implementation tasks in this repository, the user
authorizes the assistant to run configured checks, create meaningful commits,
push the task branch, and create or update its GitHub pull request without
asking separately for those routine steps. Apply this only to the current task;
preserve unrelated work. Questions, planning, and code reviews alone do not
authorize implementation or publishing.

- Read `.git-deliver.json` and the repository instructions first. If the config
  does not exist, initialize it and configure real project checks before delivery.
- Before implementation, use `python scripts/git-deliver.py --start feature-DESCRIPTIVE-TASK`
  on a clean checkout, or continue a suitable existing task branch. If unrelated
  changes exist, use an isolated worktree. Do not stage or stash someone else's work.
- After implementation, review the diff, write a concrete commit message and a
  reviewer-facing PR description, then run:
  `python scripts/git-deliver.py --files EXACT TASK FILES --message "TYPE: concrete change" --body-file /tmp/task-pr.md`
- Use explicit task files; `--all` is allowed only when every nonignored change
  belongs to the task. Run additional checks required by the repository even if
  they are not yet configured in `.git-deliver.json`.
- If the command fails, fix task-caused failures and retry. Never claim checks
  passed unless they actually ran successfully. Do not weaken checks or bypass
  branch protections. Stop and report unavailable credentials or permissions.
- Reuse an existing task PR. Check its CI and review state, attach created PRs
  when the host provides an attachment tool, and report its URL and any pending work.
- When the user requests a release promotion, use
  `python scripts/git-deliver.py --promote staging` for dev -> staging, or
  `--promote main` for staging -> main after staging validation. The script
  creates/reuses the PR without requiring a title/body or branch switch.
- After a requested PR has merged, or when the user requests remote sync, use
  `python scripts/git-deliver.py --sync dev staging` (or the requested branches).
  Default sync updates each local branch from its matching remote, without
  switching checkout, stashing, resetting, or pushing. If the user explicitly
  requests cross-branch alignment, use `--sync TARGET --sync-source SOURCE`;
  add `--push-sync` only when remote alignment is authorized. Report protection
  rejection honestly; equal code trees do not imply identical commit history.
- Do not force-push, rewrite published history, merge PRs, promote a release,
  or deploy without the user's explicit authorization for that action.
- Explicit user requests such as "local only", "do not commit", or
  "do not push" override automatic delivery for that task.

This rule applies when an assistant is working on a task. It is not a background
watcher and does not run on every file save.
