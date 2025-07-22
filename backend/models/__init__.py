from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()

class PriorityLevel(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class IdeaSize(enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"

class IdeaStatus(enum.Enum):
    OPEN = "open"
    CLAIMED = "claimed"
    COMPLETE = "complete"

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
    status = Column(Enum(IdeaStatus), default=IdeaStatus.OPEN)
    date_submitted = Column(DateTime, default=datetime.utcnow)
    
    skills = relationship('Skill', secondary=idea_skills, back_populates='ideas')
    claims = relationship('Claim', back_populates='idea')

class Skill(Base):
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    
    ideas = relationship('Idea', secondary=idea_skills, back_populates='skills')

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