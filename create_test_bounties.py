#!/usr/bin/env python
"""Create test bounties directly in the database."""

import os
import sys
os.chdir('backend')
sys.path.insert(0, os.getcwd())

from database import get_session
from models import Idea, Bounty, IdeaStatus
import uuid as uuid_lib
from datetime import datetime, timedelta
import random

def create_test_bounties():
    db = get_session()
    
    try:
        # Get some ideas
        ideas = db.query(Idea).limit(10).all()
        
        if not ideas:
            print("No ideas found!")
            return
            
        print(f"Found {len(ideas)} ideas to add bounties to")
        
        created = 0
        for idea in ideas:
            # Check if bounty exists
            existing = db.query(Bounty).filter(Bounty.idea_uuid == idea.uuid).first()
            if existing:
                print(f"Bounty already exists for idea: {idea.title}")
                continue
            
            # Create a bounty
            amount = random.choice([500, 1000, 2000, 5000])
            bounty = Bounty(
                uuid=str(uuid_lib.uuid4()),
                idea_uuid=idea.uuid,
                is_monetary=True,
                is_expensed=True,
                amount=float(amount),
                requires_approval=amount > 50,
                is_approved=True,
                approved_by='admin@company.com',
                approved_at=datetime.utcnow()
            )
            
            db.add(bounty)
            created += 1
            print(f"Created bounty of ${amount} for: {idea.title}")
        
        db.commit()
        print(f"\nCreated {created} bounties successfully!")
        
        # Verify spending totals
        from sqlalchemy import func
        total = db.query(func.sum(Bounty.amount)).filter(
            Bounty.is_monetary == True,
            Bounty.is_expensed == True,
            Bounty.is_approved == True
        ).scalar() or 0.0
        
        print(f"\nTotal approved spend in database: ${total:,.2f}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_test_bounties()