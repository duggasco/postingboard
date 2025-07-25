#!/usr/bin/env python3
"""Test SDLC features with admin authentication."""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:9094"
ADMIN_PASSWORD = "2929arch"

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
    },
    "deployed": {
        "sub_status": "deployed",
        "progress_percentage": 90,
        "comment": "Deployed to production",
        "stage_data": {
            "deployment_guide": "https://docs.example.com/deployment/project-123",
            "release_notes": "Version 1.0.0 deployed successfully",
            "environment": "production"
        }
    },
    "verified": {
        "sub_status": "verified",
        "progress_percentage": 100,
        "comment": "Deployment verified and complete",
        "stage_data": {
            "verified_by": "Admin User",
            "performance_metrics": "Response time: 150ms avg\nThroughput: 1000 req/s\nError rate: 0.01%",
            "sign_off_notes": "All acceptance criteria met. System performing as expected."
        }
    }
}

def login_admin(session):
    """Login as admin and return session."""
    print("Logging in as admin...")
    
    # First, get the login page to establish session
    login_page = session.get(f"{BASE_URL}/admin/login")
    
    # Submit login
    login_data = {"password": ADMIN_PASSWORD}
    response = session.post(f"{BASE_URL}/admin/login", data=login_data)
    
    if response.status_code == 200 or response.status_code == 302:
        print("✓ Admin login successful")
        return True
    else:
        print(f"✗ Admin login failed: {response.status_code}")
        return False

def test_update_substatus(session, idea_id, stage_name):
    """Test updating sub-status with stage-specific data."""
    print(f"\n{'='*50}")
    print(f"Testing {stage_name} stage update...")
    print(f"{'='*50}")
    
    # Get the test data
    data = STAGE_TEST_DATA[stage_name]
    
    headers = {"Content-Type": "application/json"}
    url = f"{BASE_URL}/api/ideas/{idea_id}/sub-status"
    
    print(f"Updating to: {data['sub_status']}")
    print(f"Progress: {data['progress_percentage']}%")
    print(f"Comment: {data['comment']}")
    if 'stage_data' in data:
        print("Stage-specific fields:")
        for field, value in data['stage_data'].items():
            print(f"  - {field}: {value[:50]}..." if len(str(value)) > 50 else f"  - {field}: {value}")
    
    response = session.put(url, json=data, headers=headers)
    print(f"\nAPI Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Success: {result.get('message', 'Updated successfully')}")
        print(f"  New sub-status: {result.get('sub_status')}")
        print(f"  Progress: {result.get('progress_percentage')}%")
        
        # Verify stage data was saved
        print("\nVerifying stage data was saved...")
        stage_response = session.get(f"{BASE_URL}/api/ideas/{idea_id}/stage-data?status={stage_name}")
        if stage_response.status_code == 200:
            saved_data = stage_response.json()
            print(f"✓ Stage data retrieved successfully")
            
            # Compare with what we sent
            for field, value in data.get('stage_data', {}).items():
                if field in saved_data and saved_data[field] == str(value):
                    print(f"  ✓ {field}: Verified")
                else:
                    print(f"  ✗ {field}: Mismatch or missing")
                    if field in saved_data:
                        print(f"    Expected: {value}")
                        print(f"    Got: {saved_data[field]}")
        
        return True
    else:
        print(f"✗ Error: {response.text}")
        return False

