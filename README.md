# U-Notes Deployment Guide

This guide shows how to deploy the Django app to the internet using two approaches:

## Option A: Managed Hosting (Render)

1. Push your project to a Git repository (GitHub/GitLab).
2. Create a new **Render Web Service** from the repo.
3. Set **Build Command**: `pipenv install --system --deploy && python manage.py collectstatic --noinput`
4. Set **Start Command**: `gunicorn unotes_project.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120`
5. Add environment variables:
   - `DJANGO_SECRET_KEY`: strong random string
   - `DJANGO_DEBUG`: `False`
   - `DJANGO_ALLOWED_HOSTS`: `yourservice.onrender.com`
   - `DJANGO_CSRF_TRUSTED_ORIGINS`: `https://yourservice.onrender.com`
6. Render will provision a public URL with TLS automatically.

Notes:
- For persistent file uploads, use an external storage (e.g., S3) instead of local `media/`.
- For production database, prefer PostgreSQL (Render offers managed Postgres).

## Option B: VPS (Ubuntu + Nginx + Gunicorn)

1. SSH into your server and install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   pip install pipenv gunicorn
   ```
2. Copy project to server (e.g., `/var/www/unotes/app`) and create directories:
   ```bash
   sudo mkdir -p /var/www/unotes/{app,staticfiles,media}
   sudo chown -R www-data:www-data /var/www/unotes
   ```
3. Configure environment variables in `/var/www/unotes/env` (optional):
   ```bash
   DJANGO_SECRET_KEY=your-secret
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```
4. Install app deps and collect static:
   ```bash
   cd /var/www/unotes/app
   pipenv install --system --deploy
   python manage.py collectstatic --noinput
   ```
5. Configure Gunicorn with systemd:
   - Place `deploy/gunicorn.service` into `/etc/systemd/system/gunicorn.service` and edit paths.
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable gunicorn
   sudo systemctl start gunicorn
   sudo systemctl status gunicorn --no-pager
   ```
6. Configure Nginx:
   - Copy `deploy/nginx.conf` to `/etc/nginx/sites-available/unotes` and edit `server_name` and paths.
   ```bash
   sudo ln -s /etc/nginx/sites-available/unotes /etc/nginx/sites-enabled/unotes
   sudo nginx -t
   sudo systemctl reload nginx
   ```
7. DNS and TLS:
   - Point your domain's A record to the server IP.
   - Install Let's Encrypt TLS:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

## Local quick run
```bash
pipenv install gunicorn
python manage.py collectstatic --noinput
pipenv run gunicorn unotes_project.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
```

## Environment Variables
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`
- Optional security flags auto-enabled when `DJANGO_DEBUG=False` (HSTS, secure cookies, SSL redirect).

## Storage & Database
- Local `media/` is fine on a single VPS; on managed platforms use S3-like storage.
- SQLite is okay for small demos; prefer PostgreSQL in production.
