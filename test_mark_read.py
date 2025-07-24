#!/usr/bin/env python3
"""Test marking notifications as read."""

from database import get_session
from models import Notification

db = get_session()

# Get the unread notification
unread = db.query(Notification).filter(
    Notification.user_email == 'admin@system.local',
    Notification.is_read == False
).first()

if unread:
    print(f"Found unread notification: {unread.id} - {unread.title}")
    print(f"Current is_read status: {unread.is_read}")
    
    # Mark it as unread to ensure we have test data
    unread.is_read = False
    db.commit()
    print("Ensured notification is unread for testing")
else:
    print("No unread notifications found")

db.close()