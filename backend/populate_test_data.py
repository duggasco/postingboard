#!/usr/bin/env python3
"""
Populate the database with comprehensive test data for UI testing.
This script creates users, teams, ideas, claims, and various workflow states.
"""

import uuid
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import (
    Base, Idea, Skill, Team, UserProfile, Claim, ClaimApproval,
    ManagerRequest, Notification, Bounty, StatusHistory, IdeaComment,
    IdeaExternalLink, IdeaActivity, IdeaStageData,
    IdeaStatus, SubStatus, PriorityLevel, IdeaSize, ActivityType, ExternalLinkType
)

# Database setup
engine = create_engine('sqlite:///posting_board_uuid.db')
Session = sessionmaker(bind=engine)
session = Session()

def create_uuid():
    """Generate a new UUID string"""
    return str(uuid.uuid4())

def create_teams():
    """Create predefined teams"""
    print("Creating teams...")
    teams = [
        "Cash - GPP",
        "COO - IDA", 
        "COO - Business Management",
        "SL - QAT",
        "SL - Trading",
        "SL - Product",
        "SL - Clients",
        "SL - Tech",
        "Cash - PMG",
        "Cash - US Product Strategy",
        "Cash - EMEA Product Strategy",
        "Cash - Sales",
        "Cash - CMX",
        "Engineering - Frontend",
        "Engineering - Backend",
        "Data Science",
        "DevOps"
    ]
    
    team_objects = {}
    for team_name in teams:
        team = Team(
            uuid=create_uuid(),
            name=team_name,
            is_approved=True
        )
        session.add(team)
        team_objects[team_name] = team
    
    # Add one unapproved team
    custom_team = Team(
        uuid=create_uuid(),
        name="Innovation Lab",
        is_approved=False
    )
    session.add(custom_team)
    team_objects["Innovation Lab"] = custom_team
    
    session.commit()
    return team_objects

def create_skills():
    """Create skills"""
    print("Creating skills...")
    skill_names = [
        "Python", "JavaScript", "React", "Node.js", "SQL", "MongoDB",
        "Docker", "Kubernetes", "AWS", "Azure", "Machine Learning",
        "Data Analysis", "API Development", "UI/UX Design", "Java",
        "C#", ".NET", "Angular", "Vue.js", "DevOps", "CI/CD",
        "Agile", "Scrum", "Git", "Testing", "Security"
    ]
    
    skill_objects = {}
    for skill_name in skill_names:
        skill = Skill(uuid=create_uuid(), name=skill_name)
        session.add(skill)
        skill_objects[skill_name] = skill
    
    session.commit()
    return skill_objects

