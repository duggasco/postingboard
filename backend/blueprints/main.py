from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import get_session
from models import Idea, Skill, Claim, IdeaStatus, PriorityLevel, IdeaSize, Notification
from sqlalchemy import desc, asc
from datetime import datetime
from email_utils import send_claim_notification
from decorators import require_verified_email, require_profile_complete

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
            skill_ids = request.form.getlist('skills[]')
            for skill_id in skill_ids:
                if skill_id.isdigit():
                    skill = db.query(Skill).get(int(skill_id))
                    if skill:
                        idea.skills.append(skill)
                else:
                    # Create new skill if it's a custom one
                    skill = db.query(Skill).filter_by(name=skill_id).first()
                    if not skill:
                        skill = Skill(name=skill_id)
                        db.add(skill)
                    idea.skills.append(skill)
            
            db.add(idea)
            db.flush()  # Flush to get idea.id before creating bounty
            
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
                    idea_id=idea.id,
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
                                idea_id=idea.id,
                                related_user_email=session.get('user_email')
                            )
                            db.add(notification)
                    
                    # Always notify admin
                    admin_notification = Notification(
                        user_email='admin@system.local',
                        type='bounty_approval',
                        title='Bounty Approval Required',
                        message=f'${amount:.2f} bounty requested by {session.get("user_name", session.get("user_email"))} for idea: {idea.title}',
                        idea_id=idea.id,
                        related_user_email=session.get('user_email')
                    )
                    db.add(admin_notification)
            
            db.commit()
            
            # Update session
            if 'submitted_ideas' not in session:
                session['submitted_ideas'] = []
            session['submitted_ideas'].append(idea.id)
            session.permanent = True
            
            flash('Idea submitted successfully!', 'success')
            return redirect(url_for('main.idea_detail', idea_id=idea.id))
            
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

@main_bp.route('/idea/<int:idea_id>')
def idea_detail(idea_id):
    """Show individual idea details."""
    db = get_session()
    try:
        idea = db.query(Idea).get(idea_id)
        if not idea:
            flash('Idea not found', 'error')
            return redirect(url_for('main.home'))
        return render_template('idea_detail.html', idea=idea)
    finally:
        db.close()

@main_bp.route('/idea/<int:idea_id>/claim', methods=['POST'])
@require_profile_complete
def claim_idea(idea_id):
    """Request to claim an idea - requires approvals."""
    # Check if user has permission to claim based on role
    user_role = session.get('user_role')
    if user_role not in ['citizen_developer', 'developer']:
        return jsonify({'success': False, 'message': 'Only developers can claim ideas'}), 403
    
    db = get_session()
    try:
        idea = db.query(Idea).get(idea_id)
        if not idea:
            return jsonify({'success': False, 'message': 'Idea not found'}), 404
        
        if idea.status != IdeaStatus.open:
            return jsonify({'success': False, 'message': 'Idea is not available for claiming'}), 400
        
        # Check if user already has a pending claim approval for this idea
        from models import ClaimApproval
        existing_approval = db.query(ClaimApproval).filter_by(
            idea_id=idea_id,
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
            idea_id=idea_id,
            claimer_name=session.get('user_name') or request.form.get('name'),
            claimer_email=session.get('user_email'),
            claimer_team=request.form.get('team'),
            claimer_skills=request.form.get('skills'),
            status='pending'
        )
        
        # If claimer's team doesn't have a manager, auto-approve manager approval
        if not user_profile or not user_profile.team_id:
            # No team, auto-approve manager
            claim_approval.manager_approved = True
            claim_approval.manager_approved_at = datetime.now()
            claim_approval.manager_approved_by = 'system_auto'
        else:
            # Check if the team has a manager
            team_manager = db.query(UserProfile).filter_by(
                managed_team_id=user_profile.team_id,
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
            idea_id=idea_id,
            related_user_email=claim_approval.claimer_email
        )
        db.add(owner_notification)
        
        # If claimer has a manager, notify them too
        if user_profile and user_profile.team_id:
            # Get team manager
            manager = db.query(UserProfile).filter_by(
                team_id=user_profile.team_id,
                role='manager',
                managed_team_id=user_profile.team_id
            ).first()
            
            if manager:
                manager_notification = Notification(
                    user_email=manager.email,
                    type='claim_request',
                    title='Team member claim request',
                    message=f'{claim_approval.claimer_name} from your team wants to claim "{idea.title}". Please review and approve/deny the request.',
                    idea_id=idea_id,
                    related_user_email=claim_approval.claimer_email
                )
                db.add(manager_notification)
        
        db.commit()
        
        # Update session with pending claim
        if 'pending_claims' not in session:
            session['pending_claims'] = []
        if idea_id not in session['pending_claims']:
            session['pending_claims'].append(idea_id)
        
        session.permanent = True
        
        return jsonify({'success': True, 'message': 'Claim request submitted! Waiting for approvals.'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()