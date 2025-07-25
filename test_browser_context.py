#!/usr/bin/env python3
"""
Test idea detail features in a browser context simulation.
"""

import subprocess
import json
import time

print("Testing Idea Detail Features - Browser Context Simulation")
print("=" * 60)

# Test idea UUID
idea_uuid = "52a547a5-d5f0-4e03-b2ef-2719c7d626f2"

# Step 1: Load the idea detail page
print(f"\n1. Loading idea detail page: /idea/{idea_uuid}")
result = subprocess.run([
    'curl', '-s', '-b', '/tmp/admin_cookies.txt',
    f'http://localhost:9094/idea/{idea_uuid}',
    '-o', '/tmp/idea_page.html',
    '-w', '%{http_code}'
], capture_output=True, text=True)

status_code = result.stdout.strip()
print(f"   Status: {status_code}")

# Check if the page has tab access
result = subprocess.run([
    'grep', '-c', 'has_tab_access.*true', '/tmp/idea_page.html'
], capture_output=True, text=True)

has_access = int(result.stdout.strip()) > 0
print(f"   Tab access: {'✓ Yes' if has_access else '✗ No'}")

# Step 2: Simulate tab clicks and data loading
print("\n2. Simulating tab interactions:")

tabs = [
    ("Overview", "overview-tab"),
    ("Comments", "comments-tab"),
    ("Links & Resources", "links-tab"),
    ("Activity", "activity-tab"),
    ("Status History", "history-tab")
]

for tab_name, tab_id in tabs:
    print(f"\n   {tab_name} Tab:")
    
    # Check if tab exists in HTML
    result = subprocess.run([
        'grep', '-c', f'id="{tab_id}"', '/tmp/idea_page.html'
    ], capture_output=True, text=True)
    
    tab_exists = int(result.stdout.strip()) > 0
    print(f"   - Tab exists: {'✓' if tab_exists else '✗'}")
    
    # Simulate API calls that would happen on tab click
    if tab_name == "Comments":
        endpoint = f"/api/ideas/{idea_uuid}/comments"
    elif tab_name == "Links & Resources":
        endpoint = f"/api/ideas/{idea_uuid}/external-links"
    elif tab_name == "Activity":
        endpoint = f"/api/ideas/{idea_uuid}/activities"
    elif tab_name == "Status History":
        endpoint = f"/api/ideas/{idea_uuid}/status-history"
    else:
        continue
    
    if tab_exists:
        result = subprocess.run([
            'curl', '-s', '-b', '/tmp/admin_cookies.txt',
            f'http://localhost:9094{endpoint}'
        ], capture_output=True, text=True)
        
        try:
            data = json.loads(result.stdout)
            if isinstance(data, list):
                print(f"   - Data loaded: ✓ ({len(data)} items)")
            else:
                print(f"   - Data loaded: ✓")
        except:
            print(f"   - Data load failed: ✗")

# Step 3: Test interactive features
print("\n3. Testing interactive features:")

# Test comment submission
print("\n   Comment Submission:")
comment_data = {
    "content": "Browser test comment",
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
    response = json.loads(result.stdout)
    if response.get('success'):
        print("   - Submit comment: ✓")
    else:
        print(f"   - Submit comment: ✗ ({response.get('message', 'Unknown error')})")
except:
    print("   - Submit comment: ✗ (Invalid response)")

# Test external link submission
print("\n   External Link Submission:")
link_data = {
    "link_type": "documentation",
    "title": "Test Documentation",
    "url": "https://example.com/docs",
    "description": "Browser test link"
}

result = subprocess.run([
    'curl', '-s', '-b', '/tmp/admin_cookies.txt',
    '-X', 'POST', 
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(link_data),
    f'http://localhost:9094/api/ideas/{idea_uuid}/external-links'
], capture_output=True, text=True)

try:
    response = json.loads(result.stdout)
    if response.get('success'):
        print("   - Add external link: ✓")
    else:
        print(f"   - Add external link: ✗ ({response.get('message', 'Unknown error')})")
except:
    print("   - Add external link: ✗ (Invalid response)")

# Test sub-status update
print("\n   Sub-Status Update:")
status_data = {
    "sub_status": "testing",
    "progress_percentage": 60,
    "comment": "Moving to testing phase"
}

result = subprocess.run([
    'curl', '-s', '-b', '/tmp/admin_cookies.txt',
    '-X', 'PUT',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(status_data),
    f'http://localhost:9094/api/ideas/{idea_uuid}/sub-status'
], capture_output=True, text=True)

try:
    response = json.loads(result.stdout)
    if response.get('success'):
        print("   - Update sub-status: ✓")
        print(f"     New status: {response.get('sub_status')}")
        print(f"     Progress: {response.get('progress_percentage')}%")
    else:
        print(f"   - Update sub-status: ✗ ({response.get('message', 'Unknown error')})")
except:
    print("   - Update sub-status: ✗ (Invalid response)")

# Step 4: Verify data persistence
print("\n4. Verifying data persistence:")
time.sleep(1)  # Give time for DB writes

# Re-fetch all data to verify changes
endpoints = [
    ("Comments", f"/api/ideas/{idea_uuid}/comments"),
    ("Activities", f"/api/ideas/{idea_uuid}/activities"),
    ("External Links", f"/api/ideas/{idea_uuid}/external-links"),
    ("Status History", f"/api/ideas/{idea_uuid}/status-history")
]

for name, endpoint in endpoints:
    result = subprocess.run([
        'curl', '-s', '-b', '/tmp/admin_cookies.txt',
        f'http://localhost:9094{endpoint}'
    ], capture_output=True, text=True)
    
    try:
        data = json.loads(result.stdout)
        if isinstance(data, list):
            print(f"   - {name}: {len(data)} items")
            # Check for our test data
            if name == "Comments" and any("Browser test comment" in str(item) for item in data):
                print(f"     ✓ Test comment found")
            elif name == "External Links" and any("Test Documentation" in str(item) for item in data):
                print(f"     ✓ Test link found")
            elif name == "Activities" and any("testing" in str(item) for item in data):
                print(f"     ✓ Status change activity found")
    except:
        print(f"   - {name}: Failed to load")

# Step 5: Test GANTT chart data
print("\n5. Testing GANTT chart data:")

# Check if idea has sub-status for GANTT
result = subprocess.run([
    'curl', '-s', '-b', '/tmp/admin_cookies.txt',
    f'http://localhost:9094/api/ideas'
], capture_output=True, text=True)

try:
    ideas = json.loads(result.stdout)
    test_idea = next((i for i in ideas if i['uuid'] == idea_uuid), None)
    if test_idea:
        print(f"   - Idea status: {test_idea['status']}")
        print(f"   - Sub-status: {test_idea.get('sub_status', 'None')}")
        print(f"   - Progress: {test_idea.get('progress_percentage', 0)}%")
        if test_idea.get('sub_status'):
            print("   - GANTT chart: ✓ Should be visible")
        else:
            print("   - GANTT chart: ✗ No sub-status set")
except:
    print("   - Failed to check GANTT data")

print("\n" + "=" * 60)
print("Browser context simulation complete!")

# Cleanup
import os
os.remove('/tmp/idea_page.html') if os.path.exists('/tmp/idea_page.html') else None