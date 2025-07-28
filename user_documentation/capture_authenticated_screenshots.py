#!/usr/bin/env python3
"""
Capture screenshots of authenticated pages by going through the actual login flow
"""

import os
import time
import asyncio
import json

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright not installed. Installing...")
    os.system("pip install playwright")
    os.system("python -m playwright install chromium")
    print("\nPlease run this script again after installation completes.")
    exit(1)

class AuthenticatedScreenshotCapture:
    def __init__(self):
        self.screenshots_dir = "/root/postingboard/documentation_screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.base_url = "http://localhost:9094"
        self.test_email = "testuser@example.com"
        self.test_name = "Test User"
        
    async def capture_screenshots(self):
        """Main function to capture all screenshots"""
        print("="*60)
        print("Authenticated Screenshot Capture")
        print("="*60)
        
        async with async_playwright() as p:
            # Launch browser
            print("\nLaunching browser...")
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            # Create context with viewport
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                device_scale_factor=1,
            )
            
            # Create page
            page = await context.new_page()
            
            try:
                # First authenticate the user
                await self.authenticate_user(page)
                
                # Now capture authenticated pages
                await self.capture_authenticated_pages(page)
                
                print("\n" + "="*60)
                print("✓ Screenshot capture complete!")
                print(f"Screenshots saved to: {self.screenshots_dir}")
                
            except Exception as e:
                print(f"\n✗ Error during capture: {e}")
                import traceback
                traceback.print_exc()
                
            finally:
                await browser.close()
                
    async def wait_for_load(self, page, selector=None, timeout=10000):
        """Wait for page and optional selector to load"""
        try:
            # Wait for network to be idle
            await page.wait_for_load_state('networkidle', timeout=timeout)
            
            # Wait for specific selector if provided
            if selector:
                await page.wait_for_selector(selector, timeout=timeout)
                
            # Additional wait for JavaScript rendering
            await page.wait_for_timeout(2000)
            
            return True
        except Exception as e:
            print(f"  ⚠ Load timeout: {e}")
            return False
            
    async def authenticate_user(self, page):
        """Go through the email verification flow"""
        print("\n--- Authenticating User ---")
        
        # 1. Go to verify-email page
        print(f"1. Navigating to email verification...")
        await page.goto(f"{self.base_url}/verify-email")
        await self.wait_for_load(page, "#email")
        
        # 2. Submit email
        print(f"2. Entering email: {self.test_email}")
        await page.fill("#email", self.test_email)
        await page.click("button[type='submit']")
        
        # Wait for the verification code request
        await page.wait_for_timeout(2000)
        
        # 3. Get verification code from console/logs (in dev mode it's printed)
        # For this demo, we'll use a hardcoded code that we know works in dev
        # In real usage, you'd parse the console output or database
        verification_code = "123456"  # This is typically shown in console in dev mode
        
        # Check if we're on the verify code page
        try:
            await page.wait_for_selector("#code", timeout=5000)
            print(f"3. Entering verification code: {verification_code}")
            await page.fill("#code", verification_code)
            await page.click("button[type='submit']")
            
            # Wait for redirect to profile
            await page.wait_for_timeout(3000)
            
            # 4. Complete profile if needed
            if "/profile" in page.url:
                print("4. Completing user profile...")
                await self.wait_for_load(page, "#name")
                
                # Fill profile form
                await page.fill("#name", self.test_name)
                
                # Select role
                await page.select_option("#role", "developer")
                
                # Select team
                await page.select_option("#team", "SL - Tech")
                
                # Select skills
                skills = ["Python", "JavaScript", "SQL"]
                for skill in skills:
                    skill_checkbox = await page.query_selector(f"input[type='checkbox'][value='{skill}']")
                    if skill_checkbox:
                        await skill_checkbox.check()
                
                # Submit profile
                await page.click("button[type='submit']")
                await page.wait_for_timeout(2000)
                
            print("  ✓ Authentication successful!")
            return True
            
        except Exception as e:
            print(f"  ✗ Authentication failed: {e}")
            
            # Alternative: Try to simulate session directly in backend
            print("\n  Attempting direct session injection...")
            await self.inject_session_directly(page)
            return False
    
    async def inject_session_directly(self, page):
        """Alternative method: Create session data directly"""
        # This would require backend modification or test mode
        # For now, we'll create a test endpoint or use existing dev features
        print("  Note: Direct session injection requires backend support")
        
    async def capture_page(self, page, url_path, filename, wait_selector=None, description=""):
        """Capture a single page screenshot"""
        try:
            print(f"\nCapturing: {filename}")
            print(f"  URL: {self.base_url}{url_path}")
            if description:
                print(f"  Description: {description}")
                
            # Navigate to page
            await page.goto(f"{self.base_url}{url_path}", wait_until='networkidle')
            
            # Wait for content to load
            await self.wait_for_load(page, wait_selector)
            
            # Scroll page to load lazy content
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(1000)
            
            # Take screenshot
            filepath = os.path.join(self.screenshots_dir, filename)
            await page.screenshot(path=filepath, full_page=False)
            
            # Verify
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"  ✓ Screenshot saved: {filename} ({file_size:,} bytes)")
                return True
            else:
                print(f"  ✗ Failed to save screenshot")
                return False
                
        except Exception as e:
            print(f"  ✗ Error capturing {filename}: {e}")
            return False
            
    async def capture_authenticated_pages(self, page):
        """Capture pages requiring authentication"""
        print("\n--- Capturing Authenticated Pages ---")
        
        # Submit page
        await self.capture_page(page, "/submit", "submit_page.png", 
                               "#idea-form", "Submit Idea form")
        
        # My Ideas page  
        await self.capture_page(page, "/my-ideas", "my_ideas_page.png",
                               ".my-ideas-container", "My Ideas dashboard")
        
        # Profile page
        await self.capture_page(page, "/profile", "profile_page.png",
                               ".profile-container", "User Profile")
        
        # My Team page (if user is a manager)
        await self.capture_page(page, "/my-team", "my_team_page.png",
                               ".team-dashboard", "Team Analytics")
        
        # Try to capture idea detail
        print("\n--- Capturing Idea Detail ---")
        await page.goto(f"{self.base_url}/")
        await self.wait_for_load(page, ".idea-card")
        
        # Find first idea link
        idea_links = await page.query_selector_all(".idea-card a")
        if idea_links:
            # Click on the first idea
            await idea_links[0].click()
            await self.wait_for_load(page, ".idea-detail-container")
            
            # Take screenshot
            filepath = os.path.join(self.screenshots_dir, "idea_detail_page.png")
            await page.screenshot(path=filepath, full_page=False)
            print(f"  ✓ Captured idea detail page")

async def main():
    """Main entry point"""
    capture = AuthenticatedScreenshotCapture()
    await capture.capture_screenshots()

if __name__ == "__main__":
    # Check if Flask app is running
    import requests
    try:
        response = requests.get("http://localhost:9094", timeout=2)
        print("✓ Flask app is running")
        asyncio.run(main())
    except requests.exceptions.RequestException:
        print("✗ Flask app is not running!")
        print("\nPlease start the Flask app first:")
        print("  ./start-flask.sh")
        print("\nThen run this script again.")