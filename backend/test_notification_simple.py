#!/usr/bin/env python3
"""
Simple notification system test that doesn't require database connectivity.
This tests the core notification service components in isolation.
"""

import sys
import os
import logging
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_notification_templates():
    """Test the notification templates without database."""
    logger.info("Testing notification templates...")
    
    try:
        from notifications.service import NotificationTemplates
        
        templates = NotificationTemplates()
        
        # Test trade proposal template
        trade_data = {
            "you_give": ["Christian McCaffrey", "Stefon Diggs"],
            "you_get": ["Derrick Henry"],
            "fairness_score": 85,
            "win_probability_delta": 12.5
        }
        trade_template = templates.trade_proposal(trade_data)
        logger.info(f"✓ Trade proposal template")
        logger.info(f"  Title: {trade_template['title']}")
        assert "Trade Proposal" in trade_template['title']
        assert "Christian McCaffrey" in trade_template['message']
        
        # Test waiver results template
        waiver_data = {
            "successful_claims": [
                {"player_name": "Backup RB", "bid_amount": 25}
            ],
            "failed_claims": [
                {"player_name": "Handcuff WR", "winning_bid": 50}
            ]
        }
        waiver_template = templates.waiver_results(waiver_data)
        logger.info(f"✓ Waiver results template")
        logger.info(f"  Title: {waiver_template['title']}")
        assert "Waiver Wire Results" in waiver_template['title']
        assert "Backup RB" in waiver_template['message']
        
        # Test breaking news template
        news_data = {
            "headline": "Star QB suffers season-ending injury",
            "summary": "The quarterback will miss the remainder of the season.",
            "urgency_score": 5,
            "affected_players": ["Star QB"],
            "source": "ESPN"
        }
        news_template = templates.breaking_news(news_data)
        logger.info(f"✓ Breaking news template")
        logger.info(f"  Title: {news_template['title']}")
        assert "URGENT" in news_template['title']
        assert "Star QB" in news_template['message']
        
        # Test lineup reminder template
        reminder_data = {
            "week": 8,
            "hours_until_games": 2
        }
        reminder_template = templates.lineup_reminder(reminder_data)
        logger.info(f"✓ Lineup reminder template")
        logger.info(f"  Title: {reminder_template['title']}")
        assert "Lineup Reminder" in reminder_template['title']
        assert "Week 8" in reminder_template['message']
        
        # Test injury update template
        injury_data = {
            "player_name": "Star RB",
            "status": "questionable",
            "injury_type": "Ankle sprain",
            "expected_return": "Next week",
            "fantasy_impact": "Monitor practice reports"
        }
        injury_template = templates.injury_update(injury_data)
        logger.info(f"✓ Injury update template")
        logger.info(f"  Title: {injury_template['title']}")
        assert "Star RB" in injury_template['title']
        assert "questionable" in injury_template['message']
        
        logger.info("All template tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Template test error: {e}")
        return False

def test_email_service():
    """Test email service in mock mode."""
    logger.info("Testing email service...")
    
    try:
        from notifications.service import EmailService
        
        # Create email service without credentials (mock mode)
        email_service = EmailService()
        
        result = email_service.send_email(
            "test@example.com",
            "Test Subject",
            "Test message content"
        )
        
        logger.info(f"✓ Email service test")
        logger.info(f"  Result: {result}")
        assert result['success'] is True
        assert result['mock'] is True
        
        return True
        
    except Exception as e:
        logger.error(f"Email service test error: {e}")
        return False

def test_sms_service():
    """Test SMS service in mock mode."""
    logger.info("Testing SMS service...")
    
    try:
        from notifications.service import SMSService
        
        # Create SMS service without credentials (mock mode)
        sms_service = SMSService()
        
        result = sms_service.send_sms(
            "+1234567890",
            "Test SMS message"
        )
        
        logger.info(f"✓ SMS service test")
        logger.info(f"  Result: {result}")
        assert result['success'] is True
        assert result['mock'] is True
        
        return True
        
    except Exception as e:
        logger.error(f"SMS service test error: {e}")
        return False

def test_push_service():
    """Test push notification service in mock mode."""
    logger.info("Testing push notification service...")
    
    try:
        from notifications.service import PushNotificationService
        
        # Create push service without FCM key (mock mode)
        push_service = PushNotificationService()
        
        result = push_service.send_push_notification(
            ["token1", "token2"],
            "Test Title",
            "Test message",
            {"key": "value"}
        )
        
        logger.info(f"✓ Push notification service test")
        logger.info(f"  Result: {result}")
        assert result['success'] is True
        assert result['mock'] is True
        
        return True
        
    except Exception as e:
        logger.error(f"Push service test error: {e}")
        return False

def test_service_creation():
    """Test notification service creation."""
    logger.info("Testing notification service creation...")
    
    try:
        from notifications.service import create_notification_service, EmailService, SMSService, PushNotificationService
        
        # Test individual services
        email_service = EmailService()
        sms_service = SMSService()
        push_service = PushNotificationService()
        
        logger.info("✓ Individual services created successfully")
        
        # Test composite service creation
        notification_service = create_notification_service()
        
        logger.info("✓ Notification service created successfully")
        logger.info(f"  Has email service: {notification_service.email_service is not None}")
        logger.info(f"  Has SMS service: {notification_service.sms_service is not None}")
        logger.info(f"  Has push service: {notification_service.push_service is not None}")
        logger.info(f"  Has templates: {notification_service.templates is not None}")
        
        return True
        
    except Exception as e:
        logger.error(f"Service creation test error: {e}")
        return False

def test_model_imports():
    """Test that database models can be imported."""
    logger.info("Testing database model imports...")
    
    try:
        from database.models import (
            Notification, 
            NotificationPreferences, 
            NotificationQueue,
            User
        )
        
        logger.info("✓ Database models imported successfully")
        logger.info(f"  Notification model: {Notification}")
        logger.info(f"  NotificationPreferences model: {NotificationPreferences}")
        logger.info(f"  NotificationQueue model: {NotificationQueue}")
        logger.info(f"  User model: {User}")
        
        return True
        
    except Exception as e:
        logger.error(f"Model import test error: {e}")
        return False

def main():
    """Run all notification system tests that don't require database."""
    logger.info("=" * 70)
    logger.info("FANTASY FOOTBALL NOTIFICATION SYSTEM - SIMPLE TESTS")
    logger.info("=" * 70)
    
    tests = [
        ("Model Imports", test_model_imports),
        ("Service Creation", test_service_creation),
        ("Notification Templates", test_notification_templates),
        ("Email Service", test_email_service),
        ("SMS Service", test_sms_service),
        ("Push Notification Service", test_push_service),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 50)
        
        try:
            if test_func():
                logger.info(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    # Final results
    logger.info("\n" + "=" * 70)
    logger.info(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Notification system components are working.")
        logger.info("\nNext steps:")
        logger.info("1. Set up database connection for full testing")
        logger.info("2. Configure email credentials (SMTP_EMAIL, SMTP_PASSWORD)")
        logger.info("3. Configure push notifications (FCM_SERVER_KEY)")
        logger.info("4. Configure SMS (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)")
        logger.info("5. Test with real API endpoints")
    else:
        logger.error(f"❌ {total - passed} TESTS FAILED! Please fix the issues above.")
    
    logger.info("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)