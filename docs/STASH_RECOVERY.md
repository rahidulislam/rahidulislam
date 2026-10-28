# Recovery of local main work

Reviewed after release PR #35 was merged into main. The source stashes are local
recovery points and have been retained; their changes were not blindly reapplied.

| Local stash | Result |
| --- | --- |
| `5f3383f` — README edits before switching to dev | Recover the live site/admin links in README. |
| `06a3697` — recovery before syncing the release | Recover the matching links in deployment documentation; retain current implementations for the other changes. |

## Already integrated or superseded

- PublicContact model: implemented in `apps/contacts/models.py`; the only
  normalized class difference from the saved model is the explicit
  `home_publiccontact` database table used by the domain refactor.
- PublicContact admin: matches the saved class after normalizing Python formatting.
- Seed migration and PublicContact test class: match after normalizing formatting.
  The original 0044 migration and shared contact-links template match exactly.
- Context processor: now owned by `apps.contacts`, with a compatibility import
  under `home`; the saved processor is not needed again.
- Shared contact CSS block and footer markup are already present. Keep the newer
  HTMX contact form and asset versions rather than restoring old templates/tests.
- All 33 collected static asset files in the old stash are byte-identical to
  their tracked `static/` counterparts. Do not commit those generated
  `staticfiles/` copies or overwrite newer source CSS/JavaScript with them.

## Recovered in this change

Add the previously uncommitted `https://rahidulislam.dev/` live-site link and
`https://rahidulislam.dev/admin/` admin link to README and deployment documentation.
The two stashes contain the same README addition, so it is restored only once.

The original working-directory changes and stashes remain intact until the
recovery PR has been reviewed and merged. This recovery does not change the
database, generated assets, or production deployment.
