# Deployment

The portfolio requires Python 3.12+, persistent storage for SQLite and uploaded
project media, and HTTPS. A host with a persistent disk is the simplest fit.
PythonAnywhere is suitable for this small Django portfolio; a VPS is appropriate
when more control is needed. Do not deploy SQLite or `media/` to an ephemeral
filesystem.

## Production checklist

1. Create a virtual environment and install `requirements.txt`.
2. Copy the variables from `.env.example` into the host's secret/environment
   settings. Generate `DJANGO_SECRET_KEY` with Django's
   `get_random_secret_key()` and never commit the generated value.
3. Point `DJANGO_DATABASE_PATH` and `DJANGO_MEDIA_ROOT` at persistent storage.
4. Run `python manage.py migrate` and `python manage.py collectstatic --noinput`.
5. Configure the host to serve `/static/` from `staticfiles/` and `/media/` from
   the persistent media directory. Start the WSGI app at `rahidulislam.wsgi`.
6. Attach the custom domain, enable HTTPS, and set both allowed-host and trusted-
   origin variables to the final domain.
7. Run `DJANGO_DEBUG=false ... python manage.py check --deploy` using the final
   environment before opening the site publicly.

Back up the SQLite database and media directory together. Test the contact form,
admin login, uploaded images/videos, project pages, and CV download after every
deployment. HSTS begins at one hour; raise it only after HTTPS and subdomains are
stable.

`rahidulislam.com` is the clearest primary domain if available. Redirect the
`www` hostname to the primary domain so employers see one canonical address.
