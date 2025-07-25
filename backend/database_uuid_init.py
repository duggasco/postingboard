#!/usr/bin/env python3
"""
Initialize database with UUID-only schema and test data.
No integer IDs anywhere.
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the UUID-only models
from models import (
    Base, Idea, Skill, Claim, Team, UserProfile, IdeaStatus, 
    PriorityLevel, IdeaSize, SubStatus, Notification, Bounty,
    StatusHistory, IdeaComment, IdeaExternalLink, IdeaActivity,
    ActivityType, ExternalLinkType
)

def init_database():
    """Initialize database with UUID-only schema."""
    # Create database
    db_path = 'posting_board_uuid.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    print(f"Created new database with UUID-only schema: {db_path}")
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create predefined teams
    teams = [
        Team(name='Cash - GPP', is_approved=True),
        Team(name='COO - IDA', is_approved=True),
        Team(name='COO - Business Management', is_approved=True),
        Team(name='SL - QAT', is_approved=True),
        Team(name='SL - Trading', is_approved=True),
        Team(name='SL - Product', is_approved=True),
        Team(name='SL - Clients', is_approved=True),
        Team(name='SL - Tech', is_approved=True),
        Team(name='Cash - PMG', is_approved=True),
        Team(name='Cash - US Product Strategy', is_approved=True),
        Team(name='Cash - EMEA Product Strategy', is_approved=True),
        Team(name='Cash - Sales', is_approved=True),
        Team(name='Cash - CMX', is_approved=True),
    ]
    
    for team in teams:
        session.add(team)
    
    # Create skills
    skills = [
        Skill(name='SQL/Databases'),
        Skill(name='Frontend/UI - Tableau'),
        Skill(name='Frontend/UI - Streamlit'),
        Skill(name='Frontend/UI - Web'),
        Skill(name='Frontend/UI - PowerBI'),
        Skill(name='Python'),
        Skill(name='Java'),
        Skill(name='Platform'),
        Skill(name='Regulatory'),
    ]
    
    for skill in skills:
        session.add(skill)
    
    session.commit()
    print(f"Created {len(teams)} teams and {len(skills)} skills")
    
    # Create test users
    users = [
        UserProfile(
            email='admin@company.com',
            name='Admin User',
            team_uuid=teams[0].uuid,
            role='manager',
            is_verified=True,
            managed_team_uuid=teams[0].uuid
        ),
        UserProfile(
            email='manager1@company.com',
            name='Sarah Manager',
            team_uuid=teams[1].uuid,
            role='manager',
            is_verified=True,
            managed_team_uuid=teams[1].uuid
        ),
        UserProfile(
            email='developer1@company.com',
            name='John Developer',
            team_uuid=teams[1].uuid,
            role='developer',
            is_verified=True
        ),
        UserProfile(
            email='developer2@company.com',
            name='Jane Developer',
            team_uuid=teams[2].uuid,
            role='developer',
            is_verified=True
        ),
        UserProfile(
            email='citizen1@company.com',
            name='Bob Citizen',
            team_uuid=teams[3].uuid,
            role='citizen_developer',
            is_verified=True
        ),
        UserProfile(
            email='submitter1@company.com',
            name='Alice Submitter',
            team_uuid=teams[4].uuid,
            role='idea_submitter',
            is_verified=True
        ),
    ]
    
    # Add skills to developers
    users[2].skills.extend([skills[0], skills[5], skills[6]])  # John: SQL, Python, Java
    users[3].skills.extend([skills[2], skills[5]])  # Jane: Streamlit, Python
    users[4].skills.extend([skills[1], skills[3]])  # Bob: Tableau, Web
    
    for user in users:
        session.add(user)
    
    session.commit()
    print(f"Created {len(users)} users")
    
    # Create test ideas
    ideas = [
        Idea(
            title='Automated Report Generation System',
            description='Build a system that automatically generates daily trading reports from multiple data sources. Should include data validation and error handling.',
            email='submitter1@company.com',
            benefactor_team=teams[4].name,
            size=IdeaSize.large,
            bounty='Recognition in quarterly meeting + learning opportunity',
            needed_by=datetime.now() + timedelta(days=60),
            priority=PriorityLevel.high,
            status=IdeaStatus.open,
            date_submitted=datetime.now() - timedelta(days=10)
        ),
        Idea(
            title='Dashboard for Risk Metrics',
            description='Create an interactive dashboard using Tableau to visualize risk metrics in real-time. Should connect to existing data warehouse.',
            email='manager1@company.com',
            benefactor_team=teams[1].name,
            size=IdeaSize.medium,
            bounty='Team lunch + recommendation letter',
            needed_by=datetime.now() + timedelta(days=30),
            priority=PriorityLevel.medium,
            status=IdeaStatus.claimed,
            sub_status=SubStatus.in_development,
            sub_status_updated_at=datetime.now() - timedelta(days=2),
            sub_status_updated_by='developer1@company.com',
            progress_percentage=35,
            date_submitted=datetime.now() - timedelta(days=15)
        ),
        Idea(
            title='Email Alert System Enhancement',
            description='Enhance the existing email alert system to include customizable thresholds and better formatting. Add support for attachments.',
            email='developer2@company.com',
            benefactor_team=teams[2].name,
            size=IdeaSize.small,
            bounty='Public recognition',
            needed_by=datetime.now() + timedelta(days=14),
            priority=PriorityLevel.low,
            status=IdeaStatus.complete,
            sub_status=SubStatus.verified,
            progress_percentage=100,
            date_submitted=datetime.now() - timedelta(days=20)
        ),
        Idea(
            title='Data Quality Monitoring Tool',
            description='Develop a tool to monitor data quality across all trading systems. Should flag anomalies and generate quality scores.',
            email='admin@company.com',
            benefactor_team=teams[0].name,
            size=IdeaSize.extra_large,
            bounty='Bonus consideration + conference attendance',
            needed_by=datetime.now() + timedelta(days=90),
            priority=PriorityLevel.high,
            status=IdeaStatus.open,
            date_submitted=datetime.now() - timedelta(days=5)
        ),
        Idea(
            title='Mobile App for Trade Approvals',
            description='Create a mobile application that allows managers to approve trades on the go. Must have secure authentication.',
            email='citizen1@company.com',
            benefactor_team=teams[3].name,
            size=IdeaSize.large,
            bounty='Team outing sponsorship',
            needed_by=datetime.now() + timedelta(days=45),
            priority=PriorityLevel.medium,
            status=IdeaStatus.open,
            date_submitted=datetime.now() - timedelta(days=3)
        ),
    ]
    
    # Add skills to ideas
    ideas[0].skills.extend([skills[0], skills[5]])  # SQL, Python
    ideas[1].skills.extend([skills[1], skills[0]])  # Tableau, SQL
    ideas[2].skills.extend([skills[5]])  # Python
    ideas[3].skills.extend([skills[0], skills[5], skills[6]])  # SQL, Python, Java
    ideas[4].skills.extend([skills[3], skills[6], skills[7]])  # Web, Java, Platform
    
    for idea in ideas:
        session.add(idea)
    
    session.commit()
    print(f"Created {len(ideas)} ideas")
    
    # Create monetary bounty for one idea
    bounty = Bounty(
        idea_uuid=ideas[3].uuid,
        is_monetary=True,
        is_expensed=True,
        amount=75.0,
        requires_approval=True,
        is_approved=None  # Pending approval
    )
    session.add(bounty)
    
    # Create claims
    claim1 = Claim(
        idea_uuid=ideas[1].uuid,
        claimer_email='developer1@company.com',
        claim_date=datetime.now() - timedelta(days=5)
    )
    
    claim2 = Claim(
        idea_uuid=ideas[2].uuid,
        claimer_email='developer2@company.com',
        claim_date=datetime.now() - timedelta(days=18)
    )
    
    session.add(claim1)
    session.add(claim2)
    
    # Create status history
    history1 = StatusHistory(
        idea_uuid=ideas[1].uuid,
        from_status=IdeaStatus.open,
        to_status=IdeaStatus.claimed,
        to_sub_status=SubStatus.planning,
        changed_by='developer1@company.com',
        changed_at=datetime.now() - timedelta(days=5),
        comment='Starting work on this dashboard'
    )
    
    history2 = StatusHistory(
        idea_uuid=ideas[1].uuid,
        from_sub_status=SubStatus.planning,
        to_sub_status=SubStatus.in_development,
        changed_by='developer1@company.com',
        changed_at=datetime.now() - timedelta(days=2),
        comment='Planning complete, starting development',
        duration_minutes=4320  # 3 days
    )
    
    session.add(history1)
    session.add(history2)
    
    # Create comments
    comment1 = IdeaComment(
        idea_uuid=ideas[1].uuid,
        author_email='manager1@company.com',
        author_name='Sarah Manager',
        content='Please make sure to include YTD metrics in the dashboard.',
        created_at=datetime.now() - timedelta(days=4),
        sub_status=SubStatus.planning
    )
    
    comment2 = IdeaComment(
        idea_uuid=ideas[1].uuid,
        author_email='developer1@company.com',
        author_name='John Developer',
        content='Will do! I\'m also planning to add drill-down capabilities.',
        created_at=datetime.now() - timedelta(days=3),
        sub_status=SubStatus.planning
    )
    
    session.add(comment1)
    session.add(comment2)
    
    # Create external links
    link1 = IdeaExternalLink(
        idea_uuid=ideas[1].uuid,
        link_type=ExternalLinkType.repository,
        title='Dashboard Repository',
        url='https://github.com/company/risk-dashboard',
        description='Main repository for the risk metrics dashboard',
        sub_status=SubStatus.in_development,
        created_by='developer1@company.com'
    )
    
    session.add(link1)
    
    # Create activities
    activities = [
        IdeaActivity(
            idea_uuid=ideas[1].uuid,
            activity_type=ActivityType.claimed,
            actor_email='developer1@company.com',
            actor_name='John Developer',
            description='Claimed the idea',
            created_at=datetime.now() - timedelta(days=5)
        ),
        IdeaActivity(
            idea_uuid=ideas[1].uuid,
            activity_type=ActivityType.status_changed,
            actor_email='developer1@company.com',
            actor_name='John Developer',
            description='Changed status to In Development',
            activity_data='{"from": "planning", "to": "in_development"}',
            created_at=datetime.now() - timedelta(days=2)
        ),
        IdeaActivity(
            idea_uuid=ideas[1].uuid,
            activity_type=ActivityType.comment_added,
            actor_email='manager1@company.com',
            actor_name='Sarah Manager',
            description='Added a comment',
            created_at=datetime.now() - timedelta(days=4)
        ),
    ]
    
    for activity in activities:
        session.add(activity)
    
    # Create notifications
    notifications = [
        Notification(
            user_email='admin@company.com',
            type='bounty_approval',
            title='Bounty Approval Required',
            message='$75.00 bounty requested for idea: Data Quality Monitoring Tool',
            idea_uuid=ideas[3].uuid,
            related_user_email='admin@company.com',
            created_at=datetime.now() - timedelta(hours=2)
        ),
        Notification(
            user_email='manager1@company.com',
            type='status_change',
            title='Status Updated',
            message='Dashboard for Risk Metrics is now In Development',
            idea_uuid=ideas[1].uuid,
            related_user_email='developer1@company.com',
            is_read=True,
            created_at=datetime.now() - timedelta(days=2),
            read_at=datetime.now() - timedelta(days=1)
        ),
    ]
    
    for notification in notifications:
        session.add(notification)
    
    session.commit()
    print("Created test data: claims, history, comments, links, activities, notifications")
    
    # Summary
    print("\n=== Database Initialization Complete ===")
    print(f"Database: {db_path}")
    print(f"Teams: {len(teams)}")
    print(f"Skills: {len(skills)}")
    print(f"Users: {len(users)}")
    print(f"Ideas: {len(ideas)}")
    print("\nAll data uses UUIDs exclusively - no integer IDs!")
    
    session.close()

if __name__ == '__main__':
    init_database()