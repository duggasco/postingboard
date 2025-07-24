#!/usr/bin/env python3
"""Test the notification API endpoint."""

import requests
import json

# Test as admin
print("=== Testing Notification API ===\n")

# First, login as admin
login_url = "http://localhost:9094/admin/login"
session = requests.Session()

print("1. Logging in as admin...")
login_data = {
    'password': '2929arch'
}
response = session.post(login_url, data=login_data, allow_redirects=False)
print(f"   Login response: {response.status_code}")

# Check session cookies
print("\n2. Session cookies:")
for cookie in session.cookies:
    print(f"   {cookie.name}: {cookie.value[:20]}...")

# Get user notifications
print("\n3. Fetching user notifications...")
notif_url = "http://localhost:9094/api/user/notifications"
response = session.get(notif_url)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Success: {data.get('success')}")
    print(f"   Unread count: {data.get('unread_count')}")
    print(f"   Total notifications: {len(data.get('notifications', []))}")
    
    # Show first few notifications
    for i, notif in enumerate(data.get('notifications', [])[:3]):
        print(f"\n   Notification {i+1}:")
        print(f"     Type: {notif.get('type')}")
        print(f"     Title: {notif.get('title')}")
        print(f"     Read: {notif.get('is_read')}")
        print(f"     User: {notif.get('related_user')}")
else:
    print(f"   Error: {response.text}")

# Also test admin notifications endpoint
print("\n4. Fetching admin notifications...")
admin_notif_url = "http://localhost:9094/api/admin/notifications"
response = session.get(admin_notif_url)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Success: {data.get('success')}")
    print(f"   Total pending: {data.get('total_pending')}")
    for notif in data.get('notifications', []):
        print(f"   - {notif.get('type')}: {notif.get('message')}")