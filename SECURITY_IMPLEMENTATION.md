# Security Hardening Implementation - U-Notes

## Overview
Comprehensive security implementation to protect against common penetration testing attacks and vulnerabilities.

## Security Layers Implemented

### 1. Rate Limiting Protection
**Location:** `notes/middleware.py` - `RateLimitMiddleware`

**Protection Against:**
- Brute force attacks
- DDoS attacks
- Credential stuffing
- API abuse

**Implementation:**
- **Login attempts:** 5 per minute per IP
- **Password reset:** 3 per minute per IP
- **Signup:** 3 per minute per IP
- **API calls:** 60 per minute per IP
- **General requests:** 120 per minute per IP

**How it works:**
- Uses Django cache to track requests per IP address
- Blocks excessive requests with HTTP 403 response
- Logs suspicious activity

### 2. Security Headers Middleware
**Location:** `notes/middleware.py` - `SecurityHeadersMiddleware`

**Headers Added:**
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `X-XSS-Protection: 1; mode=block` - Enables XSS filter
- `Referrer-Policy: strict-origin-when-cross-origin` - Controls referrer information
- `Content-Security-Policy` - Prevents XSS, injection attacks
- `Permissions-Policy` - Restricts browser features

### 3. Suspicious Activity Detection
**Location:** `notes/middleware.py` - `SuspiciousActivityMiddleware`

**Detects and Blocks:**
- Directory traversal attempts (`../`, `..\\`)
- XSS attempts (`<script`, `javascript:`, `onerror=`, `onload=`)
- SQL injection (`SELECT * FROM`, `UNION SELECT`, `DROP TABLE`, `--`, `/*`)
- Command injection (`exec(`, `system(`, `eval(`)
- Code injection (`<?php`, `<%`)

**Additional Features:**
- Failed login attempt tracking
- Account lockout after 5 failed attempts (15 minutes)
- Critical logging of all suspicious activity

### 4. Input Sanitization
**Location:** `notes/middleware.py` - `InputSanitizationMiddleware`

**Protection:**
- Scans POST data for HTML tags in non-content fields
- Warns about potential XSS attempts
- Logs suspicious input patterns

### 5. Form Validation & File Upload Security
**Location:** `notes/forms.py`

**File Upload Protection:**
- File extension whitelist validation
- File size limits (10 MB max)
- MIME type validation
- Dangerous file types blocked

**Allowed Extensions:**
```
pdf, doc, docx, txt, md
jpg, jpeg, png, gif, bmp, webp
mp3, wav, ogg, m4a
ppt, pptx, xls, xlsx
zip, rar
```

**Input Validation:**
- Email uniqueness checks
- Course code format validation (alphanumeric only)
- Title/name sanitization (blocks XSS attempts)
- Maximum length enforcement

### 6. Session Security
**Location:** `unotes_project/settings.py`

**Settings:**
```python
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # Prevent CSRF
SESSION_COOKIE_AGE = 43200  # 12 hour timeout
SESSION_SAVE_EVERY_REQUEST = True  # Refresh session
```

### 7. CSRF Protection
**Enhanced Settings:**
```python
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_AGE = 31449600  # 1 year
```

### 8. Password Security
**Strengthened Validators:**
- Minimum length: 12 characters (increased from 8)
- User attribute similarity check
- Common password prevention
- Numeric-only password prevention

### 9. HTTPS & Transport Security (Production)
**Settings:**
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 10. Access Control (IDOR Prevention)
**Implementation:** All views enforce ownership checks

**Protected Endpoints:**
- `note_detail` - Owner verification
- `note_update` - Owner verification
- `note_delete` - Owner verification
- `document_view` - Owner verification
- `share_note` - Owner verification
- `export_note_pdf` - Owner/shared access verification
- `export_note_markdown` - Owner/shared access verification
- `voice_notes` - Owner/shared access verification
- `delete_voice_note` - Owner verification only
- `delete_comment` - Owner or note owner verification

**Pattern:**
```python
note = get_object_or_404(Note, pk=pk, owner=request.user)
```

### 11. Security Logging
**Location:** Security events logged to `security.log`

**Logged Events:**
- Rate limit violations
- Suspicious activity patterns
- Failed login attempts
- Attack attempts (XSS, SQL injection, etc.)

**Configuration:**
```python
LOGGING = {
    'handlers': {
        'file': {
            'filename': 'security.log',
        },
    },
    'loggers': {
        'notes.middleware': {
            'level': 'WARNING',
        },
        'django.security': {
            'level': 'WARNING',
        },
    },
}
```

### 12. Cache Configuration
**Purpose:** Required for rate limiting

