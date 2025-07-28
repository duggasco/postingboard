#!/usr/bin/env python3
"""
Final approach: Use admin to create data, then capture screenshots
"""

import subprocess
import os

# Script to run inside Docker container
script_content = '''#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    base_url = "http://localhost:9094"
    screenshots_dir = "/app/documentation_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    print("Starting final screenshot capture...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        try:
            # 1. Login as admin first
            print("\\n1. Logging in as admin...")
            await page.goto(f"{base_url}/admin/login")
            await page.wait_for_timeout(2000)
            
            await page.fill("input[type='password']", "2929arch")
            await page.click("button[type='submit']")
            await page.wait_for_timeout(3000)
            
            # 2. Create some ideas through admin panel
            print("\\n2. Creating test ideas...")
            await page.goto(f"{base_url}/submit")
            await page.wait_for_timeout(2000)
            
            # Submit first idea
            await page.fill("#title", "Automated Testing Framework")
            await page.fill("#description", "Develop comprehensive automated testing to improve code quality.")
            await page.select_option("#priority", "high")
            await page.select_option("#size", "large")
            await page.fill("#bounty", "Extra PTO day")
            
            # Select team
            team_select = page.locator("#team")
            if await team_select.count() > 0:
                try:
                    await team_select.select_option("Cash - GPP")
                except:
                    pass
            
            await page.click("button:has-text('Submit Idea')")
            await page.wait_for_timeout(2000)
            
            # Submit second idea
            await page.goto(f"{base_url}/submit")
            await page.wait_for_timeout(2000)
            
            await page.fill("#title", "Real-time Dashboard")
            await page.fill("#description", "Create monitoring dashboard with live metrics.")
            await page.select_option("#priority", "medium")
            await page.select_option("#size", "medium")
            
            # Add monetary bounty
            monetary = page.locator("input#is_monetary")
            if await monetary.count() > 0:
                await monetary.check()
                await page.wait_for_timeout(500)
                
                amount = page.locator("input#amount")
                if await amount.count() > 0:
                    await amount.fill("250")
            
            await page.fill("#bounty", "Conference sponsorship")
            await page.click("button:has-text('Submit Idea')")
            await page.wait_for_timeout(2000)
            
            # 3. Now capture My Ideas page (admin will see their submitted ideas)
            print("\\n3. Capturing My Ideas page...")
            await page.goto(f"{base_url}/my-ideas")
            await page.wait_for_timeout(3000)
            
            # Wait for ideas to load
            await page.wait_for_selector(".idea-card", timeout=5000)
            
            await page.screenshot(path=f"{screenshots_dir}/my_ideas_page_final.png")
            print("   ✓ My Ideas page captured")
            
            # 4. Capture My Team page
            print("\\n4. Capturing My Team page...")
            await page.goto(f"{base_url}/my-team")
            await page.wait_for_timeout(4000)
            
            # Wait for charts to load
            await page.wait_for_timeout(2000)
            
            await page.screenshot(path=f"{screenshots_dir}/my_team_page_final.png")
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

# Write and execute the script
print("="*60)
print("Final User Screenshot Capture")
print("="*60)

with open('/tmp/final_screenshot_script.py', 'w') as f:
    f.write(script_content)

print("\n1. Copying script to container...")
subprocess.run(["docker", "cp", "/tmp/final_screenshot_script.py", "postingboard-flask-app-1:/tmp/"])

print("\n2. Running screenshot capture...")
result = subprocess.run(
    ["docker", "exec", "postingboard-flask-app-1", "python", "/tmp/final_screenshot_script.py"],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

# Copy screenshots back
print("\n3. Copying screenshots to host...")
subprocess.run(["docker", "cp", "postingboard-flask-app-1:/app/documentation_screenshots/.", "./documentation_screenshots/"])

# List new screenshots
print("\n4. New screenshots:")
if os.path.exists("./documentation_screenshots"):
    for file in ["my_ideas_page_final.png", "my_team_page_final.png"]:
        filepath = f"./documentation_screenshots/{file}"
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"   - {file} ({size:,} bytes)")

print("\n✓ Screenshot capture complete!")