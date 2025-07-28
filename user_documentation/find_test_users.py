#!/usr/bin/env python3
"""
Find test users with existing ideas for screenshot capture
"""

import subprocess

# SQL query to find users with ideas
sql_query = """
-- Find users with submitted ideas
SELECT 
    u.email,
    u.name,
    u.role,
    t.name as team_name,
    COUNT(DISTINCT i.uuid) as idea_count,
    COUNT(DISTINCT c.idea_uuid) as claimed_count
FROM user_profiles u
LEFT JOIN teams t ON u.team_uuid = t.uuid
LEFT JOIN ideas i ON u.email = i.email
LEFT JOIN claims c ON u.email = c.claimer_email
WHERE u.is_verified = 1
GROUP BY u.email
HAVING idea_count > 0 OR claimed_count > 0
ORDER BY idea_count DESC, claimed_count DESC
LIMIT 10;
"""

print("Finding test users with existing ideas...")
print("="*60)

result = subprocess.run(
    ["docker", "exec", "postingboard-flask-app-1", "sqlite3", "-header", "-column", "/app/backend/data/posting_board_uuid.db"],
    input=sql_query,
    text=True,
    capture_output=True
)

if result.returncode == 0:
    print(result.stdout)
else:
    print("Error querying database:")
    print(result.stderr)

# Also check for managers
print("\n\nFinding managers with teams...")
print("="*60)

manager_query = """
SELECT 
    u.email,
    u.name,
    u.role,
    t1.name as user_team,
    t2.name as managed_team
FROM user_profiles u
LEFT JOIN teams t1 ON u.team_uuid = t1.uuid
LEFT JOIN teams t2 ON u.managed_team_uuid = t2.uuid
WHERE u.role = 'manager' AND u.managed_team_uuid IS NOT NULL
LIMIT 5;
"""

result2 = subprocess.run(
    ["docker", "exec", "postingboard-flask-app-1", "sqlite3", "-header", "-column", "/app/backend/data/posting_board_uuid.db"],
    input=manager_query,
    text=True,
    capture_output=True
)

if result2.returncode == 0:
    print(result2.stdout)