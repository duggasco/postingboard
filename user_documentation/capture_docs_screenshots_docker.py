#!/usr/bin/env python3
"""
Capture documentation screenshots with authenticated test user using Playwright
Designed to run inside the Docker container
"""

import os
import time
import subprocess
import asyncio
import json
import random

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright not installed. Installing...")
    os.system("pip install playwright")
    os.system("python -m playwright install chromium")
    os.system("python -m playwright install-deps")
    print("\nPlease run this script again after installation completes.")
    exit(1)

class DocumentationScreenshotCapture:
    def __init__(self):
        self.screenshots_dir = "/root/postingboard/documentation_screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.base_url = "http://localhost:9094"
        self.test_email = f"doctest_{random.randint(1000, 9999)}@example.com"
        self.test_name = "Documentation Test User"
        
    async def capture_screenshots(self):
        """Main function to capture all screenshots"""
        print("="*60)
        print("Documentation Screenshot Capture with Playwright")
        print("="*60)
        print(f"Test email: {self.test_email}")
        
        async with async_playwright() as p:
            # Launch browser
            print("\nLaunching browser...")
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            
            # Create context with viewport
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                device_scale_factor=1.5,  # Higher quality screenshots
            )
            
            # Create page
            page = await context.new_page()
            
            try:
                # First authenticate the user
                await self.authenticate_user(page)
                
                # Submit a sample idea for better My Ideas screenshot
                await self.submit_sample_idea(page)
                
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
            await page.wait_for_timeout(1500)
            
            return True
        except Exception as e:
            print(f"  ⚠ Load timeout: {e}")
            return False
            
    async def get_verification_code(self):
        """Get the verification code from Docker logs"""
        try:
            # Get recent logs
            logs = subprocess.check_output(
                ["docker", "logs", "postingboard-flask-app-1", "--tail", "50"],
                text=True,
                stderr=subprocess.STDOUT
            )
            
            # Look for verification code for our test email
            for line in reversed(logs.split('\n')):
                if f"Verification code for {self.test_email}" in line:
                    # Extract the 6-digit code
                    parts = line.split(":")
                    if len(parts) > 1:
                        code = parts[-1].strip().split()[0]
                        if code.isdigit() and len(code) == 6:
                            return code
            
            # If not found in regular logs, check if it's printed to console
            print("  Code not found in logs, using default dev code...")
            return "123456"
            
        except Exception as e:
            print(f"  Error getting verification code: {e}")
            return "123456"
            
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
        await page.click("button[text='Send Verification Code']")
        
        # Wait for the verification code request
        await page.wait_for_timeout(3000)
        
        # 3. Get verification code
        verification_code = await self.get_verification_code()
        print(f"3. Found verification code: {verification_code}")
        
        # Enter the code
        try:
            await page.wait_for_selector("#code", timeout=5000)
            await page.fill("#code", verification_code)
            await page.click("button[text='Verify Email']")
            
            # Wait for redirect
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
                await page.select_option("#team-select", "Cash - GPP")
                
                # Select skills
                skills = ["Python", "JavaScript", "SQL", "React", "Data Analytics"]
                for skill in skills:
                    skill_checkbox = await page.query_selector(f"input[type='checkbox'][value='{skill}']")
                    if skill_checkbox:
                        await skill_checkbox.check()
                
                # Submit profile
                await page.click("button[text='Save Profile']")
                await page.wait_for_timeout(2000)
                
            print("  ✓ Authentication successful!")
            return True
            
        except Exception as e:
            print(f"  ✗ Authentication failed: {e}")
            return False
    
    async def submit_sample_idea(self, page):
        """Submit a sample idea to populate My Ideas page"""
        print("\n--- Submitting Sample Idea ---")
        
        await page.goto(f"{self.base_url}/submit")
        await self.wait_for_load(page, "#title")
        
        # Fill the form
        await page.fill("#title", "Automated Testing Framework")
        await page.fill("#description", 
            "Develop a comprehensive automated testing framework to improve code quality and reduce manual testing effort.\n\n"
            "Key features:\n"
            "• Unit test automation\n"
            "• Integration test suites\n"
            "• Performance benchmarking\n"
            "• Continuous integration support"
        )
        
        await page.select_option("#priority", "medium")
        await page.select_option("#size", "medium")
        await page.fill("#bounty", "Extra PTO day and team recognition")
        
        # Select skills
        skills_to_select = ["Python", "JavaScript", "Testing"]
        for skill in skills_to_select:
            skill_checkbox = await page.query_selector(f"input[type='checkbox'][value='{skill}']")
            if skill_checkbox:
                await skill_checkbox.check()
        
        # Submit
        await page.click("button[text='Submit Idea']")
        await page.wait_for_timeout(3000)
        
        print("  ✓ Sample idea submitted")
    
    async def capture_page_with_content(self, page, url_path, filename, prepare_func=None, description=""):
        """Capture a single page screenshot with optional content preparation"""
        try:
            print(f"\nCapturing: {filename}")
            print(f"  URL: {self.base_url}{url_path}")
            if description:
                print(f"  Description: {description}")
                
            # Navigate to page
            await page.goto(f"{self.base_url}{url_path}", wait_until='networkidle')
            
            # Run preparation function if provided
            if prepare_func:
                await prepare_func(page)
            
            # Wait for content to load
            await page.wait_for_timeout(2000)
            
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
    
    async def prepare_submit_form(self, page):
        """Fill out the submit form for a better screenshot"""
        await self.wait_for_load(page, "#title")
        
        # Fill in sample data
        await page.fill("#title", "Implement Advanced Analytics Dashboard")
        await page.fill("#description", 
            "We need a comprehensive analytics dashboard that provides real-time insights into our application usage patterns. "
            "The dashboard should include:\n\n"
            "• User activity metrics and trends\n"
            "• Performance monitoring capabilities\n"
            "• Custom report generation\n"
            "• Data export functionality\n\n"
            "This will help our team make data-driven decisions and improve user experience."
        )
        
        await page.select_option("#priority", "high")
        await page.select_option("#size", "large")
        
        # Add monetary bounty
        monetary_checkbox = await page.query_selector("input#is_monetary")
        if monetary_checkbox:
            await monetary_checkbox.check()
            await page.wait_for_timeout(500)
            
            # Check expensed option
            expensed_checkbox = await page.query_selector("input#is_expensed")
            if expensed_checkbox:
                await expensed_checkbox.check()
                await page.wait_for_timeout(500)
                
            # Enter amount
            amount_input = await page.query_selector("input#amount")
            if amount_input:
                await amount_input.fill("500")
        
        await page.fill("#bounty", "Recognition in company newsletter and conference attendance sponsorship")
        
        # Select skills
        skills_to_show = ["Python", "React", "Data Analytics", "SQL", "Docker"]
        for skill in skills_to_show:
            skill_checkbox = await page.query_selector(f"input[type='checkbox'][value='{skill}']")
            if skill_checkbox:
                await skill_checkbox.check()
        
        # Set a needed by date
        await page.fill("#needed_by", "2025-09-01")
    
    async def capture_authenticated_pages(self, page):
        """Capture pages requiring authentication"""
        print("\n--- Capturing Authenticated Pages ---")
        
        # Submit page with filled form
        await self.capture_page_with_content(
            page, "/submit", "submit_idea_page.png",
            prepare_func=self.prepare_submit_form,
            description="Submit Idea form with sample data"
        )
        
        # My Ideas page
        await self.capture_page_with_content(
            page, "/my-ideas", "my_ideas_page.png",
            description="My Ideas dashboard showing submitted ideas"
        )
        
        # Profile page
        await self.capture_page_with_content(
            page, "/profile", "profile_page.png",
            description="User Profile page"
        )

async def main():
    """Main entry point"""
    capture = DocumentationScreenshotCapture()
    await capture.capture_screenshots()

if __name__ == "__main__":
    # Check if we're running inside Docker or native
    if os.path.exists("/.dockerenv"):
        print("✓ Running inside Docker container")
        asyncio.run(main())
    else:
        print("Running outside Docker - executing inside container...")
        # Copy script to container and run it
        os.system("docker cp capture_docs_screenshots_docker.py postingboard-flask-app-1:/tmp/")
        os.system("docker exec postingboard-flask-app-1 python /tmp/capture_docs_screenshots_docker.py")