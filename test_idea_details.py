#!/usr/bin/env python3
"""
Test idea detail endpoints with proper authentication.
"""

import subprocess
import json

print("Testing Idea Detail Features")
print("=" * 50)

# Test UUID
idea_uuid = "52a547a5-d5f0-4e03-b2ef-2719c7d626f2"
print(f"Testing idea: {idea_uuid}")

# First, simulate logging in as the idea submitter
print("\n1. Simulating login as manager1@company.com (idea submitter)...")

# Create a session cookie file
cookie_file = "/tmp/test_cookies.txt"

# Simulate email verification and session
print("Setting up test session...")
result = subprocess.run([
    'docker', 'exec', 'postingboard-flask-app-1', 
    'python', '-c', f'''
from database import get_session
from models import UserProfile
from flask import Flask
from flask_session import Session
import tempfile
import os

# Create a minimal Flask app to generate session
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['user_email'] = 'manager1@company.com'
        sess['user_name'] = 'Bob Manager'
        sess['user_verified'] = True
        sess['user_role'] = 'manager'
        sess.permanent = True
    
    # Test comments endpoint
    resp = client.get('/api/ideas/{idea_uuid}/comments')
    print(f"Comments endpoint status: {{resp.status_code}}")
    if resp.status_code != 200:
        print(f"Comments error: {{resp.get_json()}}")
    else:
        print(f"Comments data: {{resp.get_json()}}")
'''
], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print(f"Errors: {result.stderr}")

# Now test the endpoints directly with curl
print("\n2. Testing endpoints with curl (no auth)...")

endpoints = [
    f"/api/ideas/{idea_uuid}/comments",
    f"/api/ideas/{idea_uuid}/activities", 
    f"/api/ideas/{idea_uuid}/external-links",
    f"/api/ideas/{idea_uuid}/status-history"
]

for endpoint in endpoints:
    print(f"\nTesting {endpoint}:")
    result = subprocess.run([
        'curl', '-s', f'http://localhost:9094{endpoint}'
    ], capture_output=True, text=True)
    
    try:
        data = json.loads(result.stdout)
        if 'error' in data:
            print(f"  Error: {data['error']}")
        else:
            print(f"  Success: Got {len(data) if isinstance(data, list) else 'data'}")
    except json.JSONDecodeError:
        print(f"  Failed to parse response: {result.stdout[:100]}")

# Check if the endpoints are registered
print("\n3. Checking if endpoints exist...")
result = subprocess.run([
    'docker', 'exec', 'postingboard-flask-app-1',
    'python', '-c', '''
from app import create_app
app = create_app()
print("Registered endpoints containing 'ideas':")
for rule in app.url_map.iter_rules():
    if 'ideas' in rule.rule and any(x in rule.rule for x in ['comments', 'activities', 'external-links', 'status-history']):
        print(f"  {rule.rule} -> {rule.methods}")
'''
], capture_output=True, text=True)

print(result.stdout)