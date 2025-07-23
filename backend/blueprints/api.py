from flask import Blueprint, jsonify, request, session
from database import get_session
from models import Idea, Skill, Team, Claim, IdeaStatus, PriorityLevel, IdeaSize, EmailSettings, UserProfile
from sqlalchemy import desc, asc, func
from datetime import datetime
from decorators import require_verified_email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

api_bp = Blueprint('api', __name__)

@api_bp.route('/ideas')
def get_ideas():
    """Get filtered and sorted ideas."""
    db = get_session()
    try:
        query = db.query(Idea)
        
        # Apply filters
        skill_filter = request.args.get('skill')
        if skill_filter:
            query = query.join(Idea.skills).filter(Skill.id == int(skill_filter))
        
        priority_filter = request.args.get('priority')
        if priority_filter:
            query = query.filter(Idea.priority == PriorityLevel(priority_filter))
        
        status_filter = request.args.get('status')
        if status_filter:
            query = query.filter(Idea.status == IdeaStatus(status_filter))
        
        # Apply sorting
        sort_by = request.args.get('sort', 'date_desc')
        if sort_by == 'date_desc':
            query = query.order_by(desc(Idea.date_submitted))
        elif sort_by == 'date_asc':
            query = query.order_by(asc(Idea.date_submitted))
        elif sort_by == 'priority':
            query = query.order_by(desc(Idea.priority))
        elif sort_by == 'size':
            query = query.order_by(asc(Idea.size))
        
        ideas = query.all()
        
        # Serialize ideas
        ideas_data = []
        for idea in ideas:
            idea_dict = {
                'id': idea.id,
                'title': idea.title,
                'description': idea.description,
                'email': idea.email,
                'submitter_name': idea.submitter.name if idea.submitter else None,
                'benefactor_team': idea.benefactor_team,
                'priority': idea.priority.value,
                'size': idea.size.value,
                'status': idea.status.value,
                'reward': idea.reward,
                'needed_by': idea.needed_by.strftime('%Y-%m-%d') if idea.needed_by else None,
                'date_submitted': idea.date_submitted.strftime('%Y-%m-%d'),
                'skills': [{'id': s.id, 'name': s.name} for s in idea.skills],
                'claims': [{'name': c.claimer_name, 'email': c.claimer_email, 'date': c.claim_date.strftime('%Y-%m-%d')} for c in idea.claims]
            }
            ideas_data.append(idea_dict)
        
        return jsonify(ideas_data)
    finally:
        db.close()

@api_bp.route('/skills')
def get_skills():
    """Get all skills."""
    db = get_session()
    try:
        skills = db.query(Skill).order_by(Skill.name).all()
        return jsonify([{'id': s.id, 'name': s.name} for s in skills])
    finally:
        db.close()

