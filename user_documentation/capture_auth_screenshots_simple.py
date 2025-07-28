#!/usr/bin/env python3
"""
Simple screenshot capture using test authentication route
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

async def capture_authenticated_screenshots():
    """Capture screenshots of authenticated pages"""
    screenshots_dir = "/root/postingboard/documentation_screenshots"
    base_url = "http://localhost:9094"
    
    print("="*60)
    print("Capturing Authenticated Screenshots")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            # First, use the test auth route to create a session
            print("\n1. Creating test session...")
            await page.goto(f"{base_url}/test-auth-documentation")
            await page.wait_for_timeout(2000)
            
            # Should be redirected to home page with session
            print("   ✓ Session created")
            
            # Now capture the authenticated pages
            print("\n2. Capturing Submit page...")
            await page.goto(f"{base_url}/submit")
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)
            
            # Check if we're on the submit page
            if "submit" in page.url:
                await page.screenshot(path=f"{screenshots_dir}/submit_page.png")
                print("   ✓ Submit page captured")
            else:
                print(f"   ✗ Redirected to: {page.url}")
            
            print("\n3. Capturing My Ideas page...")
            await page.goto(f"{base_url}/my-ideas")
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)
            
            if "my-ideas" in page.url:
                await page.screenshot(path=f"{screenshots_dir}/my_ideas_page.png")
                print("   ✓ My Ideas page captured")
            else:
                print(f"   ✗ Redirected to: {page.url}")
            
            print("\n4. Capturing Profile page...")
            await page.goto(f"{base_url}/profile")
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)
            
            if "profile" in page.url:
                await page.screenshot(path=f"{screenshots_dir}/profile_page.png")
                print("   ✓ Profile page captured")
            else:
                print(f"   ✗ Redirected to: {page.url}")
                
            print("\n5. Capturing My Team page...")
            # First update session to have manager role
            await page.evaluate("""
                fetch('/api/test-set-manager', {method: 'POST'}).catch(() => {});
            """)
            
            await page.goto(f"{base_url}/my-team")
            await page.wait_for_load_state('networkidle') 
            await page.wait_for_timeout(2000)
            
            # My team might redirect if not manager, that's ok
            await page.screenshot(path=f"{screenshots_dir}/my_team_page.png")
            print("   ✓ My Team page captured (if available)")
            
            print("\n" + "="*60)
            print("✓ Screenshot capture complete!")
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            await browser.close()

if __name__ == "__main__":
    # Check if Flask app is running
    import requests
    try:
        # Set development environment
        os.environ['FLASK_ENV'] = 'development'
        
        response = requests.get("http://localhost:9094", timeout=2)
        print("✓ Flask app is running")
        asyncio.run(capture_authenticated_screenshots())
    except requests.exceptions.RequestException:
        print("✗ Flask app is not running!")
        print("\nPlease start the Flask app first:")
        print("  ./start-flask.sh")
        print("\nThen run this script again.")