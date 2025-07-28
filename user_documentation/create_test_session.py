#!/usr/bin/env python3
"""
Create a test user session directly in the database for screenshot capture
"""

import subprocess
import random

test_email = f"screenshot_test_{random.randint(1000, 9999)}@example.com"
test_name = "Screenshot Test User"

# Create SQL script to insert test user
sql_script = f"""
-- Insert verified user profile
INSERT OR REPLACE INTO user_profiles (email, name, is_verified, role, team_uuid, created_at, updated_at)
SELECT 
    '{test_email}',
    '{test_name}',
    1,
    'developer',
    t.uuid,
    datetime('now'),
    datetime('now')
FROM teams t WHERE t.name = 'Cash - GPP' LIMIT 1;

-- Insert user skills
INSERT OR IGNORE INTO user_skills (user_email, skill_uuid)
SELECT '{test_email}', s.uuid
FROM skills s 
WHERE s.name IN ('Python', 'JavaScript', 'React', 'SQL', 'Data Analytics');

-- Insert a test idea
INSERT INTO ideas (
    uuid,
    title,
    description,
    email,
    benefactor_team_uuid,
    priority,
    size,
    status,
    bounty,
    created_at,
    needed_by
)
SELECT
    lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + (abs(random()) % 4), 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))),
    'Test Idea for Screenshots',
    'This is a test idea created for documentation screenshots. It demonstrates the idea submission system.',
    '{test_email}',
    t.uuid,
    'medium',
    'medium',
    'open',
    'Recognition in team meeting',
    datetime('now'),
    date('now', '+30 days')
FROM teams t WHERE t.name = 'Cash - GPP' LIMIT 1;

SELECT * FROM user_profiles WHERE email = '{test_email}';
"""

# Write SQL script
with open('/tmp/create_test_user.sql', 'w') as f:
    f.write(sql_script)

print(f"Creating test user: {test_email}")

# Copy and execute SQL in container
subprocess.run(["docker", "cp", "/tmp/create_test_user.sql", "postingboard-flask-app-1:/tmp/"])
result = subprocess.run(
    ["docker", "exec", "postingboard-flask-app-1", "sqlite3", "/app/backend/data/posting_board_uuid.db"],
    input=sql_script,
    text=True,
    capture_output=True
)

if result.returncode == 0:
    print("✓ Test user created successfully")
    print(f"Email: {test_email}")
    print(f"Name: {test_name}")
else:
    print("Error creating test user:")
    print(result.stderr)

# Create a simple screenshot script that uses session injection
screenshot_script = f"""#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    test_email = "{test_email}"
    test_name = "{test_name}"
    base_url = "http://localhost:9094"
    screenshots_dir = "/app/documentation_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    print("Starting screenshot capture with session injection...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        context = await browser.new_context(viewport={{'width': 1920, 'height': 1080}})
        page = await context.new_page()
        
        try:
            # First go to home page
            await page.goto(base_url)
            await page.wait_for_timeout(2000)
            
            # Inject session data via JavaScript
            await page.evaluate(f'''
                // Set session storage
                sessionStorage.setItem('user_email', '{{test_email}}');
                sessionStorage.setItem('user_name', '{{test_name}}');
                sessionStorage.setItem('user_verified', 'true');
                sessionStorage.setItem('user_role', 'developer');
                sessionStorage.setItem('user_team', 'Cash - GPP');
                
                // Also try localStorage
                localStorage.setItem('user_email', '{{test_email}}');
                localStorage.setItem('user_name', '{{test_name}}');
                localStorage.setItem('user_verified', 'true');
                localStorage.setItem('user_role', 'developer');
                localStorage.setItem('user_team', 'Cash - GPP');
            ''')
            
            # Create a session cookie (Flask session)
            await context.add_cookies([{{
                'name': 'session',
                'value': 'test-session-for-screenshots',
                'domain': 'localhost',
                'path': '/',
                'httpOnly': True,
                'secure': False,
                'sameSite': 'Lax'
            }}])
            
            # Capture Submit page
            print("\\n1. Capturing Submit page...")
            await page.goto(f"{{base_url}}/submit")
            await page.wait_for_timeout(3000)
            
            # Fill the form if we're on the submit page
            if "/submit" in page.url or "/verify-email" not in page.url:
                try:
                    await page.fill("#title", "Implement Advanced Analytics Dashboard")
                    await page.fill("#description", 
                        "We need a comprehensive analytics dashboard that provides real-time insights into our application usage patterns. "
                        "The dashboard should include:\\n\\n"
                        "• User activity metrics and trends\\n"
                        "• Performance monitoring capabilities\\n"
                        "• Custom report generation\\n"
                        "• Data export functionality\\n\\n"
                        "This will help our team make data-driven decisions and improve user experience."
                    )
                    
                    await page.select_option("#priority", "high")
                    await page.select_option("#size", "large")
                    
                    # Add monetary bounty
                    monetary = page.locator("input#is_monetary")
                    if await monetary.count() > 0:
                        await monetary.check()
                        await page.wait_for_timeout(500)
                        
                        amount = page.locator("input#amount")
                        if await amount.count() > 0:
                            await amount.fill("500")
                    
                    await page.fill("#bounty", "Recognition in company newsletter and conference attendance sponsorship")
                    
                    # Select skills
                    for skill in ["Python", "React", "Data Analytics"]:
                        checkbox = page.locator(f"input[type='checkbox'][value='{{skill}}']")
                        if await checkbox.count() > 0:
                            await checkbox.check()
                    
                    await page.fill("#needed_by", "2025-09-01")
                except:
                    print("   Could not fill form, capturing page as-is")
                
                await page.screenshot(path=f"{{screenshots_dir}}/submit_idea_page.png")
                print("   ✓ Submit page captured")
            else:
                print(f"   ✗ Redirected to: {{page.url}}")
                await page.screenshot(path=f"{{screenshots_dir}}/submit_idea_page.png")
            
            # Capture My Ideas page
            print("\\n2. Capturing My Ideas page...")
            await page.goto(f"{{base_url}}/my-ideas")
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path=f"{{screenshots_dir}}/my_ideas_page.png")
            print("   ✓ My Ideas page captured")
            
            # Capture Profile page  
            print("\\n3. Capturing Profile page...")
            await page.goto(f"{{base_url}}/profile")
            await page.wait_for_timeout(2000)
            
            await page.screenshot(path=f"{{screenshots_dir}}/profile_page.png")
            print("   ✓ Profile page captured")
            
            print("\\n✓ All screenshots captured!")
            
        except Exception as e:
            print(f"\\nError: {{e}}")
            import traceback
            traceback.print_exc()
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
"""

# Write and run the screenshot script
with open('/tmp/capture_with_session.py', 'w') as f:
    f.write(screenshot_script)

print("\nCopying and running screenshot script...")
subprocess.run(["docker", "cp", "/tmp/capture_with_session.py", "postingboard-flask-app-1:/tmp/"])
subprocess.run(["docker", "exec", "postingboard-flask-app-1", "python", "/tmp/capture_with_session.py"])