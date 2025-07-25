#!/usr/bin/env python3
"""
Test admin team stats API with proper authentication.
"""

import subprocess
import json

# First, let's test the team stats endpoint directly with curl
print("Testing Admin Team Stats API")
print("=" * 50)

# Test 1: Get all teams
print("\n1. Getting all teams...")
result = subprocess.run([
    'curl', '-s', 
    'http://localhost:9094/api/teams'
], capture_output=True, text=True)

if result.returncode == 0:
    teams = json.loads(result.stdout)
    print(f"Found {len(teams)} teams")
    if teams:
        first_team = teams[0]
        team_uuid = first_team.get('id')
        team_name = first_team.get('name')
        print(f"First team: {team_name} (UUID: {team_uuid})")
        
        # Test 2: Try to access team stats without auth
        print(f"\n2. Testing team stats without auth...")
        result = subprocess.run([
            'curl', '-s',
            f'http://localhost:9094/api/admin/team-stats?team_id={team_uuid}'
        ], capture_output=True, text=True)
        print(f"Response: {result.stdout[:100]}...")
        
        # Test 3: Test with simulated admin session
        print(f"\n3. Testing team stats with admin session...")
        # We need to use the Flask app directly since we can't easily manage cookies with curl
        print("NOTE: This endpoint requires proper admin session authentication")
        print("The endpoint expects: session.get('is_admin') == True")
        
        # Test 4: Test team stats endpoint structure
        print(f"\n4. Checking if team_id parameter is being processed correctly...")
        print(f"URL being tested: /api/admin/team-stats?team_id={team_uuid}")
        
else:
    print("Failed to get teams")

# Test 5: Check what happens with no team_id parameter
print("\n5. Testing without team_id parameter (should return all teams overview)...")
result = subprocess.run([
    'curl', '-s',
    'http://localhost:9094/api/admin/team-stats'
], capture_output=True, text=True)
print(f"Response: {result.stdout[:100]}...")