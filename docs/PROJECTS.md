# Managing projects

Open `/admin/`, sign in with a staff account, then choose **Projects**. The admin dashboard uses the existing Django authentication; no public editing page is exposed.

For each project, enter its identity, recruiter facts, case-study narrative, optional live URL, featured image, and publication settings. Repository URLs are not rendered publicly because most source repositories are private. Set **Is published** to make a project public. Set **Is featured** to prioritize it on the homepage. Smaller order numbers appear first.

Use the **Project images** and **Project videos** inline rows on the same edit page to upload several files. Add captions and order numbers, then save. Video formats: MP4, WebM, OGV; maximum 50 MiB per video. Choose codecs supported by your visitors' browsers. The player has controls and no autoplay. Image uploads use Django ImageField validation.

- `/projects/` shows the complete published collection.
- The homepage shows up to three featured projects, or the first three published projects if none are featured.
- `/work/<slug>/` is the canonical project case-study URL.
- Legacy `/project/<id>/` URLs redirect to the canonical slug URL.
- Drafts are excluded from listing pages, detail pages, and generated CVs.
- Previously shared curated `/work/<slug>/` URLs redirect to their imported project record.

The current curated projects can be imported into another environment with:

```bash
python manage.py migrate
python manage.py import_portfolio_projects
```

The default import creates missing projects and preserves all existing admin edits. Preview changes without writing:

```bash
python manage.py import_portfolio_projects --dry-run
```

Explicitly refresh existing projects and matching child records from the curated Python data:

```bash
python manage.py import_portfolio_projects --update-existing
```

Combine both flags to preview an update. Projects are matched by stable slug, and challenges by title within the project. Metrics and image metadata are optional source collections. The importer never copies the private `solution` field for engineering challenges.

For deployment, configure persistent media storage and a web server or storage service for `/media/`; Django's development media serving is not a production media host. Back up both the database and uploaded media. A saved file extension does not guarantee a browser supports its video codec.

### Writing a case study

The **Case study** fieldset provides recruiter facts, contribution areas, constraints,
architecture, technical decisions, validation, outcome, and lessons. Blank sections are hidden. Use paragraphs to explain
the user need, your specific responsibility, choices and tradeoffs, delivered
capabilities, and what you would improve. Record measured results only when you
can substantiate them. Repository features do not establish individual ownership.

Curated copy is grounded in repository evidence and intentionally omits internal
business rules and security-sensitive details. Add screenshots and live URLs only
when they are safe for public viewing; keep a project as a draft while its evidence
is being reviewed.