def create_users(teams, skills):
    """Create various test users with different roles"""
    print("Creating users...")
    users = []
    
    # Create managers
    managers = [
        ("alice.manager@company.com", "Alice Manager", teams["SL - Tech"], ["Agile", "Scrum"]),
        ("bob.manager@company.com", "Bob Manager", teams["Engineering - Backend"], ["Python", "DevOps"]),
        ("carol.manager@company.com", "Carol Manager", teams["Data Science"], ["Machine Learning", "Python"]),
    ]
    
    for email, name, team, skill_names in managers:
        user = UserProfile(
            email=email,
            name=name,
            team_uuid=team.uuid,
            role="manager",
            is_verified=True,
            verified_at=datetime.utcnow() - timedelta(days=30),
            created_at=datetime.utcnow() - timedelta(days=30),
            managed_team_uuid=team.uuid
        )
        session.add(user)
        users.append(user)
        
        # Add skills
        for skill_name in skill_names:
            session.execute(
                text("INSERT INTO user_skills (user_email, skill_uuid) VALUES (:email, :skill_uuid)"),
                {"email": email, "skill_uuid": skills[skill_name].uuid}
            )
    
    # Create developers
    developers = [
        ("david.dev@company.com", "David Developer", teams["Engineering - Backend"], 
         ["Python", "Docker", "SQL", "API Development", "Git"]),
        ("emma.dev@company.com", "Emma Developer", teams["Engineering - Frontend"],
         ["JavaScript", "React", "Node.js", "UI/UX Design", "Git"]),
        ("frank.dev@company.com", "Frank Developer", teams["SL - Tech"],
         ["Java", "Kubernetes", "AWS", "Git"]),
        ("grace.dev@company.com", "Grace Developer", teams["Data Science"],
         ["Python", "Machine Learning", "SQL", "Data Analysis"]),
    ]
    
    for email, name, team, skill_names in developers:
        user = UserProfile(
            email=email,
            name=name,
            team_uuid=team.uuid,
            role="developer",
            is_verified=True,
            verified_at=datetime.utcnow() - timedelta(days=20),
            created_at=datetime.utcnow() - timedelta(days=20)
        )
        session.add(user)
        users.append(user)
        
        for skill_name in skill_names:
            session.execute(
                text("INSERT INTO user_skills (user_email, skill_uuid) VALUES (:email, :skill_uuid)"),
                {"email": email, "skill_uuid": skills[skill_name].uuid}
            )
    
    # Create citizen developers
    citizen_devs = [
        ("helen.citizen@company.com", "Helen Citizen", teams["Cash - Sales"],
         ["SQL", "Data Analysis"]),
        ("ivan.citizen@company.com", "Ivan Citizen", teams["COO - Business Management"],
         ["Python", "API Development"]),
    ]
    
    for email, name, team, skill_names in citizen_devs:
        user = UserProfile(
            email=email,
            name=name,
            team_uuid=team.uuid,
            role="citizen_developer",
            is_verified=True,
            verified_at=datetime.utcnow() - timedelta(days=15),
            created_at=datetime.utcnow() - timedelta(days=15)
        )
        session.add(user)
        users.append(user)
        
        for skill_name in skill_names:
            session.execute(
                text("INSERT INTO user_skills (user_email, skill_uuid) VALUES (:email, :skill_uuid)"),
                {"email": email, "skill_uuid": skills[skill_name].uuid}
            )
    
    # Create idea submitters
    submitters = [
        ("jane.submitter@company.com", "Jane Submitter", teams["Cash - PMG"]),
        ("kevin.submitter@company.com", "Kevin Submitter", teams["COO - IDA"]),
        ("lisa.submitter@company.com", "Lisa Submitter", teams["Cash - Sales"]),
    ]
    
    for email, name, team in submitters:
        user = UserProfile(
            email=email,
            name=name,
            team_uuid=team.uuid,
            role="idea_submitter",
            is_verified=True,
            verified_at=datetime.utcnow() - timedelta(days=10),
            created_at=datetime.utcnow() - timedelta(days=10)
        )
        session.add(user)
        users.append(user)
    
    # Create unverified user
    unverified = UserProfile(
        email="mike.new@company.com",
        name="Mike Newuser",
        team_uuid=teams["Engineering - Frontend"].uuid,
        role="developer",
        is_verified=False,
        created_at=datetime.utcnow()
    )
    session.add(unverified)
    
    # Create user with pending manager request
    pending_mgr = UserProfile(
        email="nancy.pending@company.com",
        name="Nancy Pending",
        team_uuid=teams["DevOps"].uuid,
        role="developer",
        is_verified=True,
        verified_at=datetime.utcnow() - timedelta(days=2),
        created_at=datetime.utcnow() - timedelta(days=2)
    )
    session.add(pending_mgr)
    
    # Add skills for Nancy
    for skill_name in ["Docker", "Kubernetes", "CI/CD", "AWS"]:
        session.execute(
            text("INSERT INTO user_skills (user_email, skill_uuid) VALUES (:email, :skill_uuid)"),
            {"email": pending_mgr.email, "skill_uuid": skills[skill_name].uuid}
        )
    
    session.commit()
    
    # Create manager request for Nancy
    mgr_request = ManagerRequest(
        uuid=create_uuid(),
        user_email=pending_mgr.email,
        requested_team_uuid=teams["DevOps"].uuid,
        status='pending',
        requested_at=datetime.utcnow() - timedelta(hours=5)
    )
    session.add(mgr_request)
    
    # Create notification for admin about manager request
    notification = Notification(
        uuid=create_uuid(),
        user_email="admin@system.local",
        type="manager_request",
        title="New Manager Request",
        message=f"{pending_mgr.name} has requested to manage {teams['DevOps'].name}",
        related_user_email=pending_mgr.email,
        is_read=False,
        created_at=datetime.utcnow() - timedelta(hours=5)
    )
    session.add(notification)
    
    session.commit()
    return users

