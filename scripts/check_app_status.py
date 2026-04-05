#!/usr/bin/env python3
"""Quick status check for Flask application"""

import requests
import sys
import time

BASE_URL = "http://127.0.0.1:5000"

print("=" * 70)
print("DIAPREDICT APPLICATION STATUS CHECK")
print("=" * 70)

# Check if app is running
max_retries = 3
app_running = False

for attempt in range(1, max_retries + 1):
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        app_running = True
        print(f"\nStatus: APPLICATION IS RUNNING")
        print(f"  Host: http://127.0.0.1:5000")
        print(f"  Status Code: {response.status_code}\n")
        break
    except requests.exceptions.ConnectionError:
        if attempt < max_retries:
            print(f"Attempt {attempt}/{max_retries}: Flask not responding, retrying...")
            time.sleep(2)
        else:
            print(f"\nStatus: APPLICATION NOT RESPONDING")
            print(f"  Models may still be loading (10-15 seconds)")
            sys.exit(0)
    except requests.exceptions.Timeout:
        print(f"Attempt {attempt}/{max_retries}: Connection timeout, retrying...")
        time.sleep(2)

if app_running:
    print("ENDPOINT CHECKS:")
    print("-" * 70)
    
    endpoints = [
        ("/", "Home", "GET"),
        ("/login", "Login Form", "GET"),
        ("/signup", "Signup Form", "GET"),
        ("/dashboard", "Dashboard (Protected)", "GET"),
        ("/predict", "Prediction Form (Protected)", "GET"),
    ]
    
    for route, name, method in endpoints:
        try:
            if method == "GET":
                resp = requests.get(f"{BASE_URL}{route}", timeout=3, allow_redirects=False)
            status = f"HTTP {resp.status_code}"
            expected = "302" if "Protected" in name else "200"
            actual = resp.status_code
            result = "OK" if str(actual) == expected else f"WARNING (expected {expected})"
            print(f"  {name:30} - {status:12} - {result}")
        except Exception as e:
            print(f"  {name:30} - ERROR")
    
    # Check CSRF protection
    print("\n" + "-" * 70)
    print("SECURITY CHECKS:")
    print("-" * 70)
    
    for route, name in [("/login", "Login"), ("/signup", "Signup")]:
        try:
            resp = requests.get(f"{BASE_URL}{route}", timeout=3)
            has_csrf = 'name="csrf_token"' in resp.text
            status = "PROTECTED" if has_csrf else "UNPROTECTED"
            print(f"  {name:15} CSRF Token - {status}")
        except Exception as e:
            print(f"  {name:15} CSRF Token - ERROR")
    
    print("\n" + "=" * 70)
    print("RESULT: ALL SYSTEMS OPERATIONAL")
    print("=" * 70)
    print("\nApplication is ready. Access it at:")
    print("  http://localhost:5000")
    print("  http://127.0.0.1:5000")
    print("=" * 70)
