from flask import Blueprint, jsonify, request, session
from database import get_session
from models import Idea, Skill, Team, Claim, IdeaStatus, PriorityLevel, IdeaSize, EmailSettings, UserProfile, Notification, user_skills, ClaimApproval, ManagerRequest
from sqlalchemy import desc, asc, func, or_
from datetime import datetime
from decorators import require_verified_email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import io
from werkzeug.datastructures import FileStorage

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Basic health check - verify database connection
        db = get_session()
        # Run a simple query to verify database is accessible
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

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

@api_bp.route('/teams/<int:team_id>/members')
def get_team_members(team_id):
    """Get members of a team (manager only for their own team, or admin for any team)."""
    is_admin = session.get('is_admin')
    is_manager_of_team = session.get('user_role') == 'manager' and session.get('user_managed_team_id') == team_id
    
    if not is_admin and not is_manager_of_team:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    db = get_session()
    try:
        members = db.query(UserProfile).filter(
            UserProfile.team_id == team_id,
            UserProfile.role.in_(['developer', 'citizen_developer'])  # Only developers can be assigned
        ).all()
        
        members_data = []
        for member in members:
            members_data.append({
                'email': member.email,
                'name': member.name,
                'role': member.role,
                'skills': [skill.name for skill in member.skills]
            })
        
        return jsonify(members_data)
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
            # Check if this is an approval (changing from False to True)
            if not team.is_approved and is_approved:
                # Find users who belong to this team to notify them
                team_users = db.query(UserProfile).filter_by(team_id=team.id).all()
                
                for user in team_users:
                    # Create notification for each team member
                    notification = Notification(
                        user_email=user.email,
                        type='team_approved',
                        title='Team approved!',
                        message=f'Your team "{team.name}" has been approved by an administrator.',
                        related_user_email='admin@system.local'
                    )
                    db.add(notification)
            
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

