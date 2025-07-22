from flask import Blueprint, request, jsonify
from datetime import datetime
from models import Idea, Skill, IdeaSize, PriorityLevel, IdeaStatus
from database import get_db
from routes.auth import require_admin

ideas_bp = Blueprint('ideas', __name__)

@ideas_bp.route('/api/ideas', methods=['GET'])
def get_ideas():
    db = next(get_db())
    try:
        sort_by = request.args.get('sort_by', 'date_submitted')
        order = request.args.get('order', 'desc')
        
        query = db.query(Idea)
        
        filter_skill = request.args.get('skill')
        if filter_skill:
            query = query.join(Idea.skills).filter(Skill.name == filter_skill)
        
        filter_priority = request.args.get('priority')
        if filter_priority:
            query = query.filter(Idea.priority == PriorityLevel(filter_priority))
        
        filter_team = request.args.get('team')
        if filter_team:
            query = query.filter(Idea.benefactor_team == filter_team)
        
        filter_status = request.args.get('status')
        if filter_status:
            query = query.filter(Idea.status == IdeaStatus(filter_status))
        
        if sort_by == 'date_submitted':
            query = query.order_by(Idea.date_submitted.desc() if order == 'desc' else Idea.date_submitted)
        elif sort_by == 'needed_by':
            query = query.order_by(Idea.needed_by.desc() if order == 'desc' else Idea.needed_by)
        elif sort_by == 'priority':
            # Custom priority ordering: high=3, medium=2, low=1
            from sqlalchemy import case
            priority_order = case(
                (Idea.priority == PriorityLevel.high, 3),
                (Idea.priority == PriorityLevel.medium, 2),
                (Idea.priority == PriorityLevel.low, 1),
                else_=0
            )
            query = query.order_by(priority_order.desc() if order == 'desc' else priority_order)
        
        ideas = query.all()
        
        return jsonify([{
            'id': idea.id,
            'title': idea.title,
            'description': idea.description,
            'email': idea.email,
            'benefactor_team': idea.benefactor_team,
            'size': idea.size.value,
            'reward': idea.reward,
            'needed_by': idea.needed_by.isoformat(),
            'priority': idea.priority.value,
            'status': idea.status.value,
            'date_submitted': idea.date_submitted.isoformat(),
            'skills': [skill.name for skill in idea.skills],
            'claims': [{
                'id': claim.id,
                'claimer_name': claim.claimer_name,
                'claimer_email': claim.claimer_email,
                'claimer_skills': claim.claimer_skills,
                'claimer_team': claim.claimer_team,
                'claim_date': claim.claim_date.isoformat()
            } for claim in idea.claims]
        } for idea in ideas])
    finally:
        db.close()

