#!/usr/bin/env python3
"""
Script to set up a user in the database for notification testing
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.models import Base, User, NotificationPreferences

# Database configuration
DATABASE_URL = "sqlite:///fantasy_football.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def setup_user():
    """Create default user and notification preferences"""
    session = Session()
    
    try:
        # Check if user exists
        user = session.query(User).filter_by(id="7").first()
        if not user:
            print("Creating user 7 (Trashy McTrash-Face)...")
            user = User(
                id="7",
                username="trashy_mctrashface",
                email="user@example.com",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(user)
            session.commit()
            print("✅ User created successfully")
        else:
            print("User 7 already exists")
        
        # Check if notification preferences exist
        prefs = session.query(NotificationPreferences).filter_by(user_id="7").first()
        if not prefs:
            print("Creating notification preferences...")
            prefs = NotificationPreferences(
                id="prefs_7",
                user_id="7",
                email_enabled=True,
                email_trade_proposals=True,
                email_waiver_results=True,
                email_breaking_news=True,
                email_lineup_reminders=True,
                email_injury_updates=True,
                push_enabled=True,
                push_trade_proposals=True,
                push_waiver_results=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(prefs)
            session.commit()
            print("✅ Notification preferences created")
        else:
            print("Notification preferences already exist")
        
        print("\n✅ User setup complete!")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  User ID: {user.id}")
        
    except Exception as e:
        print(f"❌ Error setting up user: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("USER SETUP SCRIPT")
    print("=" * 60)
    setup_user()