@api_bp.route('/skills', methods=['POST'])
def add_skill():
    """Add a new skill (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        name = request.json.get('name')
        if not name:
            return jsonify({'success': False, 'message': 'Name is required'}), 400
        
        # Check if skill already exists
        existing = db.query(Skill).filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Skill already exists'}), 400
        
        skill = Skill(name=name)
        db.add(skill)
        db.commit()
        
        return jsonify({'success': True, 'skill': {'id': skill.id, 'name': skill.name}})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/skills/<int:skill_id>', methods=['PUT'])
def update_skill(skill_id):
    """Update a skill (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        skill = db.query(Skill).get(skill_id)
        if not skill:
            return jsonify({'success': False, 'message': 'Skill not found'}), 404
        
        name = request.json.get('name')
        if name:
            skill.name = name
        
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/skills/<int:skill_id>', methods=['DELETE'])
def delete_skill(skill_id):
    """Delete a skill (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        skill = db.query(Skill).get(skill_id)
        if not skill:
            return jsonify({'success': False, 'message': 'Skill not found'}), 404
        
        # Check if skill is in use
        if skill.ideas:
            return jsonify({'success': False, 'message': 'Cannot delete skill that is in use'}), 400
        
        db.delete(skill)
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/teams')
def get_teams():
    """Get teams - all for admin, approved only for others."""
    db = get_session()
    try:
        if session.get('is_admin'):
            # Admin sees all teams with approval status
            teams = db.query(Team).order_by(Team.name).all()
            return jsonify([{'id': t.id, 'name': t.name, 'is_approved': t.is_approved} for t in teams])
        else:
            # Non-admin users only see approved teams
            teams = db.query(Team).filter(Team.is_approved == True).order_by(Team.name).all()
            return jsonify([{'id': t.id, 'name': t.name} for t in teams])
    finally:
        db.close()

@api_bp.route('/teams', methods=['POST'])
def add_team():
    """Add a new team (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        name = request.json.get('name')
        if not name:
            return jsonify({'success': False, 'message': 'Name is required'}), 400
        
        # Check if team already exists
        existing = db.query(Team).filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Team already exists'}), 400
        
        team = Team(name=name, is_approved=True)
        db.add(team)
        db.commit()
        return jsonify({'success': True, 'id': team.id})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/teams/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    """Update a team (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        team = db.query(Team).get(team_id)
        if not team:
            return jsonify({'success': False, 'message': 'Team not found'}), 404
        
        name = request.json.get('name')
        if name:
            team.name = name
        
        is_approved = request.json.get('is_approved')
        if is_approved is not None:
            team.is_approved = is_approved
        
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/teams/<int:team_id>', methods=['DELETE'])
def delete_team(team_id):
    """Delete a team (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        team = db.query(Team).get(team_id)
        if not team:
            return jsonify({'success': False, 'message': 'Team not found'}), 404
        
        # Check if team is in use by users
        if team.users:
            return jsonify({'success': False, 'message': 'Cannot delete team that has users'}), 400
        
        db.delete(team)
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/ideas/<int:idea_id>', methods=['PUT'])
def update_idea(idea_id):
    """Update an idea (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        idea = db.query(Idea).get(idea_id)
        if not idea:
            return jsonify({'success': False, 'message': 'Idea not found'}), 404
        
        data = request.json
        if 'title' in data:
            idea.title = data['title']
        if 'team' in data:
            idea.benefactor_team = data['team']
        if 'priority' in data:
            idea.priority = PriorityLevel(data['priority'])
        if 'size' in data:
            idea.size = IdeaSize(data['size'])
        if 'status' in data:
            idea.status = IdeaStatus(data['status'])
        if 'email' in data:
            idea.email = data['email']
        
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/ideas/<int:idea_id>', methods=['DELETE'])
def delete_idea(idea_id):
    """Delete an idea (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        idea = db.query(Idea).get(idea_id)
        if not idea:
            return jsonify({'success': False, 'message': 'Idea not found'}), 404
        
        db.delete(idea)
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/ideas/<int:idea_id>/unclaim', methods=['POST'])
def unclaim_idea(idea_id):
    """Unclaim an idea by removing all claims (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        idea = db.query(Idea).get(idea_id)
        if not idea:
            return jsonify({'success': False, 'message': 'Idea not found'}), 404
        
        # Delete all claims for this idea
        claims_deleted = db.query(Claim).filter(Claim.idea_id == idea_id).delete()
        
        # Reset idea status to open
        idea.status = IdeaStatus.open
        
        db.commit()
        return jsonify({
            'success': True,
            'message': f'Unclaimed idea and removed {claims_deleted} claim(s)'
        })
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/stats')
def get_stats():
    """Get dashboard statistics."""
    db = get_session()
    try:
        stats = {
            'total_ideas': db.query(Idea).count(),
            'open_ideas': db.query(Idea).filter(Idea.status == IdeaStatus.open).count(),
            'claimed_ideas': db.query(Idea).filter(Idea.status == IdeaStatus.claimed).count(),
            'complete_ideas': db.query(Idea).filter(Idea.status == IdeaStatus.complete).count(),
            'total_skills': db.query(Skill).count()
        }
        return jsonify(stats)
    finally:
        db.close()

@api_bp.route('/my-ideas')
@require_verified_email
def get_my_ideas():
    """Get ideas submitted or claimed by the current user."""
    db = get_session()
    try:
        # Check if email parameter is provided (for email lookup)
        email_param = request.args.get('email')
        
        # Dictionary to track ideas and their relationship to user
        ideas_dict = {}
        
        if email_param:
            # Email lookup mode - search by email for both submitted and claimed
            # Get submitted ideas
            submitted_ideas = db.query(Idea).filter(
                Idea.email == email_param
            ).all()
            
            for idea in submitted_ideas:
                ideas_dict[idea.id] = {
                    'idea': idea,
                    'relationship': 'submitted'
                }
            
            # Get claimed ideas
            claimed_ideas = db.query(Idea).join(Claim).filter(
                Claim.claimer_email == email_param
            ).all()
            
            for idea in claimed_ideas:
                if idea.id in ideas_dict:
                    # User both submitted and claimed this idea
                    ideas_dict[idea.id]['relationship'] = 'both'
                else:
                    ideas_dict[idea.id] = {
                        'idea': idea,
                        'relationship': 'claimed'
                    }
        else:
            # Session mode - search by session IDs or stored email
            idea_ids = session.get('submitted_ideas', [])
            user_email = session.get('user_email')
            claimed_idea_ids = session.get('claimed_ideas', [])
            
            # For admin, show all their activities
            if session.get('is_admin'):
                user_email = 'admin@system.local'
            
            if idea_ids or user_email:
                query = db.query(Idea)
                conditions = []
                
                if idea_ids:
                    conditions.append(Idea.id.in_(idea_ids))
                if user_email:
                    conditions.append(Idea.email == user_email)
                
                if conditions:
                    from sqlalchemy import or_
                    query = query.filter(or_(*conditions))
                    submitted_ideas = query.all()
                    
                    for idea in submitted_ideas:
                        ideas_dict[idea.id] = {
                            'idea': idea,
                            'relationship': 'submitted'
                        }
            
            # Get claimed ideas from session or by email
            if claimed_idea_ids or user_email:
                conditions = []
                
                if claimed_idea_ids:
                    conditions.append(Idea.id.in_(claimed_idea_ids))
                if user_email:
                    # Also get ideas claimed by this email
                    claimed_by_email = db.query(Idea).join(Claim).filter(
                        Claim.claimer_email == user_email
                    ).all()
                    
                    for idea in claimed_by_email:
                        if idea.id in ideas_dict:
                            ideas_dict[idea.id]['relationship'] = 'both'
                        else:
                            ideas_dict[idea.id] = {
                                'idea': idea,
                                'relationship': 'claimed'
                            }
                
                if claimed_idea_ids:
                    # Get ideas by claimed IDs from session
                    claimed_ideas = db.query(Idea).filter(
                        Idea.id.in_(claimed_idea_ids)
                    ).all()
                    
                    for idea in claimed_ideas:
                        if idea.id in ideas_dict:
                            if ideas_dict[idea.id]['relationship'] == 'submitted':
                                ideas_dict[idea.id]['relationship'] = 'both'
                        else:
                            ideas_dict[idea.id] = {
                                'idea': idea,
                                'relationship': 'claimed'
                            }
        
        # Get team members' ideas if user is a manager
        team_ideas_dict = {}
        if session.get('user_role') == 'manager' and session.get('user_managed_team_id'):
            managed_team_id = session.get('user_managed_team_id')
            
            # Get all users in the managed team
            from models import UserProfile
            team_members = db.query(UserProfile).filter(
                UserProfile.team_id == managed_team_id,
                UserProfile.email != session.get('user_email')  # Exclude the manager
            ).all()
            
            for member in team_members:
                # Get ideas submitted by team members
                member_submitted = db.query(Idea).filter(
                    Idea.email == member.email
                ).all()
                
                for idea in member_submitted:
                    team_ideas_dict[idea.id] = {
                        'idea': idea,
                        'relationship': 'team_submitted',
                        'member_name': member.name,
                        'member_email': member.email
                    }
                
                # Get ideas claimed by team members
                member_claimed = db.query(Idea).join(Claim).filter(
                    Claim.claimer_email == member.email
                ).all()
                
                for idea in member_claimed:
                    if idea.id in team_ideas_dict:
                        team_ideas_dict[idea.id]['relationship'] = 'team_both'
                    else:
                        team_ideas_dict[idea.id] = {
                            'idea': idea,
                            'relationship': 'team_claimed',
                            'member_name': member.name,
                            'member_email': member.email
                        }
        
        # Sort ideas by date (newest first)
        sorted_items = sorted(
            ideas_dict.values(), 
            key=lambda x: x['idea'].date_submitted, 
            reverse=True
        )
        
        sorted_team_items = sorted(
            team_ideas_dict.values(),
            key=lambda x: x['idea'].date_submitted,
            reverse=True
        )
        
        # Serialize ideas
        ideas_data = []
        for item in sorted_items:
            idea = item['idea']
            
            # Get claim info if this is a claimed idea
            claim_info = None
            if item['relationship'] in ['claimed', 'both']:
                claim = db.query(Claim).filter(
                    Claim.idea_id == idea.id,
                    Claim.claimer_email == (email_param or user_email)
                ).first()
                if claim:
                    claim_info = {
                        'claim_date': claim.claim_date.strftime('%Y-%m-%d'),
                        'claimer_team': claim.claimer_team
                    }
            
            idea_dict = {
                'id': idea.id,
                'title': idea.title,
                'description': idea.description,
                'email': idea.email,
                'submitter_name': idea.submitter.name if idea.submitter else None,
                'priority': idea.priority.value,
                'size': idea.size.value,
                'status': idea.status.value,
                'benefactor_team': idea.benefactor_team,
                'date_submitted': idea.date_submitted.strftime('%Y-%m-%d'),
                'skills': [{'id': s.id, 'name': s.name} for s in idea.skills],
                'claims': [{'name': c.claimer_name, 'email': c.claimer_email, 'date': c.claim_date.strftime('%Y-%m-%d')} for c in idea.claims],
                'relationship': item['relationship'],
                'claim_info': claim_info
            }
            ideas_data.append(idea_dict)
        
        # Serialize team ideas
        team_ideas_data = []
        for item in sorted_team_items:
            idea = item['idea']
            
            # Get claim info for team member claims
            claim_info = None
            if item['relationship'] in ['team_claimed', 'team_both']:
                claim = db.query(Claim).filter(
                    Claim.idea_id == idea.id,
                    Claim.claimer_email == item.get('member_email')
                ).first()
                if claim:
                    claim_info = {
                        'claim_date': claim.claim_date.strftime('%Y-%m-%d'),
                        'claimer_team': claim.claimer_team
                    }
            
            idea_dict = {
                'id': idea.id,
                'title': idea.title,
                'description': idea.description,
                'email': idea.email,
                'submitter_name': idea.submitter.name if idea.submitter else None,
                'priority': idea.priority.value,
                'size': idea.size.value,
                'status': idea.status.value,
                'benefactor_team': idea.benefactor_team,
                'date_submitted': idea.date_submitted.strftime('%Y-%m-%d'),
                'skills': [{'id': s.id, 'name': s.name} for s in idea.skills],
                'claims': [{'name': c.claimer_name, 'email': c.claimer_email, 'date': c.claim_date.strftime('%Y-%m-%d')} for c in idea.claims],
                'relationship': item['relationship'],
                'member_name': item.get('member_name'),
                'member_email': item.get('member_email'),
                'claim_info': claim_info
            }
            team_ideas_data.append(idea_dict)
        
        return jsonify({
            'user_ideas': ideas_data,
            'team_ideas': team_ideas_data,
            'managed_team': session.get('user_managed_team')
        })
    finally:
        db.close()

@api_bp.route("/admin/email-settings", methods=["GET"])
def get_email_settings():
    """Get email settings (admin only)."""
    if not session.get("is_admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    db = get_session()
    try:
        settings = db.query(EmailSettings).filter_by(is_active=True).first()
        if settings:
            return jsonify({
                "success": True,
                "settings": {
                    "smtp_server": settings.smtp_server,
                    "smtp_port": settings.smtp_port,
                    "smtp_username": settings.smtp_username,
                    "smtp_password": settings.smtp_password,
                    "smtp_use_tls": settings.smtp_use_tls,
                    "from_email": settings.from_email,
                    "from_name": settings.from_name
                }
            })
        else:
            return jsonify({
                "success": True,
                "settings": {
                    "smtp_server": "",
                    "smtp_port": 587,
                    "smtp_username": "",
                    "smtp_password": "",
                    "smtp_use_tls": True,
                    "from_email": "",
                    "from_name": "Posting Board"
                }
            })
    finally:
        db.close()

@api_bp.route("/admin/email-settings", methods=["POST"])
def save_email_settings():
    """Save email settings (admin only)."""
    if not session.get("is_admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    db = get_session()
    try:
        data = request.json
        
        # Get existing settings or create new
        settings = db.query(EmailSettings).filter_by(is_active=True).first()
        if not settings:
            settings = EmailSettings()
            db.add(settings)
        
        # Update settings
        settings.smtp_server = data.get("smtp_server", "")
        settings.smtp_port = data.get("smtp_port", 587)
        settings.smtp_username = data.get("smtp_username", "")
        settings.smtp_password = data.get("smtp_password", "")
        settings.smtp_use_tls = data.get("smtp_use_tls", True)
        settings.from_email = data.get("from_email", "")
        settings.from_name = data.get("from_name", "Posting Board")
        settings.is_active = True
        
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@api_bp.route('/admin/manager-requests')
def get_manager_requests():
    """Get pending manager requests and current managers (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        from models import ManagerRequest
        
        # Get pending requests
        pending_requests = db.query(ManagerRequest).filter_by(status='pending').order_by(ManagerRequest.requested_at.desc()).all()
        
        # Get current managers
        current_managers = db.query(UserProfile).filter(
            UserProfile.managed_team_id != None,
            UserProfile.role == 'manager'
        ).all()
        
        # Serialize pending requests
        pending_data = []
        for req in pending_requests:
            pending_data.append({
                'id': req.id,
                'user_name': req.user.name if req.user else 'N/A',
                'user_email': req.user_email,
                'team_name': req.team.name if req.team else 'N/A',
                'requested_at': req.requested_at.strftime('%Y-%m-%d %H:%M:%S') if req.requested_at else None
            })
        
        # Serialize current managers
        managers_data = []
        for manager in current_managers:
            managers_data.append({
                'name': manager.name,
                'email': manager.email,
                'managed_team': manager.managed_team.name if manager.managed_team else 'N/A',
                'last_updated': manager.last_verified_at.strftime('%Y-%m-%d') if manager.last_verified_at else None
            })
        
        return jsonify({
            'pending': pending_data,
            'managers': managers_data
        })
    finally:
        db.close()

@api_bp.route('/admin/manager-requests/<int:request_id>/approve', methods=['POST'])
def approve_manager_request(request_id):
    """Approve a manager request (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        from models import ManagerRequest
        
        manager_request = db.query(ManagerRequest).get(request_id)
        if not manager_request:
            return jsonify({'success': False, 'message': 'Request not found'}), 404
        
        if manager_request.status != 'pending':
            return jsonify({'success': False, 'message': 'Request already processed'}), 400
        
        # Update the request
        manager_request.status = 'approved'
        manager_request.processed_at = datetime.now()
        manager_request.processed_by = session.get('user_email', 'admin@system.local')
        
        # Update the user's managed_team_id
        user = db.query(UserProfile).filter_by(email=manager_request.user_email).first()
        if user:
            user.managed_team_id = manager_request.requested_team_id
        
        db.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/admin/manager-requests/<int:request_id>/deny', methods=['POST'])
def deny_manager_request(request_id):
    """Deny a manager request (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        from models import ManagerRequest
        
        manager_request = db.query(ManagerRequest).get(request_id)
        if not manager_request:
            return jsonify({'success': False, 'message': 'Request not found'}), 404
        
        if manager_request.status != 'pending':
            return jsonify({'success': False, 'message': 'Request already processed'}), 400
        
        # Update the request
        manager_request.status = 'denied'
        manager_request.processed_at = datetime.now()
        manager_request.processed_by = session.get('user_email', 'admin@system.local')
        
        db.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/admin/remove-manager', methods=['POST'])
def remove_manager():
    """Remove a manager from their team (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        email = request.json.get('email')
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        user = db.query(UserProfile).filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Remove managed team
        user.managed_team_id = None
        
        db.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route("/admin/test-email", methods=["POST"])
def test_email():
    """Send a test email (admin only)."""
    if not session.get("is_admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    db = get_session()
    try:
        test_email_address = request.json.get("email")
        if not test_email_address:
            return jsonify({"success": False, "error": "Email address is required"}), 400
        
        # Get email settings
        settings = db.query(EmailSettings).filter_by(is_active=True).first()
        if not settings or not settings.smtp_server:
            return jsonify({"success": False, "error": "Email settings not configured"}), 400
        
        # Send test email
        try:
            msg = MIMEMultipart()
            msg["From"] = f"{settings.from_name} <{settings.from_email}>"
            msg["To"] = test_email_address
            msg["Subject"] = "Test Email from Posting Board"
            
            body = """This is a test email from your Posting Board application.
            
If you received this email, your email settings are configured correctly\!

Best regards,
Posting Board Admin"""
            
            msg.attach(MIMEText(body, "plain"))
            
            server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            
            server.send_message(msg)
            server.quit()
            
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to send email: {str(e)}"}), 500
    finally:
        db.close()
