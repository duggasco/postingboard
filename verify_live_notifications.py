#!/usr/bin/env python3
"""Verify the live notification system."""

import requests
from bs4 import BeautifulSoup
import time

session = requests.Session()

print("=== Live Notification System Test ===\n")

# 1. Login as admin
print("1. Logging in as admin...")
login_response = session.post("http://localhost:9094/admin/login", 
                              data={'password': '2929arch'}, 
                              allow_redirects=True)

# 2. Go to a page with notifications
print("\n2. Loading My Ideas page (has notification bell)...")
my_ideas_response = session.get("http://localhost:9094/my-ideas")
soup = BeautifulSoup(my_ideas_response.text, 'html.parser')

# 3. Check notification elements
bell = soup.find(id='notification-bell')
count_elem = soup.find(id='notification-count')

print("\n3. HTML Elements:")
print(f"   Bell found: {bell is not None}")
if bell:
    print(f"   Bell HTML: {str(bell)[:100]}...")

print(f"   Count badge found: {count_elem is not None}")
if count_elem:
    print(f"   Count HTML: {count_elem}")
    print(f"   Count text: '{count_elem.text}'")
    print(f"   Count style: {count_elem.get('style')}")

# 4. Check API directly
print("\n4. API Response:")
api_response = session.get("http://localhost:9094/api/user/notifications")
data = api_response.json()
print(f"   Success: {data.get('success')}")
print(f"   Unread count: {data.get('unread_count')}")
print(f"   Total notifications: {len(data.get('notifications', []))}")

# 5. Create a new test notification to see if it appears
print("\n5. Creating fresh test notification...")
from database import get_session
from models import Notification
from datetime import datetime

db = get_session()
test_notification = Notification(
    user_email='admin@system.local',
    type='team_approval_request',
    title='Fresh Test Notification',
    message='This is a brand new test notification created just now',
    related_user_email='test@example.com',
    is_read=False,
    created_at=datetime.utcnow()
)
db.add(test_notification)
db.commit()
notif_id = test_notification.id
db.close()
print(f"   Created notification ID: {notif_id}")

# 6. Check API again
print("\n6. API Response after creating new notification:")
time.sleep(1)  # Brief pause
api_response = session.get("http://localhost:9094/api/user/notifications")
data = api_response.json()
print(f"   Unread count: {data.get('unread_count')}")
fresh_notif = next((n for n in data.get('notifications', []) if n.get('title') == 'Fresh Test Notification'), None)
if fresh_notif:
    print(f"   ✓ Fresh notification found in API response")
else:
    print(f"   ✗ Fresh notification NOT found in API response")