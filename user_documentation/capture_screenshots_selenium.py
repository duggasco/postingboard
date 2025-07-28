#!/usr/bin/env python3
"""
Automated Screenshot Capture using Selenium
Captures screenshots with JavaScript fully loaded
"""

import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class ScreenshotAutomation:
    def __init__(self):
        self.screenshots_dir = "/root/postingboard/documentation_screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.base_url = "http://localhost:9094"
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with options for screenshots"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✓ Chrome driver initialized successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize Chrome driver: {e}")
            return False
            
    def wait_for_element(self, selector, timeout=10):
        """Wait for an element to be present and visible"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except TimeoutException:
            print(f"  ⚠ Element not found: {selector}")
            return None
            
    def wait_for_javascript(self, timeout=5):
        """Wait for JavaScript to complete loading"""
        try:
            # Wait for jQuery if present
            self.driver.execute_script("return (typeof jQuery !== 'undefined' && jQuery.active == 0) || true")
            
            # Wait for document ready state
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            return True
        except Exception as e:
            print(f"  ⚠ JavaScript wait error: {e}")
            return False
            
    def login_as_user(self, email="test@example.com", name="Test User"):
        """Simulate user login by setting session"""
        try:
            # First, navigate to verify-email page
            self.driver.get(f"{self.base_url}/verify-email")
            time.sleep(1)
            
            # Try to set session data via JavaScript
            session_data = {
                'user_email': email,
                'user_name': name,
                'user_verified': True,
                'user_role': 'developer',
                'user_team': 'SL - Tech',
                'user_skills': ['Python', 'JavaScript', 'SQL']
            }
            
            # Store session data in localStorage (if the app uses it)
            for key, value in session_data.items():
                self.driver.execute_script(
                    f"window.localStorage.setItem('{key}', '{json.dumps(value) if isinstance(value, list) else value}')"
                )
            
            print(f"✓ Simulated login as {email}")
            return True
        except Exception as e:
            print(f"✗ Login simulation failed: {e}")
            return False
            
    def login_as_admin(self):
        """Login to admin portal"""
        try:
            self.driver.get(f"{self.base_url}/admin/login")
            time.sleep(2)
            
            # Find and fill password field
            password_field = self.wait_for_element("input[type='password']")
            if password_field:
                password_field.send_keys("2929arch")
                
                # Submit form
                submit_button = self.wait_for_element("button[type='submit']")
                if submit_button:
                    submit_button.click()
                    time.sleep(2)
                    print("✓ Admin login successful")
                    return True
                    
            print("✗ Admin login failed")
            return False
        except Exception as e:
            print(f"✗ Admin login error: {e}")
            return False
            
    def capture_screenshot(self, url_path, filename, wait_selector=None, description=""):
        """Capture a screenshot of a specific page"""
        try:
            print(f"\nCapturing: {filename}")
            print(f"  URL: {self.base_url}{url_path}")
            if description:
                print(f"  Description: {description}")
                
            # Navigate to page
            self.driver.get(f"{self.base_url}{url_path}")
            
            # Wait for JavaScript to load
            self.wait_for_javascript()
            
            # Wait for specific element if provided
            if wait_selector:
                element = self.wait_for_element(wait_selector, timeout=10)
                if element:
                    print(f"  ✓ Found required element: {wait_selector}")
                    
            # Additional wait for charts/animations
            time.sleep(3)
            
            # Scroll to ensure full page is loaded
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Take screenshot
            filepath = os.path.join(self.screenshots_dir, filename)
            self.driver.save_screenshot(filepath)
            
            # Verify file was created
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
            
    def capture_all_screenshots(self):
        """Capture all required screenshots"""
        print("="*60)
        print("Automated Screenshot Capture")
        print("="*60)
        
        # Setup driver
        if not self.setup_driver():
            print("\n✗ Failed to setup Chrome driver. Please ensure Chrome and chromedriver are installed.")
            print("\nInstallation instructions:")
            print("1. Install Chrome: sudo apt-get install google-chrome-stable")
            print("2. Install chromedriver: sudo apt-get install chromium-chromedriver")
            print("   OR download from: https://chromedriver.chromium.org/")
            return
            
        try:
            # Public pages (no login required)
            public_screenshots = [
                ("/", "home_page.png", ".idea-card", "Browse Ideas page with idea cards"),
                ("/verify-email", "verify_email_page.png", ".auth-container", "Email verification page"),
            ]
            
            print("\n--- Capturing Public Pages ---")
            for url, filename, selector, desc in public_screenshots:
                self.capture_screenshot(url, filename, selector, desc)
                
            # User pages (requires login)
            print("\n--- Capturing User Pages ---")
            if self.login_as_user():
                user_screenshots = [
                    ("/submit", "submit_page.png", "#submit-form", "Submit Idea form"),
                    ("/my-ideas", "my_ideas_page.png", ".stats-container", "My Ideas dashboard"),
                    ("/profile", "profile_page.png", ".profile-form", "User Profile page"),
                ]
                
                for url, filename, selector, desc in user_screenshots:
                    self.capture_screenshot(url, filename, selector, desc)
                    
                # Capture idea detail (need to find an idea ID first)
                self.driver.get(f"{self.base_url}/")
                time.sleep(2)
                idea_links = self.driver.find_elements(By.CSS_SELECTOR, ".idea-card a")
                if idea_links:
                    first_idea_url = idea_links[0].get_attribute('href')
                    idea_path = first_idea_url.replace(self.base_url, '')
                    self.capture_screenshot(idea_path, "idea_detail_page.png", ".idea-detail", "Individual idea detail page")
                    
            # Manager/Admin pages
            print("\n--- Capturing Admin Pages ---")
            if self.login_as_admin():
                admin_screenshots = [
                    ("/admin/dashboard", "admin_dashboard.png", ".dashboard-stats", "Admin dashboard"),
                    ("/my-team", "my_team_page.png", ".team-stats", "Team analytics page"),
                ]
                
                for url, filename, selector, desc in admin_screenshots:
                    self.capture_screenshot(url, filename, selector, desc)
                    
            print("\n" + "="*60)
            print("Screenshot capture complete!")
            print(f"Screenshots saved to: {self.screenshots_dir}")
            
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                print("\n✓ Chrome driver closed")
                
    def install_dependencies(self):
        """Install required dependencies"""
        print("Installing dependencies for screenshot automation...\n")
        
        commands = [
            ("pip install selenium", "Installing Selenium"),
            ("pip install webdriver-manager", "Installing WebDriver Manager"),
        ]
        
        for cmd, desc in commands:
            print(f"{desc}...")
            os.system(cmd)
            
        print("\n✓ Dependencies installed")
        print("\nNote: You also need Chrome/Chromium and chromedriver installed:")
        print("  Ubuntu/Debian: sudo apt-get install chromium-browser chromium-chromedriver")
        print("  OR manually download chromedriver from https://chromedriver.chromium.org/")

if __name__ == "__main__":
    automation = ScreenshotAutomation()
    
    # Check if we need to install dependencies
    try:
        import selenium
        # Dependencies are installed, run the capture
        automation.capture_all_screenshots()
    except ImportError:
        print("Selenium not found. Installing dependencies...")
        automation.install_dependencies()
        print("\nPlease run this script again after installing Chrome/chromedriver")