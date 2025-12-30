# Password Reset Feature Implementation

## Overview
This document describes the password reset functionality implemented in the UNotes application.

## Features Implemented

### 1. Password Reset Views
Two custom views have been added to handle password resets:

- **CustomPasswordResetView**: Allows users to request a password reset by entering their email
- **CustomPasswordResetConfirmView**: Handles the password reset confirmation when users click the link in the email

### 2. URL Routes
The following routes have been added to `/notes/urls.py`:

- `password_reset/` - Password reset request form
- `reset/<uidb64>/<token>/` - Password reset confirmation page
- `password_reset/done/` - Confirmation message after email is sent
- `password_reset/complete/` - Success message after password is reset

### 3. Templates Created

- **password_reset.html** - Form for users to enter their email address
- **password_reset_confirm.html** - Form for users to enter their new password
- **password_reset_done.html** - Confirmation that the reset email has been sent
- **password_reset_complete.html** - Confirmation that the password has been successfully reset
- **password_reset_email.html** - Email template with reset link

### 4. Email Configuration
Email settings have been configured in `settings.py`:

- Uses environment variables for SMTP configuration
- In **production (Render)**: Uses SMTP backend with Gmail/custom email provider
- In **development**: Uses console backend for testing

**Required Environment Variables for Production:**
```
EMAIL_HOST = smtp.gmail.com (or your email provider)
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = your-email@gmail.com
EMAIL_HOST_PASSWORD = your-app-password (not regular password)
DEFAULT_FROM_EMAIL = noreply@yourdomain.com
```

### 5. Login Template Updates
The login page now includes a "Forgot your password?" link that directs users to the password reset form.

## How to Use

### For Users:
1. Click "Forgot your password?" on the login page
2. Enter their email address
3. Check their email for a password reset link (valid for 1 hour)
4. Click the link and enter their new password
5. Log in with the new password

### For Developers/Admins:
1. Configure email backend in environment variables for production
2. Test locally using console backend (emails appear in Django console)
3. Deploy to Render and set environment variables in Render dashboard

## Testing

### Local Development:
Email will be printed to the console. No actual emails are sent.

### Production (Render):
1. Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in Render environment variables
2. Users will receive actual emails at their registered email address

## Security Features

- Password reset tokens expire after 1 hour
- Tokens are cryptographically secure
- Users must verify email ownership before resetting password
- Password validation rules are enforced (minimum length, complexity)
- Django's built-in password validators are applied

## Troubleshooting

### Users not receiving emails:
1. Check spam/junk folder
2. Verify email configuration is correct in Render
3. Check Render logs for SMTP errors

### Link not working:
1. Ensure link is clicked within 1 hour
2. Request a new password reset
3. Check that ALLOWED_HOSTS includes your domain

### Invalid token error:
- Token has expired (request a new one)
- Token was modified or corrupted
