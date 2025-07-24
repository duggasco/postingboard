#!/usr/bin/env python3
"""
Migration script to change urgency field to priority and update values.
Maps:
  - not_urgent -> low
  - urgent -> medium  
  - very_urgent -> high
"""

import sqlite3
import os
import sys

def migrate_database():
    db_path = os.path.join(os.path.dirname(__file__), 'posting_board.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start transaction
        conn.execute('BEGIN')
        
        # Check if urgency column exists
        cursor.execute("PRAGMA table_info(ideas)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'urgency' not in column_names:
            print("Urgency column not found. Migration may have already been run.")
            return False
            
        if 'priority' in column_names:
            print("Priority column already exists. Migration may have already been run.")
            return False
        
        # Create new priority column
        cursor.execute("ALTER TABLE ideas ADD COLUMN priority TEXT")
        
        # Map urgency values to priority values
        cursor.execute("""
            UPDATE ideas
            SET priority = CASE urgency
                WHEN 'NOT_URGENT' THEN 'low'
                WHEN 'URGENT' THEN 'medium'
                WHEN 'VERY_URGENT' THEN 'high'
                WHEN 'not_urgent' THEN 'low'
                WHEN 'urgent' THEN 'medium'
                WHEN 'very_urgent' THEN 'high'
                ELSE urgency
            END
        """)
        
        # Create a new temporary table with the correct schema
        cursor.execute("""
            CREATE TABLE ideas_new (
                id INTEGER PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                email VARCHAR(120) NOT NULL,
                benefactor_team VARCHAR(100) NOT NULL,
                size TEXT NOT NULL,
                bounty VARCHAR(200),
                needed_by DATETIME NOT NULL,
                priority TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                date_submitted DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Copy data from old table to new table (excluding urgency column)
        cursor.execute("""
            INSERT INTO ideas_new (id, title, description, email, benefactor_team, 
                                  size, bounty, needed_by, priority, status, date_submitted)
            SELECT id, title, description, email, benefactor_team, 
                   size, bounty, needed_by, priority, status, date_submitted
            FROM ideas
        """)
        
        # Drop the old table
        cursor.execute("DROP TABLE ideas")
        
        # Rename the new table to the original name
        cursor.execute("ALTER TABLE ideas_new RENAME TO ideas")
        
        # Commit the transaction
        conn.commit()
        print("Migration completed successfully!")
        
        # Display summary
        cursor.execute("SELECT priority, COUNT(*) FROM ideas GROUP BY priority")
        results = cursor.fetchall()
        print("\nPriority distribution after migration:")
        for priority, count in results:
            print(f"  {priority}: {count} ideas")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if migrate_database():
        sys.exit(0)
    else:
        sys.exit(1)