from flask import Blueprint, jsonify, request, session
from database import get_session
from models import Idea, Skill, Team, Claim, IdeaStatus, PriorityLevel, IdeaSize, EmailSettings, UserProfile
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
    """Get members of a team (manager only for their own team)."""
    if session.get('user_role') != 'manager' or session.get('user_managed_team_id') != team_id:
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
        
        # Priority breakdown of team's ideas (both submitted and claimed)
        priority_breakdown = {}
        priority_query = db.query(Idea.priority, func.count(Idea.id)).filter(
            db.or_(
                Idea.email.in_(team_member_emails),
                Idea.id.in_(
                    db.query(Claim.idea_id).filter(Claim.claimer_email.in_(team_member_emails))
                )
            )
        ).group_by(Idea.priority).all()
        
        for priority, count in priority_query:
            priority_breakdown[priority.value] = count
        
        # Size breakdown
        size_breakdown = {}
        size_query = db.query(Idea.size, func.count(Idea.id)).filter(
            db.or_(
                Idea.email.in_(team_member_emails),
                Idea.id.in_(
                    db.query(Claim.idea_id).filter(Claim.claimer_email.in_(team_member_emails))
                )
            )
        ).group_by(Idea.size).all()
        
        for size, count in size_query:
            size_breakdown[size.value] = count
        
        # Skills distribution - what skills are most common in team's claimed ideas
        skills_distribution = db.query(Skill.name, func.count(Skill.id)).join(
            Idea.skills
        ).join(
            Claim, Claim.idea_id == Idea.id
        ).filter(
            Claim.claimer_email.in_(team_member_emails)
        ).group_by(Skill.name).order_by(func.count(Skill.id).desc()).limit(10).all()
        
        # Team member activity
        member_activity = []
        for member in team_members:
            submitted_count = db.query(Idea).filter(Idea.email == member.email).count()
            claimed_count = db.query(Claim).filter(Claim.claimer_email == member.email).count()
            completed_count = db.query(Claim).join(Idea).filter(
                Claim.claimer_email == member.email,
                Idea.status == IdeaStatus.complete
            ).count()
            
            member_activity.append({
                'name': member.name,
                'email': member.email,
                'submitted': submitted_count,
                'claimed': claimed_count,
                'completed': completed_count
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
                'priority': priority_breakdown,
                'size': size_breakdown,
                'skills': [{'skill': skill, 'count': count} for skill, count in skills_distribution]
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
            pending_approvals_data.append({
                'id': approval.id,
                'idea_id': approval.idea_id,
                'idea_title': approval.idea.title,
                'claimer_name': approval.claimer_name,
                'claimer_email': approval.claimer_email,
                'claimer_team': approval.claimer_team,
                'created_at': approval.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'owner_approved': approval.idea_owner_approved,
                'manager_approved': approval.manager_approved
            })
        
        return jsonify({
            'user_ideas': ideas_data,
            'team_ideas': team_ideas_data,
            'pending_claims': pending_claims_data,
            'pending_approvals': pending_approvals_data,
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
            
            users_data.append({
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
                'claimed_ideas_count': claimed_count
            })
        
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
