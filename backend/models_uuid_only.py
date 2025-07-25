"""
Database models using UUID-only design - no integer IDs.
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, ForeignKey, Table, Enum, Integer
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum
import uuid as uuid_lib

# Enums
class PriorityLevel(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class IdeaSize(enum.Enum):
    small = "small"
    medium = "medium" 
    large = "large"
    extra_large = "extra_large"

class IdeaStatus(enum.Enum):
    open = "open"
    claimed = "claimed"
    complete = "complete"

class SubStatus(enum.Enum):
    planning = "planning"
    in_development = "in_development"
    testing = "testing"
    awaiting_deployment = "awaiting_deployment"
    deployed = "deployed"
    verified = "verified"
    on_hold = "on_hold"
    blocked = "blocked"
    cancelled = "cancelled"
    rolled_back = "rolled_back"

class ExternalLinkType(enum.Enum):
    repository = "repository"
    pull_request = "pull_request"
    ado_work_item = "ado_work_item"
    documentation = "documentation"
    gantt_chart = "gantt_chart"
    test_results = "test_results"
    other = "other"

class ActivityType(enum.Enum):
    created = "created"
    status_changed = "status_changed"
    assigned = "assigned"
    claimed = "claimed"
    comment_added = "comment_added"
    link_added = "link_added"
    progress_updated = "progress_updated"

# Association tables using UUIDs
idea_skills = Table('idea_skills', Base.metadata,
    Column('idea_uuid', String(36), ForeignKey('ideas.uuid'), primary_key=True),
    Column('skill_uuid', String(36), ForeignKey('skills.uuid'), primary_key=True)
)

user_skills = Table('user_skills', Base.metadata,
    Column('user_email', String(120), ForeignKey('user_profiles.email'), primary_key=True),
    Column('skill_uuid', String(36), ForeignKey('skills.uuid'), primary_key=True)
)

class Idea(Base):
    __tablename__ = 'ideas'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    email = Column(String(120), nullable=False)  # Submitter's email
    benefactor_team = Column(String(100), nullable=False)
    size = Column(Enum(IdeaSize), nullable=False)
    bounty = Column(Text)
    needed_by = Column(DateTime, nullable=False)
    priority = Column(Enum(PriorityLevel), nullable=False)
    status = Column(Enum(IdeaStatus), default=IdeaStatus.open)
    sub_status = Column(Enum(SubStatus), nullable=True)
    sub_status_updated_at = Column(DateTime)
    sub_status_updated_by = Column(String(120))
    progress_percentage = Column(Integer, default=0)
    blocked_reason = Column(Text)
    expected_completion = Column(DateTime)
    date_submitted = Column(DateTime, default=datetime.utcnow)
    assigned_to_email = Column(String(120))
    assigned_at = Column(DateTime)
    assigned_by = Column(String(120))
    
    # Relationships
    skills = relationship('Skill', secondary=idea_skills, back_populates='ideas')
    claims = relationship('Claim', back_populates='idea', cascade='all, delete-orphan')
    submitter = relationship('UserProfile', foreign_keys=[email], 
                           primaryjoin="Idea.email==UserProfile.email", viewonly=True)
    assigned_to = relationship('UserProfile', foreign_keys=[assigned_to_email],
                             primaryjoin="Idea.assigned_to_email==UserProfile.email", viewonly=True)
    status_history = relationship('StatusHistory', back_populates='idea', cascade='all, delete-orphan')
    comments = relationship('IdeaComment', back_populates='idea', cascade='all, delete-orphan')
    external_links = relationship('IdeaExternalLink', back_populates='idea', cascade='all, delete-orphan')
    activities = relationship('IdeaActivity', back_populates='idea', cascade='all, delete-orphan')
    stage_data = relationship('IdeaStageData', back_populates='idea', cascade='all, delete-orphan')

class Skill(Base):
    __tablename__ = 'skills'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    
    # Relationships
    ideas = relationship('Idea', secondary=idea_skills, back_populates='skills')
    users = relationship('UserProfile', secondary=user_skills, back_populates='skills')

class Claim(Base):
    __tablename__ = 'claims'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    idea_uuid = Column(String(36), ForeignKey('ideas.uuid'), nullable=False)
    claimer_email = Column(String(120), nullable=False)
    claim_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    idea = relationship('Idea', back_populates='claims')

class Team(Base):
    __tablename__ = 'teams'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    is_approved = Column(Boolean, default=False)
    
    # Relationships
    members = relationship('UserProfile', foreign_keys='UserProfile.team_uuid', back_populates='team')
    managers = relationship('UserProfile', foreign_keys='UserProfile.managed_team_uuid', back_populates='managed_team')

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    email = Column(String(120), primary_key=True)
    name = Column(String(100), nullable=False)
    team_uuid = Column(String(36), ForeignKey('teams.uuid'))
    role = Column(String(50))  # manager, idea_submitter, citizen_developer, developer
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    managed_team_uuid = Column(String(36), ForeignKey('teams.uuid'))
    
    # Relationships
    skills = relationship('Skill', secondary=user_skills, back_populates='users')
    team = relationship('Team', foreign_keys=[team_uuid], back_populates='members')
    managed_team = relationship('Team', foreign_keys=[managed_team_uuid], back_populates='managers')

class VerificationCode(Base):
    __tablename__ = 'verification_codes'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    email = Column(String(120), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)

class ManagerRequest(Base):
    __tablename__ = 'manager_requests'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    user_email = Column(String(120), ForeignKey('user_profiles.email'), nullable=False)
    requested_team_uuid = Column(String(36), ForeignKey('teams.uuid'), nullable=False)
    status = Column(String(20), default='pending')  # pending, approved, denied
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    processed_by = Column(String(120))
    
    # Relationships
    user = relationship('UserProfile', backref='manager_requests')
    team = relationship('Team', backref='manager_requests')

class ClaimApproval(Base):
    __tablename__ = 'claim_approvals'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    idea_uuid = Column(String(36), ForeignKey('ideas.uuid'), nullable=False)
    claimer_email = Column(String(120), nullable=False)
    claimer_name = Column(String(100), nullable=False)
    claimer_team = Column(String(100))
    claimer_skills = Column(Text)
    
    # Approval tracking
    idea_owner_approved = Column(Boolean, default=None)
    manager_approved = Column(Boolean, default=None)
    idea_owner_approved_at = Column(DateTime)
    manager_approved_at = Column(DateTime)
    idea_owner_denied_at = Column(DateTime)
    manager_denied_at = Column(DateTime)
    idea_owner_approved_by = Column(String(120))
    manager_approved_by = Column(String(120))
    
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    idea = relationship('Idea', backref='claim_approvals')

class EmailSettings(Base):
    __tablename__ = 'email_settings'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    smtp_server = Column(String(255))
    smtp_port = Column(Integer, default=587)
    smtp_username = Column(String(255))
    smtp_password = Column(String(255))
    smtp_use_tls = Column(Boolean, default=True)
    from_email = Column(String(255))
    from_name = Column(String(255), default='Posting Board')
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(Base):
    __tablename__ = 'notifications'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    user_email = Column(String(120), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    idea_uuid = Column(String(36), ForeignKey('ideas.uuid'))
    related_user_email = Column(String(120))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    
    # Relationships
    idea = relationship('Idea', foreign_keys=[idea_uuid])

class Bounty(Base):
    __tablename__ = 'bounties'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    idea_uuid = Column(String(36), ForeignKey('ideas.uuid'), nullable=False, unique=True)
    is_monetary = Column(Boolean, default=False)
    is_expensed = Column(Boolean, default=False)
    amount = Column(Float, default=0.0)
    requires_approval = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=None)
    approved_by = Column(String(120))
    approved_at = Column(DateTime)
    
    # Relationships
    idea = relationship('Idea', backref='bounty_details')

class StatusHistory(Base):
    __tablename__ = 'status_history'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    idea_uuid = Column(String(36), ForeignKey('ideas.uuid'), nullable=False)
    from_status = Column(Enum(IdeaStatus))
    to_status = Column(Enum(IdeaStatus))
    from_sub_status = Column(Enum(SubStatus))
    to_sub_status = Column(Enum(SubStatus))
    changed_by = Column(String(120), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(Text)
    duration_minutes = Column(Integer)
    
    # Relationships
    idea = relationship('Idea', back_populates='status_history')

class IdeaComment(Base):
    __tablename__ = 'idea_comments'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    idea_uuid = Column(String(36), ForeignKey('ideas.uuid'), nullable=False)
    author_email = Column(String(120), nullable=False)
    author_name = Column(String(100))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_internal = Column(Boolean, default=False)
    sub_status = Column(Enum(SubStatus))
    
    # Relationships
    idea = relationship('Idea', back_populates='comments')

class IdeaExternalLink(Base):
    __tablename__ = 'idea_external_links'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    idea_uuid = Column(String(36), ForeignKey('ideas.uuid'), nullable=False)
    link_type = Column(Enum(ExternalLinkType), nullable=False)
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text)
    sub_status = Column(Enum(SubStatus))
    created_by = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    idea = relationship('Idea', back_populates='external_links')

class IdeaActivity(Base):
    __tablename__ = 'idea_activities'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    idea_uuid = Column(String(36), ForeignKey('ideas.uuid'), nullable=False)
    activity_type = Column(Enum(ActivityType), nullable=False)
    actor_email = Column(String(120), nullable=False)
    actor_name = Column(String(100))
    description = Column(Text, nullable=False)
    activity_data = Column(Text)  # JSON for additional data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    idea = relationship('Idea', back_populates='activities')

class IdeaStageData(Base):
    __tablename__ = 'idea_stage_data'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    idea_uuid = Column(String(36), ForeignKey('ideas.uuid'), nullable=False)
    sub_status = Column(Enum(SubStatus), nullable=False)
    
    # Planning fields
    requirements_doc_url = Column(String(500))
    design_spec_url = Column(String(500))
    
    # Development fields
    repository_url = Column(String(500))
    branch_name = Column(String(200))
    pull_request_urls = Column(Text)  # Multi-line
    
    # Testing fields
    test_plan_url = Column(String(500))
    test_results_summary = Column(Text)
    defects_found = Column(Integer)
    
    # Deployment fields
    deployment_guide_url = Column(String(500))
    release_notes = Column(Text)
    target_environment = Column(String(50))
    
    # Verification fields
    verified_by = Column(String(100))
    performance_metrics = Column(Text)
    signoff_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    idea = relationship('Idea', back_populates='stage_data')