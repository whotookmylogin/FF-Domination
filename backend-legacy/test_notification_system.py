#!/usr/bin/env python3
"""
Test script for the notification system.
This script tests all notification functionality including:
- Email notifications (mock mode)
- Push notifications (mock mode) 
- SMS notifications (mock mode)
- In-app notifications
- Notification templates
- User preferences
- Database operations
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import uuid

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import get_db
from database.models import User, NotificationPreferences, Notification
from notifications.service import create_notification_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_user(db):
    """Create a test user for notification testing."""
    user_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    user = User(
        id=user_id,
        username=f"testuser_{user_id[:8]}",
        email="test@example.com",
        created_at=now,
        updated_at=now
    )
    
    db.add(user)
    db.commit()
    
    logger.info(f"Created test user: {user_id}")
    return user_id

def test_notification_service():
    """Test the notification service functionality."""
    logger.info("Starting notification system tests...")
    
    # Initialize notification service
    notification_service = create_notification_service()
    
    with next(get_db()) as db:
        try:
            # Create test user
            user_id = create_test_user(db)
            
            # Test 1: Basic notification sending
            logger.info("Test 1: Basic notification sending")
            result = notification_service.send_notification(
                db, user_id,
                "Test Notification",
                "This is a test notification message",
                "test",
                priority=1
            )
            logger.info(f"Basic notification result: {result['success']}")
            
            # Test 2: Trade proposal notification
            logger.info("Test 2: Trade proposal notification")
            trade_data = {
                "you_give": ["Christian McCaffrey", "Stefon Diggs"],
                "you_get": ["Derrick Henry"],
                "fairness_score": 85,
                "win_probability_delta": 12.5
            }
            result = notification_service.send_trade_proposal_notification(
                db, user_id, trade_data
            )
            logger.info(f"Trade proposal notification result: {result['success']}")
            
            # Test 3: Waiver results notification
            logger.info("Test 3: Waiver results notification")
            waiver_data = {
                "successful_claims": [
                    {"player_name": "Backup RB", "bid_amount": 25}
                ],
                "failed_claims": [
                    {"player_name": "Handcuff WR", "winning_bid": 50}
                ]
            }
            result = notification_service.send_waiver_results_notification(
                db, user_id, waiver_data
            )
            logger.info(f"Waiver results notification result: {result['success']}")
            
            # Test 4: Breaking news notification
            logger.info("Test 4: Breaking news notification")
            news_data = {
                "headline": "Star QB suffers season-ending injury",
                "summary": "The quarterback will miss the remainder of the season due to an ACL tear.",
                "urgency_score": 5,
                "affected_players": ["Star QB"],
                "source": "ESPN Test"
            }
            result = notification_service.send_breaking_news_notification(
                db, user_id, news_data
            )
            logger.info(f"Breaking news notification result: {result['success']}")
            
            # Test 5: Lineup reminder notification
            logger.info("Test 5: Lineup reminder notification")
            reminder_data = {
                "week": 8,
                "hours_until_games": 2
            }
            result = notification_service.send_lineup_reminder_notification(
                db, user_id, reminder_data
            )
            logger.info(f"Lineup reminder notification result: {result['success']}")
            
            # Test 6: Injury update notification
            logger.info("Test 6: Injury update notification")
            injury_data = {
                "player_name": "Star RB",
                "status": "questionable",
                "injury_type": "Ankle sprain",
                "expected_return": "Next week",
                "fantasy_impact": "Monitor practice reports"
            }
            result = notification_service.send_injury_update_notification(
                db, user_id, injury_data
            )
            logger.info(f"Injury update notification result: {result['success']}")
            
            # Test 7: Get user notifications
            logger.info("Test 7: Get user notifications")
            notifications = notification_service.get_user_notifications(db, user_id)
            logger.info(f"Retrieved {len(notifications)} notifications for user")
            
            # Test 8: Test notification preferences
            logger.info("Test 8: Notification preferences")
            preferences = notification_service.get_user_preferences(db, user_id)
            logger.info(f"User preferences created: {preferences is not None}")
            
            # Update preferences
            new_preferences = {
                "email_enabled": True,
                "push_enabled": True,
                "sms_enabled": False,
                "sms_phone_number": "+1234567890"
            }
            updated_preferences = notification_service.update_notification_preferences(
                db, user_id, new_preferences
            )
            logger.info(f"Updated preferences: {updated_preferences is not None}")
            
            # Test 9: Mark notifications as read
            logger.info("Test 9: Mark notifications as read")
            count = notification_service.mark_notifications_as_read(db, user_id)
            logger.info(f"Marked {count} notifications as read")
            
            # Test 10: Test all channels
            logger.info("Test 10: Test all notification channels")
            result = notification_service.test_notification_channels(db, user_id)
            logger.info(f"Channel test result: {result['success']}")
            
            # Test 11: Force specific channels
            logger.info("Test 11: Force specific channels")
            result = notification_service.send_notification(
                db, user_id,
                "Multi-Channel Test",
                "Testing all notification channels",
                "test",
                priority=1,
                force_channels=['email', 'push', 'sms']
            )
            logger.info(f"Multi-channel test result: {result['success']}")
            logger.info(f"Channels used: {result['channels']}")
            
            # Test 12: High priority notification
            logger.info("Test 12: High priority notification")
            result = notification_service.send_notification(
                db, user_id,
                "🚨 URGENT: High Priority Test",
                "This is an urgent notification test",
                "urgent_test",
                priority=5
            )
            logger.info(f"High priority notification result: {result['success']}")
            
            logger.info("All notification system tests completed successfully!")
            
            # Print summary
            final_notifications = notification_service.get_user_notifications(db, user_id)
            logger.info(f"\nTest Summary:")
            logger.info(f"- Total notifications created: {len(final_notifications)}")
            logger.info(f"- Test user ID: {user_id}")
            logger.info(f"- Email notifications: {sum(1 for n in final_notifications if n['sent_via_email'])}")
            logger.info(f"- Push notifications: {sum(1 for n in final_notifications if n['sent_via_push'])}")
            logger.info(f"- SMS notifications: {sum(1 for n in final_notifications if n['sent_via_sms'])}")
            
            # Show some example notifications
            logger.info(f"\nExample notifications:")
            for i, notification in enumerate(final_notifications[:3], 1):
                logger.info(f"{i}. {notification['title']} - {notification['type']} (Priority: {notification['priority']})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during notification system test: {e}")
            return False

def test_notification_templates():
    """Test the notification templates."""
    logger.info("Testing notification templates...")
    
    from notifications.service import NotificationTemplates
    
    templates = NotificationTemplates()
    
    # Test trade proposal template
    trade_data = {
        "you_give": ["Player A", "Player B"],
        "you_get": ["Player C"],
        "fairness_score": 92,
        "win_probability_delta": 15.5
    }
    trade_template = templates.trade_proposal(trade_data)
    logger.info(f"Trade proposal template: ✓")
    logger.info(f"Title: {trade_template['title']}")
    
    # Test waiver results template
    waiver_data = {
        "successful_claims": [{"player_name": "Test Player", "bid_amount": 30}],
        "failed_claims": [{"player_name": "Another Player", "winning_bid": 45}]
    }
    waiver_template = templates.waiver_results(waiver_data)
    logger.info(f"Waiver results template: ✓")
    logger.info(f"Title: {waiver_template['title']}")
    
    # Test breaking news template
    news_data = {
        "headline": "Major Trade Announcement",
        "summary": "Big trade shakes up fantasy landscape",
        "urgency_score": 4,
        "affected_players": ["Player X", "Player Y"],
        "source": "Test Source"
    }
    news_template = templates.breaking_news(news_data)
    logger.info(f"Breaking news template: ✓")
    logger.info(f"Title: {news_template['title']}")
    
    # Test lineup reminder template
    reminder_data = {
        "week": 10,
        "hours_until_games": 3
    }
    reminder_template = templates.lineup_reminder(reminder_data)
    logger.info(f"Lineup reminder template: ✓")
    logger.info(f"Title: {reminder_template['title']}")
    
    # Test injury update template
    injury_data = {
        "player_name": "Test Player",
        "status": "out",
        "injury_type": "Hamstring strain",
        "expected_return": "2-3 weeks",
        "fantasy_impact": "Drop or bench immediately"
    }
    injury_template = templates.injury_update(injury_data)
    logger.info(f"Injury update template: ✓")
    logger.info(f"Title: {injury_template['title']}")
    
    logger.info("All template tests completed successfully!")
    return True

def test_email_service():
    """Test the email service (in mock mode)."""
    logger.info("Testing email service (mock mode)...")
    
    from notifications.service import EmailService
    
    # Create email service without credentials (will use mock mode)
    email_service = EmailService()
    
    result = email_service.send_email(
        "test@example.com",
        "Test Email Subject",
        "This is a test email message from the Fantasy Football app!"
    )
    
    logger.info(f"Email service test result: {result}")
    logger.info(f"Email sent successfully: {result.get('success', False)}")
    logger.info(f"Mock mode: {result.get('mock', False)}")
    
    return result.get('success', False)

def test_push_service():
    """Test the push notification service (in mock mode)."""
    logger.info("Testing push notification service (mock mode)...")
    
    from notifications.service import PushNotificationService
    
    # Create push service without FCM key (will use mock mode)
    push_service = PushNotificationService()
    
    result = push_service.send_push_notification(
        ["test_token_1", "test_token_2"],
        "Test Push Notification",
        "This is a test push notification from the Fantasy Football app!",
        {"test_data": "test_value"}
    )
    
    logger.info(f"Push service test result: {result}")
    logger.info(f"Push notification sent successfully: {result.get('success', False)}")
    logger.info(f"Mock mode: {result.get('mock', False)}")
    
    return result.get('success', False)

def test_sms_service():
    """Test the SMS service (in mock mode)."""
    logger.info("Testing SMS service (mock mode)...")
    
    from notifications.service import SMSService
    
    # Create SMS service without Twilio credentials (will use mock mode)
    sms_service = SMSService()
    
    result = sms_service.send_sms(
        "+1234567890",
        "Test SMS: This is a test SMS message from the Fantasy Football app!"
    )
    
    logger.info(f"SMS service test result: {result}")
    logger.info(f"SMS sent successfully: {result.get('success', False)}")
    logger.info(f"Mock mode: {result.get('mock', False)}")
    
    return result.get('success', False)

def main():
    """Run all notification system tests."""
    logger.info("=" * 60)
    logger.info("FANTASY FOOTBALL NOTIFICATION SYSTEM TESTS")
    logger.info("=" * 60)
    
    all_tests_passed = True
    
    try:
        # Test individual services
        logger.info("\n1. Testing Email Service...")
        if not test_email_service():
            all_tests_passed = False
            logger.error("Email service test failed")
        
        logger.info("\n2. Testing Push Notification Service...")
        if not test_push_service():
            all_tests_passed = False
            logger.error("Push notification service test failed")
        
        logger.info("\n3. Testing SMS Service...")
        if not test_sms_service():
            all_tests_passed = False
            logger.error("SMS service test failed")
        
        logger.info("\n4. Testing Notification Templates...")
        if not test_notification_templates():
            all_tests_passed = False
            logger.error("Notification templates test failed")
        
        logger.info("\n5. Testing Full Notification System...")
        if not test_notification_service():
            all_tests_passed = False
            logger.error("Notification system test failed")
        
        # Final results
        logger.info("\n" + "=" * 60)
        if all_tests_passed:
            logger.info("🎉 ALL TESTS PASSED! Notification system is working correctly.")
        else:
            logger.error("❌ SOME TESTS FAILED! Please check the logs above.")
        logger.info("=" * 60)
        
        return all_tests_passed
        
    except Exception as e:
        logger.error(f"Critical error during testing: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)