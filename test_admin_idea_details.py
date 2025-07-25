#!/usr/bin/env python3
"""
Test idea detail endpoints with admin authentication.
"""

import subprocess
import json

print("Testing Idea Detail Features with Admin Session")
print("=" * 50)

# Test UUID
idea_uuid = "52a547a5-d5f0-4e03-b2ef-2719c7d626f2"
print(f"Testing idea: {idea_uuid}")

# Step 1: Login as admin
print("\n1. Logging in as admin...")
login_result = subprocess.run([
    'curl', '-s', '-c', '/tmp/admin_cookies.txt',
    '-X', 'POST',
    '-d', 'password=2929arch',
    'http://localhost:9094/admin/login',
    '-w', '\n%{http_code}'
], capture_output=True, text=True)

response_lines = login_result.stdout.strip().split('\n')
status_code = response_lines[-1] if response_lines else ''
print(f"Login status code: {status_code}")

# Step 2: Test all SDLC endpoints
print("\n2. Testing SDLC endpoints with admin session...")

endpoints = [
    (f"/api/ideas/{idea_uuid}/comments", "Comments"),
    (f"/api/ideas/{idea_uuid}/activities", "Activities"), 
    (f"/api/ideas/{idea_uuid}/external-links", "External Links"),
    (f"/api/ideas/{idea_uuid}/status-history", "Status History")
]

for endpoint, name in endpoints:
    print(f"\n{name} ({endpoint}):")
    result = subprocess.run([
        'curl', '-s', '-b', '/tmp/admin_cookies.txt',
        f'http://localhost:9094{endpoint}'
    ], capture_output=True, text=True)
    
    try:
        data = json.loads(result.stdout)
        if isinstance(data, dict) and 'error' in data:
            print(f"  ✗ Error: {data['error']}")
        elif isinstance(data, list):
            print(f"  ✓ Success: Got {len(data)} items")
            if data and len(data) > 0:
                # Show first item as sample
                print(f"  Sample: {json.dumps(data[0], indent=2)[:200]}...")
        else:
            print(f"  ✓ Success: Got data")
            print(f"  Data: {json.dumps(data, indent=2)[:200]}...")
    except json.JSONDecodeError:
        print(f"  ✗ Failed to parse JSON response")
        print(f"  Raw response: {result.stdout[:200]}...")

# Step 3: Test sub-status endpoint
print("\n\n3. Testing sub-status update endpoint...")
test_data = {
    "sub_status": "in_development",
    "progress_percentage": 30,
    "comment": "Started development"
}

result = subprocess.run([
    'curl', '-s', '-b', '/tmp/admin_cookies.txt',
    '-X', 'PUT',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(test_data),
    f'http://localhost:9094/api/ideas/{idea_uuid}/sub-status'
], capture_output=True, text=True)

try:
    data = json.loads(result.stdout)
    if data.get('success'):
        print("  ✓ Sub-status update successful")
    else:
        print(f"  ✗ Sub-status update failed: {data.get('message', 'Unknown error')}")
except json.JSONDecodeError:
    print(f"  ✗ Failed to parse response: {result.stdout[:200]}...")

# Step 4: Test posting a comment
print("\n4. Testing comment posting...")
comment_data = {
    "content": "Test comment from admin",
    "is_internal": False
}

result = subprocess.run([
    'curl', '-s', '-b', '/tmp/admin_cookies.txt',
    '-X', 'POST',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(comment_data),
    f'http://localhost:9094/api/ideas/{idea_uuid}/comments'
], capture_output=True, text=True)

try:
    data = json.loads(result.stdout)
    if data.get('success'):
        print("  ✓ Comment posted successfully")
    else:
        print(f"  ✗ Comment posting failed: {data.get('message', 'Unknown error')}")
except json.JSONDecodeError:
    print(f"  ✗ Failed to parse response: {result.stdout[:200]}...")

# Cleanup
import os
os.remove('/tmp/admin_cookies.txt') if os.path.exists('/tmp/admin_cookies.txt') else None