from flask import Blueprint, request, jsonify
from models import Idea, Claim, IdeaStatus
from database import get_db
from utils.email import send_claim_notification

claims_bp = Blueprint('claims', __name__)

@claims_bp.route('/api/ideas/<int:idea_id>/claim', methods=['POST'])
def claim_idea(idea_id):
    db = next(get_db())
    try:
        idea = db.query(Idea).filter_by(id=idea_id).first()
        if not idea:
            return jsonify({'error': 'Idea not found'}), 404
        
        if idea.status != IdeaStatus.OPEN:
            return jsonify({'error': 'Idea is not available for claiming'}), 400
        
        data = request.json
        
        claim = Claim(
            idea_id=idea_id,
            claimer_name=data['claimer_name'],
            claimer_email=data['claimer_email'],
            claimer_skills=data.get('claimer_skills'),
            claimer_team=data.get('claimer_team')
        )
        
        idea.status = IdeaStatus.CLAIMED
        
        db.add(claim)
        db.commit()
        
        send_claim_notification(
            idea_owner_email=idea.email,
            idea_title=idea.title,
            claimer_name=claim.claimer_name,
            claimer_skills=claim.claimer_skills,
            claimer_team=claim.claimer_team
        )
        
        return jsonify({
            'id': claim.id,
            'idea_id': claim.idea_id,
            'claimer_name': claim.claimer_name,
            'claimer_email': claim.claimer_email,
            'claimer_skills': claim.claimer_skills,
            'claimer_team': claim.claimer_team,
            'claim_date': claim.claim_date.isoformat()
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()

@claims_bp.route('/api/ideas/<int:idea_id>/complete', methods=['POST'])
def complete_idea(idea_id):
    db = next(get_db())
    try:
        idea = db.query(Idea).filter_by(id=idea_id).first()
        if not idea:
            return jsonify({'error': 'Idea not found'}), 404
        
        if idea.status != IdeaStatus.CLAIMED:
            return jsonify({'error': 'Idea is not claimed'}), 400
        
        idea.status = IdeaStatus.COMPLETE
        db.commit()
        
        return jsonify({
            'id': idea.id,
            'status': idea.status.value
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.close()