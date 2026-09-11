import json
import urllib.request
import urllib.error
import sys
from typing import cast, Dict, List, Any

# Ensure UTF-8 output formatting for terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

test_cases = [
    # --- AUTH ENDPOINTS ---
    {
        "name": "Login - Empty Payload {}",
        "url": f"{BASE_URL}/auth/api/login/",
        "method": "POST",
        "raw_data": json.dumps({}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Login - Missing Password",
        "url": f"{BASE_URL}/auth/api/login/",
        "method": "POST",
        "raw_data": json.dumps({"email": "user@example.com"}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Login - Missing Email",
        "url": f"{BASE_URL}/auth/api/login/",
        "method": "POST",
        "raw_data": json.dumps({"password": "somepassword"}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Login - Invalid Data Types (Integer instead of Email/String)",
        "url": f"{BASE_URL}/auth/api/login/",
        "method": "POST",
        "raw_data": json.dumps({"email": 12345, "password": True}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Login - Malformed JSON String",
        "url": f"{BASE_URL}/auth/api/login/",
        "method": "POST",
        "raw_data": b'{"email": "test@example.com", "password": ',
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Login - Invalid Credentials",
        "url": f"{BASE_URL}/auth/api/login/",
        "method": "POST",
        "raw_data": json.dumps({"email": "nonexistent@example.com", "password": "wrongpassword"}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Register - Empty Payload {}",
        "url": f"{BASE_URL}/auth/api/register/",
        "method": "POST",
        "raw_data": json.dumps({}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Register - Invalid Email Format",
        "url": f"{BASE_URL}/auth/api/register/",
        "method": "POST",
        "raw_data": json.dumps({"email": "invalid-email-address", "password": "password123", "password_confirm": "password123"}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Register - Mismatched Passwords",
        "url": f"{BASE_URL}/auth/api/register/",
        "method": "POST",
        "raw_data": json.dumps({"email": "testmismatch@example.com", "password": "Password123", "password_confirm": "Different123"}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Register - Short Password (< 8 chars)",
        "url": f"{BASE_URL}/auth/api/register/",
        "method": "POST",
        "raw_data": json.dumps({"email": "testnew@example.com", "password": "123", "password_confirm": "123"}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Refresh Token - Empty Payload {}",
        "url": f"{BASE_URL}/auth/api/refresh/",
        "method": "POST",
        "raw_data": json.dumps({}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Refresh Token - Invalid Token String",
        "url": f"{BASE_URL}/auth/api/refresh/",
        "method": "POST",
        "raw_data": json.dumps({"refresh": "invalid_jwt_token_string"}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Forgot Password - Empty Payload {}",
        "url": f"{BASE_URL}/auth/api/forgot-password/",
        "method": "POST",
        "raw_data": json.dumps({}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Forgot Password - Invalid Email Format",
        "url": f"{BASE_URL}/auth/api/forgot-password/",
        "method": "POST",
        "raw_data": json.dumps({"email": "not-an-email"}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },

    # --- MEETINGS ENDPOINTS ---
    {
        "name": "Join Meeting API - Empty Payload {}",
        "url": f"{BASE_URL}/meetings/api/join/",
        "method": "POST",
        "raw_data": json.dumps({}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Join Meeting API - Nonexistent Room Code",
        "url": f"{BASE_URL}/meetings/api/join/",
        "method": "POST",
        "raw_data": json.dumps({"room_code": "INVALID_ROOM_CODE_9999"}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [400],
    },
    {
        "name": "Create Meeting - Unauthenticated Access",
        "url": f"{BASE_URL}/meetings/api/",
        "method": "POST",
        "raw_data": json.dumps({"title": "Unauthorized Meeting"}).encode("utf-8"),
        "headers": {"Content-Type": "application/json"},
        "expected_codes": [401, 403],
    },
]

print("=" * 75)
print("TESTING INVALID PAYLOADS & ERROR CODES Across MeetFlow APIs")
print("=" * 75)

passed_count = 0
failed_count = 0

for test in test_cases:
    url = cast(str, test["url"])
    headers = cast(Dict[str, str], test.get("headers", {}))
    body = cast(bytes, test["raw_data"])
    method = cast(str, test["method"])
    expected_codes = cast(List[int], test.get("expected_codes", [400]))
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            status_code = resp.getcode()
            response_text = resp.read().decode("utf-8")
            if status_code in expected_codes:
                print(f"[PASS] {test['name']}")
                print(f"       HTTP Status Code: {status_code}")
                print(f"       Response Snippet: {response_text[:150].replace('\n', ' ')}")
                passed_count += 1
            else:
                print(f"[UNEXPECTED SUCCESS] {test['name']}")
                print(f"       Expected {expected_codes}, but got Status {status_code}")
                print(f"       Response: {response_text[:150]}")
                failed_count += 1
            print("-" * 75)
    except urllib.error.HTTPError as e:
        status_code = e.code
        try:
            response_text = e.read().decode("utf-8")
        except Exception:
            response_text = ""
            
        if status_code in expected_codes:
            print(f"[PASS] {test['name']}")
            print(f"       HTTP Status Code: {status_code}")
            print(f"       Response Snippet: {response_text[:150].replace('\n', ' ')}")
            passed_count += 1
        elif status_code == 500:
            print(f"[FAIL - 500 SERVER CRASH] {test['name']}")
            print(f"       HTTP Status Code: 500 (Internal Server Error)")
            print(f"       Response Snippet: {response_text[:150].replace('\n', ' ')}")
            failed_count += 1
        else:
            print(f"[FAIL] {test['name']}")
            print(f"       Expected {expected_codes}, got HTTP Status Code: {status_code}")
            print(f"       Response Snippet: {response_text[:150].replace('\n', ' ')}")
            failed_count += 1
        print("-" * 75)
    except Exception as e:
        print(f"[ERROR] {test['name']} - Exception: {e}")
        failed_count += 1
        print("-" * 75)

print("\n" + "=" * 75)
print(f"TEST RESULTS SUMMARY: {passed_count} PASSED, {failed_count} FAILED out of {len(test_cases)} tests.")
print("=" * 75)

