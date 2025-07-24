#!/usr/bin/env python3
"""Test script to verify admin notification system."""

from database import get_session
from models import Notification, Team, UserProfile
from datetime import datetime

def test_admin_notifications():
    db = get_session()
    
    print("=== Testing Admin Notification System ===\n")
    
    # 1. Check existing admin notifications
    print("1. Checking existing admin@system.local notifications:")
    admin_notifs = db.query(Notification).filter_by(user_email='admin@system.local').all()
    print(f"   Total: {len(admin_notifs)}")
    for n in admin_notifs:
        print(f"   - Type: {n.type}, Read: {n.is_read}, Title: {n.title}")
    
    # 2. Check if there are any pending team approvals
    print("\n2. Checking pending team approvals:")
    pending_teams = db.query(Team).filter_by(is_approved=False).all()
    print(f"   Total pending teams: {len(pending_teams)}")
    for team in pending_teams:
        print(f"   - {team.name}")
    
    # 3. Create a test notification if needed
    unread_admin_notifs = [n for n in admin_notifs if not n.is_read]
    if len(unread_admin_notifs) == 0:
        print("\n3. Creating test notification (no unread notifications found):")
        test_notification = Notification(
            user_email='admin@system.local',
            type='team_approval_request',
            title='Test Team Approval Request',
            message='This is a test notification for admin',
            related_user_email='test@example.com',
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.add(test_notification)
        db.commit()
        print("   Created test notification")
    else:
        print(f"\n3. Found {len(unread_admin_notifs)} unread admin notifications")
    
    # 4. Test the query logic that would be used by the API
    print("\n4. Testing API query logic:")
    # Regular user notifications
    regular_notifs = db.query(Notification).filter(
        Notification.user_email == 'admin@system.local',
        Notification.is_read == False
    ).all()
    print(f"   Regular query (just admin@system.local): {len(regular_notifs)} unread")
    
    # Admin extended query (includes system notifications)
    from sqlalchemy import or_
    admin_notifs = db.query(Notification).filter(
        or_(
            Notification.user_email == 'admin@system.local',
            Notification.user_email == 'admin@system.local'  # Redundant but matches API logic
        ),
        Notification.is_read == False
    ).all()
    print(f"   Admin query (with OR clause): {len(admin_notifs)} unread")
    
    db.close()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_admin_notifications()