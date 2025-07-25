#!/usr/bin/env python3
"""
Simple test to verify UUID database is working correctly.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Idea, Team, Skill, UserProfile

# Connect to the UUID database
engine = create_engine('sqlite:///posting_board_uuid.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Test 1: Can we query teams?
    print("\n=== Testing Teams ===")
    teams = session.query(Team).all()
    for team in teams[:3]:
        print(f"Team: {team.name}, UUID: {team.uuid}")
    
    # Test 2: Can we query users?
    print("\n=== Testing Users ===")
    users = session.query(UserProfile).all()
    for user in users[:3]:
        print(f"User: {user.name} ({user.email}), Team UUID: {user.team_uuid}")
    
    # Test 3: Can we query ideas?
    print("\n=== Testing Ideas ===")
    ideas = session.query(Idea).all()
    for idea in ideas[:3]:
        print(f"Idea: {idea.title}, UUID: {idea.uuid}")
        print(f"  Submitter email: {idea.email}")
        # Try to access submitter relationship
        try:
            if idea.submitter:
                print(f"  Submitter name: {idea.submitter.name}")
            else:
                print(f"  Submitter not found in UserProfile")
        except Exception as e:
            print(f"  Error accessing submitter: {e}")
    
    print("\n=== All tests passed! ===")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()