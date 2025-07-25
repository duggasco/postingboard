#!/usr/bin/env python3
"""Test updating sub-status with stage-specific fields."""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:9094"

# Test data for different stages
STAGE_TEST_DATA = {
    "planning": {
        "sub_status": "planning",
        "progress_percentage": 10,
        "comment": "Starting planning phase",
        "stage_data": {
            "requirements_doc": "https://docs.example.com/requirements/project-123",
            "design_spec": "https://docs.example.com/design/project-123"
        }
    },
    "in_development": {
        "sub_status": "in_development",
        "progress_percentage": 35,
        "comment": "Development in progress",
        "stage_data": {
            "repository_url": "https://github.com/example/project-123",
            "branch_name": "feature/sdlc-implementation",
            "pr_urls": "https://github.com/example/project-123/pull/45\nhttps://github.com/example/project-123/pull/46"
        }
    },
    "testing": {
        "sub_status": "testing",
        "progress_percentage": 65,
        "comment": "Testing phase started",
        "stage_data": {
            "test_plan": "https://docs.example.com/test-plan/project-123",
            "test_results": "95% test coverage achieved. 2 minor bugs found and fixed.",
            "defects_found": "2"
        }
    },
    "awaiting_deployment": {
        "sub_status": "awaiting_deployment", 
        "progress_percentage": 80,
        "comment": "Ready for deployment",
        "expected_completion": (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
        "stage_data": {
            "deployment_guide": "https://docs.example.com/deployment/project-123",
            "release_notes": "Version 1.0.0\n- Added SDLC tracking\n- Improved GANTT chart\n- Stage-specific fields",
            "environment": "staging"
        }
    }
}

def test_update_substatus(idea_id, stage_name):
    """Test updating sub-status with stage-specific data."""
    print(f"\nTesting {stage_name} stage update...")
    
    # Get the test data
    data = STAGE_TEST_DATA[stage_name]
    
    # Simulate having a session cookie (in real usage, would need actual authentication)
    headers = {
        "Content-Type": "application/json",
        "Cookie": "session=test-session"  # This would need to be a real session
    }
    
    url = f"{BASE_URL}/api/ideas/{idea_id}/sub-status"
    print(f"PUT {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.put(url, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Success: {result.get('message', 'Updated successfully')}")
        print(f"  New sub-status: {result.get('sub_status')}")
        print(f"  Progress: {result.get('progress_percentage')}%")
        
        # Verify stage data was saved
        print("\nVerifying stage data was saved...")
        stage_response = requests.get(f"{BASE_URL}/api/ideas/{idea_id}/stage-data?status={stage_name}")
        if stage_response.status_code == 200:
            saved_data = stage_response.json()
            print(f"✓ Stage data retrieved: {json.dumps(saved_data, indent=2)}")
            
            # Compare with what we sent
            for field, value in data.get('stage_data', {}).items():
                if field in saved_data and saved_data[field] == str(value):
                    print(f"  ✓ {field}: Verified")
                else:
                    print(f"  ✗ {field}: Mismatch or missing")
    else:
        print(f"✗ Error: {response.text}")
    
    return response.status_code == 200

def main():
    print("="*60)
    print("  Testing Sub-Status Updates with Stage-Specific Fields")
    print("="*60)
    
    # Get a claimed idea to test with
    response = requests.get(f"{BASE_URL}/api/ideas?status=claimed")
    if response.status_code != 200:
        print("Failed to get claimed ideas")
        return
    
    ideas = response.json()
    if not ideas:
        print("No claimed ideas found")
        return
    
    # Use the first claimed idea
    test_idea = ideas[0]
    idea_id = test_idea['id']
    
    print(f"\nUsing idea ID {idea_id}: {test_idea['title']}")
    print(f"Initial status: {test_idea.get('sub_status', 'None')}")
    print(f"Initial progress: {test_idea.get('progress_percentage', 0)}%")
    
    # Note: These tests will fail with 401 without proper authentication
    print("\nNOTE: These updates require authentication. They will fail with 401 if not logged in.")
    print("To properly test, you would need to:")
    print("1. Log in through the web interface")
    print("2. Use the session cookie from your browser")
    print("3. Or test directly through the web UI")
    
    # Test each stage
    for stage in ["planning", "in_development", "testing", "awaiting_deployment"]:
        test_update_substatus(idea_id, stage)
        print("-"*40)
    
    # Check final status history
    print("\nChecking status history after updates...")
    history_response = requests.get(f"{BASE_URL}/api/ideas/{idea_id}/status-history")
    if history_response.status_code == 200:
        history = history_response.json()
        print(f"Total history entries: {len(history)}")
        if history:
            print("Recent changes:")
            for entry in history[:5]:
                print(f"  - {entry.get('to_sub_status', 'Unknown')} at {entry.get('changed_at', 'Unknown')}")
    
    # Check activity feed
    print("\nChecking activity feed after updates...")
    activity_response = requests.get(f"{BASE_URL}/api/ideas/{idea_id}/activities")
    if activity_response.status_code == 200:
        activities = activity_response.json()
        print(f"Total activities: {len(activities)}")
        if activities:
            print("Recent activities:")
            for activity in activities[:5]:
                print(f"  - {activity.get('description', 'Unknown')} at {activity.get('created_at', 'Unknown')}")

if __name__ == "__main__":
    main()