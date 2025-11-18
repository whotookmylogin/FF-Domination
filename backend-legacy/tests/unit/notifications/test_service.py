import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from notifications.service import NotificationService

class TestNotificationService(unittest.TestCase):
    """Unit tests for notification service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.notification_service = NotificationService()
        
    @patch('notifications.service.firebase_admin')
    def test_send_push_notification_success(self, mock_firebase):
        """Test successful push notification sending."""
        # Mock Firebase response
        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_firebase.messaging.send.return_value = mock_response
        
        # Test the method
        success = self.notification_service.send_push_notification(
            'test_token', 'Test Title', 'Test Body'
        )
        
        # Assertions
        self.assertTrue(success)
        mock_firebase.messaging.send.assert_called_once()
        
    @patch('notifications.service.firebase_admin')
    def test_send_push_notification_failure(self, mock_firebase):
        """Test failed push notification sending."""
        # Mock Firebase exception
        mock_firebase.messaging.send.side_effect = Exception("Firebase error")
        
        # Test the method
        success = self.notification_service.send_push_notification(
            'invalid_token', 'Test Title', 'Test Body'
        )
        
        # Assertions
        self.assertFalse(success)
        
    def test_send_trade_proposal_notification(self):
        """Test trade proposal notification sending."""
        # Mock push notification method
        self.notification_service.send_push_notification = MagicMock(return_value=True)
        
        # Test the method
        success = self.notification_service.send_trade_proposal_notification(
            'user_token', 'Team A', 'Team B', 'ACCEPT'
        )
        
        # Assertions
        self.assertTrue(success)
        self.notification_service.send_push_notification.assert_called_once()
        
    def test_send_waiver_claim_notification(self):
        """Test waiver claim notification sending."""
        # Mock push notification method
        self.notification_service.send_push_notification = MagicMock(return_value=True)
        
        # Test the method
        success = self.notification_service.send_waiver_claim_notification(
            'user_token', 'Test Player', 25.0, True
        )
        
        # Assertions
        self.assertTrue(success)
        self.notification_service.send_push_notification.assert_called_once()
        
    def test_send_news_alert(self):
        """Test news alert notification sending."""
        # Mock push notification method
        self.notification_service.send_push_notification = MagicMock(return_value=True)
        
        # Test the method
        success = self.notification_service.send_news_alert(
            'user_token', 'Breaking News', 'High impact player news', 5
        )
        
        # Assertions
        self.assertTrue(success)
        self.notification_service.send_push_notification.assert_called_once()

if __name__ == '__main__':
    unittest.main()
