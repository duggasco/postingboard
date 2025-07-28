#!/usr/bin/env python3
"""
Capture screenshots for My Ideas and My Team pages using test user authentication
First creates test data, then authenticates and captures screenshots
"""

import subprocess
import os
import random

# Generate unique test users
test_email = f"developer_{random.randint(1000, 9999)}@example.com"
test_name = "John Developer"
manager_email = f"manager_{random.randint(1000, 9999)}@example.com" 
manager_name = "Sarah Manager"

# First, create the test data
create_data_script = f"""
import os
import sys
sys.path.append('/app')

from database import get_session
from models import UserProfile, Team, Skill, UserSkill, Idea, Claim, Bounty, IdeaStatus, PriorityLevel, IdeaSize
import uuid
from datetime import datetime, timedelta

db = get_session()

try:
    # Get or create teams
    team_gpp = db.query(Team).filter_by(name='Cash - GPP').first()
    if not team_gpp:
        team_gpp = Team(uuid=str(uuid.uuid4()), name='Cash - GPP', is_approved=True)
        db.add(team_gpp)
    
    team_tech = db.query(Team).filter_by(name='SL - Tech').first()
    if not team_tech:
        team_tech = Team(uuid=str(uuid.uuid4()), name='SL - Tech', is_approved=True)
        db.add(team_tech)
    
    db.commit()
    
    # Create test developer
    developer = UserProfile(
        email='{test_email}',
        name='{test_name}',
        is_verified=True,
        role='developer',
        team_uuid=team_gpp.uuid
    )
    db.add(developer)
    
    # Create test manager
    manager = UserProfile(
        email='{manager_email}',
        name='{manager_name}',
        is_verified=True,
        role='manager',
        team_uuid=team_tech.uuid,
        managed_team_uuid=team_tech.uuid
    )
    db.add(manager)
    
    db.commit()
    
    # Add skills
    skills = ['Python', 'JavaScript', 'React', 'SQL', 'Data Analytics']
    for skill_name in skills:
        skill = db.query(Skill).filter_by(name=skill_name).first()
        if not skill:
            skill = Skill(uuid=str(uuid.uuid4()), name=skill_name)
            db.add(skill)
            db.commit()
        
        # Add skills to developer
        if skill_name in ['Python', 'JavaScript', 'React']:
            user_skill = UserSkill(user_email=developer.email, skill_uuid=skill.uuid)
            db.add(user_skill)
    
    db.commit()
    
    # Create ideas submitted by developer
    idea1 = Idea(
        uuid=str(uuid.uuid4()),
        title='Automated Testing Framework',
        description='Develop a comprehensive automated testing framework to improve code quality.',
        email=developer.email,
        benefactor_team_uuid=team_gpp.uuid,
        priority=PriorityLevel.high,
        size=IdeaSize.large,
        status=IdeaStatus.open,
        bounty='Extra PTO day and team recognition',
        created_at=datetime.utcnow() - timedelta(days=5),
        needed_by=datetime.utcnow() + timedelta(days=30)
    )
    db.add(idea1)
    
    idea2 = Idea(
        uuid=str(uuid.uuid4()),
        title='Real-time Dashboard Implementation',
        description='Create a real-time monitoring dashboard with key metrics.',
        email=developer.email,
        benefactor_team_uuid=team_gpp.uuid,
        priority=PriorityLevel.medium,
        size=IdeaSize.medium,
        status=IdeaStatus.claimed,
        bounty='Conference attendance sponsorship',
        created_at=datetime.utcnow() - timedelta(days=3)
    )
    db.add(idea2)
    
    # Create idea claimed by developer
    idea3 = Idea(
        uuid=str(uuid.uuid4()),
        title='API Documentation Generator',
        description='Build an automated tool for API documentation.',
        email='other.user@example.com',
        benefactor_team_uuid=team_tech.uuid,
        priority=PriorityLevel.medium,
        size=IdeaSize.small,
        status=IdeaStatus.claimed,
        bounty='Team lunch',
        created_at=datetime.utcnow() - timedelta(days=7)
    )
    db.add(idea3)
    db.commit()
    
    # Create claim
    claim = Claim(
        idea_uuid=idea3.uuid,
        claimer_email=developer.email,
        claimed_at=datetime.utcnow() - timedelta(days=2)
    )
    db.add(claim)
    
    # Add monetary bounty
    bounty = Bounty(
        idea_uuid=idea2.uuid,
        is_monetary=True,
        is_expensed=True,
        amount=250.00,
        is_approved=True
    )
    db.add(bounty)
    
    # Create ideas for manager's team
    idea4 = Idea(
        uuid=str(uuid.uuid4()),
        title='Performance Optimization Initiative',
        description='Optimize application performance focusing on database and APIs.',
        email='team.member1@example.com',
        benefactor_team_uuid=team_tech.uuid,
        priority=PriorityLevel.high,
        size=IdeaSize.large,
        status=IdeaStatus.open,
        bounty='Bonus consideration',
        created_at=datetime.utcnow() - timedelta(days=1)
    )
    db.add(idea4)
    
    idea5 = Idea(
        uuid=str(uuid.uuid4()),
        title='Security Audit Implementation',
        description='Conduct comprehensive security audit and implement recommendations.',
        email='team.member2@example.com',
        benefactor_team_uuid=team_tech.uuid,
        priority=PriorityLevel.high,
        size=IdeaSize.medium,
        status=IdeaStatus.claimed,
        bounty='Recognition award',
        created_at=datetime.utcnow() - timedelta(days=4)
    )
    db.add(idea5)
    
    db.commit()
    print("Test data created successfully!")
    print(f"Developer: {test_email}")
    print(f"Manager: {manager_email}")
    
except Exception as e:
    print(f"Error creating test data: {{e}}")
    db.rollback()
finally:
    db.close()
"""