@api_bp.route('/teams/<int:team_id>/deny', methods=['POST'])
def deny_team(team_id):
    """Deny a team request and clear it from all users (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        team = db.query(Team).get(team_id)
        if not team:
            return jsonify({'success': False, 'message': 'Team not found'}), 404
        
        if team.is_approved:
            return jsonify({'success': False, 'message': 'Cannot deny an already approved team'}), 400
        
        # Find all users who have this team assigned
        affected_users = db.query(UserProfile).filter_by(team_id=team.id).all()
        
        # Clear team assignment from all affected users
        for user in affected_users:
            user.team_id = None
            
            # Create notification for each affected user
            notification = Notification(
                user_email=user.email,
                type='team_denied',
                title='Team Request Denied',
                message=f'Your team request for "{team.name}" has been denied by an administrator. Please select a different team in your profile.',
                related_user_email='admin@system.local'
            )
            db.add(notification)
        
        # Delete the team
        db.delete(team)
        db.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Team denied and removed from {len(affected_users)} user(s)'
        })
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
        old_status = idea.status
        
        if 'title' in data:
            idea.title = data['title']
        if 'team' in data:
            idea.benefactor_team = data['team']
        if 'priority' in data:
            idea.priority = PriorityLevel(data['priority'])
        if 'size' in data:
            idea.size = IdeaSize(data['size'])
        if 'status' in data:
            new_status = IdeaStatus(data['status'])
            idea.status = new_status
            
            # Create notifications for status changes
            if old_status != new_status:
                # Notify submitter
                submitter_notification = Notification(
                    user_email=idea.email,
                    type='status_change',
                    title='Idea status updated',
                    message=f'Your idea "{idea.title}" has been updated from {old_status.value} to {new_status.value}.',
                    idea_id=idea_id
                )
                db.add(submitter_notification)
                
                # Notify claimers if any
                for claim in idea.claims:
                    claimer_notification = Notification(
                        user_email=claim.claimer_email,
                        type='status_change',
                        title='Claimed idea status updated',
                        message=f'The idea "{idea.title}" you claimed has been updated from {old_status.value} to {new_status.value}.',
                        idea_id=idea_id
                    )
                    db.add(claimer_notification)
                    
                # Special notification for completion
                if new_status == IdeaStatus.complete:
                    # Notify the submitter about completion
                    completion_notification = Notification(
                        user_email=idea.email,
                        type='idea_completed',
                        title='Your idea has been completed!',
                        message=f'Congratulations! Your idea "{idea.title}" has been marked as complete.',
                        idea_id=idea_id
                    )
                    db.add(completion_notification)
                    
        if 'email' in data:
            idea.email = data['email']
        if 'description' in data:
            idea.description = data['description']
        if 'reward' in data:
            idea.reward = data['reward']
        
        # Handle skills update
        if 'skill_ids' in data:
            # Clear existing skills
            idea.skills = []
            # Add new skills
            skill_ids = data['skill_ids']
            if skill_ids:
                skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
                idea.skills = skills
        
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

@api_bp.route('/admin/notifications')
def get_admin_notifications():
    """Get all pending admin notifications."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_session()
    try:
        from models import ManagerRequest, Team, ClaimApproval
        
        notifications = []
        
        # Get pending manager requests
        pending_manager_requests = db.query(ManagerRequest).filter_by(status='pending').count()
        if pending_manager_requests > 0:
            notifications.append({
                'type': 'manager_request',
                'count': pending_manager_requests,
                'message': f'{pending_manager_requests} pending manager request{"s" if pending_manager_requests > 1 else ""}',
                'link': '/admin/users',
                'priority': 'high'
            })
        
        # Get pending team approvals
        pending_teams = db.query(Team).filter_by(is_approved=False).count()
        if pending_teams > 0:
            notifications.append({
                'type': 'team_approval',
                'count': pending_teams,
                'message': f'{pending_teams} team{"s" if pending_teams > 1 else ""} pending approval',
                'link': '/admin/teams',
                'priority': 'medium'
            })
        
        # Get pending claim approvals (where both approvals are needed)
        pending_claims = db.query(ClaimApproval).filter_by(status='pending').count()
        if pending_claims > 0:
            notifications.append({
                'type': 'claim_approval',
                'count': pending_claims,
                'message': f'{pending_claims} claim{"s" if pending_claims > 1 else ""} pending approval',
                'link': '/admin/ideas',
                'priority': 'medium'
            })
        
        # Calculate total pending items
        total_pending = sum(n['count'] for n in notifications)
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'total_pending': total_pending
        })
    except Exception as e:
        print(f"Error fetching admin notifications: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch notifications'}), 500
    finally:
        db.close()

@api_bp.route('/user/notifications')
def get_user_notifications():
    """Get notifications for the current user."""
    if not session.get('user_verified'):
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'success': False, 'message': 'User email not found'}), 400
    
    # Debug logging
    print(f"Notifications API called - user_email: {user_email}, is_admin: {session.get('is_admin')}")
    
    db = get_session()
    try:
        # Get unread notifications for the user
        if session.get('is_admin'):
            # Admins also see system notifications
            notifications = db.query(Notification).filter(
                or_(
                    Notification.user_email == user_email,
                    Notification.user_email == 'admin@system.local'
                ),
                Notification.is_read == False
            ).order_by(desc(Notification.created_at)).limit(50).all()
            print(f"Admin query returned {len(notifications)} unread notifications")
        else:
            notifications = db.query(Notification).filter_by(
                user_email=user_email,
                is_read=False
            ).order_by(desc(Notification.created_at)).limit(50).all()
            print(f"Regular user query returned {len(notifications)} unread notifications")
        
        # Also get recent read notifications (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        if session.get('is_admin'):
            # Admins also see system notifications
            recent_read = db.query(Notification).filter(
                or_(
                    Notification.user_email == user_email,
                    Notification.user_email == 'admin@system.local'
                ),
                Notification.is_read == True,
                Notification.created_at >= seven_days_ago
            ).order_by(desc(Notification.created_at)).limit(20).all()
        else:
            recent_read = db.query(Notification).filter(
                Notification.user_email == user_email,
                Notification.is_read == True,
                Notification.created_at >= seven_days_ago
            ).order_by(desc(Notification.created_at)).limit(20).all()
        
        # Combine and sort
        all_notifications = notifications + recent_read
        all_notifications.sort(key=lambda x: x.created_at, reverse=True)
        
        # Serialize notifications
        notifications_data = []
        for notif in all_notifications[:50]:  # Limit total to 50
            notifications_data.append({
                'id': notif.id,
                'type': notif.type,
                'title': notif.title,
                'message': notif.message,
                'idea_id': notif.idea_id,
                'related_user': notif.related_user_email,
                'is_read': notif.is_read,
                'created_at': notif.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'time_ago': _get_time_ago(notif.created_at)
            })
        
        unread_count = len([n for n in notifications_data if not n['is_read']])
        print(f"Final unread count being returned: {unread_count}")
        
        return jsonify({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count
        })
    except Exception as e:
        print(f"Error fetching user notifications: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch notifications'}), 500
    finally:
        db.close()

def _get_time_ago(timestamp):
    """Convert timestamp to human-readable time ago format."""
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days > 0:
        if diff.days == 1:
            return "1 day ago"
        return f"{diff.days} days ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        if hours == 1:
            return "1 hour ago"
        return f"{hours} hours ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        if minutes == 1:
            return "1 minute ago"
        return f"{minutes} minutes ago"
    else:
        return "just now"

@api_bp.route('/user/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    if not session.get('user_verified'):
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    user_email = session.get('user_email')
    db = get_session()
    try:
        notification = db.query(Notification).filter_by(
            id=notification_id,
            user_email=user_email
        ).first()
        
        if not notification:
            return jsonify({'success': False, 'message': 'Notification not found'}), 404
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        print(f"Error marking notification as read: {e}")
        return jsonify({'success': False, 'error': 'Failed to update notification'}), 500
    finally:
        db.close()

@api_bp.route('/user/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete a notification."""
    if not session.get('user_verified'):
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    user_email = session.get('user_email')
    is_admin = session.get('is_admin')
    
    db = get_session()
    try:
        # Admin can delete any notification, users can only delete their own
        if is_admin:
            notification = db.query(Notification).filter_by(id=notification_id).first()
        else:
            notification = db.query(Notification).filter_by(
                id=notification_id,
                user_email=user_email
            ).first()
        
        if not notification:
            return jsonify({'success': False, 'message': 'Notification not found'}), 404
        
        db.delete(notification)
        db.commit()
        
        return jsonify({'success': True, 'message': 'Notification deleted'})
    except Exception as e:
        db.rollback()
        print(f"Error deleting notification: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete notification'}), 500
    finally:
        db.close()

@api_bp.route('/team/members/<email>')
def get_team_member(email):
    """Get details of a specific team member (manager or admin only)."""
    # Check if user is a manager with a team or an admin
    is_admin = session.get('is_admin')
    is_manager = session.get('user_role') == 'manager' and session.get('user_managed_team_id')
    
    if not is_admin and not is_manager:
        return jsonify({'success': False, 'error': 'Unauthorized. Manager role or admin access required.'}), 403
    
    db = get_session()
    try:
        # Get the team member
        member = db.query(UserProfile).filter_by(email=email).first()
        if not member:
            return jsonify({'success': False, 'error': 'Team member not found'}), 404
        
        # Verify the member belongs to the manager's team (skip for admins)
        if not is_admin and member.team_id != session.get('user_managed_team_id'):
            return jsonify({'success': False, 'error': 'Member not in your team'}), 403
        
        # Count submitted and claimed ideas
        submitted_count = db.query(Idea).filter_by(email=member.email).count()
        claimed_count = db.query(Claim).filter_by(claimer_email=member.email).count()
        
        # Count complete ideas
        complete_submitted = db.query(Idea).filter(
            Idea.email == member.email,
            Idea.status == IdeaStatus.complete
        ).count()
        
        complete_claimed = db.query(Claim).join(Idea).filter(
            Claim.claimer_email == member.email,
            Idea.status == IdeaStatus.complete
        ).count()
        
        # Count pending claims
        pending_claims = db.query(ClaimApproval).filter(
            ClaimApproval.claimer_email == member.email,
            ClaimApproval.status == 'pending'
        ).count()
        
        user_data = {
            'email': member.email,
            'name': member.name,
            'role': member.role,
            'team_id': member.team_id,
            'team_name': member.team.name if member.team else None,
            'skills': [{'id': s.id, 'name': s.name} for s in member.skills],
            'is_verified': member.is_verified,
            'created_at': member.created_at.isoformat() if member.created_at else None,
            'last_verified_at': member.last_verified_at.isoformat() if member.last_verified_at else None,
            'submitted_ideas_count': submitted_count,
            'claimed_ideas_count': claimed_count,
            'complete_submitted_count': complete_submitted,
            'complete_claimed_count': complete_claimed,
            'pending_claims_count': pending_claims
        }
        
        return jsonify({'success': True, 'user': user_data})
    finally:
        db.close()


@api_bp.route('/team/members/<email>', methods=['PUT'])
def update_team_member(email):
    """Update a team member's profile (manager or admin only)."""
    # Check if user is a manager with a team or an admin
    is_admin = session.get('is_admin')
    is_manager = session.get('user_role') == 'manager' and session.get('user_managed_team_id')
    
    if not is_admin and not is_manager:
        return jsonify({'success': False, 'error': 'Unauthorized. Manager role or admin access required.'}), 403
    
    db = get_session()
    try:
        # Get the team member
        member = db.query(UserProfile).filter_by(email=email).first()
        if not member:
            return jsonify({'success': False, 'error': 'Team member not found'}), 404
        
        # Verify the member belongs to the manager's team (skip for admins)
        if not is_admin and member.team_id != session.get('user_managed_team_id'):
            return jsonify({'success': False, 'error': 'Member not in your team'}), 403
        
        # Managers can only manage developers, not other managers (admins can edit anyone)
        if not is_admin and member.role == 'manager':
            return jsonify({'success': False, 'error': 'Cannot edit other managers'}), 403
        
        data = request.json
        
        # Update allowed fields
        if 'name' in data:
            member.name = data['name']
        
        if 'role' in data and data['role'] in ['citizen_developer', 'developer']:
            member.role = data['role']
        
        # Update skills
        if 'skill_ids' in data:
            # Clear existing skills
            member.skills = []
            # Add new skills
            skill_ids = data['skill_ids']
            if skill_ids:
                skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
                member.skills = skills
        
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()


@api_bp.route('/team-stats')
def get_team_stats():
    """Get team statistics for managers."""
    # Check if user is a manager with a team
    if session.get('user_role') != 'manager' or not session.get('user_managed_team_id'):
        return jsonify({'error': 'Unauthorized. Manager role required.'}), 403
    
    db = get_session()
    try:
        team_id = session.get('user_managed_team_id')
        user_email = session.get('user_email')
        
        # Get team object
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return jsonify({'error': 'Team not found'}), 404
        
        # Get team members
        team_members = db.query(UserProfile).filter(
            UserProfile.team_id == team_id,
            UserProfile.email != user_email  # Exclude the manager
        ).all()
        
        team_member_emails = [member.email for member in team_members]
        
        # Basic counts
        team_submitted = db.query(Idea).filter(
            Idea.email.in_(team_member_emails)
        ).count()
        
        # Get claimed ideas by team members with proper join
        from models import ClaimApproval
        team_claimed = db.query(func.count(func.distinct(Claim.idea_id))).join(
            Idea, Claim.idea_id == Idea.id
        ).filter(
            Claim.claimer_email.in_(team_member_emails)
        ).scalar() or 0
        
        # Status breakdown of team's claimed ideas
        status_breakdown = {}
        claimed_status_query = db.query(Idea.status, func.count(Idea.id)).join(
            Claim, Claim.idea_id == Idea.id
        ).filter(
            Claim.claimer_email.in_(team_member_emails)
        ).group_by(Idea.status).all()
        
        for status, count in claimed_status_query:
            status_breakdown[status.value] = count
        
        # Submitted ideas by status
        submitted_status_breakdown = {}
        submitted_status_query = db.query(Idea.status, func.count(Idea.id)).filter(
            Idea.email.in_(team_member_emails)
        ).group_by(Idea.status).all()
        
        for status, count in submitted_status_query:
            submitted_status_breakdown[status.value] = count
        
        # Priority breakdown - split by submitted vs claimed
        priority_submitted = {}
        priority_submitted_query = db.query(Idea.priority, func.count(Idea.id)).filter(
            Idea.email.in_(team_member_emails)
        ).group_by(Idea.priority).all()
        
        for priority, count in priority_submitted_query:
            priority_submitted[priority.value] = count
            
        priority_claimed = {}
        priority_claimed_query = db.query(Idea.priority, func.count(Idea.id)).join(
            Claim, Claim.idea_id == Idea.id
        ).filter(
            Claim.claimer_email.in_(team_member_emails)
        ).group_by(Idea.priority).all()
        
        for priority, count in priority_claimed_query:
            priority_claimed[priority.value] = count
        
        # Size breakdown - split by submitted vs claimed
        size_submitted = {}
        size_submitted_query = db.query(Idea.size, func.count(Idea.id)).filter(
            Idea.email.in_(team_member_emails)
        ).group_by(Idea.size).all()
        
        for size, count in size_submitted_query:
            size_submitted[size.value] = count
            
        size_claimed = {}
        size_claimed_query = db.query(Idea.size, func.count(Idea.id)).join(
            Claim, Claim.idea_id == Idea.id
        ).filter(
            Claim.claimer_email.in_(team_member_emails)
        ).group_by(Idea.size).all()
        
        for size, count in size_claimed_query:
            size_claimed[size.value] = count
        
        # Team member skills - get all skills of team members
        team_skills = {}
        for member in team_members:
            member_skills = db.query(Skill.name).join(
                user_skills, Skill.id == user_skills.c.skill_id
            ).filter(
                user_skills.c.user_id == member.id
            ).all()
            
            for (skill_name,) in member_skills:
                team_skills[skill_name] = team_skills.get(skill_name, 0) + 1
        
        # Sort team skills by count
        team_skills_list = [{'skill': skill, 'count': count} 
                           for skill, count in sorted(team_skills.items(), 
                                                    key=lambda x: x[1], 
                                                    reverse=True)][:10]
        
        # Team member activity
        member_activity = []
        for member in team_members:
            submitted_count = db.query(Idea).filter(Idea.email == member.email).count()
            claimed_count = db.query(Claim).filter(Claim.claimer_email == member.email).count()
            completed_count = db.query(Claim).join(Idea).filter(
                Claim.claimer_email == member.email,
                Idea.status == IdeaStatus.complete
            ).count()
            
            # Claims for own team vs other teams
            own_team_claims = db.query(Claim).join(Idea).filter(
                Claim.claimer_email == member.email,
                Idea.benefactor_team == team.name
            ).count()
            
            other_team_claims = db.query(Claim).join(Idea).filter(
                Claim.claimer_email == member.email,
                Idea.benefactor_team != team.name
            ).count()
            
            # Completed for own team vs other teams
            own_team_completed = db.query(Claim).join(Idea).filter(
                Claim.claimer_email == member.email,
                Idea.benefactor_team == team.name,
                Idea.status == IdeaStatus.complete
            ).count()
            
            other_team_completed = db.query(Claim).join(Idea).filter(
                Claim.claimer_email == member.email,
                Idea.benefactor_team != team.name,
                Idea.status == IdeaStatus.complete
            ).count()
            
            # Get member skills
            member_skills = [skill.name for skill in member.skills] if member.skills else []
            
            member_activity.append({
                'name': member.name,
                'email': member.email,
                'role': member.role,
                'skills': member_skills,
                'submitted': submitted_count,
                'claimed': claimed_count,
                'completed': completed_count,
                'own_team_claims': own_team_claims,
                'other_team_claims': other_team_claims,
                'own_team_completed': own_team_completed,
                'other_team_completed': other_team_completed
            })
        
        # Sort by total activity
        member_activity.sort(key=lambda x: x['submitted'] + x['claimed'], reverse=True)
        
        # Pending approvals for team
        pending_approvals = db.query(ClaimApproval).join(
            Idea, ClaimApproval.idea_id == Idea.id
        ).filter(
            ClaimApproval.claimer_email.in_(team_member_emails),
            ClaimApproval.status == 'pending',
            ClaimApproval.manager_approved == None
        ).count()
        
        # Calculate completion rate
        total_claimed = db.query(Claim).filter(
            Claim.claimer_email.in_(team_member_emails)
        ).count()
        
        completed_ideas = db.query(Claim).join(Idea).filter(
            Claim.claimer_email.in_(team_member_emails),
            Idea.status == IdeaStatus.complete
        ).count()
        
        completion_rate = round((completed_ideas / total_claimed * 100) if total_claimed > 0 else 0, 1)
        
        # Recent activity (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_submissions = db.query(Idea).filter(
            Idea.email.in_(team_member_emails),
            Idea.date_submitted >= thirty_days_ago
        ).count()
        
        recent_claims = db.query(Claim).filter(
            Claim.claimer_email.in_(team_member_emails),
            Claim.claim_date >= thirty_days_ago
        ).count()
        
        # Team claims breakdown (own team vs other teams)
        own_team_claims = db.query(Claim).join(Idea).filter(
            Claim.claimer_email.in_(team_member_emails),
            Idea.benefactor_team == team.name
        ).count()
        
        other_team_claims = db.query(Claim).join(Idea).filter(
            Claim.claimer_email.in_(team_member_emails),
            Idea.benefactor_team != team.name
        ).count()
        
        own_team_completed = db.query(Claim).join(Idea).filter(
            Claim.claimer_email.in_(team_member_emails),
            Idea.benefactor_team == team.name,
            Idea.status == IdeaStatus.complete
        ).count()
        
        other_team_completed = db.query(Claim).join(Idea).filter(
            Claim.claimer_email.in_(team_member_emails),
            Idea.benefactor_team != team.name,
            Idea.status == IdeaStatus.complete
        ).count()
        
        stats = {
            'overview': {
                'total_members': len(team_members),
                'ideas_submitted': team_submitted,
                'ideas_claimed': team_claimed,
                'completion_rate': completion_rate,
                'pending_approvals': pending_approvals
            },
            'breakdowns': {
                'status': status_breakdown,
                'submitted_status': submitted_status_breakdown,
                'priority': {
                    'submitted': priority_submitted,
                    'claimed': priority_claimed
                },
                'size': {
                    'submitted': size_submitted,
                    'claimed': size_claimed
                },
                'team_skills': team_skills_list,
                'team_claims': {
                    'own_team': own_team_claims,
                    'other_teams': other_team_claims,
                    'own_team_completed': own_team_completed,
                    'other_teams_completed': other_team_completed
                }
            },
            'member_activity': member_activity[:10],  # Top 10 members
            'recent_activity': {
                'submissions_30d': recent_submissions,
                'claims_30d': recent_claims
            }
        }
        
        return jsonify(stats)
    finally:
        db.close()

@api_bp.route('/admin/team-stats')
def get_admin_team_stats():
    """Get team statistics for admins. Can view any team or all teams."""
    # Check if user is admin
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
    
    db = get_session()
    try:
        # Get optional team_id parameter
        team_id = request.args.get('team_id', type=int)
        
        # If no team_id, return stats for all teams
        if not team_id:
            # Get all teams
            teams = db.query(Team).order_by(Team.name).all()
            all_teams_stats = []
            
            for team in teams:
                # Get team members
                team_members = db.query(UserProfile).filter(
                    UserProfile.team_id == team.id
                ).all()
                
                team_member_emails = [member.email for member in team_members]
                
                if not team_member_emails:
                    # Skip teams with no members
                    continue
                
                # Basic counts
                team_submitted = db.query(Idea).filter(
                    Idea.email.in_(team_member_emails)
                ).count()
                
                team_claimed = db.query(func.count(func.distinct(Claim.idea_id))).join(
                    Idea, Claim.idea_id == Idea.id
                ).filter(
                    Claim.claimer_email.in_(team_member_emails)
                ).scalar() or 0
                
                # Completion rate
                completed_ideas = db.query(Claim).join(Idea).filter(
                    Claim.claimer_email.in_(team_member_emails),
                    Idea.status == IdeaStatus.complete
                ).count()
                
                completion_rate = round((completed_ideas / team_claimed * 100) if team_claimed > 0 else 0, 1)
                
                all_teams_stats.append({
                    'id': team.id,
                    'name': team.name,
                    'is_approved': team.is_approved,
                    'member_count': len(team_members),
                    'submitted_count': team_submitted,
                    'claimed_count': team_claimed,
                    'completion_rate': completion_rate
                })
            
            return jsonify({'teams_overview': all_teams_stats})
        
        # Get stats for specific team
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return jsonify({'error': 'Team not found'}), 404
        
        # Get team members
        team_members = db.query(UserProfile).filter(
            UserProfile.team_id == team_id
        ).all()
        
        team_member_emails = [member.email for member in team_members]
        
        # Basic counts
        team_submitted = db.query(Idea).filter(
            Idea.email.in_(team_member_emails)
        ).count()
        
        # Get claimed ideas by team members with proper join
        from models import ClaimApproval
        team_claimed = db.query(func.count(func.distinct(Claim.idea_id))).join(
            Idea, Claim.idea_id == Idea.id
        ).filter(
            Claim.claimer_email.in_(team_member_emails)
        ).scalar() or 0
        
        # Status breakdown of team's claimed ideas
        status_breakdown = {}
        claimed_status_query = db.query(Idea.status, func.count(Idea.id)).join(
            Claim, Claim.idea_id == Idea.id
        ).filter(
            Claim.claimer_email.in_(team_member_emails)
        ).group_by(Idea.status).all()
        
        for status, count in claimed_status_query:
            status_breakdown[status.value] = count
        
        # Submitted ideas by status
        submitted_status_breakdown = {}
        submitted_status_query = db.query(Idea.status, func.count(Idea.id)).filter(
            Idea.email.in_(team_member_emails)
        ).group_by(Idea.status).all()
        
        for status, count in submitted_status_query:
            submitted_status_breakdown[status.value] = count
        
        # Priority breakdown - split by submitted vs claimed
        priority_submitted = {}
        priority_submitted_query = db.query(Idea.priority, func.count(Idea.id)).filter(
            Idea.email.in_(team_member_emails)
        ).group_by(Idea.priority).all()
        
        for priority, count in priority_submitted_query:
            priority_submitted[priority.value] = count
            
        priority_claimed = {}
        priority_claimed_query = db.query(Idea.priority, func.count(Idea.id)).join(
            Claim, Claim.idea_id == Idea.id
        ).filter(
            Claim.claimer_email.in_(team_member_emails)
        ).group_by(Idea.priority).all()
        
        for priority, count in priority_claimed_query:
            priority_claimed[priority.value] = count
        
        # Size breakdown - split by submitted vs claimed
        size_submitted = {}
        size_submitted_query = db.query(Idea.size, func.count(Idea.id)).filter(
            Idea.email.in_(team_member_emails)
        ).group_by(Idea.size).all()
        
        for size, count in size_submitted_query:
            size_submitted[size.value] = count
            
        size_claimed = {}
        size_claimed_query = db.query(Idea.size, func.count(Idea.id)).join(
            Claim, Claim.idea_id == Idea.id
        ).filter(
            Claim.claimer_email.in_(team_member_emails)
        ).group_by(Idea.size).all()
        
        for size, count in size_claimed_query:
            size_claimed[size.value] = count
        
        # Team member skills - get all skills of team members
        team_skills = {}
        for member in team_members:
            member_skills = db.query(Skill.name).join(
                user_skills, Skill.id == user_skills.c.skill_id
            ).filter(
                user_skills.c.user_id == member.id
            ).all()
            
            for (skill_name,) in member_skills:
                team_skills[skill_name] = team_skills.get(skill_name, 0) + 1
        
        # Sort team skills by count
        team_skills_list = [{'skill': skill, 'count': count} 
                           for skill, count in sorted(team_skills.items(), 
                                                    key=lambda x: x[1], 
                                                    reverse=True)][:10]
        
        # Team member activity
        member_activity = []
        for member in team_members:
            submitted_count = db.query(Idea).filter(Idea.email == member.email).count()
            claimed_count = db.query(Claim).filter(Claim.claimer_email == member.email).count()
            completed_count = db.query(Claim).join(Idea).filter(
                Claim.claimer_email == member.email,
                Idea.status == IdeaStatus.complete
            ).count()
            
            # Claims for own team vs other teams
            own_team_claims = db.query(Claim).join(Idea).filter(
                Claim.claimer_email == member.email,
                Idea.benefactor_team == team.name
            ).count()
            
            other_team_claims = db.query(Claim).join(Idea).filter(
                Claim.claimer_email == member.email,
                Idea.benefactor_team != team.name
            ).count()
            
            # Completed for own team vs other teams
            own_team_completed = db.query(Claim).join(Idea).filter(
                Claim.claimer_email == member.email,
                Idea.benefactor_team == team.name,
                Idea.status == IdeaStatus.complete
            ).count()
            
            other_team_completed = db.query(Claim).join(Idea).filter(
                Claim.claimer_email == member.email,
                Idea.benefactor_team != team.name,
                Idea.status == IdeaStatus.complete
            ).count()
            
            # Get member skills
            member_skills = [skill.name for skill in member.skills] if member.skills else []
            
            member_activity.append({
                'name': member.name,
                'email': member.email,
                'role': member.role,
                'skills': member_skills,
                'submitted': submitted_count,
                'claimed': claimed_count,
                'completed': completed_count,
                'own_team_claims': own_team_claims,
                'other_team_claims': other_team_claims,
                'own_team_completed': own_team_completed,
                'other_team_completed': other_team_completed
            })
        
        # Sort by total activity
        member_activity.sort(key=lambda x: x['submitted'] + x['claimed'], reverse=True)
        
        # Pending approvals for team
        pending_approvals = db.query(ClaimApproval).join(
            Idea, ClaimApproval.idea_id == Idea.id
        ).filter(
            ClaimApproval.claimer_email.in_(team_member_emails),
            ClaimApproval.status == 'pending',
            ClaimApproval.manager_approved == None
        ).count()
        
        # Calculate completion rate
        total_claimed = db.query(Claim).filter(
            Claim.claimer_email.in_(team_member_emails)
        ).count()
        
        completed_ideas = db.query(Claim).join(Idea).filter(
            Claim.claimer_email.in_(team_member_emails),
            Idea.status == IdeaStatus.complete
        ).count()
        
        completion_rate = round((completed_ideas / total_claimed * 100) if total_claimed > 0 else 0, 1)
        
        # Recent activity (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_submissions = db.query(Idea).filter(
            Idea.email.in_(team_member_emails),
            Idea.date_submitted >= thirty_days_ago
        ).count()
        
        recent_claims = db.query(Claim).filter(
            Claim.claimer_email.in_(team_member_emails),
            Claim.claim_date >= thirty_days_ago
        ).count()
        
        # Team claims breakdown (own team vs other teams)
        own_team_claims = db.query(Claim).join(Idea).filter(
            Claim.claimer_email.in_(team_member_emails),
            Idea.benefactor_team == team.name
        ).count()
        
        other_team_claims = db.query(Claim).join(Idea).filter(
            Claim.claimer_email.in_(team_member_emails),
            Idea.benefactor_team != team.name
        ).count()
        
        own_team_completed = db.query(Claim).join(Idea).filter(
            Claim.claimer_email.in_(team_member_emails),
            Idea.benefactor_team == team.name,
            Idea.status == IdeaStatus.complete
        ).count()
        
        other_team_completed = db.query(Claim).join(Idea).filter(
            Claim.claimer_email.in_(team_member_emails),
            Idea.benefactor_team != team.name,
            Idea.status == IdeaStatus.complete
        ).count()
        
        stats = {
            'team_name': team.name,
            'team_id': team.id,
            'overview': {
                'total_members': len(team_members),
                'ideas_submitted': team_submitted,
                'ideas_claimed': team_claimed,
                'completion_rate': completion_rate,
                'pending_approvals': pending_approvals
            },
            'breakdowns': {
                'status': status_breakdown,
                'submitted_status': submitted_status_breakdown,
                'priority': {
                    'submitted': priority_submitted,
                    'claimed': priority_claimed
                },
                'size': {
                    'submitted': size_submitted,
                    'claimed': size_claimed
                },
                'team_skills': team_skills_list,
                'team_claims': {
                    'own_team': own_team_claims,
                    'other_teams': other_team_claims,
                    'own_team_completed': own_team_completed,
                    'other_teams_completed': other_team_completed
                }
            },
            'member_activity': member_activity[:10],  # Top 10 members
            'recent_activity': {
                'submissions_30d': recent_submissions,
                'claims_30d': recent_claims
            }
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
        # Get the authenticated user's email from session
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({"error": "Authentication required. Please verify your email."}), 401
        
        # Dictionary to track ideas and their relationship to user
        ideas_dict = {}
        
        # Get submitted ideas for the authenticated user
        submitted_ideas = db.query(Idea).filter(
            Idea.email == user_email
        ).all()
        
        for idea in submitted_ideas:
            ideas_dict[idea.id] = {
                    'idea': idea,
                    'relationship': 'submitted'
                }
            
        # Get claimed ideas
        claimed_ideas = db.query(Idea).join(Claim).filter(
            Claim.claimer_email == user_email
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
                    Claim.claimer_email == user_email
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
        
        
        # Get pending claim approvals for the user
        from models import ClaimApproval
        
        # Pending and denied claims by the user
        pending_claims = db.query(ClaimApproval).filter(
            ClaimApproval.claimer_email == user_email,
            ClaimApproval.status.in_(['pending', 'denied'])
        ).all()
        
        # Pending approvals where user is the idea owner
        pending_owner_approvals = db.query(ClaimApproval).join(Idea).filter(
            Idea.email == user_email,
            ClaimApproval.status == 'pending'
        ).all()
        
        # Serialize pending claims
        pending_claims_data = []
        for approval in pending_claims:
            idea = approval.idea
            pending_claims_data.append({
                'id': idea.id,
                'title': idea.title,
                'description': idea.description,
                'email': idea.email,
                'submitter_name': idea.submitter.name if idea.submitter else None,
                'priority': idea.priority.value,
                'size': idea.size.value,
                'status': 'pending_claim',  # Special status for UI
                'benefactor_team': idea.benefactor_team,
                'date_submitted': idea.date_submitted.strftime('%Y-%m-%d'),
                'skills': [{'id': s.id, 'name': s.name} for s in idea.skills],
                'pending_approval': {
                    'id': approval.id,
                    'status': approval.status,
                    'owner_approved': approval.idea_owner_approved,
                    'manager_approved': approval.manager_approved,
                    'created_at': approval.created_at.strftime('%Y-%m-%d'),
                    'denied_at': approval.idea_owner_denied_at.strftime('%Y-%m-%d') if approval.idea_owner_denied_at else 
                                approval.manager_denied_at.strftime('%Y-%m-%d') if approval.manager_denied_at else None
                }
            })
        
        # Serialize pending approvals
        pending_approvals_data = []
        for approval in pending_owner_approvals:
            idea = approval.idea
            pending_approvals_data.append({
                'id': approval.id,
                'idea_id': approval.idea_id,
                'claimer_name': approval.claimer_name,
                'claimer_email': approval.claimer_email,
                'claimer_team': approval.claimer_team,
                'claimer_skills': approval.claimer_skills,
                'created_at': approval.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'owner_approved': approval.idea_owner_approved,
                'manager_approved': approval.manager_approved,
                'idea': {
                    'id': idea.id,
                    'title': idea.title,
                    'description': idea.description,
                    'benefactor_team': idea.benefactor_team,
                    'priority': idea.priority.value,
                    'status': idea.status.value
                }
            })
        
        return jsonify({
            'ideas': ideas_data,
            'pending_claims': pending_claims_data,
            'pending_approvals': pending_approvals_data
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
        
        # Update the user's managed_team_id and role
        user = db.query(UserProfile).filter_by(email=manager_request.user_email).first()
        if user:
            user.managed_team_id = manager_request.requested_team_id
            user.role = 'manager'  # Also change their role to manager
        
        # Create notification for the approved manager
        if user and manager_request.team:
            manager_notification = Notification(
                user_email=manager_request.user_email,
                type='manager_approved',
                title='Manager request approved!',
                message=f'Your request to manage team "{manager_request.team.name}" has been approved. You can now view and manage your team\'s activities.',
                related_user_email='admin@system.local'
            )
            db.add(manager_notification)
            
            # Notify existing team members about their new manager
            team_members = db.query(UserProfile).filter_by(team_id=manager_request.requested_team_id).all()
            for member in team_members:
                if member.email != manager_request.user_email:  # Don't notify the manager about themselves
                    member_notification = Notification(
                        user_email=member.email,
                        type='new_manager',
                        title='New team manager',
                        message=f'{user.name or manager_request.user_email} is now managing your team "{manager_request.team.name}".',
                        related_user_email=manager_request.user_email
                    )
                    db.add(member_notification)
        
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
        
        # Create notification for the denied request
        if manager_request.team:
            denial_notification = Notification(
                user_email=manager_request.user_email,
                type='manager_denied',
                title='Manager request denied',
                message=f'Your request to manage team "{manager_request.team.name}" has been denied.',
                related_user_email='admin@system.local'
            )
            db.add(denial_notification)
        
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
        
        # Optionally change role back (if specified in request)
        if 'change_role' in request.json and request.json['change_role']:
            new_role = request.json.get('new_role', 'developer')
            if new_role in ['developer', 'citizen_developer', 'idea_submitter']:
                user.role = new_role
        
        db.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/claim-approvals/pending')
def get_pending_claim_approvals():
    """Get pending claim approvals for the current user (as idea owner or manager)."""
    if not session.get('user_verified'):
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    db = get_session()
    try:
        from models import ClaimApproval, Idea
        user_email = session.get('user_email')
        
        # Get approvals where user is the idea owner
        owner_approvals = db.query(ClaimApproval).join(Idea).filter(
            Idea.email == user_email,
            ClaimApproval.status == 'pending',
            ClaimApproval.idea_owner_approved == None
        ).all()
        
        # Get approvals where user is a manager of the claimer's team
        manager_approvals = []
        if session.get('user_role') == 'manager' and session.get('user_managed_team_id'):
            managed_team_id = session.get('user_managed_team_id')
            
            # Get team members' emails
            team_members = db.query(UserProfile).filter(
                UserProfile.team_id == managed_team_id
            ).all()
            team_emails = [member.email for member in team_members]
            
            if team_emails:
                manager_approvals = db.query(ClaimApproval).filter(
                    ClaimApproval.claimer_email.in_(team_emails),
                    ClaimApproval.status == 'pending',
                    ClaimApproval.manager_approved == None
                ).all()
        
        # Serialize approvals
        owner_data = []
        for approval in owner_approvals:
            owner_data.append({
                'id': approval.id,
                'idea_id': approval.idea_id,
                'idea_title': approval.idea.title,
                'claimer_name': approval.claimer_name,
                'claimer_email': approval.claimer_email,
                'claimer_team': approval.claimer_team,
                'created_at': approval.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        manager_data = []
        for approval in manager_approvals:
            manager_data.append({
                'id': approval.id,
                'idea_id': approval.idea_id,
                'idea_title': approval.idea.title,
                'claimer_name': approval.claimer_name,
                'claimer_email': approval.claimer_email,
                'claimer_team': approval.claimer_team,
                'created_at': approval.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'as_owner': owner_data,
            'as_manager': manager_data
        })
    finally:
        db.close()

@api_bp.route('/claim-approvals/<int:approval_id>/approve', methods=['POST'])
def approve_claim(approval_id):
    """Approve a claim request (as idea owner or manager)."""
    if not session.get('user_verified'):
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    db = get_session()
    try:
        from models import ClaimApproval, Idea, Claim, IdeaStatus
        
        approval = db.query(ClaimApproval).get(approval_id)
        if not approval:
            return jsonify({'success': False, 'message': 'Approval request not found'}), 404
        
        if approval.status != 'pending':
            return jsonify({'success': False, 'message': 'This request has already been processed'}), 400
        
        user_email = session.get('user_email')
        idea = approval.idea
        
        # Check if user is the idea owner
        if idea.email == user_email and approval.idea_owner_approved is None:
            approval.idea_owner_approved = True
            approval.idea_owner_approved_at = datetime.now()
            approval.idea_owner_approved_by = user_email
        
        # Check if user is the claimer's manager
        elif session.get('user_role') == 'manager' and approval.manager_approved is None:
            # Verify user manages the claimer's team
            claimer = db.query(UserProfile).filter_by(email=approval.claimer_email).first()
            if claimer and claimer.team_id == session.get('user_managed_team_id'):
                approval.manager_approved = True
                approval.manager_approved_at = datetime.now()
                approval.manager_approved_by = user_email
            else:
                return jsonify({'success': False, 'message': 'You are not authorized to approve this claim'}), 403
        else:
            return jsonify({'success': False, 'message': 'You are not authorized to approve this claim'}), 403
        
        # Check if both approvals are complete
        if approval.idea_owner_approved and approval.manager_approved:
            # Create the actual claim
            claim = Claim(
                idea_id=approval.idea_id,
                claimer_name=approval.claimer_name,
                claimer_email=approval.claimer_email,
                claimer_team=approval.claimer_team,
                claimer_skills=approval.claimer_skills,
                claim_date=datetime.now()
            )
            
            # Update idea status
            idea.status = IdeaStatus.claimed
            
            # Update approval status
            approval.status = 'approved'
            
            db.add(claim)
            
            # Create notifications
            # Notify claimer that their claim was approved
            claimer_notification = Notification(
                user_email=approval.claimer_email,
                type='claim_approved',
                title='Claim Approved!',
                message=f'Your claim for "{idea.title}" has been approved. You can now start working on it.',
                idea_id=idea.id,
                related_user_email=idea.email
            )
            db.add(claimer_notification)
            
            # Notify idea owner that their idea was claimed
            owner_notification = Notification(
                user_email=idea.email,
                type='claim_approved',
                title='Your idea has been claimed',
                message=f'{approval.claimer_name} has successfully claimed your idea "{idea.title}".',
                idea_id=idea.id,
                related_user_email=approval.claimer_email
            )
            db.add(owner_notification)
            
            # Update claimer's session if they're the current user
            if approval.claimer_email == session.get('user_email'):
                if 'claimed_ideas' not in session:
                    session['claimed_ideas'] = []
                if approval.idea_id not in session['claimed_ideas']:
                    session['claimed_ideas'].append(approval.idea_id)
                    
                # Remove from pending claims
                if 'pending_claims' in session and approval.idea_id in session['pending_claims']:
                    session['pending_claims'].remove(approval.idea_id)
                
                session.permanent = True
        
        db.commit()
        
        return jsonify({'success': True, 'message': 'Approval recorded successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/claim-approvals/<int:approval_id>/deny', methods=['POST'])
def deny_claim(approval_id):
    """Deny a claim request (as idea owner or manager)."""
    if not session.get('user_verified'):
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    db = get_session()
    try:
        from models import ClaimApproval, Idea
        
        approval = db.query(ClaimApproval).get(approval_id)
        if not approval:
            return jsonify({'success': False, 'message': 'Approval request not found'}), 404
        
        if approval.status != 'pending':
            return jsonify({'success': False, 'message': 'This request has already been processed'}), 400
        
        user_email = session.get('user_email')
        idea = approval.idea
        
        # Check if user is the idea owner
        if idea.email == user_email and approval.idea_owner_approved is None:
            approval.idea_owner_approved = False
            approval.idea_owner_denied_at = datetime.now()
            approval.idea_owner_approved_by = user_email
            approval.status = 'denied'
        
        # Check if user is the claimer's manager
        elif session.get('user_role') == 'manager' and approval.manager_approved is None:
            # Verify user manages the claimer's team
            claimer = db.query(UserProfile).filter_by(email=approval.claimer_email).first()
            if claimer and claimer.team_id == session.get('user_managed_team_id'):
                approval.manager_approved = False
                approval.manager_denied_at = datetime.now()
                approval.manager_approved_by = user_email
                approval.status = 'denied'
            else:
                return jsonify({'success': False, 'message': 'You are not authorized to deny this claim'}), 403
        else:
            return jsonify({'success': False, 'message': 'You are not authorized to deny this claim'}), 403
        
        # Create notification for claimer
        claimer_notification = Notification(
            user_email=approval.claimer_email,
            type='claim_denied',
            title='Claim Denied',
            message=f'Your claim request for "{idea.title}" has been denied.',
            idea_id=idea.id,
            related_user_email=user_email
        )
        db.add(claimer_notification)
        
        db.commit()
        
        return jsonify({'success': True, 'message': 'Claim request denied'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@api_bp.route('/ideas/<int:idea_id>/assign', methods=['POST'])
def assign_idea(idea_id):
    """Assign an idea to a team member (manager only)."""
    if session.get('user_role') != 'manager' or not session.get('user_managed_team_id'):
        return jsonify({'success': False, 'message': 'Only managers can assign ideas'}), 403
    
    db = get_session()
    try:
        from models import Idea
        
        idea = db.query(Idea).get(idea_id)
        if not idea:
            return jsonify({'success': False, 'message': 'Idea not found'}), 404
        
        # Verify the idea belongs to the manager's team
        if idea.benefactor_team != session.get('user_managed_team'):
            return jsonify({'success': False, 'message': 'You can only assign ideas for your team'}), 403
        
        assignee_email = request.json.get('assignee_email')
        if not assignee_email:
            return jsonify({'success': False, 'message': 'Assignee email is required'}), 400
        
        # Verify assignee is in the manager's team
        assignee = db.query(UserProfile).filter_by(email=assignee_email).first()
        if not assignee or assignee.team_id != session.get('user_managed_team_id'):
            return jsonify({'success': False, 'message': 'Assignee must be a member of your team'}), 400
        
        # Update assignment
        idea.assigned_to_email = assignee_email
        idea.assigned_at = datetime.now()
        idea.assigned_by = session.get('user_email')
        
        # Create notification for assignee
        assignee_notification = Notification(
            user_email=assignee_email,
            type='assigned',
            title='New idea assigned to you',
            message=f'{session.get("user_name", "Your manager")} has assigned the idea "{idea.title}" to you.',
            idea_id=idea_id,
            related_user_email=session.get('user_email')
        )
        db.add(assignee_notification)
        
        # Also notify the idea submitter
        submitter_notification = Notification(
            user_email=idea.email,
            type='assigned',
            title='Your idea has been assigned',
            message=f'Your idea "{idea.title}" has been assigned to {assignee.name} by {session.get("user_name", "a manager")}.',
            idea_id=idea_id,
            related_user_email=assignee_email
        )
        db.add(submitter_notification)
        
        db.commit()
        
        return jsonify({'success': True, 'message': f'Idea assigned to {assignee.name}'})
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

@api_bp.route('/admin/bulk-upload/ideas', methods=['POST'])
def bulk_upload_ideas():
    """Bulk upload ideas from CSV file (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'File must be a CSV'}), 400
    
    db = get_session()
    errors = []
    imported_count = 0
    
    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        required_fields = ['title', 'description', 'email', 'benefactor_team', 'size', 'priority', 'needed_by']
        
        # Validate headers
        if not all(field in csv_reader.fieldnames for field in required_fields):
            missing = [f for f in required_fields if f not in csv_reader.fieldnames]
            return jsonify({
                'success': False, 
                'message': f'Missing required columns: {", ".join(missing)}'
            }), 400
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Skip empty rows
                if not any(row.values()):
                    continue
                
                # Validate required fields
                for field in required_fields:
                    if not row.get(field, '').strip():
                        errors.append(f"Row {row_num}: Missing required field '{field}'")
                        continue
                
                # Parse enums
                try:
                    size = IdeaSize(row['size'].strip().lower().replace(' ', '_'))
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid size '{row['size']}'. Must be: small, medium, large, or extra_large")
                    continue
                
                try:
                    priority = PriorityLevel(row['priority'].strip().lower())
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid priority '{row['priority']}'. Must be: low, medium, or high")
                    continue
                
                # Parse date
                try:
                    needed_by = datetime.strptime(row['needed_by'].strip(), '%Y-%m-%d')
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid date format '{row['needed_by']}'. Use YYYY-MM-DD")
                    continue
                
                # Check if team exists
                team_name = row['benefactor_team'].strip()
                team = db.query(Team).filter_by(name=team_name).first()
                if not team:
                    errors.append(f"Row {row_num}: Team '{team_name}' does not exist")
                    continue
                
                # Parse status if provided
                status = IdeaStatus.open  # default
                if row.get('status', '').strip():
                    try:
                        status = IdeaStatus(row['status'].strip().lower())
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid status '{row['status']}'. Must be: open, claimed, or complete")
                        continue
                
                # Create idea
                idea = Idea(
                    title=row['title'].strip(),
                    description=row['description'].strip(),
                    email=row['email'].strip().lower(),
                    benefactor_team=team_name,
                    size=size,
                    priority=priority,
                    needed_by=needed_by,
                    status=status,
                    reward=row.get('reward', '').strip() or None
                )
                
                # Handle skills
                if row.get('skills', '').strip():
                    skill_names = [s.strip() for s in row['skills'].split(',') if s.strip()]
                    for skill_name in skill_names:
                        # Get or create skill
                        skill = db.query(Skill).filter_by(name=skill_name).first()
                        if not skill:
                            skill = Skill(name=skill_name)
                            db.add(skill)
                            db.flush()  # Get skill ID
                        idea.skills.append(skill)
                
                db.add(idea)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: Error processing row - {str(e)}")
                continue
        
        db.commit()
        
        return jsonify({
            'success': True,
            'imported': imported_count,
            'errors': errors,
            'message': f'Successfully imported {imported_count} ideas'
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': f'Error processing file: {str(e)}',
            'errors': errors
        }), 500
    finally:
        db.close()

@api_bp.route('/admin/bulk-upload/users', methods=['POST'])
def bulk_upload_users():
    """Bulk upload users from CSV file (admin only)."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'File must be a CSV'}), 400
    
    db = get_session()
    errors = []
    imported_count = 0
    
    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        required_fields = ['email', 'name', 'role', 'team']
        
        # Validate headers
        if not all(field in csv_reader.fieldnames for field in required_fields):
            missing = [f for f in required_fields if f not in csv_reader.fieldnames]
            return jsonify({
                'success': False, 
                'message': f'Missing required columns: {", ".join(missing)}'
            }), 400
        
        valid_roles = ['manager', 'idea_submitter', 'citizen_developer', 'developer']
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Skip empty rows
                if not any(row.values()):
                    continue
                
                # Validate required fields
                for field in required_fields:
                    if not row.get(field, '').strip():
                        errors.append(f"Row {row_num}: Missing required field '{field}'")
                        continue
                
                email = row['email'].strip().lower()
                
                # Check if user already exists
                existing_user = db.query(UserProfile).filter_by(email=email).first()
                if existing_user:
                    errors.append(f"Row {row_num}: User with email '{email}' already exists")
                    continue
                
                # Validate role
                role = row['role'].strip().lower()
                if role not in valid_roles:
                    errors.append(f"Row {row_num}: Invalid role '{role}'. Must be one of: {', '.join(valid_roles)}")
                    continue
                
                # Check if team exists
                team_name = row['team'].strip()
                team = db.query(Team).filter_by(name=team_name).first()
                if not team:
                    errors.append(f"Row {row_num}: Team '{team_name}' does not exist")
                    continue
                
                # Create user profile
                user = UserProfile(
                    email=email,
                    name=row['name'].strip(),
                    role=role,
                    team_id=team.id,
                    is_verified=row.get('is_verified', 'true').lower() == 'true'
                )
                
                # Handle skills for developers and citizen developers
                if role in ['developer', 'citizen_developer'] and row.get('skills', '').strip():
                    skill_names = [s.strip() for s in row['skills'].split(',') if s.strip()]
                    for skill_name in skill_names:
                        # Get or create skill
                        skill = db.query(Skill).filter_by(name=skill_name).first()
                        if not skill:
                            skill = Skill(name=skill_name)
                            db.add(skill)
                            db.flush()  # Get skill ID
                        user.skills.append(skill)
                
                db.add(user)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: Error processing row - {str(e)}")
                continue
        
        db.commit()
        
        return jsonify({
            'success': True,
            'imported': imported_count,
            'errors': errors,
            'message': f'Successfully imported {imported_count} users'
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': f'Error processing file: {str(e)}',
            'errors': errors
        }), 500
    finally:
        db.close()

@api_bp.route('/admin/users', methods=['GET'])
def get_admin_users():
    """Get all users for admin management."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Admin access required.'}), 403
    
    db = get_session()
    try:
        users = db.query(UserProfile).all()
        
        users_data = []
        for user in users:
            # Count submitted and claimed ideas
            submitted_count = db.query(Idea).filter_by(email=user.email).count()
            claimed_count = db.query(Claim).filter_by(claimer_email=user.email).count()
            
            # Count complete ideas (both submitted and claimed)
            complete_submitted = db.query(Idea).filter(
                Idea.email == user.email,
                Idea.status == IdeaStatus.complete
            ).count()
            
            complete_claimed = db.query(Idea).join(Claim).filter(
                Claim.claimer_email == user.email,
                Idea.status == IdeaStatus.complete
            ).count()
            
            # Count pending claims
            pending_claims = db.query(ClaimApproval).filter(
                ClaimApproval.claimer_email == user.email,
                ClaimApproval.status == 'pending'
            ).count()
            
            # Check for pending manager request
            pending_manager_request = db.query(ManagerRequest).filter(
                ManagerRequest.user_email == user.email,
                ManagerRequest.status == 'pending'
            ).first()
            
            user_data = {
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'team_id': user.team_id,
                'team_name': user.team.name if user.team else None,
                'managed_team_id': user.managed_team_id,
                'managed_team_name': user.managed_team.name if user.managed_team else None,
                'skills': [{'id': skill.id, 'name': skill.name} for skill in user.skills],
                'is_verified': user.is_verified,
                'submitted_ideas_count': submitted_count,
                'claimed_ideas_count': claimed_count,
                'complete_submitted_count': complete_submitted,
                'complete_claimed_count': complete_claimed,
                'pending_claims_count': pending_claims,
                'has_pending_manager_request': pending_manager_request is not None,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_verified_at': user.last_verified_at.isoformat() if user.last_verified_at else None
            }
            
            # Add pending manager request details if exists
            if pending_manager_request:
                user_data['pending_manager_request'] = {
                    'id': pending_manager_request.id,
                    'requested_team_id': pending_manager_request.requested_team_id,
                    'requested_team': pending_manager_request.team.name if pending_manager_request.team else None,
                    'requested_at': pending_manager_request.requested_at.isoformat() if pending_manager_request.requested_at else None
                }
            
            users_data.append(user_data)
        
        return jsonify({
            'success': True,
            'users': users_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@api_bp.route('/admin/users/<email>', methods=['PUT'])
def update_admin_user(email):
    """Update a user's profile."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Admin access required.'}), 403
    
    data = request.json
    db = get_session()
    try:
        user = db.query(UserProfile).filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'error': 'User not found.'}), 404
        
        # Track role changes for manager workflow
        old_role = user.role
        old_managed_team_id = user.managed_team_id
        
        # Update user fields
        if 'name' in data:
            user.name = data['name']
        if 'role' in data:
            user.role = data['role']
        if 'team_id' in data:
            user.team_id = data['team_id']
        if 'managed_team_id' in data:
            user.managed_team_id = data['managed_team_id']
        if 'is_verified' in data:
            user.is_verified = data['is_verified']
        
        # Handle manager role changes
        if 'role' in data:
            # If changing FROM manager to another role, clear managed team
            if old_role == 'manager' and data['role'] != 'manager':
                user.managed_team_id = None
                
            # If changing TO manager and they have a pending request, auto-approve it
            if old_role != 'manager' and data['role'] == 'manager':
                # Check for pending manager request
                pending_request = db.query(ManagerRequest).filter_by(
                    user_email=user.email,
                    status='pending'
                ).first()
                
                if pending_request:
                    # Approve the pending request
                    pending_request.status = 'approved'
                    pending_request.processed_at = datetime.utcnow()
                    pending_request.processed_by = 'admin'
                    
                    # Set the managed team from the request if not already set
                    if not user.managed_team_id and pending_request.requested_team_id:
                        user.managed_team_id = pending_request.requested_team_id
        
        # Update skills
        if 'skill_ids' in data:
            # Clear existing skills
            user.skills = []
            # Add new skills
            if data['skill_ids']:
                skills = db.query(Skill).filter(Skill.id.in_(data['skill_ids'])).all()
                user.skills = skills
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully.'
        })
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@api_bp.route('/admin/users/<email>', methods=['DELETE'])
def delete_admin_user(email):
    """Delete a user and their associated data."""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Admin access required.'}), 403
    
    db = get_session()
    try:
        user = db.query(UserProfile).filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'error': 'User not found.'}), 404
        
        # Delete associated manager requests
        db.query(ManagerRequest).filter_by(user_email=email).delete()
        
        # Delete associated claim approvals
        db.query(ClaimApproval).filter_by(claimer_email=email).delete()
        
        # Delete the user
        db.delete(user)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully.'
        })
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()
