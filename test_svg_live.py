#!/usr/bin/env python3
"""Test SVG GANTT by opening in browser."""

import requests
import time

BASE_URL = "http://localhost:9094"
ADMIN_PASSWORD = "2929arch"

def main():
    session = requests.Session()
    
    # Login as admin
    session.get(f"{BASE_URL}/admin/login")
    response = session.post(f"{BASE_URL}/admin/login", data={"password": ADMIN_PASSWORD})
    
    if response.status_code in [200, 302]:
        print("✓ Admin login successful")
        
        # Get a claimed idea with sub-status
        response = session.get(f"{BASE_URL}/api/ideas?status=claimed")
        if response.status_code == 200:
            ideas = response.json()
            test_idea = None
            
            # Find idea with sub-status and progress
            for idea in ideas:
                if idea.get('sub_status') and idea.get('progress_percentage', 0) > 0:
                    test_idea = idea
                    break
            
            if not test_idea and ideas:
                test_idea = ideas[0]
            
            if test_idea:
                idea_id = test_idea['id']
                url = f"{BASE_URL}/idea/{idea_id}"
                
                print(f"\nTest idea: {test_idea['title']}")
                print(f"ID: {idea_id}")
                print(f"Status: {test_idea.get('sub_status', 'None')}")
                print(f"Progress: {test_idea.get('progress_percentage', 0)}%")
                print(f"Size: {test_idea.get('size')}")
                print(f"\nURL: {url}")
                print("\n" + "="*60)
                print("MANUAL TESTING INSTRUCTIONS:")
                print("="*60)
                print("1. Open the URL above in your browser")
                print("2. Log in as admin if needed")
                print("3. Check if the GANTT chart appears")
                print("4. Hover over phases to see tooltips")
                print("5. Click on phases to see if modal opens")
                print("6. Try the Export Timeline button")
                print("\nCheck browser console for any errors (F12)")
                print("\nExpected behavior:")
                print("- SVG GANTT chart with 5 phases")
                print("- Tooltips on hover with phase details")
                print("- Linked items count if available")
                print("- Click opens update modal")

if __name__ == "__main__":
    main()