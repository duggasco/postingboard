#!/usr/bin/env python3
"""
Test script for UUID implementation with dual ID support.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/backend')

from database import get_session, DATABASE_URL
from models import Idea, Team, Skill, UserProfile
from uuid_utils import is_valid_uuid, get_by_identifier, ensure_uuid
import uuid

def test_uuid_generation():
    """Test that models generate UUIDs correctly."""
    print("Testing UUID generation...")
    db = get_session()
    
    try:
        # Create a test idea
        test_idea = Idea(
            title="Test UUID Idea",
            description="Testing UUID generation",
            email="test@example.com",
            benefactor_team="Test Team",
            size="small",
            priority="low",
            status="open"
        )
        
        # Check if UUID is generated
        print(f"  UUID before save: {test_idea.uuid}")
        
        db.add(test_idea)
        db.commit()
        
        print(f"  UUID after save: {test_idea.uuid}")
        print(f"  Integer ID: {test_idea.id}")
        
        # Verify UUID format
        if is_valid_uuid(test_idea.uuid):
            print("  ✓ Valid UUID format")
        else:
            print("  ✗ Invalid UUID format")
            
        # Clean up
        db.delete(test_idea)
        db.commit()
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

def test_dual_lookup():
    """Test looking up records by both UUID and integer ID."""
    print("\nTesting dual ID lookup...")
    db = get_session()
    
    try:
        # Get an existing idea
        idea = db.query(Idea).first()
        if not idea:
            print("  No ideas found to test")
            return
            
        print(f"  Test idea: {idea.title}")
        print(f"  Integer ID: {idea.id}")
        print(f"  UUID: {idea.uuid}")
        
        # Test integer ID lookup
        by_id = get_by_identifier(Idea, idea.id, db)
        if by_id and by_id.id == idea.id:
            print("  ✓ Integer ID lookup works")
        else:
            print("  ✗ Integer ID lookup failed")
            
        # Test UUID lookup
        if idea.uuid:
            by_uuid = get_by_identifier(Idea, idea.uuid, db)
            if by_uuid and by_uuid.id == idea.id:
                print("  ✓ UUID lookup works")
            else:
                print("  ✗ UUID lookup failed")
        else:
            print("  ! No UUID present - need to run migration")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
    finally:
        db.close()

def test_api_endpoints():
    """Test API endpoints with both ID types."""
    print("\nTesting API endpoints...")
    
    import requests
    base_url = "http://localhost:9094"
    
    try:
        # Get ideas list
        response = requests.get(f"{base_url}/api/ideas")
        if response.status_code == 200:
            ideas = response.json()
            if ideas and len(ideas) > 0:
                idea = ideas[0]
                print(f"  Sample idea: {idea.get('title')}")
                print(f"  Has UUID field: {'uuid' in idea}")
                print(f"  UUID value: {idea.get('uuid')}")
                
                # Test accessing idea by UUID
                if idea.get('uuid'):
                    response = requests.get(f"{base_url}/idea/{idea['uuid']}")
                    if response.status_code == 200:
                        print("  ✓ Can access idea page by UUID")
                    else:
                        print(f"  ✗ Failed to access by UUID: {response.status_code}")
                        
                # Test accessing idea by ID
                response = requests.get(f"{base_url}/idea/{idea['id']}")
                if response.status_code == 200:
                    print("  ✓ Can still access idea page by integer ID")
                else:
                    print(f"  ✗ Failed to access by ID: {response.status_code}")
                    
        else:
            print(f"  ✗ Failed to get ideas: {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Error testing endpoints: {e}")

def check_migration_status():
    """Check how many records have UUIDs."""
    print("\nChecking migration status...")
    db = get_session()
    
    try:
        tables = ['ideas', 'teams', 'skills', 'user_profiles']
        
        for table in tables:
            total = db.execute(f"SELECT COUNT(*) FROM {table}").scalar()
            with_uuid = db.execute(f"SELECT COUNT(*) FROM {table} WHERE uuid IS NOT NULL").scalar()
            without_uuid = db.execute(f"SELECT COUNT(*) FROM {table} WHERE uuid IS NULL").scalar()
            
            print(f"  {table}:")
            print(f"    Total: {total}")
            print(f"    With UUID: {with_uuid}")
            print(f"    Without UUID: {without_uuid}")
            
            if without_uuid > 0:
                print(f"    ! Need to run migration for {without_uuid} records")
                
    except Exception as e:
        print(f"  ✗ Error checking status: {e}")
    finally:
        db.close()

def main():
    print("UUID Implementation Test")
    print("========================")
    print(f"Database: {DATABASE_URL}")
    print()
    
    # Run tests
    check_migration_status()
    test_uuid_generation()
    test_dual_lookup()
    test_api_endpoints()
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()