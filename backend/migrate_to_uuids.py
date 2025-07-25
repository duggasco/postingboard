#!/usr/bin/env python3
"""
Migration script to add UUID columns to all tables and populate them.
This is Phase 1 of the UUID migration - adding UUIDs alongside integer IDs.
"""

import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import DATABASE_URL
import sys
import time

def add_uuid_columns(engine):
    """Add UUID columns to all tables."""
    tables = [
        'ideas', 'skills', 'teams', 'claims', 'user_profiles',
        'verification_codes', 'manager_requests', 'claim_approvals',
        'email_settings', 'notifications', 'bounties', 'status_history',
        'idea_comments', 'idea_external_links', 'idea_activities', 
        'idea_stage_data'
    ]
    
    with engine.connect() as conn:
        for table in tables:
            try:
                print(f"Adding UUID column to {table}...")
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN uuid VARCHAR(36)"))
                conn.commit()
                print(f"✓ Added UUID column to {table}")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"  UUID column already exists in {table}")
                else:
                    print(f"✗ Error adding UUID column to {table}: {e}")
                    conn.rollback()

def populate_uuids(engine):
    """Generate and populate UUIDs for all existing records."""
    tables = [
        'ideas', 'skills', 'teams', 'claims', 'user_profiles',
        'verification_codes', 'manager_requests', 'claim_approvals',
        'email_settings', 'notifications', 'bounties', 'status_history',
        'idea_comments', 'idea_external_links', 'idea_activities', 
        'idea_stage_data'
    ]
    
    with engine.connect() as conn:
        for table in tables:
            try:
                # Get records without UUIDs
                result = conn.execute(text(f"SELECT id FROM {table} WHERE uuid IS NULL"))
                records = result.fetchall()
                
                if records:
                    print(f"Populating UUIDs for {len(records)} records in {table}...")
                    
                    # Update each record with a new UUID
                    for record in records:
                        new_uuid = str(uuid.uuid4())
                        conn.execute(
                            text(f"UPDATE {table} SET uuid = :uuid WHERE id = :id"),
                            {"uuid": new_uuid, "id": record[0]}
                        )
                    
                    conn.commit()
                    print(f"✓ Updated {len(records)} records in {table}")
                else:
                    print(f"  No records to update in {table}")
                    
            except Exception as e:
                print(f"✗ Error populating UUIDs in {table}: {e}")
                conn.rollback()

def add_uuid_indexes(engine):
    """Add unique indexes on UUID columns."""
    tables = [
        'ideas', 'skills', 'teams', 'claims', 'user_profiles',
        'verification_codes', 'manager_requests', 'claim_approvals',
        'email_settings', 'notifications', 'bounties', 'status_history',
        'idea_comments', 'idea_external_links', 'idea_activities', 
        'idea_stage_data'
    ]
    
    with engine.connect() as conn:
        for table in tables:
            try:
                index_name = f"ix_{table}_uuid"
                print(f"Adding unique index on {table}.uuid...")
                conn.execute(text(f"CREATE UNIQUE INDEX {index_name} ON {table}(uuid)"))
                conn.commit()
                print(f"✓ Added unique index on {table}.uuid")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"  Index already exists on {table}.uuid")
                else:
                    print(f"✗ Error adding index on {table}.uuid: {e}")
                    conn.rollback()

def verify_migration(engine):
    """Verify that all tables have UUID columns with values."""
    tables = [
        'ideas', 'skills', 'teams', 'claims', 'user_profiles',
        'verification_codes', 'manager_requests', 'claim_approvals',
        'email_settings', 'notifications', 'bounties', 'status_history',
        'idea_comments', 'idea_external_links', 'idea_activities', 
        'idea_stage_data'
    ]
    
    print("\nVerifying migration...")
    all_good = True
    
    with engine.connect() as conn:
        for table in tables:
            try:
                # Check for NULL UUIDs
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table} WHERE uuid IS NULL"))
                null_count = result.scalar()
                
                # Check total count
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                total_count = result.scalar()
                
                if null_count > 0:
                    print(f"✗ {table}: {null_count}/{total_count} records missing UUIDs")
                    all_good = False
                else:
                    print(f"✓ {table}: All {total_count} records have UUIDs")
                    
            except Exception as e:
                print(f"✗ Error checking {table}: {e}")
                all_good = False
    
    return all_good

def main():
    """Run the UUID migration."""
    print("UUID Migration Script - Phase 1")
    print("==============================")
    print(f"Database: {DATABASE_URL}")
    print()
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Step 1: Add UUID columns
    print("Step 1: Adding UUID columns...")
    add_uuid_columns(engine)
    print()
    
    # Step 2: Populate UUIDs
    print("Step 2: Populating UUIDs...")
    populate_uuids(engine)
    print()
    
    # Step 3: Add indexes
    print("Step 3: Adding unique indexes...")
    add_uuid_indexes(engine)
    print()
    
    # Step 4: Verify
    if verify_migration(engine):
        print("\n✓ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update application code to use UUIDs")
        print("2. Test with dual ID support")
        print("3. Migrate foreign keys to use UUIDs")
    else:
        print("\n✗ Migration had errors. Please check and fix before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()