# Managing projects

Open `/admin/`, sign in with a staff account, then choose **Projects**. The admin dashboard uses the existing Django authentication; no public editing page is exposed.

For each project, enter a title, category, short summary, full description, features (one per line), optional live URL and source URL, featured image, and optional client/date. Set **Is published** to make it public. Set **Is featured** to prioritize it on the homepage. Smaller order numbers appear first.

Use the **Project images** and **Project videos** inline rows on the same edit page to upload several files. Add captions and order numbers, then save. Video formats: MP4, WebM, OGV; maximum 50 MiB per video. Choose codecs supported by your visitors' browsers. The player has controls and no autoplay. Image uploads use Django ImageField validation.

- `/projects/` shows the complete published collection.
- The homepage shows up to three featured projects, or the first three published projects if none are featured.
- `/project/<id>/` shows descriptions, links, images, and videos.
- Drafts are excluded from listing pages, detail pages, and generated CVs.
- Previously shared curated `/work/<slug>/` URLs redirect to their imported project record.

The current curated projects have been imported into the local database. For another environment run `python manage.py migrate` followed by `python manage.py import_portfolio_projects`. The import does not overwrite existing project records.

For deployment, configure persistent media storage and a web server or storage service for `/media/`; Django's development media serving is not a production media host. Back up both the database and uploaded media. A saved file extension does not guarantee a browser supports its video codec.

### Writing a case study

The **Case study** fieldset provides Problem, Contribution, Technical decisions,
Outcome, and Lessons fields. Blank sections are hidden. Use paragraphs to explain
the user need, your specific responsibility, choices and tradeoffs, delivered
capabilities, and what you would improve. Record measured results only when you
can substantiate them. Repository features do not establish individual ownership.

Initial copy for the four existing projects is grounded in the local backend
repositories and this portfolio. The data migration fills empty fields without
overwriting existing case-study text. Edit this copy directly in admin afterward.

The initial repository links point to the matching repositories under the
`rahidulislam` GitHub account. Add screenshots and live URLs only when they are
safe for public viewing; keep a project as a draft while its evidence is being
reviewed.
