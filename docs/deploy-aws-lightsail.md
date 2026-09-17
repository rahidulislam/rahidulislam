# Deploy to AWS Lightsail

This guide deploys the portfolio to an Ubuntu Lightsail instance with Nginx,
Gunicorn, systemd, SQLite, persistent media, and Let's Encrypt HTTPS. Local
development and the existing PythonAnywhere deployment remain unchanged.

The examples use `rahidulislam.com`, the `ubuntu` instance user, and
`/srv/rahidulislam`. Replace the domain if necessary before copying the Nginx
and environment templates.

## 1. Create the instance

1. Create an Ubuntu 24.04 LTS Lightsail instance.
2. Create and attach a static IP before configuring DNS. A normal public IP can
   change when an instance is stopped and started.
3. In the instance Networking tab, allow TCP ports 80 and 443 from the internet.
   Restrict TCP port 22 to your own IP address when practical.
4. Point the domain's `A` records for `@` and `www` to the static IP.

Do not open Gunicorn or database ports publicly. Nginx is the only public
application entry point.

## 2. Install system packages

Connect over SSH and run:

```bash
sudo apt update
sudo apt install -y git nginx python3-venv python3-pip certbot python3-certbot-nginx
```

## 3. Create the application and data directories

```bash
sudo mkdir -p /srv/rahidulislam /var/lib/rahidulislam/media
sudo chown -R ubuntu:www-data /srv/rahidulislam /var/lib/rahidulislam
sudo chmod 750 /var/lib/rahidulislam
cd /srv/rahidulislam
git clone https://github.com/rahidulislam/rahidulislam.git current
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r current/requirements.txt
```

The SQLite database and uploaded media live under `/var/lib/rahidulislam`, not
inside the Git checkout. Updating or rolling back code therefore does not
replace production data.

## 4. Configure secrets

Copy the versioned example, generate a unique key, and edit the resulting root-
owned file:

```bash
sudo cp /srv/rahidulislam/current/deploy/lightsail/rahidulislam.env.example /etc/rahidulislam.env
sudo chmod 600 /etc/rahidulislam.env
/srv/rahidulislam/venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
sudo nano /etc/rahidulislam.env
```

Paste the generated value into `DJANGO_SECRET_KEY`. Confirm the final domain in
`DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS`. Never commit
`/etc/rahidulislam.env`.

For the first HTTP-only smoke test, temporarily set
`DJANGO_SECURE_SSL_REDIRECT=false`. Change it to `true` immediately after the
certificate is installed.

## 5. Initialize Django

Load the environment without printing it, then migrate and collect static files:

```bash
set -a
source /etc/rahidulislam.env
set +a
cd /srv/rahidulislam/current
/srv/rahidulislam/venv/bin/python manage.py migrate
/srv/rahidulislam/venv/bin/python manage.py collectstatic --noinput
/srv/rahidulislam/venv/bin/python manage.py check --deploy
```

The deployment check will warn that HSTS preloading is disabled. That is
intentional during the initial rollout; do not enable preload until the domain
and all subdomains have served HTTPS reliably for an extended period.

Create an admin only if one does not already exist:

```bash
/srv/rahidulislam/venv/bin/python manage.py createsuperuser
```

## 6. Install systemd and Nginx configuration

```bash
sudo cp deploy/lightsail/rahidulislam.service /etc/systemd/system/rahidulislam.service
sudo cp deploy/lightsail/nginx.conf /etc/nginx/sites-available/rahidulislam
sudo ln -s /etc/nginx/sites-available/rahidulislam /etc/nginx/sites-enabled/rahidulislam
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl daemon-reload
sudo systemctl enable --now rahidulislam
sudo systemctl reload nginx
```

Verify both services before requesting a certificate:

```bash
sudo systemctl --no-pager --full status rahidulislam
sudo systemctl --no-pager --full status nginx
curl -I -H 'Host: rahidulislam.com' http://127.0.0.1/
```

Use `sudo journalctl -u rahidulislam -n 100 --no-pager` if Gunicorn does not
start.

## 7. Enable HTTPS

After DNS resolves to the static IP:

```bash
sudo certbot --nginx -d rahidulislam.com -d www.rahidulislam.com
sudo certbot renew --dry-run
sudo sed -i 's/DJANGO_SECURE_SSL_REDIRECT=false/DJANGO_SECURE_SSL_REDIRECT=true/' /etc/rahidulislam.env
sudo systemctl restart rahidulislam
```

Choose the HTTPS redirect when Certbot offers it. Keep HSTS at 3600 seconds
until HTTPS and every included subdomain have been stable. Then it can be raised
deliberately through `DJANGO_SECURE_HSTS_SECONDS`.

## 8. Deploy updates

Back up data before every deployment:

```bash
sudo install -d -m 750 -o ubuntu -g www-data /var/backups/rahidulislam
sudo cp --preserve=timestamps /var/lib/rahidulislam/db.sqlite3 /var/backups/rahidulislam/db-$(date +%Y%m%d-%H%M%S).sqlite3
sudo tar -C /var/lib/rahidulislam -czf /var/backups/rahidulislam/media-$(date +%Y%m%d-%H%M%S).tar.gz media
```

Then update safely:

```bash
cd /srv/rahidulislam/current
git fetch --prune
git pull --ff-only
/srv/rahidulislam/venv/bin/pip install -r requirements.txt
set -a; source /etc/rahidulislam.env; set +a
/srv/rahidulislam/venv/bin/python manage.py migrate
/srv/rahidulislam/venv/bin/python manage.py collectstatic --noinput
/srv/rahidulislam/venv/bin/python manage.py check --deploy
sudo systemctl restart rahidulislam
sudo systemctl reload nginx
```

Verify the homepage, project pages, admin login, contact form, media uploads, and
CV download after deployment.

## Rollback

Record the previous Git revision before updating with `git rev-parse HEAD`. To
roll code back, check out that known revision, reinstall its requirements, run
`migrate`, collect static files, and restart the service. Restore the database
backup only when a migration changed data incompatibly; code rollback alone is
safer for most releases.

```bash
cd /srv/rahidulislam/current
git checkout PREVIOUS_COMMIT
/srv/rahidulislam/venv/bin/pip install -r requirements.txt
set -a; source /etc/rahidulislam.env; set +a
/srv/rahidulislam/venv/bin/python manage.py migrate
/srv/rahidulislam/venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart rahidulislam
```

## Operations

```bash
sudo systemctl restart rahidulislam
sudo systemctl reload nginx
sudo journalctl -u rahidulislam -f
sudo nginx -t
```

Create scheduled Lightsail snapshots and copy `/var/lib/rahidulislam` backups
off the instance. A snapshot is useful for disaster recovery but is not a
replacement for a separate database and media backup.
