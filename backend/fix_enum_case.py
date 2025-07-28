#!/usr/bin/env python3
"""Fix enum case mismatches in the database"""

from database import get_session
from sqlalchemy import text

def fix_enum_cases():
    """Update all enum values to lowercase in the database"""
    db = get_session()
    
    try:
        # Fix IdeaStatus enum values
        print("Fixing IdeaStatus enum values...")
        db.execute(text("UPDATE ideas SET status = LOWER(status) WHERE status != LOWER(status)"))
        
        # Fix PriorityLevel enum values  
        print("Fixing PriorityLevel enum values...")
        db.execute(text("UPDATE ideas SET priority = LOWER(priority) WHERE priority != LOWER(priority)"))
        
        # Fix IdeaSize enum values
        print("Fixing IdeaSize enum values...")
        db.execute(text("UPDATE ideas SET size = LOWER(size) WHERE size != LOWER(size)"))
        # Handle EXTRA_LARGE -> extra_large
        db.execute(text("UPDATE ideas SET size = 'extra_large' WHERE size = 'extra large' OR size = 'EXTRA LARGE'"))
        
        db.commit()
        print("✅ All enum values have been fixed to lowercase!")
        
        # Verify the fix
        result = db.execute(text("SELECT COUNT(*) FROM ideas WHERE status != LOWER(status) OR priority != LOWER(priority) OR size != LOWER(size)"))
        count = result.scalar()
        print(f"Ideas with uppercase enums remaining: {count}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_enum_cases()