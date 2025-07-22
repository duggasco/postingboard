from flask import Blueprint, jsonify, request
from models import Skill
from database import get_db
from routes.auth import require_admin

skills_bp = Blueprint('skills', __name__)

@skills_bp.route('/api/skills', methods=['GET'])
def get_skills():
    db = next(get_db())
    try:
        skills = db.query(Skill).order_by(Skill.name).all()
        return jsonify([{
            'id': skill.id,
            'name': skill.name
        } for skill in skills])
    finally:
        db.close()

@skills_bp.route('/api/admin/skills', methods=['POST'])
@require_admin
def create_skill():
    db = next(get_db())
    try:
        data = request.json
        skill_name = data.get('name')
        
        if not skill_name:
            return jsonify({'error': 'Skill name is required'}), 400
        
        # Check if skill already exists
        existing_skill = db.query(Skill).filter_by(name=skill_name).first()
        if existing_skill:
            return jsonify({'error': 'Skill already exists'}), 400
        
        skill = Skill(name=skill_name)
        db.add(skill)
        db.commit()
        
        return jsonify({
            'id': skill.id,
            'name': skill.name
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()

@skills_bp.route('/api/admin/skills/<int:skill_id>', methods=['PUT'])
@require_admin
def update_skill(skill_id):
    db = next(get_db())
    try:
        skill = db.query(Skill).filter_by(id=skill_id).first()
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        data = request.json
        new_name = data.get('name')
        
        if not new_name:
            return jsonify({'error': 'Skill name is required'}), 400
        
        # Check if another skill already has this name
        existing_skill = db.query(Skill).filter_by(name=new_name).filter(Skill.id != skill_id).first()
        if existing_skill:
            return jsonify({'error': 'Another skill with this name already exists'}), 400
        
        skill.name = new_name
        db.commit()
        
        return jsonify({
            'id': skill.id,
            'name': skill.name
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()

@skills_bp.route('/api/admin/skills/<int:skill_id>', methods=['DELETE'])
@require_admin
def delete_skill(skill_id):
    db = next(get_db())
    try:
        skill = db.query(Skill).filter_by(id=skill_id).first()
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        # Check if skill is being used by any ideas
        if skill.ideas:
            return jsonify({'error': f'Cannot delete skill. It is used by {len(skill.ideas)} ideas.'}), 400
        
        db.delete(skill)
        db.commit()
        
        return jsonify({'message': 'Skill deleted successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()