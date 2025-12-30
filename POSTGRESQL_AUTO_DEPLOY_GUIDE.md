# PostgreSQL + Auto-Deploy Setup Guide

## The Three Things You Asked About

---

## ❓ Question 1: How to Set Up PostgreSQL

### Step-by-Step

#### 1. Go to Render Dashboard
```
https://dashboard.render.com/
```

#### 2. Create New Database
```
Click "New +" button (top right)
↓
Select "PostgreSQL"
↓
Fill in:
  Name: u-notes-db
  Database: u_notes
  User: u_notes
  Region: (Pick same region as your app)
  PostgreSQL Version: 15 (default)
↓
Click "Create Database"
```

#### 3. Wait for Creation
```
Shows "Creating..." status
↓
After 1-2 minutes, shows "Available" (green)
↓
You're done!
```

#### 4. Get Your Connection String
```
Go to: u-notes-db → "Connections"
↓
Find: "Internal Database URL"
↓
Copy it - you'll need this next
↓
Format looks like:
postgresql://u_notes:xyz123abc@dpg-abc.region.postgres.render.com:5432/u_notes
```

---

## ❓ Question 2: How to Add Environment Variables

### Step-by-Step

#### 1. Create Your Web Service
```
Dashboard → "New +" → "Web Service"
↓
Select "GitHub"
↓
Select your u-notes repository
↓
Name: u-notes
Region: SAME AS DATABASE (important!)
Branch: main
↓
Click "Create Web Service"
```

#### 2. Wait for First Deploy
```
Service shows "Building..." status
↓
Takes 3-5 minutes first time
↓
Keep watching the Logs tab
↓
Should eventually show "Service is live"
```

#### 3. Add Environment Variables
```
Your Service page → Environment tab (left sidebar)
↓
Scroll to "Environment Variables"
↓
Click "Add Environment Variable"
```

#### 4. Add These Variables (One by One)

**CRITICAL - Database Connection:**
```
Name: DATABASE_URL
Value: [PASTE the Internal Database URL from step 1.4]

Example:
postgresql://u_notes:abc123xyz@dpg-abc123.us-east-1.postgres.render.com:5432/u_notes
```

**Django Settings:**
```
Name: DJANGO_DEBUG
Value: False

Name: DJANGO_ALLOWED_HOSTS
Value: [your-app-name].onrender.com

Example: u-notes.onrender.com
```

**Security Settings (copy exactly):**
```
Name: DJANGO_SECURE_SSL_REDIRECT
Value: True

Name: DJANGO_SESSION_COOKIE_SECURE
Value: True

Name: DJANGO_CSRF_COOKIE_SECURE
Value: True

Name: DJANGO_SECURE_HSTS_SECONDS
Value: 31536000

Name: DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS
Value: True

Name: DJANGO_SECURE_HSTS_PRELOAD
Value: True

Name: DJANGO_SECURE_CONTENT_TYPE_NOSNIFF
Value: True

Name: DJANGO_SECURE_BROWSER_XSS_FILTER
Value: True

Name: DJANGO_X_FRAME_OPTIONS
Value: DENY

Name: DJANGO_CSRF_TRUSTED_ORIGINS
Value: https://*.onrender.com
```

#### 5. Save All Changes
```
After adding all variables
↓
Click "Save Changes"
↓
Service automatically redeploys
↓
Watch Logs tab during redeployment
↓
Should complete in 1-2 minutes
```

---

## ❓ Question 3: Auto-Deployment from GitHub

### How It Works

```
You push code to GitHub main branch
        ↓
Render detects the push (webhook)
        ↓
Render automatically pulls the new code
        ↓
Runs: pip install -r requirements.txt
        ↓
Runs: python manage.py migrate
        ↓
Runs: python manage.py collectstatic --noinput
        ↓
Restarts Gunicorn server
        ↓
App is now updated!
```

### Setting It Up

#### 1. GitHub Connection Already Set
```
Since you connected GitHub when creating the Web Service,
auto-deploy is already enabled!

No additional configuration needed.
```

#### 2. Make a Code Change
```bash
# Edit any file, for example:
echo "# Updated" >> README.md

# Add the change
git add README.md

# Commit it
git commit -m "Update README"

# Push it
git push origin main
```

#### 3. Watch It Deploy
```
Go to: Dashboard → Your Service → "Logs" tab
↓
Within 10 seconds, you'll see:
"Detected git push to repository..."
↓
Then you'll see build starting:
"Building from main branch..."
↓
Watch the full build process
↓
Completes with: "Service is live"
```

#### 4. Your App Is Updated
```
Refresh your app URL
↓
Changes are live!
```

### Automatic Redeploy Summary

| When You Do This | This Happens Automatically |
|---|---|
| `git push origin main` | Render detects push |
| | Pulls latest code |
| | Installs dependencies |
| | Runs migrations |
| | Collects static files |
| | Restarts web server |
| | App is live with new code |
| **Result:** | Your app auto-updates! ✅ |

---

## Complete Workflow: From Start to Live

### 1. PostgreSQL Setup (10 minutes)
```bash
□ Create database on Render
□ Note down Internal Database URL
□ Confirm status shows "Available"
```

### 2. Web Service Setup (5 minutes)
```bash
□ Create web service on Render
□ Connect to GitHub repository
□ Select main branch
□ Wait for first build to complete
```

