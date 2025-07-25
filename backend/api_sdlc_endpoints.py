# SDLC Tracking API Endpoints
# This file contains the API endpoints for enhanced SDLC tracking features

from flask import request, jsonify, session
from datetime import datetime
from database import get_session
from models import (
    UserProfile, Idea, SubStatus, StatusHistory, 
    IdeaComment, IdeaActivity, ActivityType,
    IdeaExternalLink, ExternalLinkType
)

def register_sdlc_endpoints(api_bp):
    """Register SDLC tracking endpoints with the API blueprint."""
    
    @api_bp.route('/ideas/<int:idea_id>/sub-status', methods=['PUT'])
    def update_idea_sub_status(idea_id):
        """Update idea sub-status and related fields."""
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        db = get_session()
        try:
            idea = db.query(Idea).get(idea_id)
            if not idea:
                return jsonify({'success': False, 'error': 'Idea not found'}), 404
            
            # Check permissions
            is_claimer = any(claim.claimer_email == user_email for claim in idea.claims)
            is_admin = session.get('is_admin', False)
            is_team_manager = False
            
            if session.get('user_managed_team_id'):
                # Check if any claimer is from manager's team
                for claim in idea.claims:
                    claimer = db.query(UserProfile).filter_by(email=claim.claimer_email).first()
                    if claimer and claimer.team_id == session.get('user_managed_team_id'):
                        is_team_manager = True
                        break
            
            if not (is_claimer or is_admin or is_team_manager):
                return jsonify({'success': False, 'error': 'You do not have permission to update this idea'}), 403
            
            data = request.get_json()
            
            # Create status history entry
            history = StatusHistory(
                idea_id=idea_id,
                from_status=idea.status,
                to_status=idea.status,  # Status doesn't change, only sub-status
                from_sub_status=idea.sub_status,
                to_sub_status=SubStatus(data['sub_status']) if data.get('sub_status') else None,
                changed_by=user_email,
                comment=data.get('comment')
            )
            
            # Calculate duration in previous status
            if idea.sub_status_updated_at:
                history.duration_minutes = int((datetime.now() - idea.sub_status_updated_at).total_seconds() / 60)
            
            db.add(history)
            
            # Update idea fields
            idea.sub_status = SubStatus(data['sub_status']) if data.get('sub_status') else None
            idea.sub_status_updated_at = datetime.now()
            idea.sub_status_updated_by = user_email
            idea.progress_percentage = data.get('progress_percentage', 0)
            
            if data.get('blocked_reason'):
                idea.blocked_reason = data['blocked_reason']
            elif idea.sub_status not in [SubStatus.blocked, SubStatus.on_hold]:
                idea.blocked_reason = None  # Clear if not blocked
            
            if data.get('expected_completion'):
                idea.expected_completion = datetime.strptime(data['expected_completion'], '%Y-%m-%d')
            
            # Create activity entry
            activity = IdeaActivity(
                idea_id=idea_id,
                activity_type=ActivityType.status_change,
                actor_email=user_email,
                actor_name=session.get('user_name', user_email),
                description=f"updated status to {data['sub_status'].replace('_', ' ').title()}"
            )
            db.add(activity)
            
            db.commit()
            
            return jsonify({'success': True})
            
        except Exception as e:
            db.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            db.close()
    
    @api_bp.route('/ideas/<int:idea_id>/comments', methods=['GET', 'POST'])
    def handle_idea_comments(idea_id):
        """Get or add comments for an idea."""
        db = get_session()
        try:
            if request.method == 'GET':
                # Get all comments for the idea
                comments = db.query(IdeaComment).filter_by(idea_id=idea_id).order_by(IdeaComment.created_at.desc()).all()
                
                comments_data = []
                for comment in comments:
                    comments_data.append({
                        'id': comment.id,
                        'author_name': comment.author_name or comment.author_email,
                        'author_email': comment.author_email,
                        'content': comment.content,
                        'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
                        'is_internal': comment.is_internal,
                        'sub_status': comment.sub_status.value if comment.sub_status else None
                    })
                
                return jsonify(comments_data)
            
            else:  # POST
                user_email = session.get('user_email')
                if not user_email:
                    return jsonify({'success': False, 'error': 'Authentication required'}), 401
                
                data = request.get_json()
                
                # Create comment
                comment = IdeaComment(
                    idea_id=idea_id,
                    author_email=user_email,
                    author_name=session.get('user_name', user_email),
                    content=data['content'],
                    is_internal=data.get('is_internal', False)
                )
                db.add(comment)
                
                # Create activity
                activity = IdeaActivity(
                    idea_id=idea_id,
                    activity_type=ActivityType.comment_added,
                    actor_email=user_email,
                    actor_name=session.get('user_name', user_email),
                    description='added a comment'
                )
                db.add(activity)
                
                db.commit()
                
                return jsonify({'success': True, 'comment_id': comment.id})
        
        except Exception as e:
            if request.method == 'POST':
                db.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            db.close()
    
    @api_bp.route('/ideas/<int:idea_id>/external-links', methods=['GET', 'POST'])
    def handle_idea_external_links(idea_id):
        """Get or add external links for an idea."""
        db = get_session()
        try:
            if request.method == 'GET':
                # Get all links for the idea
                links = db.query(IdeaExternalLink).filter_by(idea_id=idea_id).order_by(IdeaExternalLink.created_at.desc()).all()
                
                links_data = []
                for link in links:
                    links_data.append({
                        'id': link.id,
                        'link_type': link.link_type.value,
                        'title': link.title,
                        'url': link.url,
                        'description': link.description,
                        'creator_name': link.creator.name if link.creator else link.created_by,
                        'created_at': link.created_at.strftime('%B %d, %Y'),
                        'sub_status': link.sub_status.value if link.sub_status else None
                    })
                
                return jsonify(links_data)
            
            else:  # POST
                user_email = session.get('user_email')
                if not user_email:
                    return jsonify({'success': False, 'error': 'Authentication required'}), 401
                
                data = request.get_json()
                
                # Create link
                link = IdeaExternalLink(
                    idea_id=idea_id,
                    link_type=ExternalLinkType(data['link_type']),
                    title=data['title'],
                    url=data['url'],
                    description=data.get('description'),
                    created_by=user_email
                )
                db.add(link)
                
                # Create activity
                activity = IdeaActivity(
                    idea_id=idea_id,
                    activity_type=ActivityType.link_added,
                    actor_email=user_email,
                    actor_name=session.get('user_name', user_email),
                    description=f"added a {data['link_type'].replace('_', ' ')}"
                )
                db.add(activity)
                
                db.commit()
                
                return jsonify({'success': True, 'link_id': link.id})
        
        except Exception as e:
            if request.method == 'POST':
                db.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            db.close()
    
    @api_bp.route('/ideas/<int:idea_id>/activities', methods=['GET'])
    def get_idea_activities(idea_id):
        """Get activity feed for an idea."""
        db = get_session()
        try:
            activities = db.query(IdeaActivity).filter_by(idea_id=idea_id).order_by(IdeaActivity.created_at.desc()).limit(50).all()
            
            activities_data = []
            for activity in activities:
                activities_data.append({
                    'id': activity.id,
                    'activity_type': activity.activity_type.value,
                    'actor_name': activity.actor_name or activity.actor_email,
                    'description': activity.description,
                    'created_at': activity.created_at.strftime('%B %d, %Y at %I:%M %p'),
                    'activity_data': activity.activity_data
                })
            
            return jsonify(activities_data)
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            db.close()