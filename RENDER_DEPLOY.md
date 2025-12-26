# Render Deployment Guide for U-Notes

## 1. Prerequisites

- A GitHub/GitLab repository with your Django project pushed (including the new `render.yaml`).
- A Render account (https://render.com).

## 2. Deploy via Render Blueprint (Recommended)

1. Go to https://render.com/blueprint-dashboard
2. Click **New Blueprint Instance**
3. Select your Git repo where `render.yaml` exists
4. Render will auto-detect and provision the service (web, persistent disk, env vars)
5. **After creation**, update environment variables:
   - Go to your service Dashboard → **Environment**
   - Update `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` to your assigned Render URL (e.g., `u-notes-xyz.onrender.com`)
   - Click **Save** and Render will auto-redeploy
6. Visit your service URL (e.g., `https://u-notes-xyz.onrender.com`)

## 3. Manual Deployment (without Blueprint)

1. In Render Dashboard, click **New +** → **Web Service**
2. Select your Git repo
3. Configure:
   - **Name**: `u-notes`
   - **Runtime**: Python 3.13
   - **Build Command**: `pipenv install --system --deploy && python manage.py migrate && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn unotes_project.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120`
4. Add Environment Variables (same as `render.yaml`):
   - `DJANGO_SECRET_KEY`: auto-generated or strong random
   - `DJANGO_DEBUG`: `False`
   - `DJANGO_ALLOWED_HOSTS`: your Render URL
   - `DJANGO_CSRF_TRUSTED_ORIGINS`: `https://your-render-url.onrender.com`
   - `DJANGO_SQLITE_PATH`: `/var/data/db.sqlite3`
   - `DJANGO_MEDIA_ROOT`: `/var/data/media`
5. Add a Disk:
   - **Name**: `data`
   - **Mount Path**: `/var/data`
   - **Size**: 10 GB (or as needed)
6. Click **Create Web Service** and wait for deployment

## 4. Verify Deployment

- Check logs in Render Dashboard to confirm:
  - Database migrations ran
  - Static files collected
  - Service started successfully
- Visit your app URL in browser

## 5. Custom Domain (Optional)

1. Render Dashboard → Your Service → **Settings**
2. Scroll to **Custom Domains**
3. Add your domain (e.g., `unotes.yourdomain.com`)
4. Follow Render's DNS instructions to point your domain

## 6. Troubleshooting

- **Static files missing**: Ensure `collectstatic` runs in build command and WhiteNoise is installed
- **Media files lost after redeploy**: They're stored on the persistent disk; check if environment vars point to `/var/data`
- **Migrations not running**: Add `python manage.py migrate` to build command
- **500 error on startup**: Check logs; common issues are missing env vars or database errors

## 7. Next Steps

- Monitor logs in Render Dashboard
- Update `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` if using a custom domain
- Consider upgrading to PostgreSQL (managed database) for production stability
