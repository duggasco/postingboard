#!/usr/bin/env python3
"""Test current Canvas GANTT implementation to understand its behavior."""

import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "http://localhost:9094"
ADMIN_PASSWORD = "2929arch"

def login_admin(session):
    """Login as admin."""
    session.get(f"{BASE_URL}/admin/login")
    response = session.post(f"{BASE_URL}/admin/login", data={"password": ADMIN_PASSWORD})
    return response.status_code in [200, 302]

def analyze_gantt_implementation(idea_id):
    """Analyze the current GANTT implementation for a specific idea."""
    session = requests.Session()
    
    if not login_admin(session):
        print("Failed to login as admin")
        return
    
    # Get the idea detail page
    response = session.get(f"{BASE_URL}/idea/{idea_id}")
    if response.status_code != 200:
        print(f"Failed to get idea detail page: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract GANTT-related information
    print("\n=== Current GANTT Implementation Analysis ===\n")
    
    # Check for canvas element
    canvas = soup.find('canvas', id='gantt-canvas')
    if canvas:
        print("✓ Canvas element found")
        print(f"  - ID: {canvas.get('id')}")
        print(f"  - Style: {canvas.get('style')}")
    
    # Check for GANTT container
    container = soup.find('div', id='gantt-chart-container')
    if container:
        print("\n✓ GANTT container found")
        print(f"  - Style: {container.get('style')}")
    
    # Look for JavaScript functions
    scripts = soup.find_all('script')
    gantt_functions = []
    phase_data = None
    
    for script in scripts:
        if script.string:
            content = script.string
            # Look for GANTT-related functions
            if 'renderGanttChart' in content:
                gantt_functions.append('renderGanttChart')
            if 'exportGanttChart' in content:
                gantt_functions.append('exportGanttChart')
            if 'showGanttSettingsModal' in content:
                gantt_functions.append('showGanttSettingsModal')
            
            # Extract phase definitions
            if 'phases = [' in content and 'startOffset:' in content:
                # Try to extract the phases array
                start = content.find('phases = [')
                if start != -1:
                    # Find the matching closing bracket
                    bracket_count = 0
                    i = start + 9  # Skip 'phases = '
                    phase_str = ''
                    while i < len(content):
                        char = content[i]
                        phase_str += char
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                break
                        i += 1
                    
                    print(f"\n✓ Phase data structure found:")
                    print(phase_str[:200] + "..." if len(phase_str) > 200 else phase_str)
    
    print(f"\n✓ JavaScript functions found: {', '.join(gantt_functions)}")
    
    # Check for interactive elements
    print("\n✓ Interactive elements:")
    buttons = soup.find_all('button', onclick=True)
    for button in buttons:
        onclick = button.get('onclick', '')
        if 'gantt' in onclick.lower() or 'timeline' in onclick.lower():
            print(f"  - Button: {button.text.strip()} → {onclick}")
    
    # Check for legend
    legend = soup.find('div', style=lambda x: x and 'Planned' in str(x))
    if legend:
        print("\n✓ Legend found with color indicators")
    
    # Get idea data to understand progress calculation
    idea_data_script = None
    for script in scripts:
        if script.string and 'ideaData = {' in script.string:
            content = script.string
            start = content.find('ideaData = {')
            if start != -1:
                end = content.find('};', start)
                if end != -1:
                    data_str = content[start+11:end+1]
                    print(f"\n✓ Idea data structure:")
                    print(data_str[:200] + "..." if len(data_str) > 200 else data_str)
    
    return True

def test_with_different_statuses():
    """Test GANTT with ideas in different statuses."""
    session = requests.Session()
    
    if not login_admin(session):
        print("Failed to login as admin")
        return
    
    # Get ideas in different states
    statuses_to_test = ['claimed', 'complete']
    
    for status in statuses_to_test:
        print(f"\n\n=== Testing with {status} ideas ===")
        
        response = session.get(f"{BASE_URL}/api/ideas?status={status}")
        if response.status_code == 200:
            ideas = response.json()
            if ideas:
                # Test with first idea that has sub_status
                for idea in ideas[:3]:
                    if idea.get('sub_status'):
                        print(f"\nIdea {idea['id']}: {idea['title']}")
                        print(f"  - Status: {idea['status']}")
                        print(f"  - Sub-status: {idea.get('sub_status', 'None')}")
                        print(f"  - Progress: {idea.get('progress_percentage', 0)}%")
                        print(f"  - Size: {idea.get('size')}")
                        
                        # Analyze this idea's GANTT
                        analyze_gantt_implementation(idea['id'])
                        break

def main():
    print("=== Testing Current Canvas GANTT Implementation ===\n")
    
    # First, find a good test idea
    session = requests.Session()
    if login_admin(session):
        # Get a claimed idea with sub-status
        response = session.get(f"{BASE_URL}/api/ideas?status=claimed")
        if response.status_code == 200:
            ideas = response.json()
            test_idea = None
            
            # Find an idea with interesting sub-status
            for idea in ideas:
                if idea.get('sub_status') in ['in_development', 'testing', 'awaiting_deployment']:
                    test_idea = idea
                    break
            
            if not test_idea and ideas:
                test_idea = ideas[0]
            
            if test_idea:
                print(f"Using test idea: {test_idea['id']} - {test_idea['title']}")
                print(f"Status: {test_idea.get('sub_status', 'None')}, Progress: {test_idea.get('progress_percentage', 0)}%")
                
                analyze_gantt_implementation(test_idea['id'])
                
                # Test with different statuses
                test_with_different_statuses()
            else:
                print("No suitable test ideas found")

if __name__ == "__main__":
    main()