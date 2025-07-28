#!/usr/bin/env python3
"""
Create a test user with ideas for documentation screenshots
"""

import subprocess
import random
import uuid

test_email = "john.developer@example.com"
test_name = "John Developer"
manager_email = "sarah.manager@example.com"
manager_name = "Sarah Manager"

# Create SQL script to insert test users and ideas
sql_script = f"""
-- Create teams if they don't exist
INSERT OR IGNORE INTO teams (uuid, name, is_approved, created_at)
VALUES 
    (lower(hex(randomblob(16))), 'Cash - GPP', 1, datetime('now')),
    (lower(hex(randomblob(16))), 'SL - Tech', 1, datetime('now'));

-- Create skills if they don't exist
INSERT OR IGNORE INTO skills (uuid, name, created_at)
VALUES 
    (lower(hex(randomblob(16))), 'Python', datetime('now')),
    (lower(hex(randomblob(16))), 'JavaScript', datetime('now')),
    (lower(hex(randomblob(16))), 'React', datetime('now')),
    (lower(hex(randomblob(16))), 'SQL', datetime('now')),
    (lower(hex(randomblob(16))), 'Data Analytics', datetime('now')),
    (lower(hex(randomblob(16))), 'Docker', datetime('now')),
    (lower(hex(randomblob(16))), 'Testing', datetime('now'));

-- Create test developer user
INSERT OR REPLACE INTO user_profiles (email, name, is_verified, role, team_uuid, created_at, updated_at)
SELECT 
    '{test_email}',
    '{test_name}',
    1,
    'developer',
    t.uuid,
    datetime('now'),
    datetime('now')
FROM teams t WHERE t.name = 'Cash - GPP' LIMIT 1;

-- Create test manager user
INSERT OR REPLACE INTO user_profiles (email, name, is_verified, role, team_uuid, managed_team_uuid, created_at, updated_at)
SELECT 
    '{manager_email}',
    '{manager_name}',
    1,
    'manager',
    t.uuid,
    t.uuid,  -- Managing the same team
    datetime('now'),
    datetime('now')
FROM teams t WHERE t.name = 'SL - Tech' LIMIT 1;

-- Add skills to users
INSERT OR IGNORE INTO user_skills (user_email, skill_uuid)
SELECT '{test_email}', s.uuid
FROM skills s 
WHERE s.name IN ('Python', 'JavaScript', 'React', 'SQL', 'Docker');

INSERT OR IGNORE INTO user_skills (user_email, skill_uuid)
SELECT '{manager_email}', s.uuid
FROM skills s 
WHERE s.name IN ('Python', 'Data Analytics', 'SQL');

-- Create some ideas submitted by the developer
INSERT OR REPLACE INTO ideas (
    uuid, title, description, email, benefactor_team_uuid, 
    priority, size, status, bounty, created_at, needed_by
)
SELECT
    lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + (abs(random()) % 4), 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))),
    'Automated Testing Framework',
    'Develop a comprehensive automated testing framework to improve code quality and reduce manual testing effort. This will include unit tests, integration tests, and end-to-end testing capabilities.',
    '{test_email}',
    t.uuid,
    'high',
    'large',
    'open',
    'Extra PTO day and team recognition',
    datetime('now', '-5 days'),
    date('now', '+30 days')
FROM teams t WHERE t.name = 'Cash - GPP' LIMIT 1;

INSERT OR REPLACE INTO ideas (
    uuid, title, description, email, benefactor_team_uuid, 
    priority, size, status, bounty, created_at, needed_by
)
SELECT
    lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + (abs(random()) % 4), 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))),
    'Real-time Dashboard Implementation',
    'Create a real-time monitoring dashboard that displays key metrics and system health indicators. Should update automatically without page refresh.',
    '{test_email}',
    t.uuid,
    'medium',
    'medium',
    'claimed',
    'Conference attendance sponsorship',
    datetime('now', '-3 days'),
    date('now', '+14 days')
FROM teams t WHERE t.name = 'Cash - GPP' LIMIT 1;

-- Create an idea submitted by another user that our developer claimed
INSERT OR REPLACE INTO ideas (
    uuid, title, description, email, benefactor_team_uuid, 
    priority, size, status, bounty, created_at, needed_by
)
SELECT
    lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + (abs(random()) % 4), 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))),
    'API Documentation Generator',
    'Build an automated tool that generates API documentation from code comments and endpoint definitions. Should support multiple output formats.',
    'other.user@example.com',
    t.uuid,
    'medium',
    'small',
    'claimed',
    'Team lunch and recognition',
    datetime('now', '-7 days'),
    date('now', '+21 days')
FROM teams t WHERE t.name = 'SL - Tech' LIMIT 1;

-- Create the claim for the last idea
INSERT OR REPLACE INTO claims (idea_uuid, claimer_email, claimed_at)
SELECT i.uuid, '{test_email}', datetime('now', '-2 days')
FROM ideas i 
WHERE i.title = 'API Documentation Generator'
LIMIT 1;

-- Add a monetary bounty to one idea
INSERT OR REPLACE INTO bounties (idea_uuid, is_monetary, is_expensed, amount, is_approved, requires_approval)
SELECT i.uuid, 1, 1, 250.00, 1, 0
FROM ideas i 
WHERE i.title = 'Real-time Dashboard Implementation'
LIMIT 1;

-- Create some ideas for the manager's team
INSERT OR REPLACE INTO ideas (
    uuid, title, description, email, benefactor_team_uuid, 
    priority, size, status, bounty, created_at, needed_by
)
SELECT
    lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + (abs(random()) % 4), 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))),
    'Performance Optimization Initiative',
    'Analyze and optimize application performance, focusing on database queries and API response times. Target 50% improvement in key metrics.',
    'team.member@example.com',
    t.uuid,
    'high',
    'large',
    'open',
    'Bonus consideration',
    datetime('now', '-1 days'),
    date('now', '+45 days')
FROM teams t WHERE t.name = 'SL - Tech' LIMIT 1;

-- Verify the data was created
SELECT 'Test users created:' as info;
SELECT email, name, role FROM user_profiles WHERE email IN ('{test_email}', '{manager_email}');

SELECT '\\nIdeas created:' as info;
SELECT title, email, status FROM ideas WHERE email = '{test_email}' OR benefactor_team_uuid IN (SELECT uuid FROM teams WHERE name IN ('Cash - GPP', 'SL - Tech'));
"""

# Execute the SQL script
print("Creating test users and ideas...")
print("="*60)

result = subprocess.run(
    ["docker", "exec", "postingboard-flask-app-1", "sqlite3", "/app/backend/data/posting_board_uuid.db"],
    input=sql_script,
    text=True,
    capture_output=True
)

if result.returncode == 0:
    print("✓ Test data created successfully")
    print(result.stdout)
    print(f"\nTest Developer: {test_email}")
    print(f"Test Manager: {manager_email}")
else:
    print("Error creating test data:")
    print(result.stderr)