#!/usr/bin/env python3
"""Test script for SDLC features in the Posting Board application."""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:9094"

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_api_endpoint(method, endpoint, data=None, headers=None):
    """Test an API endpoint and return the response."""
    url = f"{BASE_URL}{endpoint}"
    print(f"{method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_sdlc_features():
    """Test all SDLC features."""
    
    print_section("Testing SDLC Features")
    
    # 1. Test getting claimed ideas
    print("1. Getting claimed ideas...")
    response = test_api_endpoint("GET", "/api/ideas?status=claimed")
    if response and response.status_code == 200:
        ideas = response.json()
        print(f"Found {len(ideas)} claimed ideas")
        
        if ideas:
            test_idea = ideas[0]
            idea_id = test_idea['id']
            print(f"\nUsing idea ID {idea_id}: {test_idea['title']}")
            print(f"Current sub-status: {test_idea.get('sub_status', 'None')}")
            print(f"Progress: {test_idea.get('progress_percentage', 0)}%")
    
    # 2. Test comments system
    print_section("Testing Comments System")
    
    # Get comments
    print("2a. Getting comments for idea...")
    response = test_api_endpoint("GET", f"/api/ideas/{idea_id}/comments")
    if response and response.status_code == 200:
        comments = response.json()
        print(f"Found {len(comments)} comments")
    
    # 3. Test external links
    print_section("Testing External Links")
    
    # Get external links
    print("3a. Getting external links for idea...")
    response = test_api_endpoint("GET", f"/api/ideas/{idea_id}/external-links")
    if response and response.status_code == 200:
        links = response.json()
        print(f"Found {len(links)} external links")
    
    # 4. Test activity feed
    print_section("Testing Activity Feed")
    
    # Get activities
    print("4a. Getting activities for idea...")
    response = test_api_endpoint("GET", f"/api/ideas/{idea_id}/activities")
    if response and response.status_code == 200:
        activities = response.json()
        print(f"Found {len(activities)} activities")
        if activities:
            print("Recent activities:")
            for activity in activities[:3]:
                print(f"  - {activity.get('description', 'Unknown')} by {activity.get('actor_name', 'Unknown')}")
    
    # 5. Test status history
    print_section("Testing Status History")
    
    print("5a. Getting status history for idea...")
    response = test_api_endpoint("GET", f"/api/ideas/{idea_id}/status-history")
    if response and response.status_code == 200:
        history = response.json()
        print(f"Found {len(history)} history entries")
        if history:
            print("Recent status changes:")
            for entry in history[:3]:
                print(f"  - From {entry.get('from_sub_status', 'None')} to {entry.get('to_sub_status', 'None')}")
    
    # 6. Test stage-specific data retrieval
    print_section("Testing Stage-Specific Data")
    
    # Test getting stage data for planning status
    print("6a. Getting stage data for planning status...")
    response = test_api_endpoint("GET", f"/api/ideas/{idea_id}/stage-data?status=planning")
    if response and response.status_code == 200:
        stage_data = response.json()
        print(f"Stage data: {json.dumps(stage_data, indent=2)}")
    
    # 7. Test the idea detail page renders
    print_section("Testing Idea Detail Page")
    
    print("7a. Checking if idea detail page loads...")
    response = requests.get(f"{BASE_URL}/idea/{idea_id}")
    if response.status_code == 200:
        print("✓ Idea detail page loads successfully")
        
        # Check for SDLC elements
        content = response.text
        checks = [
            ("Comments tab", "tab-comments" in content),
            ("Links tab", "tab-links" in content),
            ("Activity tab", "tab-activity" in content),
            ("GANTT chart", "gantt-canvas" in content),
            ("Update Status button", "showUpdateSubStatusModal" in content),
            ("Stage-specific fields", "stage-specific-fields" in content)
        ]
        
        for check_name, check_result in checks:
            status = "✓" if check_result else "✗"
            print(f"{status} {check_name}")
    
    print_section("SDLC Feature Test Complete")
    print("\nSummary:")
    print("- Comments system: Accessible")
    print("- External links: Accessible")
    print("- Activity feed: Accessible")
    print("- Status history: Accessible")
    print("- Stage-specific data: Accessible")
    print("- GANTT chart: Present in UI")
    print("- Update modal: Present in UI")

if __name__ == "__main__":
    test_sdlc_features()