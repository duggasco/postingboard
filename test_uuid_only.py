#!/usr/bin/env python3
"""
Test that only UUID access works and integer ID access is blocked.
"""

import requests
import sys

BASE_URL = "http://localhost:9094"

def test_uuid_only_access():
    """Test that we can only access resources by UUID, not integer ID."""
    print("Testing UUID-only access...")
    
    # Get a list of ideas
    response = requests.get(f"{BASE_URL}/api/ideas")
    if response.status_code != 200:
        print(f"✗ Failed to get ideas: {response.status_code}")
        return
        
    ideas = response.json()
    if not ideas:
        print("✗ No ideas found to test")
        return
        
    idea = ideas[0]
    print(f"\nTest idea: {idea.get('title')}")
    print(f"UUID (as 'id'): {idea.get('id')}")
    print(f"UUID field: {idea.get('uuid')}")
    
    # Check that we're getting UUIDs in the response
    idea_id = idea.get('id')
    if len(idea_id) == 36 and '-' in idea_id:
        print("✓ API returns UUID as 'id'")
    else:
        print("✗ API still returns integer ID")
        
    # Test accessing by UUID
    response = requests.get(f"{BASE_URL}/idea/{idea_id}")
    if response.status_code == 200:
        print("✓ Can access idea by UUID")
    else:
        print(f"✗ Cannot access by UUID: {response.status_code}")
        
    # Test that integer ID access fails
    # Try with a common integer ID
    for test_id in [1, 2, 3, 10, 100]:
        response = requests.get(f"{BASE_URL}/idea/{test_id}", allow_redirects=False)
        if response.status_code == 404 or response.status_code == 302:
            print(f"✓ Integer ID {test_id} access blocked (status: {response.status_code})")
        else:
            print(f"✗ Integer ID {test_id} still accessible! (status: {response.status_code})")
            
    # Test API endpoints
    print("\nTesting API endpoints...")
    
    # Test comments endpoint with integer
    response = requests.get(f"{BASE_URL}/api/ideas/1/comments")
    if response.status_code in [400, 403, 404]:
        print(f"✓ Comments API blocks integer ID (status: {response.status_code})")
    else:
        print(f"✗ Comments API allows integer ID! (status: {response.status_code})")
        
    # Test with UUID
    response = requests.get(f"{BASE_URL}/api/ideas/{idea_id}/comments")
    expected_status = 403  # Should be blocked without auth
    if response.status_code == expected_status:
        print(f"✓ Comments API works with UUID (status: {response.status_code})")
    else:
        print(f"! Comments API UUID status: {response.status_code}")

def test_skill_and_team_uuids():
    """Test that skills and teams also return UUIDs."""
    print("\nTesting skill and team UUIDs...")
    
    # Test skills
    response = requests.get(f"{BASE_URL}/api/skills")
    if response.status_code == 200:
        skills = response.json()
        if skills:
            skill = skills[0]
            skill_id = skill.get('id')
            if len(str(skill_id)) == 36 and '-' in str(skill_id):
                print("✓ Skills API returns UUIDs")
            else:
                print(f"✗ Skills API returns integer IDs: {skill_id}")
    
    # Test teams
    response = requests.get(f"{BASE_URL}/api/teams")
    if response.status_code == 200:
        teams = response.json()
        if teams:
            team = teams[0]
            team_id = team.get('id')
            if len(str(team_id)) == 36 and '-' in str(team_id):
                print("✓ Teams API returns UUIDs")
            else:
                print(f"✗ Teams API returns integer IDs: {team_id}")

def main():
    print("UUID-Only Access Test")
    print("=====================")
    print()
    
    test_uuid_only_access()
    test_skill_and_team_uuids()
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()