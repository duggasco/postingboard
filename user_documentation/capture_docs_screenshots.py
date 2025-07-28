#!/usr/bin/env python3
"""
Capture documentation screenshots with authenticated test user
"""
import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import random
import string

def setup_driver():
    """Setup Chrome driver with options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--force-device-scale-factor=1.5")
    return webdriver.Chrome(options=chrome_options)

def create_test_user(driver, base_url):
    """Create a test user account and verify email"""
    test_email = f"test_user_{random.randint(1000, 9999)}@example.com"
    print(f"Creating test user: {test_email}")
    
    # Go to verify email page
    driver.get(f"{base_url}/verify-email")
    time.sleep(2)
    
    # Request verification code
    email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys(test_email)
    driver.find_element(By.XPATH, "//button[text()='Send Verification Code']").click()
    time.sleep(2)
    
    # Get verification code from logs
    logs = subprocess.check_output(["docker", "logs", "postingboard-flask-app-1", "--tail", "20"], text=True)
    code = None
    for line in logs.split('\n'):
        if "Verification code for" in line and test_email in line:
            # Extract the 6-digit code
            parts = line.split("Verification code for")[1].split(":")
            if len(parts) > 1:
                code = parts[1].strip().split()[0]
                break
    
    if not code:
        print("Could not find verification code in logs")
        return None
    
    print(f"Found verification code: {code}")
    
    # Enter verification code
    code_input = driver.find_element(By.NAME, "code")
    code_input.send_keys(code)
    driver.find_element(By.XPATH, "//button[text()='Verify Email']").click()
    time.sleep(2)
    
    # Complete profile
    driver.get(f"{base_url}/profile")
    time.sleep(2)
    
    name_input = driver.find_element(By.ID, "name")
    name_input.clear()
    name_input.send_keys("Test User")
    
    # Select role - Developer
    role_select = Select(driver.find_element(By.ID, "role"))
    role_select.select_by_value("developer")
    
    # Select team
    team_select = Select(driver.find_element(By.ID, "team-select"))
    team_select.select_by_visible_text("Cash - GPP")
    
    # Select some skills
    driver.find_element(By.XPATH, "//input[@type='checkbox' and @value='Python']").click()
    driver.find_element(By.XPATH, "//input[@type='checkbox' and @value='JavaScript']").click()
    
    # Save profile
    driver.find_element(By.XPATH, "//button[text()='Save Profile']").click()
    time.sleep(2)
    
    return test_email

def capture_screenshots(base_url="http://localhost:9094"):
    """Capture screenshots of authenticated pages"""
    driver = setup_driver()
    output_dir = "documentation_screenshots"
    
    try:
        # Create test user
        test_email = create_test_user(driver, base_url)
        if not test_email:
            print("Failed to create test user")
            return
        
        print(f"Test user created: {test_email}")
        
        # Capture Submit Idea page
        print("Capturing Submit Idea page...")
        driver.get(f"{base_url}/submit")
        time.sleep(3)
        
        # Fill in some sample data to make the form look more complete
        driver.find_element(By.ID, "title").send_keys("Implement Advanced Analytics Dashboard")
        driver.find_element(By.ID, "description").send_keys(
            "We need a comprehensive analytics dashboard that provides real-time insights into our application usage patterns. "
            "The dashboard should include:\n\n"
            "• User activity metrics and trends\n"
            "• Performance monitoring capabilities\n"
            "• Custom report generation\n"
            "• Data export functionality\n\n"
            "This will help our team make data-driven decisions and improve user experience."
        )
        
        # Select priority
        priority_select = Select(driver.find_element(By.ID, "priority"))
        priority_select.select_by_value("high")
        
        # Select size
        size_select = Select(driver.find_element(By.ID, "size"))
        size_select.select_by_value("large")
        
        # Add bounty
        driver.find_element(By.ID, "bounty").send_keys("Recognition in company newsletter and team lunch")
        
        # Select skills
        driver.find_element(By.XPATH, "//input[@type='checkbox' and @value='Python']").click()
        driver.find_element(By.XPATH, "//input[@type='checkbox' and @value='React']").click()
        driver.find_element(By.XPATH, "//input[@type='checkbox' and @value='Data Analytics']").click()
        
        # Take screenshot
        driver.save_screenshot(f"{output_dir}/submit_idea_page.png")
        print(f"✓ Saved Submit Idea page screenshot")
        
        # Capture My Ideas page
        print("Capturing My Ideas page...")
        driver.get(f"{base_url}/my-ideas")
        time.sleep(3)
        
        # The page might be empty, so let's submit an idea first
        driver.get(f"{base_url}/submit")
        time.sleep(2)
        
        # Quick submit an idea
        driver.find_element(By.ID, "title").send_keys("Automated Testing Framework")
        driver.find_element(By.ID, "description").send_keys(
            "Develop a comprehensive automated testing framework to improve code quality and reduce manual testing effort."
        )
        Select(driver.find_element(By.ID, "priority")).select_by_value("medium")
        Select(driver.find_element(By.ID, "size")).select_by_value("medium")
        driver.find_element(By.ID, "bounty").send_keys("Extra PTO day")
        driver.find_element(By.XPATH, "//input[@type='checkbox' and @value='Python']").click()
        
        # Submit the form
        driver.find_element(By.XPATH, "//button[text()='Submit Idea']").click()
        time.sleep(3)
        
        # Now go back to My Ideas
        driver.get(f"{base_url}/my-ideas")
        time.sleep(3)
        
        driver.save_screenshot(f"{output_dir}/my_ideas_page.png")
        print(f"✓ Saved My Ideas page screenshot")
        
        # Also capture the profile page for completeness
        print("Capturing Profile page...")
        driver.get(f"{base_url}/profile")
        time.sleep(2)
        driver.save_screenshot(f"{output_dir}/profile_page.png")
        print(f"✓ Saved Profile page screenshot")
        
        print("\nAll screenshots captured successfully!")
        
    except Exception as e:
        print(f"Error capturing screenshots: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_screenshots()