**Implementation:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'OPTIONS': {'MAX_ENTRIES': 10000}
    }
}
```

## Attack Vectors Mitigated

### 1. Cross-Site Scripting (XSS)
✅ Content Security Policy headers
✅ X-XSS-Protection header
✅ Input sanitization in forms
✅ HTML tag detection in non-content fields
✅ CKEditor configuration (removePlugins: 'Iframe')

### 2. SQL Injection
✅ Django ORM (parameterized queries by default)
✅ Suspicious SQL pattern detection
✅ Input validation and sanitization

### 3. Cross-Site Request Forgery (CSRF)
✅ Django CSRF middleware enabled
✅ CSRF tokens required for all POST requests
✅ SameSite cookie attribute
✅ CSRF cookie HttpOnly flag

### 4. Clickjacking
✅ X-Frame-Options: DENY header
✅ Content-Security-Policy: frame-ancestors 'none'

### 5. Brute Force Attacks
✅ Rate limiting on login endpoint (5/minute)
✅ Account lockout after 5 failed attempts
✅ 15-minute lockout period

### 6. Session Hijacking
✅ Secure session cookies (HTTPS only in production)
✅ HttpOnly cookies (no JavaScript access)
✅ SameSite: Strict attribute
✅ 12-hour session timeout

### 7. Insecure Direct Object References (IDOR)
✅ Owner verification on all sensitive endpoints
✅ get_object_or_404 with owner filter
✅ Shared access verification where applicable

### 8. File Upload Vulnerabilities
✅ File extension whitelist
✅ File size limits (10 MB)
✅ MIME type validation
✅ Dangerous extensions blocked (.exe, .sh, .bat, etc.)

### 9. Command Injection
✅ Suspicious command pattern detection
✅ No direct shell execution in application
✅ Input sanitization

### 10. DDoS Protection
✅ Rate limiting (120 requests/minute general)
✅ Per-endpoint rate limits
✅ IP-based request tracking

### 11. Directory Traversal
✅ Path traversal pattern detection
✅ Django's built-in file serving protection
✅ Middleware blocks ../ and ..\\ patterns

### 12. Information Disclosure
✅ DEBUG=False in production
✅ Custom error pages
✅ Secure referrer policy
✅ No verbose error messages to end users

## Testing Security Features

### Test Rate Limiting:
```bash
# Attempt rapid login requests
for i in {1..10}; do
    curl -X POST http://localhost:8000/login/ \
        -d "username=test&password=test"
    echo "Request $i"
done
```

### Test XSS Protection:
```bash
# Try to inject script in form
curl -X POST http://localhost:8000/notes/create/ \
    -d "title=<script>alert('XSS')</script>&content=test"
```

### Test SQL Injection:
```bash
# Try SQL injection in search
curl "http://localhost:8000/search/?q=' OR '1'='1"
```

### Test Directory Traversal:
```bash
# Try to access files outside document root
curl "http://localhost:8000/media/../../../etc/passwd"
```

### Test File Upload:
```bash
# Try to upload disallowed file type
curl -F "file=@malicious.exe" http://localhost:8000/documents/upload/
```

## Security Checklist

✅ **Authentication & Authorization**
- [x] Strong password requirements (12+ characters)
- [x] Rate limiting on login
- [x] Account lockout mechanism
- [x] Secure session management
- [x] CSRF protection
- [x] Login required decorators on sensitive views

✅ **Input Validation**
- [x] Form validation
- [x] File upload restrictions
- [x] Input sanitization
- [x] XSS protection

✅ **Data Protection**
- [x] HTTPS enforcement (production)
- [x] Secure cookies
- [x] SQL injection protection
- [x] Access control (IDOR prevention)

✅ **Infrastructure**
- [x] Security headers
- [x] Rate limiting
- [x] Logging and monitoring
- [x] Error handling

✅ **File Security**
- [x] File type validation
- [x] File size limits
- [x] Safe file storage
- [x] Path traversal protection

## Production Deployment Checklist

Before deploying to production:

1. **Environment Variables**
   ```bash
   export DJANGO_DEBUG=False
   export DJANGO_SECRET_KEY="your-very-long-random-secret-key"
   export DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
   export DJANGO_CSRF_TRUSTED_ORIGINS="https://yourdomain.com"
   ```

2. **Database**
   - Use PostgreSQL or MySQL (not SQLite)
   - Enable SSL connections
   - Regular backups

3. **Static Files**
   ```bash
   python manage.py collectstatic --no-input
   ```

4. **Web Server**
   - Use Gunicorn/uWSGI
   - Configure nginx/Apache with SSL
   - Enable HTTPS
   - Install SSL certificate (Let's Encrypt)

5. **Monitoring**
   - Set up error monitoring (Sentry)
   - Monitor security.log file
   - Set up alerts for suspicious activity

6. **Regular Updates**
   ```bash
   pip install --upgrade Django
   pip install --upgrade -r requirements.txt
   ```

## Security Maintenance

### Daily:
- Check security.log for suspicious activity
- Monitor failed login attempts

### Weekly:
- Review rate limiting effectiveness
- Check for security updates

### Monthly:
- Update dependencies
- Review access logs
- Test security features

### Quarterly:
- Conduct security audit
- Update security policies
- Review and update rate limits

## Additional Recommendations

1. **Enable 2FA (Two-Factor Authentication)**
   - Install django-two-factor-auth
   - Require for admin accounts

2. **Database Encryption**
   - Enable encryption at rest
   - Use encrypted connections

3. **API Security** (if applicable)
   - Implement API key authentication
   - Add API rate limiting
   - Version your API

4. **Backup Security**
   - Encrypt backups
   - Store offsite
   - Regular restore tests

5. **Intrusion Detection**
   - Consider WAF (Web Application Firewall)
   - Implement fail2ban
   - Monitor for anomalies

## Contact & Support

For security issues or questions:
- Review this documentation
- Check Django security guidelines
- Consult OWASP Top 10

**Remember:** Security is an ongoing process, not a one-time implementation.
