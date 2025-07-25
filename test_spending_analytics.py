#!/usr/bin/env python
"""Test script for spending analytics functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import get_session
from models import Idea, Bounty, IdeaStatus, PriorityLevel, IdeaSize, Team
import uuid as uuid_lib
from datetime import datetime, timedelta
import random

def create_test_bounties():
    """Create test bounties for spending analytics."""
    db = get_session()
    
    try:
        # Get all ideas
        ideas = db.query(Idea).all()
        teams = db.query(Team).filter(Team.is_approved == True).all()
        
        if not ideas:
            print("No ideas found in database. Please run database initialization first.")
            return
        
        if not teams:
            print("No teams found in database. Please run database initialization first.")
            return
        
        print(f"Found {len(ideas)} ideas and {len(teams)} teams")
        
        # Create bounties for random ideas
        created_count = 0
        for idea in random.sample(ideas, min(20, len(ideas))):
            # Check if bounty already exists
            existing_bounty = db.query(Bounty).filter(Bounty.idea_uuid == idea.uuid).first()
            if existing_bounty:
                continue
            
            # Create monetary bounty
            is_monetary = random.choice([True, True, False])  # 2/3 chance of monetary
            is_expensed = is_monetary and random.choice([True, True, False])  # 2/3 chance if monetary
            
            if is_expensed:
                # Generate amount based on idea size
                if idea.size == IdeaSize.small:
                    amount = random.randint(100, 500)
                elif idea.size == IdeaSize.medium:
                    amount = random.randint(500, 2000)
                elif idea.size == IdeaSize.large:
                    amount = random.randint(2000, 5000)
                else:  # extra_large
                    amount = random.randint(5000, 10000)
                
                # Determine if requires approval (over $50)
                requires_approval = amount > 50
                
                # Random approval status
                if requires_approval:
                    is_approved = random.choice([True, True, False, None])  # Some approved, some pending
                else:
                    is_approved = True
                
                bounty = Bounty(
                    uuid=str(uuid_lib.uuid4()),
                    idea_uuid=idea.uuid,
                    is_monetary=is_monetary,
                    is_expensed=is_expensed,
                    amount=float(amount),
                    requires_approval=requires_approval,
                    is_approved=is_approved,
                    approved_by='admin@company.com' if is_approved == True else None,
                    approved_at=datetime.utcnow() if is_approved == True else None
                )
            else:
                # Non-monetary bounty
                bounty = Bounty(
                    uuid=str(uuid_lib.uuid4()),
                    idea_uuid=idea.uuid,
                    is_monetary=False,
                    is_expensed=False,
                    amount=0.0,
                    requires_approval=False,
                    is_approved=None
                )
            
            db.add(bounty)
            created_count += 1
            
            # Also update the idea's date to create monthly trend
            if is_expensed and is_approved:
                # Spread ideas across last 6 months
                months_ago = random.randint(0, 5)
                idea.date_submitted = datetime.utcnow() - timedelta(days=months_ago * 30 + random.randint(0, 29))
        
        db.commit()
        print(f"Created {created_count} test bounties")
        
        # Show spending summary
        print("\nSpending Analytics Summary:")
        print("-" * 50)
        
        # Total approved spend
        total_approved = db.query(func.sum(Bounty.amount)).filter(
            Bounty.is_monetary == True,
            Bounty.is_expensed == True,
            Bounty.is_approved == True
        ).scalar() or 0.0
        print(f"Total Approved Spend: ${total_approved:,.2f}")
        
        # Pending approval
        pending_approval = db.query(func.sum(Bounty.amount)).filter(
            Bounty.is_monetary == True,
            Bounty.is_expensed == True,
            Bounty.requires_approval == True,
            Bounty.is_approved == None
        ).scalar() or 0.0
        print(f"Pending Approval: ${pending_approval:,.2f}")
        
        # By team
        print("\nSpending by Team:")
        from sqlalchemy import func
        team_spending = db.query(
            Idea.benefactor_team,
            func.sum(Bounty.amount).label('total')
        ).join(
            Bounty, Idea.uuid == Bounty.idea_uuid
        ).filter(
            Bounty.is_monetary == True,
            Bounty.is_expensed == True,
            Bounty.is_approved == True
        ).group_by(Idea.benefactor_team).order_by(func.sum(Bounty.amount).desc()).all()
        
        for team, total in team_spending[:5]:
            print(f"  {team}: ${total:,.2f}")
        
    except Exception as e:
        print(f"Error creating test bounties: {e}")
        db.rollback()
    finally:
        db.close()

def test_api_endpoints():
    """Test the API endpoints for spending analytics."""
    import requests
    
    print("\n\nTesting API Endpoints:")
    print("-" * 50)
    
    # Test stats endpoint
    try:
        response = requests.get('http://localhost:9094/api/stats')
        if response.status_code == 200:
            data = response.json()
            if 'spending' in data:
                print("✓ /api/stats includes spending data")
                print(f"  Total Approved: ${data['spending']['total_approved_spend']:,.2f}")
                print(f"  Pending: ${data['spending']['pending_approval_spend']:,.2f}")
                print(f"  Top Teams: {len(data['spending']['top_spending_teams'])} teams")
            else:
                print("✗ /api/stats missing spending data")
        else:
            print(f"✗ /api/stats returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing /api/stats: {e}")
    
    # Test team stats endpoint (requires auth)
    print("\nNote: Team stats endpoints require authentication to test fully")

if __name__ == '__main__':
    from sqlalchemy import func
    
    print("Testing Spending Analytics Implementation")
    print("=" * 50)
    
    # Create test data
    create_test_bounties()
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n\nTesting Complete!")
    print("You can now:")
    print("1. Visit the Admin Dashboard to see organization-wide spending analytics")
    print("2. Visit My Team page (as a manager) to see team-specific spending analytics")