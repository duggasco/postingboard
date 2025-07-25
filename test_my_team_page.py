#!/usr/bin/env python3
"""
Test the My Team page functionality with UUID changes.
"""

import requests
import json

BASE_URL = "http://localhost:9094"

def test_my_team_page():
    """Test My Team page data flow."""
    print("Testing My Team Page Data Flow...")
    print("=" * 50)
    
    # Step 1: Get teams list (what admin dropdown does)
    print("\n1. Loading teams for dropdown...")
    response = requests.get(f"{BASE_URL}/api/teams")
    if response.status_code != 200:
        print(f"✗ Failed to get teams: {response.status_code}")
        return
        
    teams = response.json()
    print(f"✓ Loaded {len(teams)} teams")
    
    # Show first few teams
    for i, team in enumerate(teams[:3]):
        print(f"   - {team['name']} (UUID: {team['id']})")
    
    # Step 2: Simulate selecting a team (what happens when admin selects from dropdown)
    if teams:
        selected_team = teams[0]
        team_uuid = selected_team['id']
        print(f"\n2. Simulating team selection: {selected_team['name']}")
        print(f"   Team UUID: {team_uuid}")
        
        # This is what the frontend would call
        api_url = f"/api/admin/team-stats?team_id={team_uuid}"
        print(f"   API call: {api_url}")
        
        # Note: Would need admin auth to actually call this
        
    # Step 3: Test all teams overview (no team_id parameter)
    print("\n3. Testing all teams overview...")
    api_url = "/api/admin/team-stats"
    print(f"   API call: {api_url}")
    
    # Step 4: Check that the frontend is using correct ID field
    print("\n4. Verifying team data structure...")
    if teams:
        team = teams[0]
        if 'id' in team and 'name' in team:
            print("✓ Team has 'id' and 'name' fields")
            if len(str(team['id'])) == 36:
                print("✓ 'id' field contains UUID")
            else:
                print("✗ 'id' field is not a UUID")
        else:
            print("✗ Team missing required fields")
            print(f"   Available fields: {list(team.keys())}")

def test_ideas_api():
    """Test that ideas API also returns UUIDs correctly."""
    print("\n\nTesting Ideas API...")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/ideas?limit=1")
    if response.status_code == 200:
        ideas = response.json()
        if ideas:
            idea = ideas[0]
            print(f"✓ Got idea: {idea.get('title', 'No title')}")
            print(f"  ID (UUID): {idea.get('id')}")
            if len(str(idea.get('id', ''))) == 36:
                print("✓ Ideas API returns UUIDs")
            else:
                print("✗ Ideas API not returning UUIDs")

if __name__ == "__main__":
    test_my_team_page()
    test_ideas_api()