# Render Deployment Checklist

## Pre-Deployment (Local Testing)

- [ ] All code pushed to GitHub/GitLab
- [ ] `requirements.txt` updated with all dependencies
- [ ] `render.yaml` configured correctly
- [ ] `.env.example` created with all environment variables
- [ ] `.gitignore` configured to exclude `.env` and sensitive files
- [ ] Database migrations created: `python manage.py makemigrations`
- [ ] Migrations run locally: `python manage.py migrate`
- [ ] Static files collected locally: `python manage.py collectstatic --noinput`
- [ ] Server runs locally: `python manage.py runserver`
- [ ] Login functionality works
- [ ] AI features (summarize, flashcards) work locally
- [ ] Voice note recording works
- [ ] File uploads/exports work

## Render Account Setup

- [ ] Render account created (https://render.com)
- [ ] GitHub/GitLab connected to Render
- [ ] Repository authorized for Render access

## Deployment Steps

### Option A: Blueprint Deployment (Easier)
- [ ] `render.yaml` exists in repository root
- [ ] Go to https://render.com/blueprint-dashboard
- [ ] Click "New Blueprint Instance"
- [ ] Select your repository
- [ ] Confirm auto-configuration
- [ ] Create service

### Option B: Manual Deployment
- [ ] Go to https://render.com dashboard
- [ ] Click "New +" → "Web Service"
- [ ] Select repository
- [ ] Configure:
  - [ ] Name: `u-notes`
  - [ ] Runtime: Python 3.13
  - [ ] Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
  - [ ] Start Command: `gunicorn unotes_project.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --worker-class sync --timeout 120`

## Environment Variables

- [ ] `DJANGO_SECRET_KEY` - Let Render generate (or use strong random)
- [ ] `DJANGO_DEBUG` = `False`
- [ ] `DJANGO_ALLOWED_HOSTS` = `*` or your domain
- [ ] `DJANGO_CSRF_TRUSTED_ORIGINS` = `https://*.onrender.com`
- [ ] `DJANGO_SECURE_SSL_REDIRECT` = `True`
- [ ] `DJANGO_SESSION_COOKIE_SECURE` = `True`
- [ ] `DJANGO_CSRF_COOKIE_SECURE` = `True`
- [ ] `DJANGO_SECURE_HSTS_SECONDS` = `31536000`
- [ ] `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` = `True`
- [ ] `DJANGO_SECURE_HSTS_PRELOAD` = `True`

## Disk Configuration

- [ ] Persistent Disk added:
  - [ ] Name: `data`
  - [ ] Mount Path: `/var/data`
  - [ ] Size: 10 GB (or as needed)

## Deployment Monitoring

- [ ] Build starts automatically
- [ ] Check "Logs" tab during build
- [ ] Verify no build errors
- [ ] Verify migrations complete successfully
- [ ] Verify static files collected (40+ files)
- [ ] Service shows as "Live"
- [ ] URL is accessible from browser

## Post-Deployment Testing

- [ ] App loads at `https://u-notes-xxx.onrender.com`
- [ ] Login page displays correctly
- [ ] Can login with admin account (username: `admin`)
- [ ] CSS/styling loads correctly (no 404 errors)
- [ ] Create a new note (test basic functionality)
- [ ] Summarize note (test AI feature)
- [ ] Generate flashcards (test AI feature)
- [ ] Record voice note (test media feature)
- [ ] Export as PDF (test export feature)
- [ ] Export as Markdown (test export feature)
- [ ] Add comment to note (test collaboration)
- [ ] Visit analytics dashboard (test dashboard)
- [ ] Check browser console for JavaScript errors (F12)

## SSL/HTTPS Verification

- [ ] URL is `https://` (secure connection)
- [ ] No SSL certificate warnings
- [ ] Redirect from `http://` to `https://` works
- [ ] Check SSL info (click padlock icon in browser)

## Performance Checks

- [ ] Pages load within 3-5 seconds
- [ ] Images/media load correctly
- [ ] Interactions are responsive
- [ ] No console errors or warnings
- [ ] Check Render Metrics tab (CPU/Memory usage)

## Database & Storage

- [ ] Persistent disk shows as mounted at `/var/data`
- [ ] Database file exists: `/var/data/db.sqlite3`
- [ ] Media directory exists: `/var/data/media`
- [ ] Uploaded files persist across service restarts

## Maintenance Setup

- [ ] Understand how to view logs: Dashboard → Logs
- [ ] Know how to redeploy: Dashboard → Manual Deploy
- [ ] Know how to update environment variables: Settings → Environment
- [ ] Set up monitoring: Check Metrics tab regularly
- [ ] Backup plan established (export database periodically)

## Optional Enhancements

- [ ] Custom domain configured (if you have one)
- [ ] Email notifications set up (if needed)
- [ ] OpenAI API key added (for enhanced AI features)
- [ ] PostgreSQL upgraded (for better performance at scale)
- [ ] Redis cache added (for better performance)
- [ ] CDN configured (for static file delivery)

## Final Verification

- [ ] App is fully functional
- [ ] All features tested
- [ ] No errors in logs
- [ ] Database working correctly
- [ ] Files persisting correctly
- [ ] Ready for production use!

---

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Build fails | Check logs for specific error, ensure all dependencies in `requirements.txt` |
| Static files 404 | Verify `python manage.py collectstatic` in build command |
| CSRF errors | Update `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` |
| Database errors | Ensure migrations run: check build command and logs |
| Files don't persist | Verify persistent disk is mounted at `/var/data` |
| SSL errors | Wait 5-10 mins for certificate, clear browser cache |
| Can't log in | Verify database migrated successfully |
| Media files missing | Check media uploads folder path in settings |

---

## Deployment Success Criteria

✅ You've successfully deployed when:
1. App is accessible at `https://u-notes-xxx.onrender.com`
2. All pages load with correct styling
3. You can log in and navigate the app
4. Database persists across service restarts
5. Uploaded files persist across service restarts
6. AI features (summarize, flashcards) work
7. No critical errors in logs
8. Performance is acceptable (<5s page load)

---

## Next Steps After Deployment

1. **Share with others**: Give them the Render URL
2. **Create accounts**: Set up accounts for team members
3. **Monitor**: Check logs weekly for issues
4. **Backup**: Export database monthly
5. **Update**: Push code updates and they auto-deploy
6. **Scale**: Upgrade Render plan if needed

---

## Support Resources

- Render Docs: https://render.com/docs
- Django Docs: https://docs.djangoproject.com
- U-Notes README: See project README.md
- Issues: Check Render logs for detailed errors

---

🚀 **Congratulations on deploying U-Notes!**

Your free AI-powered note-taking app is now live on the internet!
