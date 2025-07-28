#!/usr/bin/env python3
"""
Final documentation screenshot capture script - runs in Docker
"""

import subprocess
import time
import os
import random

# Generate a unique test email
test_email = f"doctest_{random.randint(1000, 9999)}@example.com"
test_name = "Documentation Test User"

# Create the screenshot capture script for Docker
script_content = f'''#!/usr/bin/env python3
import asyncio
import os
import time
import subprocess
from playwright.async_api import async_playwright

async def main():
    test_email = "{test_email}"
    test_name = "{test_name}"
    base_url = "http://localhost:9094"
    screenshots_dir = "/app/documentation_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    print("Starting documentation screenshot capture...")
    print(f"Test email: {{test_email}}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        page = await browser.new_page(viewport={{'width': 1920, 'height': 1080}})
        
        try:
            # 1. Email verification flow
            print("\\n1. Starting email verification...")
            await page.goto(f"{{base_url}}/verify-email")
            await page.wait_for_timeout(2000)
            
            # Enter email
            await page.fill("#email", test_email)
            await page.click("button:has-text('Send Verification Code')")
            await page.wait_for_timeout(3000)
            
            # Get verification code from logs
            logs = subprocess.check_output(["tail", "-n", "50", "/app/flask_app.log"], text=True)
            code = None
            for line in reversed(logs.split('\\n')):
                if f"Verification code for {{test_email}}" in line and ":" in line:
                    code = line.split(":")[-1].strip().split()[0]
                    if code.isdigit() and len(code) == 6:
                        break
            
            if not code:
                # Try console output
                print("Code not in logs, checking console output...")
                code = "123456"  # Default dev code
            
            print(f"Using verification code: {{code}}")
            
            # Enter code
            await page.fill("#code", code)
            await page.click("button:has-text('Verify Email')")
            await page.wait_for_timeout(3000)
            
            # 2. Complete profile
            if "/profile" in page.url:
                print("\\n2. Completing profile...")
                await page.fill("#name", test_name)
                await page.select_option("#role", "developer")
                await page.select_option("#team-select", "Cash - GPP")
                
                # Select skills
                for skill in ["Python", "JavaScript", "React", "SQL", "Data Analytics"]:
                    checkbox = page.locator(f"input[type='checkbox'][value='{{skill}}']")
                    if await checkbox.count() > 0:
                        await checkbox.check()
                
                await page.click("button:has-text('Save Profile')")
                await page.wait_for_timeout(2000)
            
            # 3. Capture Submit page with filled form
            print("\\n3. Capturing Submit page...")
            await page.goto(f"{{base_url}}/submit")
            await page.wait_for_timeout(2000)
            
            # Fill the form
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
            
            # Take screenshot
            await page.screenshot(path=f"{{screenshots_dir}}/submit_idea_page.png")
            print("   ✓ Submit page captured")
            
            # Actually submit to have content for My Ideas
            await page.click("button:has-text('Submit Idea')")
            await page.wait_for_timeout(3000)
            
            # 4. Capture My Ideas page
            print("\\n4. Capturing My Ideas page...")
            await page.goto(f"{{base_url}}/my-ideas")
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path=f"{{screenshots_dir}}/my_ideas_page.png")
            print("   ✓ My Ideas page captured")
            
            # 5. Capture Profile page
            print("\\n5. Capturing Profile page...")
            await page.goto(f"{{base_url}}/profile")
            await page.wait_for_timeout(2000)
            
            await page.screenshot(path=f"{{screenshots_dir}}/profile_page.png")
            print("   ✓ Profile page captured")
            
            print("\\n✓ All screenshots captured successfully!")
            
        except Exception as e:
            print(f"\\nError: {{e}}")
            import traceback
            traceback.print_exc()
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
'''

# Write the script
with open('/tmp/docker_screenshot_script.py', 'w') as f:
    f.write(script_content)

print("="*60)
print("Documentation Screenshot Capture")
print("="*60)

# Copy script to container
print("\n1. Copying script to container...")
subprocess.run(["docker", "cp", "/tmp/docker_screenshot_script.py", "postingboard-flask-app-1:/tmp/"])

# Install playwright in container if needed
print("\n2. Installing Playwright in container...")
subprocess.run(["docker", "exec", "postingboard-flask-app-1", "pip", "install", "playwright"])
subprocess.run(["docker", "exec", "postingboard-flask-app-1", "playwright", "install", "chromium"])
subprocess.run(["docker", "exec", "postingboard-flask-app-1", "playwright", "install-deps"])

# Run the script
print("\n3. Running screenshot capture...")
result = subprocess.run(
    ["docker", "exec", "postingboard-flask-app-1", "python", "/tmp/docker_screenshot_script.py"],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

# Copy screenshots back to host
print("\n4. Copying screenshots to host...")
subprocess.run(["docker", "cp", "postingboard-flask-app-1:/app/documentation_screenshots/.", "./documentation_screenshots/"])

print("\n✓ Screenshot capture complete!")
print(f"Screenshots saved to: ./documentation_screenshots/")