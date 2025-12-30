"""
Security Middleware for U-Notes Application
Provides additional security layers to prevent common attacks
"""
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
import time
import hashlib
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware to prevent brute force attacks and DDoS
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Requests per minute for different endpoints
        self.rate_limits = {
            'login': 5,  # 5 login attempts per minute
            'password_reset': 3,  # 3 password reset requests per minute
            'signup': 3,  # 3 signup attempts per minute
            'api': 60,  # 60 API calls per minute
            'default': 120,  # 120 requests per minute for general endpoints
        }
        super().__init__(get_response)
    
    def process_request(self, request):
        # Skip rate limiting for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        # Get client IP address
        ip_address = self.get_client_ip(request)
        
        # Determine rate limit based on endpoint
        rate_limit_key = 'default'
        if '/login' in request.path:
            rate_limit_key = 'login'
        elif '/password_reset' in request.path:
            rate_limit_key = 'password_reset'
        elif '/signup' in request.path:
            rate_limit_key = 'signup'
        elif request.path.startswith('/api/'):
            rate_limit_key = 'api'
        
        # Create cache key
        cache_key = f'rate_limit:{rate_limit_key}:{ip_address}'
        
        # Get current request count
        request_count = cache.get(cache_key, 0)
        
        # Check if limit exceeded
        max_requests = self.rate_limits.get(rate_limit_key, self.rate_limits['default'])
        if request_count >= max_requests:
            logger.warning(f'Rate limit exceeded for IP: {ip_address} on endpoint: {request.path}')
            return HttpResponseForbidden('Rate limit exceeded. Please try again later.')
        
        # Increment counter
        cache.set(cache_key, request_count + 1, 60)  # 60 seconds window
        
        return None
    
    def get_client_ip(self, request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    """
    
    def process_response(self, request, response):
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        if not settings.DEBUG:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
                "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )
            response['Content-Security-Policy'] = csp
        
        # Permissions Policy (formerly Feature-Policy)
        response['Permissions-Policy'] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        return response


class SuspiciousActivityMiddleware(MiddlewareMixin):
    """
    Detect and block suspicious activity patterns
    """
    
    def process_request(self, request):
        ip_address = self.get_client_ip(request)
        user = request.user if hasattr(request, 'user') else AnonymousUser()
        
        # Check for common attack patterns in request
        suspicious_patterns = [
            '../',  # Directory traversal
            '..\\',  # Windows directory traversal
            '<script',  # XSS attempt
            'javascript:',  # XSS attempt
            'onerror=',  # XSS attempt
            'onload=',  # XSS attempt
            'SELECT * FROM',  # SQL injection
            'UNION SELECT',  # SQL injection
            'DROP TABLE',  # SQL injection
            '--',  # SQL comment
            '/*',  # SQL comment
            'exec(',  # Command injection
            'system(',  # Command injection
            'eval(',  # Code injection
            '<?php',  # PHP injection
            '<%',  # ASP injection
        ]
        
        # Check URL, query string, and POST data
        full_path = request.get_full_path()
        post_data = str(request.POST) if request.method == 'POST' else ''
        
        for pattern in suspicious_patterns:
            if pattern.lower() in full_path.lower() or pattern.lower() in post_data.lower():
                logger.critical(
                    f'Suspicious activity detected! IP: {ip_address}, User: {user}, '
                    f'Pattern: {pattern}, Path: {request.path}'
                )
                # Block the request
                return HttpResponseForbidden('Suspicious activity detected. This incident has been logged.')
        
        # Check for excessive failed login attempts
        if '/login' in request.path and request.method == 'POST':
            failed_attempts_key = f'failed_login:{ip_address}'
            failed_attempts = cache.get(failed_attempts_key, 0)
            
            if failed_attempts >= 5:
                # Lock account for 15 minutes after 5 failed attempts
                lockout_key = f'login_lockout:{ip_address}'
                if cache.get(lockout_key):
                    logger.warning(f'Login lockout active for IP: {ip_address}')
                    return HttpResponseForbidden('Too many failed login attempts. Please try again in 15 minutes.')
                cache.set(lockout_key, True, 900)  # 15 minutes
        
        return None
    
    def process_response(self, request, response):
        # Track failed login attempts
        if '/login' in request.path and request.method == 'POST':
            ip_address = self.get_client_ip(request)
            
            # If login failed (redirect to login page or form errors)
            if response.status_code in [200, 302] and hasattr(response, 'context_data'):
                if response.context_data and response.context_data.get('form') and response.context_data['form'].errors:
                    failed_attempts_key = f'failed_login:{ip_address}'
                    failed_attempts = cache.get(failed_attempts_key, 0)
                    cache.set(failed_attempts_key, failed_attempts + 1, 3600)  # Track for 1 hour
            
            # Clear failed attempts on successful login
            elif response.status_code == 302 and not request.path in response.get('Location', ''):
                failed_attempts_key = f'failed_login:{ip_address}'
                cache.delete(failed_attempts_key)
        
        return response
    
    def get_client_ip(self, request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class InputSanitizationMiddleware(MiddlewareMixin):
    """
    Sanitize user input to prevent XSS and other injection attacks
    """
    
    def process_request(self, request):
        # Don't process file uploads
        if request.content_type and 'multipart/form-data' in request.content_type:
            return None
        
        # Sanitize POST data
        if request.method == 'POST' and request.POST:
            sanitized_post = request.POST.copy()
            for key, value in request.POST.items():
                if isinstance(value, str):
                    # Check for potential XSS in non-content fields
                    if key not in ['content', 'answer', 'question', 'transcription']:
                        if self.contains_html_tags(value):
                            logger.warning(
                                f'HTML tags detected in input field: {key}, Value: {value[:100]}'
                            )
            request.POST = sanitized_post
        
        return None
    
    def contains_html_tags(self, text):
        """Check if text contains HTML tags"""
        html_patterns = ['<script', '<iframe', '<object', '<embed', '<style', 'javascript:', 'onerror=', 'onload=']
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in html_patterns)