### 3. Environment Variables (5 minutes)
```bash
□ Add DATABASE_URL
□ Add DJANGO_DEBUG
□ Add DJANGO_ALLOWED_HOSTS
□ Add all security variables
□ Click "Save Changes"
□ Wait for redeployment
```

### 4. Test Your App (5 minutes)
```bash
□ Visit your app URL
□ Log in (admin / password123)
□ Create a note
□ Summarize it
□ Generate flashcards
□ Test voice notes
```

### 5. Change Admin Password (2 minutes)
```bash
□ Click Profile (top right)
□ Click "Change Password"
□ Set a strong password
□ Remember this password!
```

### 6. Test Auto-Deploy (5 minutes)
```bash
□ Make small code change locally
□ git add .
□ git commit -m "Test deploy"
□ git push origin main
□ Watch Render Logs
□ Confirm deployment completes
□ Refresh app to see changes
```

**Total Time: ~35 minutes from zero to production!**

---

## Your App URL

After deployment, your app will be live at:

```
https://u-notes-YOUR_CHOSEN_NAME.onrender.com
```

Example:
```
https://u-notes.onrender.com
```

### Custom Domain (Optional Later)
```
Service → Settings → Custom Domains
↓
Add your own domain
↓
Follow DNS instructions
```

---

## Checking Deployment Status

### While Deploying
```
Service page → "Logs" tab
↓
Watch real-time build output
↓
Shows each step:
  - Pulling code
  - Installing packages
  - Running migrations
  - Starting server
```

### After Deployment
```
Service page → top shows:
  ✅ "Live" badge (green) = Working
  ❌ "Failed" badge (red) = Error
```

### Manual Redeploy
```
Service page → top right
↓
"Redeploy Latest Commit"
↓
Starts build immediately
↓
Check Logs to watch progress
```

---

## Common Issues & Solutions

### Issue 1: DATABASE_URL Format Wrong
```
Error: could not connect to server

Solution:
1. Copy "Internal Database URL" (not External)
2. Don't modify the URL
3. Paste exactly as-is into DATABASE_URL
4. Save and redeploy
```

### Issue 2: DJANGO_ALLOWED_HOSTS Error
```
Error: Invalid HTTP_HOST header

Solution:
1. Check your actual app domain
   (shown at top of Service page)
2. Add exactly as shown in DJANGO_ALLOWED_HOSTS
3. Include full domain, no http://
4. Save and redeploy
```

### Issue 3: Auto-Deploy Not Triggering
```
Pushed code but nothing happens

Solution:
1. Confirm pushing to "main" branch
2. Check GitHub Actions (should show green checkmark)
3. Manually redeploy: "Redeploy Latest Commit"
4. Check Service Logs for errors
```

### Issue 4: Database Not Found
```
Error: could not translate host name

Solution:
1. Check database status (should be green)
2. Use "Internal Database URL" (for Render services)
3. Keep database and service in same region
4. Redeploy web service
```

---

## Environment Variable Reference

| Variable | Example Value | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection |
| `DJANGO_DEBUG` | `False` | Disable debug mode in production |
| `DJANGO_ALLOWED_HOSTS` | `u-notes.onrender.com` | Allow your domain |
| `DJANGO_SECURE_SSL_REDIRECT` | `True` | Force HTTPS |
| `DJANGO_SESSION_COOKIE_SECURE` | `True` | Secure cookies |
| `DJANGO_CSRF_COOKIE_SECURE` | `True` | Protect CSRF token |
| `DJANGO_SECURE_HSTS_SECONDS` | `31536000` | HSTS enabled for 1 year |
| `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` | HSTS on subdomains |
| `DJANGO_SECURE_HSTS_PRELOAD` | `True` | HSTS preload list |
| `DJANGO_SECURE_CONTENT_TYPE_NOSNIFF` | `True` | Prevent MIME sniffing |
| `DJANGO_SECURE_BROWSER_XSS_FILTER` | `True` | XSS protection |
| `DJANGO_X_FRAME_OPTIONS` | `DENY` | Prevent clickjacking |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com` | Trust Render domain |

---

## Next Steps

### Before You Deploy
- [ ] All code committed to GitHub
- [ ] Database connection string copied
- [ ] All environment variables ready

### During Deployment
- [ ] Watch Logs during build
- [ ] Confirm "Service is live" message
- [ ] Note your app URL

### After Deployment
- [ ] Visit your app URL
- [ ] Log in and test features
- [ ] Change admin password
- [ ] Test auto-deploy with small change
- [ ] Monitor Logs periodically

---

## You're All Set! 🚀

Your U-Notes app is:
- ✅ Fully built and tested
- ✅ PostgreSQL database ready
- ✅ Environment variables configured
- ✅ Auto-deploy enabled on GitHub
- ✅ Ready for production!

Every time you push to GitHub, your app automatically updates. No manual deploys needed!

### Quick Checklist

```
□ PostgreSQL database created on Render
□ Internal Database URL copied
□ Web service created and connected to GitHub
□ All 14 environment variables added and saved
□ Service shows "Live" status (green)
□ Visited app URL and logged in
□ Changed admin password
□ Tested by pushing small change
□ Confirmed auto-deploy works

You're LIVE! 🎉
```

---

**Status: READY FOR PRODUCTION DEPLOYMENT**

Any issues? Check Common Issues section above or see RENDER_FINAL_DEPLOYMENT.md for more details.
