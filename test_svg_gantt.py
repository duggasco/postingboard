#!/usr/bin/env python3
"""Test the new SVG GANTT implementation."""

import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "http://localhost:9094"
ADMIN_PASSWORD = "2929arch"

def login_admin(session):
    """Login as admin."""
    session.get(f"{BASE_URL}/admin/login")
    response = session.post(f"{BASE_URL}/admin/login", data={"password": ADMIN_PASSWORD})
    return response.status_code in [200, 302]

def test_svg_gantt(idea_id):
    """Test the SVG GANTT implementation."""
    session = requests.Session()
    
    if not login_admin(session):
        print("Failed to login as admin")
        return
    
    print(f"\n=== Testing SVG GANTT for Idea {idea_id} ===\n")
    
    # Get the idea detail page
    response = session.get(f"{BASE_URL}/idea/{idea_id}")
    if response.status_code != 200:
        print(f"Failed to get idea detail page: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for SVG element
    svg = soup.find('svg', id='gantt-svg')
    if svg:
        print("✓ SVG element found")
        print(f"  - ID: {svg.get('id')}")
        print(f"  - Style: {svg.get('style')}")
        
        # Check for SVG content
        groups = svg.find_all('g')
        print(f"\n✓ SVG contains {len(groups)} groups")
        
        # Check for tooltip container
        tooltip = soup.find('div', id='gantt-tooltip')
        if tooltip:
            print("\n✓ Tooltip container found")
            print(f"  - Style: {tooltip.get('style')}")
    else:
        print("✗ SVG element NOT found")
        
    # Check for JavaScript errors by looking for error patterns
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'renderGanttChart' in script.string:
            # Check for syntax errors in our implementation
            if 'canvas.width' in script.string:
                print("\n⚠️  Found reference to canvas.width - may cause errors")
            if 'ctx.' in script.string:
                print("\n⚠️  Found reference to ctx - Canvas context still in use")
    
    # Test the API endpoints that the tooltips will use
    print("\n=== Testing Related API Endpoints ===")
    
    # Test stage data endpoint
    stages = ['planning', 'in_development', 'testing', 'awaiting_deployment', 'verified']
    for stage in stages:
        response = session.get(f"{BASE_URL}/api/ideas/{idea_id}/stage-data?status={stage}")
        print(f"\nStage data for {stage}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"  - Data: {json.dumps(data, indent=2)}")
    
    return True

def main():
    print("=== Testing SVG GANTT Implementation ===\n")
    
    session = requests.Session()
    if login_admin(session):
        # Get a claimed idea with sub-status
        response = session.get(f"{BASE_URL}/api/ideas?status=claimed")
        if response.status_code == 200:
            ideas = response.json()
            
            # Find idea with interesting data
            test_idea = None
            for idea in ideas:
                if idea.get('sub_status') and idea.get('progress_percentage', 0) > 0:
                    test_idea = idea
                    break
            
            if not test_idea and ideas:
                test_idea = ideas[0]
            
            if test_idea:
                print(f"Using test idea: {test_idea['id']} - {test_idea['title']}")
                print(f"Status: {test_idea.get('sub_status', 'None')}, Progress: {test_idea.get('progress_percentage', 0)}%")
                
                test_svg_gantt(test_idea['id'])
                
                # Also test with a complete idea
                response = session.get(f"{BASE_URL}/api/ideas?status=complete")
                if response.status_code == 200:
                    complete_ideas = response.json()
                    if complete_ideas:
                        complete_idea = complete_ideas[0]
                        print(f"\n\nTesting with complete idea: {complete_idea['id']} - {complete_idea['title']}")
                        test_svg_gantt(complete_idea['id'])

if __name__ == "__main__":
    main()