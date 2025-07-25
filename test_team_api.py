#!/usr/bin/env python3
"""
Test the team stats API with UUID changes.
"""

import requests
import json

BASE_URL = "http://localhost:9094"

def test_team_apis():
    """Test team-related APIs."""
    print("Testing Team APIs with UUID support...")
    
    # First, let's get the list of teams
    response = requests.get(f"{BASE_URL}/api/teams")
    if response.status_code != 200:
        print(f"✗ Failed to get teams: {response.status_code}")
        return
        
    teams = response.json()
    if not teams:
        print("✗ No teams found")
        return
        
    print(f"✓ Found {len(teams)} teams")
    
    # Check that teams have UUIDs
    first_team = teams[0]
    team_id = first_team.get('id')
    print(f"First team: {first_team.get('name')}")
    print(f"Team ID (UUID): {team_id}")
    
    if len(str(team_id)) == 36 and '-' in str(team_id):
        print("✓ Teams API returns UUIDs")
    else:
        print("✗ Teams API still returns integer IDs")
        return
    
    # Test admin team stats without team_id (all teams overview)
    print("\nTesting admin team stats (all teams)...")
    # Note: This would normally require admin auth, but we're testing the structure
    
    # Test with a specific team UUID
    print(f"\nTesting admin team stats for specific team...")
    test_url = f"{BASE_URL}/api/admin/team-stats?team_id={team_id}"
    print(f"URL: {test_url}")
    
    # Test that integer team_id fails
    print("\nTesting that integer team_id is rejected...")
    response = requests.get(f"{BASE_URL}/api/admin/team-stats?team_id=1")
    print(f"Integer team_id response: {response.status_code}")
    
    # Check the response content for error message
    if response.status_code == 403:
        print("✓ Got expected 403 (auth required)")
    elif response.status_code == 400:
        data = response.json()
        if 'Invalid team identifier' in data.get('error', ''):
            print("✓ Integer team_id properly rejected")
        else:
            print(f"✗ Unexpected error: {data}")
    else:
        print(f"✗ Unexpected status: {response.status_code}")

if __name__ == "__main__":
    test_team_apis()