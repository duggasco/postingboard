"""
Initialize predefined teams on app startup if they don't exist.
This ensures teams are always available even on fresh installations.
"""
from database import get_session
from models import Team

def ensure_teams_exist():
    """Check if teams exist, create them if not."""
    db = get_session()
    try:
        # Check if any teams exist
        team_count = db.query(Team).count()
        
        if team_count == 0:
            print("No teams found, initializing predefined teams...")
            
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
                db.add(team)
            
            db.commit()
            print(f"Created {len(teams)} predefined teams")
        else:
            print(f"Found {team_count} existing teams")
            
    except Exception as e:
        print(f"Error ensuring teams exist: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    ensure_teams_exist()