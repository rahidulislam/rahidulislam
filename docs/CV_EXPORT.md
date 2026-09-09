# Automatic CV download

`/cv/download/` generates a fresh Europass-style PDF in memory using ReportLab. Both the homepage and PDF read `home.portfolio_data.get_portfolio_data()`. There is no upload or separate PDF replacement step, and responses use `Cache-Control: no-store`.

## Update content once

- Django admin profile fields override nonempty defaults: name, profession, address, email, phone, website and biography.
- GitHub and LinkedIn records in SocialMedia override the default links.
- Experience records replace matching default employers; new employers are added to both website and CV. Keep one active record per employer for unambiguous default replacement.
- Education and skills records replace their default lists when present.
- Projects are included alongside the curated case studies; matching project names replace curated summaries.
- When no admin content exists, `home/cv_profile.json` supplies profile/experience/skills defaults, and `home/portfolio_content.py` supplies curated projects. Updating these sources also updates the next download.
- Language descriptions live in `home/cv_profile.json`; no new proficiency is inferred.

Install `requirements.txt` and run `python manage.py migrate`. Migration 0021 corrects existing Wege records to Sep 2023–Jun 2024.

## Optional file export

`python scripts/export_cv.py` saves a snapshot to `output/pdf/Rahidul_Islam_Python_Developer_CV.pdf` using the same live content and renderer. This is useful for email attachments and the GitHub README link; the website download does not depend on this file. GitHub-hosted files cannot change until regenerated and pushed.

The PDF follows Europass-style sections but is not an official Europass-service export. Reference: https://europass.europa.eu/en/create-europass-cv
