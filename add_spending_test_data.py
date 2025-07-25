#!/usr/bin/env python
"""Add comprehensive test data for spending analytics."""

import os
import sys
# In container, we're already in the app directory
if os.path.exists('backend'):
    os.chdir('backend')
sys.path.insert(0, os.getcwd())

from database import get_session
from models import Idea, Bounty, IdeaStatus, PriorityLevel, IdeaSize, Team, Claim, UserProfile
import uuid as uuid_lib
from datetime import datetime, timedelta
import random

def add_spending_test_data():
    db = get_session()
    
    try:
        print("Adding comprehensive test data for spending analytics...")
        print("=" * 60)
        
        # Get all ideas and teams
        ideas = db.query(Idea).all()
        teams = db.query(Team).filter(Team.is_approved == True).all()
        users = db.query(UserProfile).filter(UserProfile.role.in_(['developer', 'citizen_developer'])).all()
        
        if not ideas or not teams or not users:
            print("ERROR: Missing required data. Please run database initialization first.")
            return
        
        print(f"Found: {len(ideas)} ideas, {len(teams)} teams, {len(users)} developers")
        
        # Delete existing bounties for clean test
        existing_bounties = db.query(Bounty).count()
        if existing_bounties > 0:
            print(f"Removing {existing_bounties} existing bounties...")
            db.query(Bounty).delete()
            db.commit()
        
        created_bounties = []
        
        # 1. Create bounties for all existing ideas
        for idea in ideas:
            # Determine bounty amount based on size and priority
            base_amounts = {
                IdeaSize.small: [100, 250, 500],
                IdeaSize.medium: [500, 1000, 2000],
                IdeaSize.large: [2000, 3500, 5000],
                IdeaSize.extra_large: [5000, 7500, 10000]
            }
            
            priority_multiplier = {
                PriorityLevel.low: 0.8,
                PriorityLevel.medium: 1.0,
                PriorityLevel.high: 1.5
            }
            
            # Get base amount for size
            base_amount = random.choice(base_amounts.get(idea.size, [1000]))
            
            # Apply priority multiplier
            amount = int(base_amount * priority_multiplier.get(idea.priority, 1.0))
            
            # 80% chance of monetary bounty
            is_monetary = random.random() < 0.8
            
            if is_monetary:
                # 90% chance of being expensed if monetary
                is_expensed = random.random() < 0.9
                
                if is_expensed:
                    requires_approval = amount > 50  # Everything over $50 needs approval
                    
                    # Approval status based on amount and status
                    if idea.status == IdeaStatus.complete:
                        is_approved = True  # Completed ideas should be approved
                    elif idea.status == IdeaStatus.claimed:
                        is_approved = True if random.random() < 0.8 else None  # 80% approved
                    else:  # open
                        is_approved = True if random.random() < 0.5 else None  # 50% approved
                    
                    bounty = Bounty(
                        uuid=str(uuid_lib.uuid4()),
                        idea_uuid=idea.uuid,
                        is_monetary=True,
                        is_expensed=True,
                        amount=float(amount),
                        requires_approval=requires_approval,
                        is_approved=is_approved,
                        approved_by='admin@company.com' if is_approved == True else None,
                        approved_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)) if is_approved == True else None
                    )
                else:
                    # Monetary but not expensed
                    bounty = Bounty(
                        uuid=str(uuid_lib.uuid4()),
                        idea_uuid=idea.uuid,
                        is_monetary=True,
                        is_expensed=False,
                        amount=0.0,
                        requires_approval=False,
                        is_approved=None
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
            created_bounties.append(bounty)
        
        # 2. Create additional ideas with varied dates for trend analysis
        print("\nCreating additional ideas for trend analysis...")
        
        # Create 30 more ideas spread across the last 6 months
        for month_ago in range(6):
            for _ in range(5):  # 5 ideas per month
                # Random team
                team = random.choice(teams)
                
                # Create idea
                idea_date = datetime.utcnow() - timedelta(days=month_ago * 30 + random.randint(0, 29))
                idea_size = random.choice(list(IdeaSize))
                idea_priority = random.choice(list(PriorityLevel))
                
                idea = Idea(
                    uuid=str(uuid_lib.uuid4()),
                    title=f"Test Idea - {idea_date.strftime('%B')} - {team.name[:10]}",
                    description=f"Test idea created for spending analytics in {idea_date.strftime('%B %Y')}",
                    email=random.choice(['manager1@company.com', 'developer1@company.com', 'admin@company.com']),
                    benefactor_team=team.name,
                    size=idea_size,
                    bounty=f"Test bounty for {idea_date.strftime('%B')}",
                    needed_by=datetime.utcnow() + timedelta(days=90),
                    priority=idea_priority,
                    status=random.choice([IdeaStatus.open, IdeaStatus.claimed, IdeaStatus.complete]),
                    date_submitted=idea_date
                )
                db.add(idea)
                db.flush()  # Get the UUID
                
                # Add claim if claimed or complete
                if idea.status in [IdeaStatus.claimed, IdeaStatus.complete]:
                    claimer = random.choice(users)
                    claim = Claim(
                        uuid=str(uuid_lib.uuid4()),
                        idea_uuid=idea.uuid,
                        claimer_email=claimer.email,
                        claim_date=idea_date + timedelta(days=random.randint(1, 10))
                    )
                    db.add(claim)
                
                # Create bounty with amount based on month (for trend visualization)
                base_amount = random.randint(500, 5000)
                # Add some variation by month
                month_multiplier = 1.0 + (0.1 * (5 - month_ago))  # Newer months have higher spending
                amount = int(base_amount * month_multiplier)
                
                bounty = Bounty(
                    uuid=str(uuid_lib.uuid4()),
                    idea_uuid=idea.uuid,
                    is_monetary=True,
                    is_expensed=True,
                    amount=float(amount),
                    requires_approval=amount > 50,
                    is_approved=True if idea.status == IdeaStatus.complete else (True if random.random() < 0.7 else None),
                    approved_by='admin@company.com' if idea.status == IdeaStatus.complete else None,
                    approved_at=idea_date + timedelta(days=random.randint(1, 5)) if idea.status == IdeaStatus.complete else None
                )
                db.add(bounty)
                created_bounties.append(bounty)
        
        # Commit all changes
        db.commit()
        
        print(f"\nCreated {len(created_bounties)} bounties")
        
        # 3. Show summary statistics
        print("\n" + "=" * 60)
        print("SPENDING ANALYTICS SUMMARY")
        print("=" * 60)
        
        # Total approved spend
        from sqlalchemy import func
        total_approved = db.query(func.sum(Bounty.amount)).filter(
            Bounty.is_monetary == True,
            Bounty.is_expensed == True,
            Bounty.is_approved == True
        ).scalar() or 0.0
        print(f"\nTotal Approved Spend: ${total_approved:,.2f}")
        
        # Pending approval
        pending_approval = db.query(func.sum(Bounty.amount)).filter(
            Bounty.is_monetary == True,
            Bounty.is_expensed == True,
            Bounty.requires_approval == True,
            Bounty.is_approved == None
        ).scalar() or 0.0
        print(f"Pending Approval: ${pending_approval:,.2f}")
        
        # Actual spend (completed)
        actual_spend = db.query(func.sum(Bounty.amount)).join(
            Idea, Bounty.idea_uuid == Idea.uuid
        ).filter(
            Idea.status == IdeaStatus.complete,
            Bounty.is_monetary == True,
            Bounty.is_expensed == True,
            Bounty.is_approved == True
        ).scalar() or 0.0
        print(f"Actual Spend (Completed): ${actual_spend:,.2f}")
        
        # Committed spend (claimed)
        committed_spend = db.query(func.sum(Bounty.amount)).join(
            Idea, Bounty.idea_uuid == Idea.uuid
        ).filter(
            Idea.status == IdeaStatus.claimed,
            Bounty.is_monetary == True,
            Bounty.is_expensed == True,
            Bounty.is_approved == True
        ).scalar() or 0.0
        print(f"Committed Spend (In Progress): ${committed_spend:,.2f}")
        
        # Top spending teams
        print("\nTop Spending Teams:")
        team_spending = db.query(
            Idea.benefactor_team,
            func.sum(Bounty.amount).label('total'),
            func.count(Bounty.uuid).label('count')
        ).join(
            Bounty, Idea.uuid == Bounty.idea_uuid
        ).filter(
            Bounty.is_monetary == True,
            Bounty.is_expensed == True,
            Bounty.is_approved == True
        ).group_by(Idea.benefactor_team).order_by(func.sum(Bounty.amount).desc()).limit(5).all()
        
        for i, (team, total, count) in enumerate(team_spending, 1):
            print(f"  {i}. {team}: ${total:,.2f} ({count} bounties)")
        
        # Monthly trend
        print("\nMonthly Spending Trend (Last 6 Months):")
        for i in range(5, -1, -1):
            start_date = datetime.utcnow().replace(day=1) - timedelta(days=i * 30)
            end_date = (start_date + timedelta(days=32)).replace(day=1)
            
            month_spend = db.query(func.sum(Bounty.amount)).join(
                Idea, Bounty.idea_uuid == Idea.uuid
            ).filter(
                Idea.date_submitted >= start_date,
                Idea.date_submitted < end_date,
                Bounty.is_monetary == True,
                Bounty.is_expensed == True,
                Bounty.is_approved == True
            ).scalar() or 0.0
            
            print(f"  {start_date.strftime('%B %Y')}: ${month_spend:,.2f}")
        
        # Spending by priority
        print("\nSpending by Priority:")
        priority_spending = db.query(
            Idea.priority,
            func.sum(Bounty.amount).label('total')
        ).join(
            Bounty, Idea.uuid == Bounty.idea_uuid
        ).filter(
            Bounty.is_monetary == True,
            Bounty.is_expensed == True,
            Bounty.is_approved == True
        ).group_by(Idea.priority).all()
        
        for priority, total in priority_spending:
            print(f"  {priority.value.capitalize()}: ${total:,.2f}")
        
        # Spending by size
        print("\nSpending by Size:")
        size_spending = db.query(
            Idea.size,
            func.sum(Bounty.amount).label('total')
        ).join(
            Bounty, Idea.uuid == Bounty.idea_uuid
        ).filter(
            Bounty.is_monetary == True,
            Bounty.is_expensed == True,
            Bounty.is_approved == True
        ).group_by(Idea.size).all()
        
        for size, total in size_spending:
            print(f"  {size.value.replace('_', ' ').title()}: ${total:,.2f}")
        
        print("\n" + "=" * 60)
        print("Test data created successfully!")
        print("You can now view the spending analytics in:")
        print("1. Admin Dashboard - Organization-wide spending overview")
        print("2. My Team page - Team-specific spending analytics (login as a manager)")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    add_spending_test_data()