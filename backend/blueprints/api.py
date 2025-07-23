from flask import Blueprint, jsonify, request, session
from database import get_session
from models import Idea, Skill, Claim, IdeaStatus, PriorityLevel, IdeaSize
from sqlalchemy import desc, asc, func
from datetime import datetime

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
        
        status_filter = request.args.get('status', 'open')
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
                'benefactor_team': idea.benefactor_team,
                'priority': idea.priority.value,
                'size': idea.size.value,
                'status': idea.status.value,
                'reward': idea.reward,
                'needed_by': idea.needed_by.strftime('%Y-%m-%d') if idea.needed_by else None,
                'date_submitted': idea.date_submitted.strftime('%Y-%m-%d'),
                'skills': [{'id': s.id, 'name': s.name} for s in idea.skills],
                'claims': [{'name': c.claimer_name, 'date': c.claim_date.strftime('%Y-%m-%d')} for c in idea.claims]
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

@api_bp.route('/stats')
def get_stats():
    """Get dashboard statistics."""
    db = get_session()
    try:
        stats = {
            'total_ideas': db.query(Idea).count(),
            'open_ideas': db.query(Idea).filter_by(status=IdeaStatus.open).count(),
            'claimed_ideas': db.query(Idea).filter_by(status=IdeaStatus.claimed).count(),
            'complete_ideas': db.query(Idea).filter_by(status=IdeaStatus.complete).count(),
            'total_skills': db.query(Skill).count()
        }
        return jsonify(stats)
    finally:
        db.close()

@api_bp.route('/my-ideas')
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
        
        # Sort ideas by date (newest first)
        sorted_items = sorted(
            ideas_dict.values(), 
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
                'priority': idea.priority.value,
                'size': idea.size.value,
                'status': idea.status.value,
                'benefactor_team': idea.benefactor_team,
                'date_submitted': idea.date_submitted.strftime('%Y-%m-%d'),
                'skills': [{'id': s.id, 'name': s.name} for s in idea.skills],
                'relationship': item['relationship'],
                'claim_info': claim_info
            }
            ideas_data.append(idea_dict)
        
        return jsonify(ideas_data)
    finally:
        db.close()