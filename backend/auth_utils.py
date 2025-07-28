import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import UserProfile, VerificationCode, Skill, Team, Notification, ManagerRequest
from email_utils import send_verification_code

def generate_verification_code():
    """Generate a 6-digit verification code."""
    return ''.join(random.choices(string.digits, k=6))

def create_verification_code(db: Session, email: str):
    """Create a new verification code for the given email."""
    # Check for existing active codes
    active_codes = db.query(VerificationCode).filter(
        VerificationCode.email == email,
        VerificationCode.is_used == False,
        VerificationCode.expires_at > datetime.utcnow()
    ).all()
    
    # Check rate limiting - max 3 active codes
    if len(active_codes) >= 3:
        # Check if any code was created in the last 15 minutes
        recent_code = db.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.created_at > datetime.utcnow() - timedelta(minutes=15)
        ).order_by(VerificationCode.created_at.desc()).first()
        
        if recent_code:
            wait_time = 15 - int((datetime.utcnow() - recent_code.created_at).total_seconds() / 60)
            return {
                'success': False,
                'error': f'Too many verification attempts. Please wait {wait_time} minutes before requesting a new code.'
            }
    
    # Create or get user profile
    user = db.query(UserProfile).filter_by(email=email).first()
    if not user:
        # Create user with empty name for now - they'll fill it during profile completion
        user = UserProfile(email=email, name='')
        db.add(user)
        db.commit()
    
    # Generate new code
    code = generate_verification_code()
    verification = VerificationCode(
        email=email,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=3)
    )
    db.add(verification)
    db.commit()
    
    # Send email
    email_sent = send_verification_code(email, code)
    
    return {
        'success': True,
        'code_id': verification.uuid,
        'email_sent': email_sent
    }

def verify_code(db: Session, email: str, code: str):
    """Verify a verification code."""
    # Get the most recent unused code for this email
    verification = db.query(VerificationCode).filter(
        VerificationCode.email == email,
        VerificationCode.code == code,
        VerificationCode.is_used == False
    ).order_by(VerificationCode.created_at.desc()).first()
    
    if not verification:
        return {
            'success': False,
            'error': 'Invalid verification code.'
        }
    
    # Check if expired
    if verification.is_expired():
        return {
            'success': False,
            'error': 'Verification code has expired. Please request a new one.'
        }
    
    # Mark as used
    verification.is_used = True
    
    # Update user profile
    user = db.query(UserProfile).filter_by(email=email).first()
    user.is_verified = True
    user.last_verified_at = datetime.utcnow()
    
    db.commit()
    
    return {
        'success': True,
        'user': user
    }

def is_user_verified(db: Session, email: str):
    """Check if a user email is verified."""
    user = db.query(UserProfile).filter_by(email=email).first()
    return user and user.is_verified

def get_user_profile(db: Session, email: str):
    """Get user profile by email."""
    return db.query(UserProfile).filter_by(email=email).first()

def update_user_profile(db: Session, email: str, name: str = None, role: str = None, team_uuid: str = None, managed_team_uuid: str = None, skill_ids: list = None, create_manager_request: bool = False):
    """Update user profile with name, role, team, managed team, and skills."""
    user = db.query(UserProfile).filter_by(email=email).first()
    if not user:
        return None
    
    if name is not None:
        user.name = name
    
    if role is not None:
        user.role = role
        
    if team_uuid is not None:
        old_team_uuid = user.team_uuid
        user.team_uuid = team_uuid
        
        # If team changed, notify the manager of the new team
        if old_team_uuid != team_uuid and team_uuid is not None:
            # Team and Notification already imported at top
            # Get the team name
            team = db.query(Team).filter_by(uuid=team_uuid).first()
            if team:
                # Find the manager of this team
                manager = db.query(UserProfile).filter_by(
                    managed_team_uuid=team_uuid,
                    role='manager'
                ).first()
                
                if manager:
                    # Create notification for the manager
                    notification = Notification(
                        user_email=manager.email,
                        type='new_team_member',
                        title='New team member joined',
                        message=f'{name or email} has joined your team "{team.name}".',
                        related_user_email=email
                    )
                    db.add(notification)
    
    # Handle manager team assignment
    if managed_team_uuid is not None and create_manager_request:
        # Create a manager request instead of direct assignment
        # ManagerRequest already imported at top
        
        # Check if there's already a pending request
        existing_request = db.query(ManagerRequest).filter_by(
            user_email=email,
            requested_team_uuid=managed_team_uuid,
            status='pending'
        ).first()
        
        if not existing_request:
            manager_request = ManagerRequest(
                user_email=email,
                requested_team_uuid=managed_team_uuid,
                status='pending'
            )
            db.add(manager_request)
        
        # Don't set managed_team_uuid directly when creating request
    elif managed_team_uuid is not None and not create_manager_request:
        # Direct assignment (from admin approval)
        user.managed_team_uuid = managed_team_uuid
    
    if skill_ids is not None:
        # Clear existing skills
        user.skills = []
        # Add new skills
        # Skill already imported at top
        for skill_id in skill_ids:
            skill = db.query(Skill).filter_by(uuid=skill_id).first()
            if skill:
                user.skills.append(skill)
    
    db.commit()
    return user

def cleanup_expired_codes(db: Session):
    """Clean up expired verification codes (optional maintenance task)."""
    expired = db.query(VerificationCode).filter(
        VerificationCode.expires_at < datetime.utcnow(),
        VerificationCode.is_used == False
    ).all()
    
    for code in expired:
        code.is_used = True
    
    db.commit()
    return len(expired)