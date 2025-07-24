#!/usr/bin/env python3
"""Check notification database state."""

from database import get_session
from models import Notification
from datetime import datetime, timedelta

db = get_session()

print("=== Notification Database Check ===\n")

# 1. All admin notifications
print("1. All admin@system.local notifications:")
admin_notifs = db.query(Notification).filter_by(user_email='admin@system.local').order_by(Notification.created_at.desc()).all()
print(f"   Total: {len(admin_notifs)}")
for n in admin_notifs:
    print(f"   - ID: {n.id}, Type: {n.type}, Read: {n.is_read}, Created: {n.created_at}")

# 2. Unread count
unread = [n for n in admin_notifs if not n.is_read]
print(f"\n2. Unread notifications: {len(unread)}")

# 3. Create a fresh unread notification
print("\n3. Creating fresh unread notification...")
fresh = Notification(
    user_email='admin@system.local',
    type='team_approval_request',
    title='Debug Test Notification',
    message='This notification was created for debugging the bell icon',
    related_user_email='debug@test.com',
    is_read=False,
    created_at=datetime.utcnow()
)
db.add(fresh)
db.commit()
print(f"   Created notification ID: {fresh.id}")

# 4. Final count
unread_final = db.query(Notification).filter(
    Notification.user_email == 'admin@system.local',
    Notification.is_read == False
).count()
print(f"\n4. Final unread count: {unread_final}")

db.close()