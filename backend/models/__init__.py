from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table, Text, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()

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

idea_skills = Table('idea_skills', Base.metadata,
    Column('idea_id', Integer, ForeignKey('ideas.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

class Idea(Base):
    __tablename__ = 'ideas'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    email = Column(String(120), nullable=False)
    benefactor_team = Column(String(100), nullable=False)
    size = Column(Enum(IdeaSize), nullable=False)
    reward = Column(String(200))
    needed_by = Column(DateTime, nullable=False)
    priority = Column(Enum(PriorityLevel), nullable=False)
    status = Column(Enum(IdeaStatus), default=IdeaStatus.open)
    date_submitted = Column(DateTime, default=datetime.utcnow)
    assigned_to_email = Column(String(120))  # Manager can assign to team member
    assigned_at = Column(DateTime)
    assigned_by = Column(String(120))  # Manager who made the assignment
    
    skills = relationship('Skill', secondary=idea_skills, back_populates='ideas')
    claims = relationship('Claim', back_populates='idea')
    submitter = relationship('UserProfile', foreign_keys=[email], primaryjoin="Idea.email==UserProfile.email", viewonly=True)
    assigned_to = relationship('UserProfile', foreign_keys=[assigned_to_email], primaryjoin="Idea.assigned_to_email==UserProfile.email", viewonly=True)

class Skill(Base):
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    
    ideas = relationship('Idea', secondary=idea_skills, back_populates='skills')

class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    is_approved = Column(Boolean, default=True)  # Pre-defined teams are approved by default
    
    # Relationships
    users = relationship('UserProfile', foreign_keys='UserProfile.team_id', back_populates='team')

class Claim(Base):
    __tablename__ = 'claims'
    
    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    claimer_name = Column(String(100), nullable=False)
    claimer_email = Column(String(120), nullable=False)
    claimer_skills = Column(Text)
    claimer_team = Column(String(100))
    claim_date = Column(DateTime, default=datetime.utcnow)
    
    idea = relationship('Idea', back_populates='claims')

# Many-to-many relationship between UserProfile and Skill
user_skills = Table('user_skills', Base.metadata,
    Column('user_id', Integer, ForeignKey('user_profiles.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    name = Column(String(100))
    role = Column(String(50))  # 'manager', 'idea_submitter', 'citizen_developer', 'developer'
    team_id = Column(Integer, ForeignKey('teams.id'))
    managed_team_id = Column(Integer, ForeignKey('teams.id'))  # Team that manager oversees
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_verified_at = Column(DateTime)
    
    # Relationships
    skills = relationship('Skill', secondary=user_skills, backref='users')
    team = relationship('Team', foreign_keys=[team_id], back_populates='users')
    managed_team = relationship('Team', foreign_keys=[managed_team_id])
    verification_codes = relationship('VerificationCode', back_populates='user', cascade='all, delete-orphan')
    
    def can_claim_ideas(self):
        """Check if user can claim ideas based on their role."""
        return self.role in ['citizen_developer', 'developer']

class VerificationCode(Base):
    __tablename__ = 'verification_codes'
    
    id = Column(Integer, primary_key=True)
    user_email = Column(String(120), ForeignKey('user_profiles.email'), nullable=False)
    code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    
    # Relationship
    user = relationship('UserProfile', back_populates='verification_codes')
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        return not self.is_used and not self.is_expired()

class ManagerRequest(Base):
    __tablename__ = 'manager_requests'
    
    id = Column(Integer, primary_key=True)
    user_email = Column(String(120), ForeignKey('user_profiles.email'), nullable=False)
    requested_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    status = Column(String(20), default='pending')  # pending, approved, denied
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    processed_by = Column(String(120))  # admin who processed the request
    
    # Relationships
    user = relationship('UserProfile', foreign_keys=[user_email])
    team = relationship('Team', foreign_keys=[requested_team_id])

class ClaimApproval(Base):
    __tablename__ = 'claim_approvals'
    
    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    claimer_email = Column(String(120), nullable=False)
    claimer_name = Column(String(100), nullable=False)
    claimer_team = Column(String(100))
    claimer_skills = Column(Text)
    
    # Approval tracking
    idea_owner_approved = Column(Boolean, default=None)  # None = pending, True = approved, False = denied
    manager_approved = Column(Boolean, default=None)
    idea_owner_approved_at = Column(DateTime)
    manager_approved_at = Column(DateTime)
    idea_owner_denied_at = Column(DateTime)
    manager_denied_at = Column(DateTime)
    
    # Who processed the approvals
    idea_owner_approved_by = Column(String(120))
    manager_approved_by = Column(String(120))
    
    # Overall status
    status = Column(String(20), default='pending')  # pending, approved, denied, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    idea = relationship('Idea', backref='claim_approvals')

class EmailSettings(Base):
    __tablename__ = 'email_settings'
    
    id = Column(Integer, primary_key=True)
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
    
    id = Column(Integer, primary_key=True)
    user_email = Column(String(120), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # claim_request, claim_approved, claim_denied, status_change, assigned, new_team_member
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    idea_id = Column(Integer, ForeignKey('ideas.id'))
    related_user_email = Column(String(120))  # Email of the other user involved (claimer, assigner, etc.)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    
    # Relationships
    idea = relationship('Idea', foreign_keys=[idea_id])