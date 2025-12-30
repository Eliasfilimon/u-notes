# Performance Optimization Guide for UNotes on Render

## Issue: Long Load Times

### Root Causes to Investigate

1. **Cold Starts on Render's Free Tier**
   - Render's free tier spins down after 15 minutes of inactivity
   - First request after spin-down takes 30-60 seconds
   - Solution: Upgrade to paid tier or use Render's paid uptime protection

2. **Database Queries**
   - Inefficient queries that N+1 problem
   - Missing database indexes on frequently queried fields

3. **Static Assets**
   - Uncompressed CSS/JS files
   - Large images not optimized
   - Missing caching headers

4. **Django Initialization**
   - Settings loading
   - Middleware processing
   - Template compilation

## Optimization Strategies

### 1. Fix Cold Start Issue (Immediate Action)

**Option A: Upgrade to Paid Plan**
- Go to your Render dashboard
- Upgrade service from Free to Starter ($10/month)
- This includes continuous uptime with no spin-down

**Option B: Keep-Alive Pings (Temporary for Free Tier)**
Add a scheduled job to ping your app every 14 minutes:

```python
# Add to your project's scheduled tasks
# Example: use a cron job service like EasyCron.com
# Ping: https://your-app.onrender.com/
```

### 2. Optimize Database Queries

**Add select_related() and prefetch_related():**

Update [notes/views.py](notes/views.py) queries:

```python
@login_required
def note_list(request, course_id=None, topic_id=None):
    notes = Note.objects.filter(
        owner=request.user
    ).select_related(
        'owner', 'topic'
    ).prefetch_related(
        'comments', 'shared_with'
    ).order_by('-updated_at')
    # ... rest of view
```

**Add Database Indexes:**

Update [notes/models.py](notes/models.py):

```python
class Note(models.Model):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['owner', '-updated_at']),
            models.Index(fields=['owner', 'topic']),
        ]
        ordering = ['-updated_at']

class Course(models.Model):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['owner']),
        ]

class Topic(models.Model):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['owner', 'course']),
        ]
```

Then run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Enable Query Caching

Add caching to frequently accessed data:

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unotes-cache',
    }
}

# In views.py
from django.views.decorators.cache import cache_page
from django.core.cache import cache

@cache_page(60 * 5)  # Cache for 5 minutes
@login_required
def note_list(request):
    # ... view code ...
```

### 4. Optimize Static Files

**Minify and Compress:**

```bash
# Ensure collectstatic is run during build
python manage.py collectstatic --noinput

# Enable compression in settings.py
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**Update Render Build Command:**

In `render.yaml` or Render dashboard:
```yaml
buildCommand: |
  pip install -r requirements.txt
  python manage.py collectstatic --noinput
  python manage.py migrate
```

### 5. Enable Browser Caching

Add to [unotes_project/settings.py](unotes_project/settings.py):

```python
# Cache static files for 1 year in browser
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Add cache headers for static files
STATICFILES_DIRS = []
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Add middleware for caching
MIDDLEWARE = [
    # ... existing middleware ...
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]
```

### 6. Use a CDN (Optional but Recommended)

**Use Render's built-in CDN or Cloudflare:**

1. Go to Render Dashboard
2. Service Settings → Environment → Add CDN
3. Or configure Cloudflare for your domain:
   - Add CNAME record pointing to your Render app
   - Enable Cloudflare's caching

### 7. Monitor Performance

**Enable Django Debug Toolbar (Development Only):**

```bash
pip install django-debug-toolbar
```

Add to `settings.py`:
```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

**Monitor with Render's Metrics:**
- Go to Render Dashboard
- View real-time metrics for your service
- Check CPU, memory, and request times

### 8. Environment Variables for Render

Set these in your Render dashboard (Settings → Environment):

```
DEBUG=False
DJANGO_ENVIRONMENT=production
DJANGO_ALLOWED_HOSTS=your-app.onrender.com
DATABASE_URL=postgresql://...  (if using PostgreSQL)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Performance Checklist

- [ ] Upgrade to Render paid tier (if using free tier)
- [ ] Add select_related() and prefetch_related() to querysets
- [ ] Create database indexes on frequently queried fields
- [ ] Run migrations for new indexes
- [ ] Enable static file compression
- [ ] Configure cache headers
- [ ] Test with Google PageSpeed Insights
- [ ] Monitor Render metrics dashboard
- [ ] Set up CDN (optional)
- [ ] Test password reset functionality in production

## Expected Results

After optimization:
- **Initial load**: 2-5 seconds (was 30-60 on free tier cold start)
- **Subsequent requests**: 200-500ms
- **Static assets**: Cached locally by browser
- **Database queries**: Reduced from 10+ to 2-3 per page load

## Monitoring After Deployment

1. Test the app at: https://your-app.onrender.com
2. Open browser DevTools → Network tab
3. Check:
   - Total page load time
   - Individual asset load times
   - Cache status (should show "disk cache" for static files)
4. Monitor Render dashboard for errors

## Additional Resources

- [Render Deployment Guide](https://render.com/docs)
- [Django Performance Optimization](https://docs.djangoproject.com/en/4.2/topics/performance/)
- [PostgreSQL Setup for Render](RENDER_POSTGRESQL_SETUP.md)
- [Deployment Checklist](RENDER_CHECKLIST.md)