def test_comments(session, idea_id):
    """Test adding and retrieving comments."""
    print(f"\n{'='*50}")
    print("Testing Comments System")
    print(f"{'='*50}")
    
    # Add a comment
    comment_data = {
        "content": "This is a test comment from the SDLC testing script.",
        "is_internal": False
    }
    
    print("Adding a comment...")
    response = session.post(f"{BASE_URL}/api/ideas/{idea_id}/comments", 
                          json=comment_data, 
                          headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        print("✓ Comment added successfully")
        
        # Add an internal comment
        internal_comment = {
            "content": "This is an internal note for the team.",
            "is_internal": True
        }
        response = session.post(f"{BASE_URL}/api/ideas/{idea_id}/comments", 
                              json=internal_comment,
                              headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print("✓ Internal comment added successfully")
    
    # Get comments
    print("\nRetrieving comments...")
    response = session.get(f"{BASE_URL}/api/ideas/{idea_id}/comments")
    if response.status_code == 200:
        comments = response.json()
        print(f"✓ Retrieved {len(comments)} comments")
        for comment in comments:
            internal = " (Internal)" if comment.get('is_internal') else ""
            print(f"  - {comment['author_name']}: {comment['content'][:50]}...{internal}")

def test_external_links(session, idea_id):
    """Test adding and retrieving external links."""
    print(f"\n{'='*50}")
    print("Testing External Links")
    print(f"{'='*50}")
    
    # Add external links
    links = [
        {
            "link_type": "repository",
            "title": "Main Repository",
            "url": "https://github.com/example/project-123",
            "description": "Main project repository"
        },
        {
            "link_type": "pull_request",
            "title": "PR #45 - SDLC Implementation",
            "url": "https://github.com/example/project-123/pull/45",
            "description": "Implements SDLC tracking features"
        },
        {
            "link_type": "test_results",
            "title": "Test Results Dashboard",
            "url": "https://testing.example.com/project-123",
            "description": "Automated test results"
        }
    ]
    
    for link in links:
        print(f"Adding {link['link_type']} link...")
        response = session.post(f"{BASE_URL}/api/ideas/{idea_id}/external-links",
                              json=link,
                              headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print(f"✓ Added: {link['title']}")
        else:
            print(f"✗ Failed to add: {link['title']}")
    
    # Get links
    print("\nRetrieving external links...")
    response = session.get(f"{BASE_URL}/api/ideas/{idea_id}/external-links")
    if response.status_code == 200:
        links = response.json()
        print(f"✓ Retrieved {len(links)} external links")
        for link in links:
            print(f"  - [{link['link_type']}] {link['title']}: {link['url']}")

def check_activity_feed(session, idea_id):
    """Check the activity feed."""
    print(f"\n{'='*50}")
    print("Checking Activity Feed")
    print(f"{'='*50}")
    
    response = session.get(f"{BASE_URL}/api/ideas/{idea_id}/activities")
    if response.status_code == 200:
        activities = response.json()
        print(f"✓ Found {len(activities)} activities")
        print("\nRecent activities:")
        for activity in activities[:10]:
            print(f"  - {activity['created_at']}: {activity['description']} by {activity['actor_name']}")
            if activity.get('activity_data'):
                try:
                    data = json.loads(activity['activity_data'])
                    if 'old_sub_status' in data and 'new_sub_status' in data:
                        print(f"    Status change: {data['old_sub_status']} → {data['new_sub_status']}")
                except:
                    pass

def check_status_history(session, idea_id):
    """Check the status history."""
    print(f"\n{'='*50}")
    print("Checking Status History")
    print(f"{'='*50}")
    
    response = session.get(f"{BASE_URL}/api/ideas/{idea_id}/status-history")
    if response.status_code == 200:
        history = response.json()
        print(f"✓ Found {len(history)} history entries")
        print("\nStatus change timeline:")
        for entry in history:
            from_status = entry.get('from_sub_status') or 'None'
            to_status = entry.get('to_sub_status') or 'None'
            print(f"  - {entry['changed_at']}: {from_status} → {to_status}")
            if entry.get('comment'):
                print(f"    Comment: {entry['comment']}")
            if entry.get('duration_minutes'):
                print(f"    Duration in previous status: {entry['duration_minutes']} minutes")

def main():
    print("="*60)
    print("  SDLC Feature Testing with Admin Authentication")
    print("="*60)
    
    # Create a session for cookie persistence
    session = requests.Session()
    
    # Login as admin
    if not login_admin(session):
        print("Failed to login as admin. Exiting.")
        return
    
    # Get a claimed idea to test with
    response = session.get(f"{BASE_URL}/api/ideas?status=claimed")
    if response.status_code != 200:
        print("Failed to get claimed ideas")
        return
    
    ideas = response.json()
    if not ideas:
        print("No claimed ideas found")
        return
    
    # Use the first claimed idea without sub-status
    test_idea = None
    for idea in ideas:
        if not idea.get('sub_status'):
            test_idea = idea
            break
    
    if not test_idea:
        test_idea = ideas[0]  # Fallback to first idea
    
    idea_id = test_idea['id']
    
    print(f"\nUsing idea ID {idea_id}: {test_idea['title']}")
    print(f"Initial status: {test_idea.get('sub_status', 'None')}")
    print(f"Initial progress: {test_idea.get('progress_percentage', 0)}%")
    
    # Test comments and links first
    test_comments(session, idea_id)
    test_external_links(session, idea_id)
    
    # Test each stage update
    stages = ["planning", "in_development", "testing", "awaiting_deployment", "deployed", "verified"]
    success_count = 0
    
    for stage in stages:
        if test_update_substatus(session, idea_id, stage):
            success_count += 1
        # Small delay between updates
        import time
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"Successfully updated {success_count}/{len(stages)} stages")
    print(f"{'='*60}")
    
    # Check final results
    check_activity_feed(session, idea_id)
    check_status_history(session, idea_id)
    
    # Final idea status
    print(f"\n{'='*50}")
    print("Final Idea Status")
    print(f"{'='*50}")
    
    response = session.get(f"{BASE_URL}/api/ideas?status=complete")
    if response.status_code == 200:
        ideas = response.json()
        for idea in ideas:
            if idea['id'] == idea_id:
                print(f"Title: {idea['title']}")
                print(f"Status: {idea['status']}")
                print(f"Sub-status: {idea.get('sub_status', 'None')}")
                print(f"Progress: {idea.get('progress_percentage', 0)}%")
                break
    
    print("\n✓ SDLC Feature Testing Complete!")

if __name__ == "__main__":
    main()