def create_ideas(users, teams, skills):
    """Create ideas in various states"""
    print("Creating ideas...")
    ideas = []
    
    # Helper to get random skills
    def get_random_skills(count):
        return random.sample(list(skills.values()), min(count, len(skills)))
    
    # 1. Open ideas with no claims
    open_ideas = [
        {
            "title": "Automate Monthly Reporting Dashboard",
            "description": "Create an automated dashboard that pulls data from multiple sources and generates monthly reports for executive team. Currently this process takes 2 days of manual work each month.",
            "submitter": "jane.submitter@company.com",
            "team": "Cash - PMG",
            "skills": ["Python", "SQL", "Data Analysis"],
            "size": IdeaSize.medium,
            "priority": PriorityLevel.high,
            "bounty": "Extra day off after completion",
            "days_ago": 5
        },
        {
            "title": "Customer Feedback Analysis Tool",
            "description": "Build a tool to analyze customer feedback from various channels (email, chat, surveys) and categorize common issues using NLP.",
            "submitter": "kevin.submitter@company.com",
            "team": "COO - IDA",
            "skills": ["Python", "Machine Learning", "API Development"],
            "size": IdeaSize.large,
            "priority": PriorityLevel.medium,
            "bounty": "Recognition in company newsletter",
            "days_ago": 3
        },
        {
            "title": "Mobile App for Field Sales",
            "description": "Develop a mobile application for field sales team to access customer data, update opportunities, and sync with CRM offline.",
            "submitter": "lisa.submitter@company.com",
            "team": "Cash - Sales",
            "skills": ["React", "Node.js", "API Development"],
            "size": IdeaSize.extra_large,
            "priority": PriorityLevel.high,
            "bounty": "Team dinner celebration",
            "days_ago": 7,
            "is_monetary": True,
            "amount": 500
        },
        {
            "title": "Automated Testing Framework",
            "description": "Create a comprehensive automated testing framework for our web applications to reduce manual QA time.",
            "submitter": "alice.manager@company.com",
            "team": "SL - Tech",
            "skills": ["JavaScript", "Testing", "CI/CD"],
            "size": IdeaSize.medium,
            "priority": PriorityLevel.low,
            "bounty": "Flexible work hours for a month",
            "days_ago": 10
        },
        {
            "title": "Data Visualization Library",
            "description": "Build a reusable data visualization component library for consistent charts across all applications.",
            "submitter": "bob.manager@company.com",
            "team": "Engineering - Backend",
            "skills": ["JavaScript", "React"],
            "size": IdeaSize.small,
            "priority": PriorityLevel.medium,
            "bounty": "Conference attendance sponsorship",
            "days_ago": 1
        }
    ]
    
    for idea_data in open_ideas:
        idea_uuid = create_uuid()
        idea = Idea(
            uuid=idea_uuid,
            title=idea_data["title"],
            description=idea_data["description"],
            email=idea_data["submitter"],
            benefactor_team=idea_data["team"],
            size=idea_data["size"],
            bounty=idea_data["bounty"],
            needed_by=datetime.utcnow() + timedelta(days=30),
            priority=idea_data["priority"],
            status=IdeaStatus.open,
            date_submitted=datetime.utcnow() - timedelta(days=idea_data["days_ago"])
        )
        session.add(idea)
        
        # Add skills
        for skill_name in idea_data["skills"]:
            if skill_name in skills:
                session.execute(
                    text("INSERT INTO idea_skills (idea_uuid, skill_uuid) VALUES (:idea_uuid, :skill_uuid)"),
                    {"idea_uuid": idea_uuid, "skill_uuid": skills[skill_name].uuid}
                )
        
        # Add monetary bounty if specified
        if idea_data.get("is_monetary"):
            bounty = Bounty(
                uuid=create_uuid(),
                idea_uuid=idea_uuid,
                is_monetary=True,
                is_expensed=True,
                amount=idea_data.get("amount", 100),
                requires_approval=idea_data.get("amount", 100) > 50
            )
            session.add(bounty)
            
            # Create approval notification if needed
            if bounty.requires_approval:
                notif = Notification(
                    uuid=create_uuid(),
                    user_email="alice.manager@company.com",
                    type="bounty_approval",
                    title="Bounty Approval Required",
                    message=f"Idea '{idea.title}' has a ${bounty.amount} bounty requiring approval",
                    idea_uuid=idea_uuid,
                    is_read=False,
                    created_at=idea.date_submitted
                )
                session.add(notif)
        
        ideas.append(idea)
    
    # 2. Ideas with pending claim approvals
    pending_claims = [
        {
            "title": "Inventory Management System",
            "description": "Replace manual inventory tracking with automated system integrated with suppliers.",
            "submitter": "jane.submitter@company.com",
            "team": "Cash - PMG",
            "claimer": "david.dev@company.com",
            "skills": ["Python", "SQL", "API Development"],
            "size": IdeaSize.large,
            "priority": PriorityLevel.high,
            "days_ago": 8
        },
        {
            "title": "Employee Onboarding Portal",
            "description": "Create self-service portal for new employee onboarding with task tracking.",
            "submitter": "kevin.submitter@company.com",
            "team": "COO - IDA",
            "claimer": "emma.dev@company.com",
            "skills": ["React", "Node.js", "UI/UX Design"],
            "size": IdeaSize.medium,
            "priority": PriorityLevel.medium,
            "days_ago": 6
        }
    ]
    
    for claim_data in pending_claims:
        idea_uuid = create_uuid()
        idea = Idea(
            uuid=idea_uuid,
            title=claim_data["title"],
            description=claim_data["description"],
            email=claim_data["submitter"],
            benefactor_team=claim_data["team"],
            size=claim_data["size"],
            bounty="Public recognition and thank you",
            needed_by=datetime.utcnow() + timedelta(days=45),
            priority=claim_data["priority"],
            status=IdeaStatus.open,
            date_submitted=datetime.utcnow() - timedelta(days=claim_data["days_ago"])
        )
        session.add(idea)
        
        # Add skills
        for skill_name in claim_data["skills"]:
            if skill_name in skills:
                session.execute(
                    text("INSERT INTO idea_skills (idea_uuid, skill_uuid) VALUES (:idea_uuid, :skill_uuid)"),
                    {"idea_uuid": idea_uuid, "skill_uuid": skills[skill_name].uuid}
                )
        
        # Create claim approval
        claimer = session.query(UserProfile).filter_by(email=claim_data["claimer"]).first()
        claimer_team = session.query(Team).filter_by(uuid=claimer.team_uuid).first() if claimer.team_uuid else None
        approval = ClaimApproval(
            uuid=create_uuid(),
            idea_uuid=idea_uuid,
            claimer_email=claimer.email,
            claimer_name=claimer.name,
            claimer_team=claimer_team.name if claimer_team else None,
            claimer_skills=", ".join(claim_data["skills"]),
            status='pending',
            created_at=datetime.utcnow() - timedelta(days=claim_data["days_ago"] - 2)
        )
        session.add(approval)
        
        # Create notifications
        # For idea owner
        owner_notif = Notification(
            uuid=create_uuid(),
            user_email=idea.email,
            type="claim_request",
            title="New Claim Request",
            message=f"{claimer.name} wants to claim your idea: {idea.title}",
            idea_uuid=idea_uuid,
            related_user_email=claimer.email,
            is_read=False,
            created_at=approval.created_at
        )
        session.add(owner_notif)
        
        # For claimer's manager
        if claimer.team_uuid:
            manager = session.query(UserProfile).filter_by(
                managed_team_uuid=claimer.team_uuid,
                role="manager"
            ).first()
            if manager:
                mgr_notif = Notification(
                    uuid=create_uuid(),
                    user_email=manager.email,
                    type="claim_approval",
                    title="Claim Approval Required",
                    message=f"{claimer.name} wants to claim: {idea.title}",
                    idea_uuid=idea_uuid,
                    related_user_email=claimer.email,
                    is_read=False,
                    created_at=approval.created_at
                )
                session.add(mgr_notif)
        
        ideas.append(idea)
    
    # 3. Claimed ideas with various sub-statuses
    claimed_ideas = [
        {
            "title": "API Rate Limiting Implementation",
            "description": "Implement rate limiting on all public APIs to prevent abuse and ensure fair usage.",
            "submitter": "alice.manager@company.com",
            "team": "SL - Tech",
            "claimer": "frank.dev@company.com",
            "skills": ["Java", "API Development", "Security"],
            "size": IdeaSize.medium,
            "priority": PriorityLevel.high,
            "sub_status": SubStatus.in_development,
            "progress": 45,
            "days_ago": 15,
            "claim_days_ago": 10
        },
        {
            "title": "Machine Learning Model for Fraud Detection",
            "description": "Develop ML model to detect fraudulent transactions in real-time.",
            "submitter": "carol.manager@company.com",
            "team": "Data Science",
            "claimer": "grace.dev@company.com",
            "skills": ["Python", "Machine Learning", "Data Analysis"],
            "size": IdeaSize.large,
            "priority": PriorityLevel.high,
            "sub_status": SubStatus.testing,
            "progress": 75,
            "days_ago": 20,
            "claim_days_ago": 15
        },
        {
            "title": "Cloud Migration Strategy",
            "description": "Plan and execute migration of on-premise services to cloud infrastructure.",
            "submitter": "bob.manager@company.com",
            "team": "Engineering - Backend",
            "claimer": "david.dev@company.com",
            "skills": ["AWS", "Docker", "DevOps"],
            "size": IdeaSize.extra_large,
            "priority": PriorityLevel.medium,
            "sub_status": SubStatus.planning,
            "progress": 20,
            "days_ago": 12,
            "claim_days_ago": 8
        },
        {
            "title": "Real-time Analytics Dashboard",
            "description": "Build real-time analytics dashboard for monitoring system performance.",
            "submitter": "helen.citizen@company.com",
            "team": "Cash - Sales",
            "claimer": "emma.dev@company.com",
            "skills": ["React", "JavaScript"],
            "size": IdeaSize.medium,
            "priority": PriorityLevel.medium,
            "sub_status": SubStatus.blocked,
            "progress": 30,
            "blocked_reason": "Waiting for data access permissions from security team",
            "days_ago": 18,
            "claim_days_ago": 12
        }
    ]
    
    for claimed_data in claimed_ideas:
        idea_uuid = create_uuid()
        idea = Idea(
            uuid=idea_uuid,
            title=claimed_data["title"],
            description=claimed_data["description"],
            email=claimed_data["submitter"],
            benefactor_team=claimed_data["team"],
            size=claimed_data["size"],
            bounty="Career development opportunity",
            needed_by=datetime.utcnow() + timedelta(days=60),
            priority=claimed_data["priority"],
            status=IdeaStatus.claimed,
            sub_status=claimed_data["sub_status"],
            progress_percentage=claimed_data["progress"],
            blocked_reason=claimed_data.get("blocked_reason"),
            date_submitted=datetime.utcnow() - timedelta(days=claimed_data["days_ago"]),
            sub_status_updated_at=datetime.utcnow() - timedelta(days=2),
            sub_status_updated_by=claimed_data["claimer"]
        )
        
        if claimed_data["sub_status"] in [SubStatus.planning, SubStatus.in_development]:
            idea.expected_completion = datetime.utcnow() + timedelta(days=30)
        
        session.add(idea)
        
        # Add skills
        for skill_name in claimed_data["skills"]:
            if skill_name in skills:
                session.execute(
                    text("INSERT INTO idea_skills (idea_uuid, skill_uuid) VALUES (:idea_uuid, :skill_uuid)"),
                    {"idea_uuid": idea_uuid, "skill_uuid": skills[skill_name].uuid}
                )
        
        # Create claim
        claim = Claim(
            uuid=create_uuid(),
            idea_uuid=idea_uuid,
            claimer_email=claimed_data["claimer"],
            claim_date=datetime.utcnow() - timedelta(days=claimed_data["claim_days_ago"])
        )
        session.add(claim)
        
        # Add status history
        status_hist = StatusHistory(
            uuid=create_uuid(),
            idea_uuid=idea_uuid,
            from_status=IdeaStatus.open,
            to_status=IdeaStatus.claimed,
            from_sub_status=None,
            to_sub_status=claimed_data["sub_status"],
            changed_by=claimed_data["claimer"],
            changed_at=claim.claim_date,
            comment="Claim approved by idea owner and manager"
        )
        session.add(status_hist)
        
        # Add development comments
        if claimed_data["sub_status"] == SubStatus.in_development:
            comment = IdeaComment(
                uuid=create_uuid(),
                idea_uuid=idea_uuid,
                author_email=claimed_data["claimer"],
                author_name=session.query(UserProfile).filter_by(email=claimed_data["claimer"]).first().name,
                content="Started implementation. Created feature branch and set up development environment.",
                created_at=datetime.utcnow() - timedelta(days=5),
                sub_status=SubStatus.in_development
            )
            session.add(comment)
            
            # Add external link
            link = IdeaExternalLink(
                uuid=create_uuid(),
                idea_uuid=idea_uuid,
                link_type=ExternalLinkType.repository,
                title="Feature Branch",
                url=f"https://github.com/company/repo/tree/feature/{idea.title.lower().replace(' ', '-')}",
                description="Development branch for this feature",
                sub_status=SubStatus.in_development,
                created_by=claimed_data["claimer"],
                created_at=datetime.utcnow() - timedelta(days=5)
            )
            session.add(link)
        
        # Add stage data for planning/development
        if claimed_data["sub_status"] in [SubStatus.planning, SubStatus.in_development]:
            stage_data = IdeaStageData(
                uuid=create_uuid(),
                idea_uuid=idea_uuid,
                sub_status=claimed_data["sub_status"],
                requirements_doc_url="https://wiki.company.com/requirements/" + idea.title.lower().replace(' ', '-'),
                created_at=datetime.utcnow() - timedelta(days=3)
            )
            session.add(stage_data)
        
        ideas.append(idea)
    
    # 4. Completed ideas
    completed_ideas = [
        {
            "title": "Automated Email Templates",
            "description": "Create system for automated email templates with personalization.",
            "submitter": "lisa.submitter@company.com",
            "team": "Cash - Sales",
            "claimer": "ivan.citizen@company.com",
            "skills": ["Python", "API Development"],
            "size": IdeaSize.small,
            "priority": PriorityLevel.low,
            "days_ago": 30,
            "claim_days_ago": 25,
            "complete_days_ago": 5
        },
        {
            "title": "Security Audit Tool",
            "description": "Tool to automatically audit application security configurations.",
            "submitter": "alice.manager@company.com",
            "team": "SL - Tech",
            "claimer": "frank.dev@company.com",
            "skills": ["Security", "Python", "DevOps"],
            "size": IdeaSize.medium,
            "priority": PriorityLevel.high,
            "days_ago": 40,
            "claim_days_ago": 35,
            "complete_days_ago": 10
        }
    ]
    
    for completed_data in completed_ideas:
        idea_uuid = create_uuid()
        idea = Idea(
            uuid=idea_uuid,
            title=completed_data["title"],
            description=completed_data["description"],
            email=completed_data["submitter"],
            benefactor_team=completed_data["team"],
            size=completed_data["size"],
            bounty="Gift card and recognition",
            needed_by=datetime.utcnow() - timedelta(days=completed_data["complete_days_ago"]),
            priority=completed_data["priority"],
            status=IdeaStatus.complete,
            sub_status=SubStatus.verified,
            progress_percentage=100,
            date_submitted=datetime.utcnow() - timedelta(days=completed_data["days_ago"]),
            sub_status_updated_at=datetime.utcnow() - timedelta(days=completed_data["complete_days_ago"]),
            sub_status_updated_by=completed_data["claimer"]
        )
        session.add(idea)
        
        # Add skills
        for skill_name in completed_data["skills"]:
            if skill_name in skills:
                session.execute(
                    text("INSERT INTO idea_skills (idea_uuid, skill_uuid) VALUES (:idea_uuid, :skill_uuid)"),
                    {"idea_uuid": idea_uuid, "skill_uuid": skills[skill_name].uuid}
                )
        
        # Create claim
        claim = Claim(
            uuid=create_uuid(),
            idea_uuid=idea_uuid,
            claimer_email=completed_data["claimer"],
            claim_date=datetime.utcnow() - timedelta(days=completed_data["claim_days_ago"])
        )
        session.add(claim)
        
        # Add completion comment
        comment = IdeaComment(
            uuid=create_uuid(),
            idea_uuid=idea_uuid,
            author_email=completed_data["claimer"],
            author_name=session.query(UserProfile).filter_by(email=completed_data["claimer"]).first().name,
            content="Feature completed and deployed to production. All tests passing.",
            created_at=datetime.utcnow() - timedelta(days=completed_data["complete_days_ago"]),
            sub_status=SubStatus.verified
        )
        session.add(comment)
        
        ideas.append(idea)
    
    # 5. Assigned ideas
    assigned_idea = Idea(
        uuid=create_uuid(),
        title="Performance Optimization Study",
        description="Analyze and optimize application performance bottlenecks.",
        email="bob.manager@company.com",
        benefactor_team="Engineering - Backend",
        size=IdeaSize.medium,
        bounty="Technical training budget",
        needed_by=datetime.utcnow() + timedelta(days=20),
        priority=PriorityLevel.medium,
        status=IdeaStatus.open,
        date_submitted=datetime.utcnow() - timedelta(days=2),
        assigned_to_email="david.dev@company.com",
        assigned_at=datetime.utcnow() - timedelta(hours=6),
        assigned_by="bob.manager@company.com"
    )
    session.add(assigned_idea)
    
    # Add notification for assignment
    assign_notif = Notification(
        uuid=create_uuid(),
        user_email="david.dev@company.com",
        type="assigned",
        title="Idea Assigned to You",
        message=f"Bob Manager has assigned you to work on: {assigned_idea.title}",
        idea_uuid=assigned_idea.uuid,
        related_user_email="bob.manager@company.com",
        is_read=False,
        created_at=assigned_idea.assigned_at
    )
    session.add(assign_notif)
    
    session.commit()
    return ideas

