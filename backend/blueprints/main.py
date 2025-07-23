from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import get_session
from models import Idea, Skill, Claim, IdeaStatus, PriorityLevel, IdeaSize
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
            reward = request.form.get('reward')
            if reward:
                idea.reward = reward
                
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
    
    return render_template('submit.html')

@main_bp.route('/my-ideas')
@require_verified_email
def my_ideas():
    """Show ideas submitted by the current user."""
    return render_template('my_ideas.html')

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
    """Claim an idea."""
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
        
        # Create claim
        claim = Claim(
            idea_id=idea_id,
            claimer_name=session.get('user_name') or request.form.get('name'),  # Use session name if available
            claimer_email=session.get('user_email'),  # Use session email
            claimer_team=request.form.get('team'),
            claimer_skills=request.form.get('skills'),
            claim_date=datetime.now()
        )
        
        # Update idea status
        idea.status = IdeaStatus.claimed
        
        db.add(claim)
        db.commit()
        
        # Update session with claimed idea
        if 'claimed_ideas' not in session:
            session['claimed_ideas'] = []
        if idea_id not in session['claimed_ideas']:
            session['claimed_ideas'].append(idea_id)
        
        session.permanent = True
        
        # Send email notification
        try:
            send_claim_notification(idea, claim)
        except:
            pass  # Don't fail if email doesn't work
        
        return jsonify({'success': True, 'message': 'Idea claimed successfully!'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()