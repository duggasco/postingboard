#!/usr/bin/env python3
"""
Test admin team stats with proper authentication using curl.
"""

import subprocess
import json
import os

print("Testing Admin Team Stats with Authentication")
print("=" * 50)

# Step 1: Login as admin and get session cookie
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

# Step 2: Test team stats API with cookie
print("\n2. Testing team stats API with admin session...")
stats_result = subprocess.run([
    'curl', '-s', '-b', '/tmp/admin_cookies.txt',
    'http://localhost:9094/api/admin/team-stats'
], capture_output=True, text=True)

try:
    data = json.loads(stats_result.stdout)
    print(f"Response type: {type(data)}")
    
    if 'teams_overview' in data:
        teams = data['teams_overview']
        print(f"\nFound {len(teams)} teams in overview:")
        for team in teams[:3]:  # Show first 3 teams
            print(f"  - {team['name']} (UUID: {team['id']})")
            print(f"    Members: {team.get('member_count', 0)}, Submitted: {team.get('submitted_count', 0)}, Claimed: {team.get('claimed_count', 0)}")
    elif 'error' in data:
        print(f"Error: {data['error']}")
    else:
        print("Unexpected response structure:")
        print(json.dumps(data, indent=2)[:500])
except json.JSONDecodeError:
    print(f"Failed to parse JSON response: {stats_result.stdout[:200]}")

# Step 3: Test with specific team UUID
print("\n3. Getting teams list first...")
teams_result = subprocess.run([
    'curl', '-s',
    'http://localhost:9094/api/teams'
], capture_output=True, text=True)

try:
    teams = json.loads(teams_result.stdout)
    if teams and len(teams) > 0:
        first_team = teams[0]
        team_uuid = first_team['id']
        team_name = first_team['name']
        
        print(f"\n4. Testing stats for specific team: {team_name} ({team_uuid})...")
        team_stats_result = subprocess.run([
            'curl', '-s', '-b', '/tmp/admin_cookies.txt',
            f'http://localhost:9094/api/admin/team-stats?team_id={team_uuid}'
        ], capture_output=True, text=True)
        
        try:
            team_data = json.loads(team_stats_result.stdout)
            if 'teamId' in team_data:
                print(f"Successfully retrieved stats for team: {team_data.get('teamName')}")
                print(f"Team UUID: {team_data.get('teamId')}")
                if 'overview' in team_data:
                    overview = team_data['overview']
                    print(f"Members: {overview.get('total_members', 0)}")
                    print(f"Ideas Submitted: {overview.get('ideas_submitted', 0)}")
                    print(f"Ideas Claimed: {overview.get('ideas_claimed', 0)}")
            elif 'error' in team_data:
                print(f"Error: {team_data['error']}")
            else:
                print("Response structure:")
                print(json.dumps(team_data, indent=2)[:300])
        except json.JSONDecodeError:
            print(f"Failed to parse team stats JSON: {team_stats_result.stdout[:200]}")
except json.JSONDecodeError:
    print("Failed to get teams list")

# Cleanup
os.remove('/tmp/admin_cookies.txt') if os.path.exists('/tmp/admin_cookies.txt') else None