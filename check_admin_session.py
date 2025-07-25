#!/usr/bin/env python3
"""
Check admin session data and fix if needed.
"""

import subprocess
import json

print("Checking Admin Session Data")
print("=" * 50)

# Create a test script to check session data
test_script = '''
from app import create_app
from flask import session
import json

app = create_app()

# Create a test request context
with app.test_request_context():
    with app.test_client() as client:
        # Login as admin
        response = client.post('/admin/login', data={'password': '2929arch'})
        print(f"Login status: {response.status_code}")
        
        # Check session data
        with client.session_transaction() as sess:
            print("\\nSession data after admin login:")
            for key, value in sess.items():
                print(f"  {key}: {value}")
            
            # Check what's missing
            print("\\nChecking for required fields:")
            required_fields = ['user_email', 'user_verified', 'user_name']
            missing = []
            for field in required_fields:
                if field in sess:
                    print(f"  ✓ {field}: {sess.get(field)}")
                else:
                    print(f"  ✗ {field}: MISSING")
                    missing.append(field)
            
            if missing:
                print("\\nAdding missing session data...")
                # Add missing admin data
                if 'user_email' not in sess:
                    sess['user_email'] = 'admin@system.local'
                if 'user_verified' not in sess:
                    sess['user_verified'] = True
                if 'user_name' not in sess:
                    sess['user_name'] = 'Admin'
                sess.permanent = True
                
                print("\\nUpdated session data:")
                for field in required_fields:
                    print(f"  {field}: {sess.get(field)}")
        
        # Test sub-status endpoint with updated session
        print("\\nTesting sub-status endpoint with session:")
        response = client.put(
            '/api/ideas/52a547a5-d5f0-4e03-b2ef-2719c7d626f2/sub-status',
            json={
                'sub_status': 'in_development',
                'progress_percentage': 30,
                'comment': 'Test from admin session'
            }
        )
        print(f"Sub-status update status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.get_json()}")
        else:
            print(f"Success: {response.get_json()}")
'''

# Run the test script in the container
result = subprocess.run([
    'docker', 'exec', 'postingboard-flask-app-1',
    'python', '-c', test_script
], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print(f"\nErrors:\n{result.stderr}")