# Screenshot capture script
screenshot_script = f"""
import asyncio
from playwright.async_api import async_playwright
import os
import subprocess

async def get_verification_code(email):
    # In dev mode, we'll use a simple code
    return "123456"

async def authenticate_user(page, email, name, role, team_name):
    print(f"\\nAuthenticating as {{email}}...")
    
    # Go to verify-email page
    await page.goto("http://localhost:9094/verify-email")
    await page.wait_for_timeout(2000)
    
    # Enter email
    await page.fill("#email", email)
    await page.click("button[type='submit']:has-text('Send Verification Code')")
    await page.wait_for_timeout(2000)
    
    # Get and enter verification code
    code = await get_verification_code(email)
    await page.fill("#code", code)
    await page.click("button[type='submit']:has-text('Verify Email')")
    await page.wait_for_timeout(3000)
    
    # Check if we need to complete profile
    if "/profile" in page.url:
        print("Completing profile...")
        await page.fill("#name", name)
        await page.select_option("#role", role)
        await page.select_option("#team-select", team_name)
        
        # Select some skills
        for skill in ["Python", "JavaScript", "React"]:
            checkbox = page.locator(f"input[type='checkbox'][value='{{skill}}']")
            if await checkbox.count() > 0:
                await checkbox.check()
        
        await page.click("button:has-text('Save Profile')")
        await page.wait_for_timeout(2000)
    
    print("   ✓ Authentication successful")

async def main():
    screenshots_dir = "/app/documentation_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    print("Starting user screenshot capture...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        # First capture developer pages
        print("\\n=== Capturing Developer Pages ===")
        page = await browser.new_page(viewport={{'width': 1920, 'height': 1080}})
        
        try:
            # Authenticate as developer
            await authenticate_user(page, "{test_email}", "{test_name}", "developer", "Cash - GPP")
            
            # Capture My Ideas page
            print("\\nCapturing My Ideas page...")
            await page.goto("http://localhost:9094/my-ideas")
            await page.wait_for_timeout(3000)
            await page.screenshot(path=f"{{screenshots_dir}}/my_ideas_page.png")
            print("   ✓ My Ideas page captured")
            
        except Exception as e:
            print(f"Error capturing developer pages: {{e}}")
        
        await page.close()
        
        # Now capture manager pages
        print("\\n=== Capturing Manager Pages ===")
        page = await browser.new_page(viewport={{'width': 1920, 'height': 1080}})
        
        try:
            # Authenticate as manager
            await authenticate_user(page, "{manager_email}", "{manager_name}", "manager", "SL - Tech")
            
            # Capture My Team page
            print("\\nCapturing My Team page...")
            await page.goto("http://localhost:9094/my-team")
            await page.wait_for_timeout(3000)
            await page.screenshot(path=f"{{screenshots_dir}}/my_team_page.png")
            print("   ✓ My Team page captured")
            
        except Exception as e:
            print(f"Error capturing manager pages: {{e}}")
        
        await browser.close()
    
    print("\\n✓ All screenshots captured!")

if __name__ == "__main__":
    asyncio.run(main())
"""

print("="*60)
print("User Screenshot Capture")
print("="*60)

# Create test data
print("\n1. Creating test data...")
with open('/tmp/create_test_data.py', 'w') as f:
    f.write(create_data_script)

subprocess.run(["docker", "cp", "/tmp/create_test_data.py", "postingboard-flask-app-1:/tmp/"])
result = subprocess.run(
    ["docker", "exec", "postingboard-flask-app-1", "python", "/tmp/create_test_data.py"],
    capture_output=True,
    text=True
)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

# Capture screenshots
print("\n2. Capturing screenshots...")
with open('/tmp/capture_user_screenshots.py', 'w') as f:
    f.write(screenshot_script)

subprocess.run(["docker", "cp", "/tmp/capture_user_screenshots.py", "postingboard-flask-app-1:/tmp/"])
result = subprocess.run(
    ["docker", "exec", "postingboard-flask-app-1", "python", "/tmp/capture_user_screenshots.py"],
    capture_output=True,
    text=True
)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

# Copy screenshots back
print("\n3. Copying screenshots to host...")
subprocess.run(["docker", "cp", "postingboard-flask-app-1:/app/documentation_screenshots/.", "./documentation_screenshots/"])

print("\n✓ Screenshot capture complete!")
print(f"Screenshots saved to: ./documentation_screenshots/")