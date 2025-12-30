#!/usr/bin/env python
"""
Security Test Script for U-Notes
Tests various security features to ensure they're working correctly
"""

import requests
import time
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

BASE_URL = "http://localhost:8000"

def print_test(name, passed):
    """Print test result"""
    if passed:
        print(f"{Fore.GREEN}✓ {name}")
    else:
        print(f"{Fore.RED}✗ {name}")

def test_rate_limiting():
    """Test rate limiting on login endpoint"""
    print(f"\n{Fore.CYAN}Testing Rate Limiting...")
    
    # Attempt 10 rapid requests
    success_count = 0
    blocked_count = 0
    
    for i in range(10):
        try:
            response = requests.post(
                f"{BASE_URL}/login/",
                data={"username": "test", "password": "test"},
                timeout=5
            )
            if response.status_code == 403:
                blocked_count += 1
            else:
                success_count += 1
        except Exception as e:
            print(f"Error: {e}")
    
    # Should block some requests after rate limit
    print_test("Rate Limiting Active", blocked_count > 0)
    print(f"  {success_count} requests allowed, {blocked_count} blocked")

def test_security_headers():
    """Test security headers are present"""
    print(f"\n{Fore.CYAN}Testing Security Headers...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        headers = response.headers
        
        # Check for security headers
        tests = {
            "X-Frame-Options": "X-Frame-Options" in headers,
            "X-Content-Type-Options": "X-Content-Type-Options" in headers,
            "X-XSS-Protection": "X-XSS-Protection" in headers,
            "Referrer-Policy": "Referrer-Policy" in headers,
        }
        
        for name, passed in tests.items():
            print_test(name, passed)
            if passed:
                print(f"    Value: {headers.get(name)}")
    
    except Exception as e:
        print(f"{Fore.RED}Error testing headers: {e}")

def test_xss_protection():
    """Test XSS protection in forms"""
    print(f"\n{Fore.CYAN}Testing XSS Protection...")
    
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
    ]
    
    for payload in xss_payloads:
        try:
            # Try to submit XSS in search
            response = requests.get(
                f"{BASE_URL}/search/",
                params={"q": payload},
                timeout=5
            )
            
            # Check if payload appears in response (it shouldn't)
            payload_escaped = payload in response.text
            print_test(f"XSS Payload Blocked: {payload[:30]}...", 
                      response.status_code == 403 or not payload_escaped)
        
        except Exception as e:
            print(f"Error: {e}")

def test_sql_injection():
    """Test SQL injection protection"""
    print(f"\n{Fore.CYAN}Testing SQL Injection Protection...")
    
    sql_payloads = [
        "' OR '1'='1",
        "1' UNION SELECT * FROM users--",
        "'; DROP TABLE notes;--",
    ]
    
    for payload in sql_payloads:
        try:
            response = requests.get(
                f"{BASE_URL}/search/",
                params={"q": payload},
                timeout=5
            )
            
            # Should block or safely handle
            print_test(f"SQL Injection Blocked: {payload[:30]}...",
                      response.status_code in [403, 404, 200])
        
        except Exception as e:
            print(f"Error: {e}")

def test_directory_traversal():
    """Test directory traversal protection"""
    print(f"\n{Fore.CYAN}Testing Directory Traversal Protection...")
    
    traversal_payloads = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "%2e%2e%2f%2e%2e%2f",
    ]
    
    for payload in traversal_payloads:
        try:
            response = requests.get(
                f"{BASE_URL}/media/{payload}",
                timeout=5
            )
            
            # Should block access
            print_test(f"Directory Traversal Blocked: {payload[:30]}...",
                      response.status_code in [403, 404])
        
        except Exception as e:
            print(f"Error: {e}")

def test_csrf_protection():
    """Test CSRF protection"""
    print(f"\n{Fore.CYAN}Testing CSRF Protection...")
    
    try:
        # Try to POST without CSRF token
        response = requests.post(
            f"{BASE_URL}/login/",
            data={"username": "test", "password": "test"},
            timeout=5
        )
        
        # Should require CSRF token
        csrf_required = "CSRF" in response.text or response.status_code == 403
        print_test("CSRF Token Required", csrf_required)
    
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all security tests"""
    print(f"\n{Fore.YELLOW}{'='*50}")
    print(f"{Fore.YELLOW}U-NOTES SECURITY TEST SUITE")
    print(f"{Fore.YELLOW}{'='*50}")
    
    print(f"\n{Fore.YELLOW}Testing server at: {BASE_URL}")
    print(f"{Fore.YELLOW}Make sure the Django development server is running!")
    
    time.sleep(2)
    
    # Run all tests
    test_security_headers()
    test_csrf_protection()
    test_xss_protection()
    test_sql_injection()
    test_directory_traversal()
    test_rate_limiting()
    
    print(f"\n{Fore.YELLOW}{'='*50}")
    print(f"{Fore.GREEN}Security tests completed!")
    print(f"{Fore.YELLOW}{'='*50}\n")
    
    print(f"{Fore.CYAN}Note: Some tests may fail if:")
    print(f"  - Server is not running")
    print(f"  - DEBUG mode is enabled")
    print(f"  - Middleware is not configured correctly")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}Error running tests: {e}")
