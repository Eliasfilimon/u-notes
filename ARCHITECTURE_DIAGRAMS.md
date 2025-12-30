# Architecture & Flow Diagrams

## Password Reset Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PASSWORD RESET FLOW                          │
└─────────────────────────────────────────────────────────────────────┘

1. USER INITIATES RESET
   ┌──────────────────┐
   │ Login Page       │
   │ "Forgot pwd?"    │
   └────────┬─────────┘
            │ Click Link
            ▼
   ┌──────────────────────────────┐
   │ password_reset.html          │
   │ Form: Enter Email Address    │
   └────────┬─────────────────────┘
            │ Submit
            ▼

2. GENERATE TOKEN & SEND EMAIL
   ┌──────────────────────────────────────┐
   │ CustomPasswordResetView              │
   │ - Generate secure token              │
   │ - Token expires in 1 hour            │
   │ - Create reset link                  │
   └────────┬─────────────────────────────┘
            │ Send Email
            ▼
   ┌──────────────────────────────────────┐
   │ password_reset_email.html            │
   │ Email with reset link                │
   └────────┬─────────────────────────────┘
            │ Email sent to user
            ▼
   ┌──────────────────────────────────────┐
   │ password_reset_done.html             │
   │ "Check your email"                   │
   └──────────────────────────────────────┘

3. USER RECEIVES EMAIL
   ┌────────────────────────────────┐
   │ User's Email Inbox             │
   │ Subject: Password Reset        │
   │ Body: Click link:              │
   │  /reset/<uid>/<token>/         │
   └────────┬───────────────────────┘
            │ User clicks link
            ▼

4. USER ENTERS NEW PASSWORD
   ┌────────────────────────────────┐
   │ password_reset_confirm.html    │
   │ Verify token is valid          │
   │ Form: Enter New Password       │
   └────────┬───────────────────────┘
            │ Submit new password
            ▼

5. PASSWORD UPDATED
   ┌────────────────────────────────┐
   │ CustomPasswordResetConfirmView │
   │ - Validate token              │
   │ - Hash new password            │
   │ - Update database              │
   │ - Invalidate token             │
   └────────┬───────────────────────┘
            │ Success
            ▼
   ┌────────────────────────────────┐
   │ password_reset_complete.html   │
   │ "Password reset successful"    │
   │ "Go to Login"                  │
   └────────┬───────────────────────┘
            │ User clicks "Login"
            ▼

6. LOGIN WITH NEW PASSWORD
   ┌────────────────────────────────┐
   │ Login Page                     │
   │ Username: [user]               │
   │ Password: [new password]       │
   └────────┬───────────────────────┘
            │ Submit
            ▼
   ┌────────────────────────────────┐
   │ ✅ LOGIN SUCCESSFUL            │
   │ Redirects to Dashboard         │
   └────────────────────────────────┘
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      DJANGO APPLICATION                             │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ URLS (notes/urls.py)                                             │
├──────────────────────────────────────────────────────────────────┤
│ ✓ /password_reset/                                              │
│   └─> CustomPasswordResetView                                   │
│                                                                   │
│ ✓ /reset/<uidb64>/<token>/                                      │
│   └─> CustomPasswordResetConfirmView                            │
│                                                                   │
│ ✓ /password_reset/done/                                         │
│   └─> TemplateView                                              │
│                                                                   │
│ ✓ /password_reset/complete/                                     │
│   └─> TemplateView                                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ VIEWS (notes/views.py)                                           │
├──────────────────────────────────────────────────────────────────┤
│ class CustomPasswordResetView(PasswordResetView)                 │
│   - Displays password reset form                                 │
│   - Validates email address                                      │
│   - Generates secure token                                       │
│   - Sends email with reset link                                  │
│                                                                   │
│ class CustomPasswordResetConfirmView(PasswordResetConfirmView)   │
│   - Displays password confirm form                               │
│   - Validates token                                              │
│   - Updates user password                                        │
│   - Confirms success                                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ TEMPLATES (notes/templates/notes/)                               │
├──────────────────────────────────────────────────────────────────┤
│ password_reset.html                                              │
│   ├─ Form to enter email                                         │
│   └─ Submit button                                               │
│                                                                   │
│ password_reset_done.html                                         │
│   ├─ "Email sent" message                                        │
│   └─ Instructions to check email                                 │
│                                                                   │
│ password_reset_email.html                                        │
│   ├─ Email subject                                               │
│   ├─ Greeting with user name                                     │
│   ├─ Reset link with token                                       │
│   └─ Token expiry message                                        │
│                                                                   │
│ password_reset_confirm.html                                      │
│   ├─ Form to enter new password                                  │
│   ├─ Submit button                                               │
│   └─ Invalid token error message                                 │
│                                                                   │
│ password_reset_complete.html                                     │
│   ├─ "Password reset successful" message                         │
│   └─ Login button                                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ EMAIL CONFIGURATION (unotes_project/settings.py)                │
├──────────────────────────────────────────────────────────────────┤
│ Development:  Console Backend (emails print to console)          │
│ Production:   SMTP Backend (emails sent via Gmail/provider)      │
│                                                                   │
│ Environment Variables:                                           │
│   - EMAIL_BACKEND                                                │
│   - EMAIL_HOST (smtp.gmail.com)                                  │
│   - EMAIL_PORT (587)                                             │
│   - EMAIL_USE_TLS (True)                                         │
│   - EMAIL_HOST_USER (your-email@gmail.com)                       │
│   - EMAIL_HOST_PASSWORD (app-password)                           │
│   - DEFAULT_FROM_EMAIL (noreply@yourdomain.com)                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ DATABASE (Using Built-in Django User Model)                      │
├──────────────────────────────────────────────────────────────────┤
│ Table: auth_user                                                 │
│   ├─ id (PK)                                                     │
│   ├─ username                                                    │
│   ├─ password (hashed)      ← UPDATED HERE                       │
│   ├─ email                                                       │
│   ├─ first_name                                                  │
│   └─ last_name                                                   │
│                                                                   │
│ Password Reset Token: Generated in-memory                        │
│   ├─ UID (user id, base64)                                       │
│   ├─ Token (random secure string)                                │
│   └─ Expires after 1 hour                                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## Email Backend Selection