def create_admin_notifications():
    """Create admin notifications for pending items"""
    print("Creating admin notifications...")
    
    # Team approval notification (already created in create_teams)
    team_notif = Notification(
        uuid=create_uuid(),
        user_email="admin@system.local",
        type="team_approval_request",
        title="Team Approval Required",
        message="Innovation Lab team is pending approval",
        is_read=False,
        created_at=datetime.utcnow() - timedelta(days=1)
    )
    session.add(team_notif)
    
    session.commit()

def main():
    """Main function to populate all test data"""
    print("Starting test data population...")
    
    # Clear existing data (optional - comment out if you want to append)
    print("Clearing existing data...")
    session.query(IdeaActivity).delete()
    session.query(IdeaStageData).delete()
    session.query(IdeaExternalLink).delete()
    session.query(IdeaComment).delete()
    session.query(StatusHistory).delete()
    session.query(Bounty).delete()
    session.query(Notification).delete()
    session.query(ClaimApproval).delete()
    session.query(ManagerRequest).delete()
    session.query(Claim).delete()
    session.execute(text("DELETE FROM idea_skills"))
    session.execute(text("DELETE FROM user_skills"))
    session.query(Idea).delete()
    session.query(UserProfile).delete()
    session.query(Skill).delete()
    session.query(Team).delete()
    session.commit()
    
    # Create data
    teams = create_teams()
    skills = create_skills()
    users = create_users(teams, skills)
    ideas = create_ideas(users, teams, skills)
    create_admin_notifications()
    
    print("\nTest data population complete!")
    print(f"Created {len(teams)} teams")
    print(f"Created {len(skills)} skills")
    print(f"Created {len(users)} users")
    print(f"Created {len(ideas)} ideas")
    print("\nYou can now test the following workflows:")
    print("- Browse open ideas and filter by skills/priority")
    print("- Login as different users to see role-based features")
    print("- Approve/deny claim requests")
    print("- Update idea sub-statuses")
    print("- View team performance metrics")
    print("- Process manager requests as admin")
    print("\nTest user emails:")
    print("Managers: alice.manager@company.com, bob.manager@company.com")
    print("Developers: david.dev@company.com, emma.dev@company.com")
    print("Citizen Devs: helen.citizen@company.com, ivan.citizen@company.com")
    print("Submitters: jane.submitter@company.com, kevin.submitter@company.com")
    print("Admin: use password '2929arch' to access /admin")

if __name__ == "__main__":
    main()