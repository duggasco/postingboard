#!/usr/bin/env python3
"""Simulate the browser flow for admin notifications."""

import requests
from bs4 import BeautifulSoup

session = requests.Session()

print("=== Simulating Browser Flow ===\n")

# 1. Login as admin
print("1. Logging in as admin...")
login_response = session.post("http://localhost:9094/admin/login", 
                              data={'password': '2929arch'}, 
                              allow_redirects=True)
print(f"   Final URL: {login_response.url}")
print(f"   Status: {login_response.status_code}")

# 2. Check if notification bell is in the HTML
print("\n2. Checking if notification bell is in HTML...")
soup = BeautifulSoup(login_response.text, 'html.parser')
bell = soup.find(id='notification-bell')
if bell:
    print("   ✓ Notification bell found in HTML")
else:
    print("   ✗ Notification bell NOT found in HTML")
    # Check if user_email is in session
    nav_items = soup.find_all('li', class_='nav-notification')
    print(f"   Nav notification items found: {len(nav_items)}")

# 3. Check session state
print("\n3. Checking session state via profile endpoint...")
profile_response = session.get("http://localhost:9094/profile")
if profile_response.status_code == 302:  # Redirect means not verified
    print("   User not verified (redirected)")
else:
    print(f"   Profile page status: {profile_response.status_code}")

# 4. Direct API call
print("\n4. Direct API call to /api/user/notifications...")
api_response = session.get("http://localhost:9094/api/user/notifications")
print(f"   Status: {api_response.status_code}")
if api_response.status_code == 200:
    data = api_response.json()
    print(f"   Response: {data}")

# 5. Check JavaScript includes
print("\n5. Checking if main.js is included...")
scripts = soup.find_all('script', src=True)
main_js_found = any('main.js' in script['src'] for script in scripts)
print(f"   main.js included: {main_js_found}")

# 6. Look for any error messages
print("\n6. Checking for error messages...")
flashes = soup.find_all(class_='flashes')
if flashes:
    print("   Flash messages found:")
    for flash in flashes:
        print(f"   - {flash.get_text().strip()}")