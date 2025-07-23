import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Skill, Team, UserProfile, VerificationCode, EmailSettings

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///posting_board.db')
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    default_skills = [
        "SQL/Databases",
        "Frontend/UI - Tableau", 
        "Frontend/UI - Streamlit",
        "Frontend/UI - Web",
        "Frontend/UI - PowerBI",
        "Python",
        "Java",
        "Platform",
        "Regulatory"
    ]
    
    for skill_name in default_skills:
        existing_skill = db.query(Skill).filter_by(name=skill_name).first()
        if not existing_skill:
            skill = Skill(name=skill_name)
            db.add(skill)
    
    # Initialize default teams
    default_teams = [
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
        "Cash - CMX"
    ]
    
    for team_name in default_teams:
        existing_team = db.query(Team).filter_by(name=team_name).first()
        if not existing_team:
            team = Team(name=team_name, is_approved=True)
            db.add(team)
    
    db.commit()
    db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_session():
    return SessionLocal()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")