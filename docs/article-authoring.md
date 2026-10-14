# Article authoring

Open Django admin → Articles → Add or select an article.

1. Set the English title, unique slug, topic and introduction. Add Bengali translations when available; empty translations use the English content.
2. Upload a cover image (a landscape 16:9 image works best). Describe it in Image alt and optionally add a caption. Articles without a cover use the local engineering illustration.
3. Write content using the formatting toolbar. Select text before applying Bold, Italic or Link. Heading, List, Quote and Code insert Markdown. Preview uses the same safe server renderer as the published article. Raw HTML is escaped.
4. To insert an inline image, use Image and replace the example URL with an uploaded cover's media URL or a trusted HTTPS image URL. Add meaningful image description text between the brackets.
5. Add a source reference and publication date; enable Is published when ready, then Save. Preview does not save or publish changes. Save before navigating away.

The public library supports search in English/Bengali titles and summaries and exact topic filters. Reading time uses the longer language body at 200 words/minute; related articles show published entries sharing the same topic.

Deployment: install requirements, run `python3 manage.py migrate`, then `python3 manage.py collectstatic --noinput`. Ensure persistent media storage and serving are configured for uploaded covers.
