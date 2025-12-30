# Render Deployment Guide for U-Notes

## Table of Contents
1. [Quick Start (5 minutes)](#quick-start)
2. [Detailed Setup](#detailed-setup)
3. [Troubleshooting](#troubleshooting)
4. [Post-Deployment](#post-deployment)

---

## Quick Start

### Prerequisites
- GitHub or GitLab account
- Render account (free tier available: https://render.com)
- Your U-Notes repository pushed to GitHub/GitLab

### Step-by-Step Deployment

#### 1. **Connect Your Repository to Render**
   1. Go to https://render.com
   2. Sign up/Login
   3. Click **"New +"** → **"Web Service"**
   4. Connect your GitHub/GitLab account
   5. Select your U-Notes repository

#### 2. **Configure the Web Service**
   ```
   Name: u-notes
   Runtime: Python 3.13
   Build Command: pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   Start Command: gunicorn unotes_project.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --worker-class sync --timeout 120
   ```

#### 3. **Add Environment Variables**
   Go to **Dashboard** → **Your Service** → **Environment**
   
   | Key | Value | Auto-Generate |
   |-----|-------|---|
   | `DJANGO_SECRET_KEY` | Leave empty | ✓ Yes |
   | `DJANGO_DEBUG` | `False` | |
   | `DJANGO_ALLOWED_HOSTS` | `*` | |
   | `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com` | |
   | `DJANGO_SECURE_SSL_REDIRECT` | `True` | |
   | `DJANGO_SESSION_COOKIE_SECURE` | `True` | |
   | `DJANGO_CSRF_COOKIE_SECURE` | `True` | |

#### 4. **Add Persistent Disk**
   1. Go to **Disks** tab
   2. Click **"Add Disk"**
   3. Configure:
      - **Name**: `data`
      - **Mount Path**: `/var/data`
      - **Size**: 10 GB

#### 5. **Deploy**
   1. Click **"Create Web Service"**
   2. Wait 5-10 minutes for deployment to complete
   3. Check **Logs** tab to monitor build progress

#### 6. **Verify Deployment**
   - Your app URL will be: `https://u-notes-xxxxx.onrender.com`
   - Check the **Logs** tab for any errors
   - Visit your URL and log in to verify it works

---

## Detailed Setup

### Using Blueprint (Recommended)

If `render.yaml` is in your repository:

1. Go to https://render.com/blueprint-dashboard
2. Click **"New Blueprint Instance"**
3. Select your repository
4. Render auto-configures everything from `render.yaml`
5. Update `DJANGO_SECRET_KEY` after deployment (Render generates one automatically)

### Manual Setup (Alternative)

Follow the Quick Start steps above for full control.

---

## Environment Variables Explained

### Required
- **`DJANGO_SECRET_KEY`**: Encryption key for Django (Render auto-generates)
- **`DJANGO_DEBUG`**: Must be `False` in production
- **`DJANGO_ALLOWED_HOSTS`**: Your domain(s) (e.g., `u-notes.onrender.com`)

### Security (Render automatically enables these)
- **`DJANGO_SECURE_SSL_REDIRECT`**: Forces HTTPS (`True`)
- **`DJANGO_SESSION_COOKIE_SECURE`**: Secure cookies (`True`)
- **`DJANGO_CSRF_COOKIE_SECURE`**: CSRF token protection (`True`)
- **`DJANGO_CSRF_TRUSTED_ORIGINS`**: Allowed cross-origin requests

### Optional
- **`OPENAI_API_KEY`**: For enhanced AI features (leave empty to use free features)
- **`EMAIL_HOST`**, **`EMAIL_PORT`**: For email notifications

---

## Database & File Storage

### SQLite Database
- **Location**: `/var/data/db.sqlite3` (persists across deployments)
- **Auto-Backup**: Consider exporting backups regularly
- **Performance**: Good for small-to-medium apps (up to 10K users)

### Media Files (Uploads)
- **Location**: `/var/data/media` (persists across deployments)
- **Includes**: User-uploaded documents, voice notes, etc.
- **Size Limit**: Based on disk allocation (default: 10 GB)

---

## Troubleshooting

### Build Fails
**Error**: `Command exited with non-zero code`

**Solution**:
1. Check **Logs** tab for specific error
2. Ensure `requirements.txt` has all dependencies
3. Verify Python version is 3.13+
4. Run `pip install -r requirements.txt` locally to test

### Static Files Not Loading
**Error**: CSS/JavaScript files return 404

**Solution**:
1. Ensure build command includes: `python manage.py collectstatic --noinput`
2. Check `STATIC_ROOT = BASE_DIR / 'staticfiles'` in settings.py
3. Verify WhiteNoise middleware is in `MIDDLEWARE` list

### Database Migrations Fail
**Error**: Migration error during build

**Solution**:
1. Check **Logs** for migration errors
2. Run migrations locally: `python manage.py migrate`
3. Commit migra files to repository
4. Redeploy: Click **"Manual Deploy"** on Render dashboard

### CSRF or SSL Certificate Errors
**Error**: 403 Forbidden or SSL/TLS errors

**Solution**:
1. Update `DJANGO_ALLOWED_HOSTS` to include your Render URL
2. Update `DJANGO_CSRF_TRUSTED_ORIGINS` with `https://` URLs
3. Wait 5-10 minutes for SSL certificate to provision
4. Clear browser cache and restart browser

### Pages Return 500 Error
**Error**: Internal Server Error

**Solution**:
1. Check **Logs** tab for detailed error
2. Set `DJANGO_DEBUG=True` temporarily (not recommended for production)
3. Check database is writable: `ls -la /var/data/`
4. Restart service: Dashboard → **Manual Deploy**

---

## Post-Deployment

### Initial Setup
1. Visit `https://your-app-name.onrender.com`
2. Log in with admin account (or create new superuser)
3. Create courses, topics, and test features

### Create Superuser (Admin)
If needed, run in Render shell or via Django:
```bash
python manage.py createsuperuser
```

### Custom Domain (Optional)
1. Go to **Settings** → **Custom Domain**
2. Add your domain (e.g., `notes.example.com`)
3. Update DNS records as instructed by Render
4. Update `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` in environment variables

### Monitoring
- **Logs**: Check regularly for errors
- **CPU/Memory**: Monitor in **Metrics** tab
- **Disk Space**: Monitor via **Logs** or disk size
- **Backups**: Manually export database periodically

### Updates & Redeployment
1. Push changes to GitHub
2. Render auto-redeploys on push (if auto-deploy is enabled)
3. OR manually deploy: Dashboard → **Manual Deploy**
4. Migrations run automatically during deployment

---

## Performance Tips

### For Free Tier
- App will sleep after 15 minutes of inactivity
- Use higher-tier plan if you need 24/7 availability
- Static files cached by WhiteNoise for fast delivery

### Optimization
1. Enable gzip compression (automatic with WhiteNoise)
2. Use 4 gunicorn workers for small workloads
3. Implement database indexes for frequently queried fields
4. Cache API responses with Redis (paid upgrade)

### Database Optimization
- Regular backups to external storage
- Monitor database size in Metrics
- Consider upgrading to PostgreSQL if SQLite becomes bottleneck

---

## Production Checklist

- [ ] `DJANGO_SECRET_KEY` generated and secure
- [ ] `DJANGO_DEBUG = False`
- [ ] `DJANGO_ALLOWED_HOSTS` set to your domain
- [ ] SSL/HTTPS enabled (automatic on Render)
- [ ] CSRF protection enabled
- [ ] Static files collect successfully
- [ ] Database migrations run without errors
- [ ] Admin user created
- [ ] Test login functionality
- [ ] Test file uploads (voice notes, documents)
- [ ] Verify email notifications (if enabled)
- [ ] Monitor logs for errors
- [ ] Set up automated backups

---

## Costs

### Render Pricing
- **Free Tier**: 
  - 1 shared-cpu-1gb web service
  - Auto-sleep after 15 mins inactivity
  - Great for learning/testing
  
- **Paid Tier** (starting ~$7/month):
  - Always-on instance
  - Dedicated resources
  - Custom domains
  - Better performance

### Upgrade Path
1. Start with Free tier for testing
2. Upgrade to Pro when traffic increases
3. Add PostgreSQL database for scale
4. Add Redis for caching

---

## Support

- **Render Docs**: https://render.com/docs
- **Django Docs**: https://docs.djangoproject.com
- **Common Issues**: https://render.com/docs/troubleshooting

---

## Summary

U-Notes is now ready for production on Render! 

**Key Points**:
- ✅ Zero-cost deployment (free tier available)
- ✅ Automatic HTTPS/SSL
- ✅ Persistent storage for database and uploads
- ✅ Auto-scaling with Render
- ✅ Easy to upgrade later

**Next Steps**:
1. Deploy to Render using steps above
2. Create admin account
3. Start creating notes
4. Share with friends/classmates
5. Enjoy your free AI-powered study app!

🚀 Happy deploying!

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
