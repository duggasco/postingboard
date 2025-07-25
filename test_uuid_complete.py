#!/usr/bin/env python3
"""
Test the complete UUID-only system.
"""

import requests
import json

BASE_URL = "http://localhost:9094"

def test_uuid_only_system():
    """Test that the system only uses UUIDs, no integer IDs."""
    print("Testing Complete UUID-Only System")
    print("=" * 50)
    
    # Test 1: Get ideas and verify UUIDs
    print("\n1. Testing Ideas API...")
    response = requests.get(f"{BASE_URL}/api/ideas")
    if response.status_code == 200:
        ideas = response.json()
        if ideas:
            idea = ideas[0]
            idea_id = idea.get('id')
            print(f"✓ Got idea: {idea.get('title')}")
            print(f"  ID field (should be UUID): {idea_id}")
            
            # Verify it's a UUID
            if len(str(idea_id)) == 36 and '-' in str(idea_id):
                print("✓ Ideas API returns UUIDs")
            else:
                print("✗ Ideas API not returning UUIDs!")
                
            # Check other fields
            if 'submitter_name' in idea:
                print(f"  Submitter: {idea.get('submitter_name')}")
    else:
        print(f"✗ Failed to get ideas: {response.status_code}")
    
    # Test 2: Get teams and verify UUIDs
    print("\n2. Testing Teams API...")
    response = requests.get(f"{BASE_URL}/api/teams")
    if response.status_code == 200:
        teams = response.json()
        if teams:
            team = teams[0]
            team_id = team.get('id')
            print(f"✓ Got team: {team.get('name')}")
            print(f"  ID field (should be UUID): {team_id}")
            
            if len(str(team_id)) == 36 and '-' in str(team_id):
                print("✓ Teams API returns UUIDs")
            else:
                print("✗ Teams API not returning UUIDs!")
    
    # Test 3: Get skills and verify UUIDs
    print("\n3. Testing Skills API...")
    response = requests.get(f"{BASE_URL}/api/skills")
    if response.status_code == 200:
        skills = response.json()
        if skills:
            skill = skills[0]
            skill_id = skill.get('id')
            print(f"✓ Got skill: {skill.get('name')}")
            print(f"  ID field (should be UUID): {skill_id}")
            
            if len(str(skill_id)) == 36 and '-' in str(skill_id):
                print("✓ Skills API returns UUIDs")
            else:
                print("✗ Skills API not returning UUIDs!")
    
    # Test 4: Test that integer IDs are rejected
    print("\n4. Testing Integer ID Rejection...")
    
    # Try to access idea with integer ID
    response = requests.get(f"{BASE_URL}/idea/1", allow_redirects=False)
    if response.status_code in [302, 404]:
        print("✓ Integer ID access blocked for ideas")
    else:
        print(f"✗ Integer ID still accessible! Status: {response.status_code}")
    
    # Try API endpoint with integer ID
    response = requests.get(f"{BASE_URL}/api/ideas/1/comments")
    if response.status_code in [400, 403, 404]:
        print("✓ API blocks integer ID access")
    else:
        print(f"✗ API allows integer IDs! Status: {response.status_code}")
    
    # Test 5: Check database has no integer IDs exposed
    print("\n5. Checking API Responses for Integer IDs...")
    response = requests.get(f"{BASE_URL}/api/ideas?limit=1")
    if response.status_code == 200:
        data = response.json()
        if data:
            # Check if response contains any numeric IDs
            json_str = json.dumps(data)
            # Look for patterns like "id": 123 or "team_id": 456
            import re
            int_id_pattern = re.findall(r'"[^"]*_?id"\s*:\s*\d+', json_str)
            if int_id_pattern:
                print(f"✗ Found integer IDs in response: {int_id_pattern}")
            else:
                print("✓ No integer IDs found in API response")

def test_uuid_relationships():
    """Test that foreign key relationships work with UUIDs."""
    print("\n\nTesting UUID Foreign Key Relationships")
    print("=" * 50)
    
    # Get an idea with claims
    response = requests.get(f"{BASE_URL}/api/ideas?status=claimed")
    if response.status_code == 200:
        ideas = response.json()
        claimed_ideas = [i for i in ideas if i.get('claims')]
        if claimed_ideas:
            idea = claimed_ideas[0]
            print(f"\n✓ Found claimed idea: {idea.get('title')}")
            print(f"  Idea UUID: {idea.get('id')}")
            
            claims = idea.get('claims', [])
            if claims:
                print(f"  Claims: {len(claims)}")
                for claim in claims:
                    print(f"    - Claimed by: {claim.get('name')} on {claim.get('date')}")
            
            # Test accessing the idea detail
            idea_uuid = idea.get('id')
            response = requests.get(f"{BASE_URL}/idea/{idea_uuid}")
            if response.status_code == 200:
                print("  ✓ Can access idea detail page with UUID")
            else:
                print(f"  ✗ Cannot access idea detail: {response.status_code}")

if __name__ == "__main__":
    test_uuid_only_system()
    test_uuid_relationships()