```
┌──────────────────────────┐
│   Django Settings        │
│   DEBUG = True/False     │
└────────────┬─────────────┘
             │
         ┌───┴───┐
         │       │
    ┌────▼────┐ ┌────▼────────────────┐
    │ DEBUG=  │ │ DEBUG=False          │
    │ True    │ │ (Production)         │
    └────┬────┘ └────┬─────────────────┘
         │            │
         ▼            ▼
    Console       SMTP
    Backend       Backend
    │             │
    │ ┌───────────┘
    │ │ Uses:
    │ │ - EMAIL_HOST
    │ │ - EMAIL_PORT
    │ │ - EMAIL_HOST_USER
    │ │ - EMAIL_HOST_PASSWORD
    │ │ - EMAIL_USE_TLS
    │ │
    │ └─> Sends Real Emails
    │
    └─> Prints to Console
        (For Testing)
```

---

## Security Features

```
┌──────────────────────────────────────────────────────────────┐
│                   SECURITY FEATURES                          │
└──────────────────────────────────────────────────────────────┘

1. TOKEN GENERATION
   ├─ Cryptographically secure random token
   ├─ Includes user ID (base64 encoded)
   ├─ Unique per reset request
   └─ Expires after 1 hour

2. PASSWORD VALIDATION
   ├─ Minimum 8 characters
   ├─ Cannot be too similar to username
   ├─ Cannot be a common password
   ├─ Cannot be all numbers
   └─ Must differ from previous password

3. EMAIL VERIFICATION
   ├─ Only owner of email can reset password
   ├─ Email must exist in system
   └─ Token sent to registered email only

4. TOKEN VALIDATION
   ├─ Token signature verified
   ├─ Expiry time checked
   ├─ User still exists check
   └─ Invalid tokens show error message

5. HTTPS/SECURITY
   ├─ All forms use CSRF protection
   ├─ Passwords transmitted over HTTPS
   ├─ Secure cookies in production
   ├─ Security headers enabled
   └─ HSTS enabled (if configured)
```

---

## Performance Flow

```
┌─────────────────────────────────────────┐
│         REQUEST COMING IN               │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼────────┐
         │ Check Cache    │
         └───────┬────────┘
                 │
         ┌───────▼────────────────┐
         │ Hit: Return Cached     │
         │ Miss: Continue         │
         └───────┬────────────────┘
                 │
         ┌───────▼────────────────┐
         │ Execute View Function  │
         └───────┬────────────────┘
                 │
         ┌───────▼────────────────┐
         │ Database Queries       │
         │ (Should be optimized)  │
         └───────┬────────────────┘
                 │
         ┌───────▼────────────────┐
         │ Render Template        │
         └───────┬────────────────┘
                 │
         ┌───────▼────────────────┐
         │ Cache Result           │
         │ (If configured)        │
         └───────┬────────────────┘
                 │
         ┌───────▼────────────────┐
         │ Return Response        │
         └────────────────────────┘
```

---

## Data Flow: Password Reset Email

```
┌────────────────────────────────────────────────────────────┐
│         PASSWORD RESET EMAIL GENERATION                   │
└────────────────────────────────────────────────────────────┘

1. USER DATA
   User {
     - id: 123
     - username: john
     - email: john@example.com
     - first_name: John
   }

2. TOKEN GENERATION
   ├─ uid = base64_encode("123") = "MTIz"
   ├─ token = random_secure_string()
   ├─ signature = hmac(secret, uid+token)
   └─ expires_at = now() + 1 hour

3. EMAIL CONTEXT
   {
     user: User,
     uid: "MTIz",
     token: "abc-123-def-456",
     protocol: "https",
     domain: "yourdomain.com",
     url: "/reset/MTIz/abc-123-def-456/"
   }

4. RENDERED EMAIL
   Subject: Password Reset
   
   Body:
   Hi John,
   
   To reset your password, click the link below:
   https://yourdomain.com/reset/MTIz/abc-123-def-456/
   
   This link expires in 1 hour.
   
   Best regards,
   UNotes Team

5. EMAIL SENT
   SMTP Connection:
   ├─ HOST: smtp.gmail.com
   ├─ PORT: 587
   ├─ AUTH: EMAIL_HOST_USER
   ├─ TO: john@example.com
   └─ STATUS: ✓ Sent
```

---

## Summary

This implementation uses Django's built-in password reset system with:
- Secure token generation
- Email backend configuration
- Template-based emails
- Standard security practices
- Easy integration with existing auth

**All components are production-ready and follow Django best practices.**