@ideas_bp.route('/api/ideas', methods=['POST'])
def create_idea():
    db = next(get_db())
    try:
        data = request.json
        print(f"Received data: {data}")  # Debug logging
        
        idea = Idea(
            title=data['title'],
            description=data['description'],
            email=data['email'],
            benefactor_team=data['benefactor_team'],
            size=IdeaSize(data['size']),
            reward=data.get('reward'),
            needed_by=datetime.fromisoformat(data['needed_by']),
            priority=PriorityLevel(data['priority'])
        )
        
        skill_names = data.get('skills', [])
        for skill_name in skill_names:
            skill = db.query(Skill).filter_by(name=skill_name).first()
            if not skill:
                skill = Skill(name=skill_name)
                db.add(skill)
            idea.skills.append(skill)
        
        db.add(idea)
        db.commit()
        
        return jsonify({
            'id': idea.id,
            'title': idea.title,
            'description': idea.description,
            'email': idea.email,
            'benefactor_team': idea.benefactor_team,
            'size': idea.size.value,
            'reward': idea.reward,
            'needed_by': idea.needed_by.isoformat(),
            'priority': idea.priority.value,
            'status': idea.status.value,
            'date_submitted': idea.date_submitted.isoformat(),
            'skills': [skill.name for skill in idea.skills]
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()

@ideas_bp.route('/api/ideas/<int:idea_id>', methods=['GET'])
def get_idea(idea_id):
    db = next(get_db())
    try:
        idea = db.query(Idea).filter_by(id=idea_id).first()
        if not idea:
            return jsonify({'error': 'Idea not found'}), 404
        
        return jsonify({
            'id': idea.id,
            'title': idea.title,
            'description': idea.description,
            'email': idea.email,
            'benefactor_team': idea.benefactor_team,
            'size': idea.size.value,
            'reward': idea.reward,
            'needed_by': idea.needed_by.isoformat(),
            'priority': idea.priority.value,
            'status': idea.status.value,
            'date_submitted': idea.date_submitted.isoformat(),
            'skills': [skill.name for skill in idea.skills],
            'claims': [{
                'id': claim.id,
                'claimer_name': claim.claimer_name,
                'claimer_email': claim.claimer_email,
                'claimer_skills': claim.claimer_skills,
                'claimer_team': claim.claimer_team,
                'claim_date': claim.claim_date.isoformat()
            } for claim in idea.claims]
        })
    finally:
        db.close()

@ideas_bp.route('/api/admin/ideas/<int:idea_id>', methods=['PUT'])
@require_admin
def update_idea(idea_id):
    db = next(get_db())
    try:
        idea = db.query(Idea).filter_by(id=idea_id).first()
        if not idea:
            return jsonify({'error': 'Idea not found'}), 404
        
        data = request.json
        
        # Update basic fields
        if 'title' in data:
            idea.title = data['title']
        if 'description' in data:
            idea.description = data['description']
        if 'email' in data:
            idea.email = data['email']
        if 'benefactor_team' in data:
            idea.benefactor_team = data['benefactor_team']
        if 'size' in data:
            idea.size = IdeaSize(data['size'])
        if 'reward' in data:
            idea.reward = data['reward']
        if 'needed_by' in data:
            idea.needed_by = datetime.fromisoformat(data['needed_by'])
        if 'priority' in data:
            idea.priority = PriorityLevel(data['priority'])
        if 'status' in data:
            idea.status = IdeaStatus(data['status'])
        
        # Update skills if provided
        if 'skills' in data:
            # Clear existing skills
            idea.skills.clear()
            
            # Add new skills
            skill_names = data['skills']
            for skill_name in skill_names:
                skill = db.query(Skill).filter_by(name=skill_name).first()
                if not skill:
                    skill = Skill(name=skill_name)
                    db.add(skill)
                idea.skills.append(skill)
        
        db.commit()
        
        return jsonify({
            'id': idea.id,
            'title': idea.title,
            'description': idea.description,
            'email': idea.email,
            'benefactor_team': idea.benefactor_team,
            'size': idea.size.value,
            'reward': idea.reward,
            'needed_by': idea.needed_by.isoformat(),
            'priority': idea.priority.value,
            'status': idea.status.value,
            'date_submitted': idea.date_submitted.isoformat(),
            'skills': [skill.name for skill in idea.skills],
            'claims': [{
                'id': claim.id,
                'claimer_name': claim.claimer_name,
                'claimer_email': claim.claimer_email,
                'claimer_skills': claim.claimer_skills,
                'claimer_team': claim.claimer_team,
                'claim_date': claim.claim_date.isoformat()
            } for claim in idea.claims]
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()

@ideas_bp.route('/api/admin/ideas/<int:idea_id>', methods=['DELETE'])
@require_admin
def delete_idea(idea_id):
    db = next(get_db())
    try:
        idea = db.query(Idea).filter_by(id=idea_id).first()
        if not idea:
            return jsonify({'error': 'Idea not found'}), 404
        
        # Delete the idea (cascade will handle related claims)
        db.delete(idea)
        db.commit()
        
        return jsonify({'message': 'Idea deleted successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()