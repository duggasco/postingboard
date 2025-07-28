#!/usr/bin/env python3
"""
Automated Screenshot Capture using Playwright
Alternative to Selenium - often easier to setup and more reliable
"""

import os
import time
import asyncio

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright not installed. Installing...")
    os.system("pip install playwright")
    os.system("python -m playwright install chromium")
    print("\nPlease run this script again after installation completes.")
    exit(1)

class PlaywrightScreenshotCapture:
    def __init__(self):
        self.screenshots_dir = "/root/postingboard/documentation_screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.base_url = "http://localhost:9094"
        
    async def capture_screenshots(self):
        """Main function to capture all screenshots"""
        print("="*60)
        print("Automated Screenshot Capture with Playwright")
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
                # Capture public pages
                await self.capture_public_pages(page)
                
                # Simulate user session
                await self.setup_user_session(page, context)
                await self.capture_user_pages(page)
                
                # Capture admin pages
                await self.login_admin(page)
                await self.capture_admin_pages(page)
                
                print("\n" + "="*60)
                print("✓ Screenshot capture complete!")
                print(f"Screenshots saved to: {self.screenshots_dir}")
                
            except Exception as e:
                print(f"\n✗ Error during capture: {e}")
                
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
            
    async def capture_public_pages(self, page):
        """Capture pages that don't require authentication"""
        print("\n--- Capturing Public Pages ---")
        
        screenshots = [
            ("/", "home_page.png", ".idea-grid", "Browse Ideas page"),
            ("/verify-email", "verify_email_page.png", ".verification-container", "Email verification"),
        ]
        
        for url, filename, selector, desc in screenshots:
            await self.capture_page(page, url, filename, selector, desc)
            
    async def setup_user_session(self, page, context):
        """Setup user session by injecting cookies/localStorage"""
        print("\n--- Setting up user session ---")
        
        # Navigate to home page first
        await page.goto(self.base_url)
        
        # Inject session data into localStorage
        await page.evaluate("""
            localStorage.setItem('user_email', 'demo@example.com');
            localStorage.setItem('user_name', 'Demo User');
            localStorage.setItem('user_verified', 'true');
            localStorage.setItem('user_role', 'developer');
            localStorage.setItem('user_team', 'SL - Tech');
            localStorage.setItem('user_skills', JSON.stringify(['Python', 'JavaScript', 'SQL']));
        """)
        
        # Try to set cookies for Flask session
        await context.add_cookies([{
            'name': 'session',
            'value': 'demo-session',
            'domain': 'localhost',
            'path': '/'
        }])
        
        print("  ✓ User session configured")
        
    async def capture_user_pages(self, page):
        """Capture pages requiring user authentication"""
        print("\n--- Capturing User Pages ---")
        
        screenshots = [
            ("/submit", "submit_page.png", "#idea-form", "Submit Idea form"),
            ("/my-ideas", "my_ideas_page.png", ".my-ideas-container", "My Ideas dashboard"),
            ("/profile", "profile_page.png", ".profile-container", "User Profile"),
        ]
        
        for url, filename, selector, desc in screenshots:
            await self.capture_page(page, url, filename, selector, desc)
            
        # Try to capture idea detail
        await page.goto(f"{self.base_url}/")
        await self.wait_for_load(page, ".idea-card")
        
        # Find first idea link
        idea_link = await page.query_selector(".idea-card a")
        if idea_link:
            href = await idea_link.get_attribute('href')
            if href:
                idea_path = href.replace(self.base_url, '')
                await self.capture_page(page, idea_path, "idea_detail_page.png", 
                                      ".idea-detail-container", "Idea detail page")
                                      
    async def login_admin(self, page):
        """Login to admin portal"""
        print("\n--- Admin Login ---")
        
        try:
            await page.goto(f"{self.base_url}/admin/login")
            await self.wait_for_load(page, "input[type='password']")
            
            # Fill password
            await page.fill("input[type='password']", "2929arch")
            
            # Submit
            await page.click("button[type='submit']")
            
            # Wait for redirect
            await page.wait_for_timeout(2000)
            
            print("  ✓ Admin login successful")
            return True
            
        except Exception as e:
            print(f"  ✗ Admin login failed: {e}")
            return False
            
    async def capture_admin_pages(self, page):
        """Capture admin/manager pages"""
        print("\n--- Capturing Admin Pages ---")
        
        screenshots = [
            ("/admin/dashboard", "admin_dashboard.png", ".admin-dashboard", "Admin dashboard"),
            ("/my-team", "my_team_page.png", ".team-dashboard", "Team analytics"),
        ]
        
        for url, filename, selector, desc in screenshots:
            await self.capture_page(page, url, filename, selector, desc)

async def main():
    """Main entry point"""
    capture = PlaywrightScreenshotCapture()
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