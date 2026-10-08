# Project evidence

These case studies are based on local repository implementation evidence. They do not establish deployment, production usage, business outcomes, or sole authorship.

| Case study | Sources inspected | Evidence-supported scope |
| --- | --- | --- |
| TalentBridge | `talentbridge/README.md`; `apps/candidates/models.py`; `apps/vacancies/models.py` | Django REST backend for candidates, skills, experience, employers, vacancies, and workflow-related fields. |
| Smart Document Vault | `dms_saas/README.md`; `PROJECT_CONTEXT.md`; `apps/documents/models.py` | Workspace-scoped document API with metadata, versioned files, and scan states. README notes some areas are not launch-complete. |
| HotelMotel | `hotelmotel_saas/apps/bookings/models.py`; hotel, room, housekeeping, and access-control models | Django applications/models for hotels, rooms, guests, bookings/stays, housekeeping, billing, and access control. No README was present. |
| Portfolio Website | This repository `README.md`; `home/models.py`; `home/views.py` | Django portfolio with database-backed content and persisted contact messages. |

No live status, metrics, production scale, client results, language proficiency, visa sponsorship, or exclusive ownership is claimed.

## V3 publication rules

- Homepage evidence is qualitative unless a `ProjectMetric` has a documented source.
- Featured screenshots identify the product interface; they do not prove deployment status or usage.
- Experience bullets describe contribution areas and validation practices without exposing private business rules.
- A missing live URL is rendered as an unavailable status, never as a placeholder link.
- Repository URLs remain private unless the project has an explicit public-source decision.

### DMS and TalentBridge showcase — 8 October 2026

Imported the user-provided assets from `/home/rahidulislam/Videos/dms-portfolio-2026-10-08` and `/home/rahidulislam/Videos/talentbridge-portfolio-2026-10-08` into tracked static assets. DMS includes four screenshots and an MP4 montage; TalentBridge includes six screenshots and an MP4 montage. Both use synthetic demo data. Source provenance notes are retained beside each screenshot set. The videos are screenshot montages, not recordings of live interactions or backend verification.

TalentBridge now uses its dashboard screenshot as the featured preview and `https://crm.tbcglobal.de/` as its live URL. Migration 0042 updates the existing database entry; curated defaults cover fresh installs and fallback pages.
