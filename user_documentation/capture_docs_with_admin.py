#!/usr/bin/env python3
"""
Capture documentation screenshots using admin login
"""

import subprocess
import os

# Create the screenshot capture script for Docker
script_content = '''#!/usr/bin/env python3
import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    base_url = "http://localhost:9094"
    screenshots_dir = "/app/documentation_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    print("Starting documentation screenshot capture with admin login...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        try:
            # 1. Login as admin
            print("\\n1. Logging in as admin...")
            await page.goto(f"{base_url}/admin/login")
            await page.wait_for_timeout(2000)
            
            # Enter admin password
            await page.fill("input[type='password']", "2929arch")
            await page.click("button[type='submit']")
            await page.wait_for_timeout(3000)
            
            print("   ✓ Admin login successful")
            
            # 2. Capture Submit page with filled form
            print("\\n2. Capturing Submit page...")
            await page.goto(f"{base_url}/submit")
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
            
            # Select team
            team_select = page.locator("#team")
            if await team_select.count() > 0:
                await team_select.select_option("Cash - GPP")
            
            # Select skills
            for skill in ["Python", "React", "Data Analytics"]:
                checkbox = page.locator(f"input[type='checkbox'][value='{skill}']")
                if await checkbox.count() > 0:
                    await checkbox.check()
            
            await page.fill("#needed_by", "2025-09-01")
            
            # Take screenshot
            await page.screenshot(path=f"{screenshots_dir}/submit_idea_page.png")
            print("   ✓ Submit page captured")
            
            # 3. Capture My Ideas page
            print("\\n3. Capturing My Ideas page...")
            await page.goto(f"{base_url}/my-ideas")
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path=f"{screenshots_dir}/my_ideas_page.png")
            print("   ✓ My Ideas page captured")
            
            # 4. Capture Admin Dashboard
            print("\\n4. Capturing Admin Dashboard...")
            await page.goto(f"{base_url}/admin/dashboard")
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path=f"{screenshots_dir}/admin_dashboard_page.png")
            print("   ✓ Admin Dashboard captured")
            
            # 5. Capture My Team page
            print("\\n5. Capturing My Team page...")
            await page.goto(f"{base_url}/my-team")
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path=f"{screenshots_dir}/my_team_page.png")
            print("   ✓ My Team page captured")
            
            print("\\n✓ All screenshots captured successfully!")
            
        except Exception as e:
            print(f"\\nError: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
'''

# Write the script
with open('/tmp/admin_screenshot_script.py', 'w') as f:
    f.write(script_content)

print("="*60)
print("Documentation Screenshot Capture with Admin Login")
print("="*60)

# Copy script to container
print("\n1. Copying script to container...")
subprocess.run(["docker", "cp", "/tmp/admin_screenshot_script.py", "postingboard-flask-app-1:/tmp/"])

# Run the script
print("\n2. Running screenshot capture...")
result = subprocess.run(
    ["docker", "exec", "postingboard-flask-app-1", "python", "/tmp/admin_screenshot_script.py"],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

# Copy screenshots back to host
print("\n3. Copying screenshots to host...")
subprocess.run(["docker", "cp", "postingboard-flask-app-1:/app/documentation_screenshots/.", "./documentation_screenshots/"])

# List captured screenshots
print("\n4. Captured screenshots:")
if os.path.exists("./documentation_screenshots"):
    for file in os.listdir("./documentation_screenshots"):
        if file.endswith(".png"):
            size = os.path.getsize(f"./documentation_screenshots/{file}")
            print(f"   - {file} ({size:,} bytes)")

print("\n✓ Screenshot capture complete!")
print(f"Screenshots saved to: ./documentation_screenshots/")