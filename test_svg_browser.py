#!/usr/bin/env python3
"""Open browser to test SVG GANTT visually."""

import requests
import webbrowser
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
        
        # Get a claimed idea
        response = session.get(f"{BASE_URL}/api/ideas?status=claimed")
        if response.status_code == 200:
            ideas = response.json()
            if ideas:
                # Find idea with sub-status
                test_idea = None
                for idea in ideas:
                    if idea.get('sub_status'):
                        test_idea = idea
                        break
                
                if test_idea:
                    idea_id = test_idea['id']
                    url = f"{BASE_URL}/idea/{idea_id}"
                    
                    print(f"\nTest idea: {test_idea['title']}")
                    print(f"Status: {test_idea.get('sub_status', 'None')}")
                    print(f"Progress: {test_idea.get('progress_percentage', 0)}%")
                    print(f"\nOpening in browser: {url}")
                    print("\nCheck the browser console for JavaScript errors:")
                    print("1. Right-click and select 'Inspect'")
                    print("2. Go to the Console tab")
                    print("3. Look for any red error messages")
                    print("\nAlso check if the GANTT chart is visible and interactive")
                    
                    # Save cookies to file for manual testing
                    with open('test_cookies.txt', 'w') as f:
                        for cookie in session.cookies:
                            f.write(f"{cookie.name}={cookie.value}\n")
                    
                    print("\nSession cookies saved to test_cookies.txt")
                    webbrowser.open(url)

if __name__ == "__main__":
    main()