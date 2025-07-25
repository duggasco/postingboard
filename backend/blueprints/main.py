from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import get_session
from models import Idea, Skill, Claim, IdeaStatus, PriorityLevel, IdeaSize, Notification
from sqlalchemy import desc, asc
from datetime import datetime
from email_utils import send_claim_notification
from decorators import require_verified_email, require_profile_complete
from uuid_utils import get_by_identifier, get_identifier_for_url, is_valid_uuid

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Home page with idea browsing and filtering."""
    return render_template('home.html')

@main_bp.route('/submit', methods=['GET', 'POST'])
@require_verified_email
def submit():
    """Submit a new idea."""
    if request.method == 'POST':
        db = get_session()
        try:
            # Create new idea
            idea = Idea(
                title=request.form.get('title'),
                description=request.form.get('description'),
                email=session.get('user_email'),  # Use session email
                benefactor_team=request.form.get('team'),
                priority=PriorityLevel(request.form.get('priority')),
                size=IdeaSize(request.form.get('size')),
                status=IdeaStatus.open,
                date_submitted=datetime.now()
            )
            
            # Handle optional fields
            bounty = request.form.get('bounty')
            if bounty:
                idea.bounty = bounty
                
            needed_by = request.form.get('needed_by')
            if needed_by:
                idea.needed_by = datetime.strptime(needed_by, '%Y-%m-%d')
            
            # Handle skills
            skill_uuids = request.form.getlist('skills[]')
            for skill_uuid in skill_uuids:
                if is_valid_uuid(skill_uuid):
                    skill = get_by_identifier(Skill, skill_uuid, db)
                    if skill:
                        idea.skills.append(skill)
                else:
                    # Create new skill if it's a custom one
                    skill = db.query(Skill).filter_by(name=skill_uuid).first()
                    if not skill:
                        skill = Skill(name=skill_uuid)
                        db.add(skill)
                    idea.skills.append(skill)
            
            db.add(idea)
            db.flush()  # Flush to get idea.uuid before creating bounty
            
            # Handle bounty if monetary is checked
            is_monetary = request.form.get('is_monetary') == 'on'
            if is_monetary:
                from models import Bounty, Notification
                is_expensed = request.form.get('is_expensed') == 'on'
                amount = 0.0
                
                if is_expensed:
                    amount_str = request.form.get('amount', '0')
                    try:
                        amount = float(amount_str) if amount_str else 0.0
                    except ValueError:
                        amount = 0.0
                
                # Create bounty record
                bounty = Bounty(
                    idea_uuid=idea.uuid,
                    is_monetary=is_monetary,
                    is_expensed=is_expensed,
                    amount=amount,
                    requires_approval=amount > 50
                )
                db.add(bounty)
                
                # If amount > $50, create notification for managers and admins
                if amount > 50:
                    # Get user's manager
                    from models import UserProfile
                    user_profile = db.query(UserProfile).filter_by(email=session.get('user_email')).first()
                    
                    # Notify user's manager if they have one
                    if user_profile and user_profile.managed_team_id:
                        managers = db.query(UserProfile).filter_by(
                            managed_team_id=user_profile.team_id,
                            role='manager'
                        ).all()
                        
                        for manager in managers:
                            notification = Notification(
                                user_email=manager.email,
                                type='bounty_approval',
                                title='Bounty Approval Required',
                                message=f'${amount:.2f} bounty requested for idea: {idea.title}',
                                idea_uuid=idea.uuid,
                                related_user_email=session.get('user_email')
                            )
                            db.add(notification)
                    
                    # Always notify admin
                    admin_notification = Notification(
                        user_email='admin@system.local',
                        type='bounty_approval',
                        title='Bounty Approval Required',
                        message=f'${amount:.2f} bounty requested by {session.get("user_name", session.get("user_email"))} for idea: {idea.title}',
                        idea_uuid=idea.uuid,
                        related_user_email=session.get('user_email')
                    )
                    db.add(admin_notification)
            
            db.commit()
            
            # Update session
            if 'submitted_ideas' not in session:
                session['submitted_ideas'] = []
            session['submitted_ideas'].append(idea.uuid)
            session.permanent = True
            
            flash('Idea submitted successfully!', 'success')
            return redirect(url_for('main.idea_detail', identifier=idea.uuid))
            
        except Exception as e:
            db.rollback()
            flash(f'Error submitting idea: {str(e)}', 'error')
        finally:
            db.close()
    
    # Get user's assigned team from session
    user_team = session.get('user_team')
    return render_template('submit.html', user_team=user_team)

@main_bp.route('/my-ideas')
@require_verified_email
def my_ideas():
    """Show ideas submitted by the current user."""
    return render_template('my_ideas.html')


@main_bp.route('/my-team')
@require_verified_email
def my_team():
    """Show team management page for managers and admins."""
    # Check if user is a manager or admin
    if session.get('user_role') != 'manager' and not session.get('is_admin'):
        flash('Access denied. Manager or admin role required.', 'error')
        return redirect(url_for('main.home'))
    
    return render_template('my_team.html')

@main_bp.route('/idea/<identifier>')
def idea_detail(identifier):
    """Show individual idea details."""
    # Only allow UUID format
    from uuid_utils import is_valid_uuid
    if not is_valid_uuid(identifier):
        flash('Invalid idea identifier', 'error')
        return redirect(url_for('main.home'))
        
    db = get_session()
    try:
        idea = get_by_identifier(Idea, identifier, db)
        if not idea:
            flash('Idea not found', 'error')
            return redirect(url_for('main.home'))
        
        # Determine if user has access to sensitive tabs
        has_tab_access = False
        user_email = session.get('user_email')
        
        if user_email:
            # Check if user is admin
            if session.get('is_admin'):
                has_tab_access = True
            # Check if user is the idea submitter
            elif idea.email == user_email:
                has_tab_access = True
            # Check if user is a direct claimer
            elif any(claim.claimer_email == user_email for claim in idea.claims):
                has_tab_access = True
            else:
                # Check if user is a manager of the submitter or any claimer
                from models import UserProfile
                user_profile = db.query(UserProfile).filter_by(
                    email=user_email,
                    role='manager'
                ).first()
                
                if user_profile and user_profile.managed_team_id:
                    # Get all team members' emails
                    team_members = db.query(UserProfile).filter_by(
                        team_id=user_profile.managed_team_id
                    ).all()
                    team_emails = [member.email for member in team_members]
                    
                    # Check if submitter is in the team
                    if idea.email in team_emails:
                        has_tab_access = True
                    # Check if any claimer is in the team
                    elif any(claim.claimer_email in team_emails for claim in idea.claims):
                        has_tab_access = True
        
        # Serialize status history for JavaScript
        status_history_data = []
        if idea.status_history:
            for history in idea.status_history:
                status_history_data.append({
                    'from_status': history.from_status.value if history.from_status else None,
                    'to_status': history.to_status.value if history.to_status else None,
                    'from_sub_status': history.from_sub_status.value if history.from_sub_status else None,
                    'to_sub_status': history.to_sub_status.value if history.to_sub_status else None,
                    'changed_by': history.changed_by,
                    'changed_at': history.changed_at.isoformat() if history.changed_at else None,
                    'comment': history.comment,
                    'duration_minutes': history.duration_minutes
                })
        
        return render_template('idea_detail.html', 
                             idea=idea, 
                             status_history_json=status_history_data,
                             has_tab_access=has_tab_access)
    finally:
        db.close()

@main_bp.route('/idea/<identifier>/claim', methods=['POST'])
@require_profile_complete
def claim_idea(identifier):
    """Request to claim an idea - requires approvals."""
    # Only allow UUID format
    from uuid_utils import is_valid_uuid
    if not is_valid_uuid(identifier):
        return jsonify({'success': False, 'message': 'Invalid idea identifier'}), 400
        
    # Check if user has permission to claim based on role
    user_role = session.get('user_role')
    if user_role not in ['citizen_developer', 'developer']:
        return jsonify({'success': False, 'message': 'Only developers can claim ideas'}), 403
    
    db = get_session()
    try:
        idea = get_by_identifier(Idea, identifier, db)
        if not idea:
            return jsonify({'success': False, 'message': 'Idea not found'}), 404
        
        if idea.status != IdeaStatus.open:
            return jsonify({'success': False, 'message': 'Idea is not available for claiming'}), 400
        
        # Check if user already has a pending claim approval for this idea
        from models import ClaimApproval
        existing_approval = db.query(ClaimApproval).filter_by(
            idea_uuid=idea.uuid,
            claimer_email=session.get('user_email'),
            status='pending'
        ).first()
        
        if existing_approval:
            return jsonify({'success': False, 'message': 'You already have a pending claim request for this idea'}), 400
        
        # Get user profile to check if they have a manager
        from models import UserProfile
        user_profile = db.query(UserProfile).filter_by(email=session.get('user_email')).first()
        
        # Create claim approval request
        claim_approval = ClaimApproval(
            idea_uuid=idea.uuid,
            claimer_name=session.get('user_name') or request.form.get('name'),
            claimer_email=session.get('user_email'),
            claimer_team=request.form.get('team'),
            claimer_skills=request.form.get('skills'),
            status='pending'
        )
        
        # If claimer's team doesn't have a manager, auto-approve manager approval
        if not user_profile or not user_profile.team_uuid:
            # No team, auto-approve manager
            claim_approval.manager_approved = True
            claim_approval.manager_approved_at = datetime.now()
            claim_approval.manager_approved_by = 'system_auto'
        else:
            # Check if the team has a manager
            team_manager = db.query(UserProfile).filter_by(
                managed_team_uuid=user_profile.team_uuid,
                role='manager'
            ).first()
            if not team_manager:
                # Team has no manager, auto-approve
                claim_approval.manager_approved = True
                claim_approval.manager_approved_at = datetime.now()
                claim_approval.manager_approved_by = 'system_auto'
        
        db.add(claim_approval)
        
        # Create notifications
        # Notify idea owner about the claim request
        owner_notification = Notification(
            user_email=idea.email,
            type='claim_request',
            title='New claim request',
            message=f'{claim_approval.claimer_name} wants to claim your idea "{idea.title}". Please review and approve/deny the request.',
            idea_uuid=idea.uuid,
            related_user_email=claim_approval.claimer_email
        )
        db.add(owner_notification)
        
        # If claimer has a manager, notify them too
        if user_profile and user_profile.team_uuid:
            # Get team manager
            manager = db.query(UserProfile).filter_by(
                team_uuid=user_profile.team_uuid,
                role='manager',
                managed_team_uuid=user_profile.team_uuid
            ).first()
            
            if manager:
                manager_notification = Notification(
                    user_email=manager.email,
                    type='claim_request',
                    title='Team member claim request',
                    message=f'{claim_approval.claimer_name} from your team wants to claim "{idea.title}". Please review and approve/deny the request.',
                    idea_uuid=idea.uuid,
                    related_user_email=claim_approval.claimer_email
                )
                db.add(manager_notification)
        
        db.commit()
        
        # Update session with pending claim
        if 'pending_claims' not in session:
            session['pending_claims'] = []
        if idea.uuid not in session['pending_claims']:
            session['pending_claims'].append(idea.uuid)
        
        session.permanent = True
        
        return jsonify({'success': True, 'message': 'Claim request submitted! Waiting for approvals.'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()