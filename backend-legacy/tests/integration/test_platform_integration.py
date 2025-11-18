import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from platforms.service import PlatformIntegrationService

class TestPlatformIntegrationServiceIntegration(unittest.TestCase):
    """Integration tests for platform integration service."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize with dummy credentials
        self.platform_service = PlatformIntegrationService(
            espn_cookie="dummy_cookie",
            sleeper_token="dummy_token"
        )
        
    def test_platform_service_initialization(self):
        """Test that platform service initializes with both integrations."""
        self.assertIsNotNone(self.platform_service.espn_integration)
        self.assertIsNotNone(self.platform_service.sleeper_integration)
        
    @patch('platforms.espn.ESPNIntegration.get_user_data')
    def test_espn_user_data_integration(self, mock_get_user_data):
        """Test ESPN user data integration."""
        # Mock response
        mock_user_data = {
            'user_id': 'espn_user_123',
            'display_name': 'Test ESPN User'
        }
        mock_get_user_data.return_value = mock_user_data
        
        # Test the integration
        user_data = self.platform_service.get_user_data('espn', 'espn_user_123')
        
        # Assertions
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data['user_id'], 'espn_user_123')
        self.assertEqual(user_data['display_name'], 'Test ESPN User')
        mock_get_user_data.assert_called_once_with('espn_user_123')
        
    @patch('platforms.sleeper.SleeperIntegration.get_user_data')
    def test_sleeper_user_data_integration(self, mock_get_user_data):
        """Test Sleeper user data integration."""
        # Mock response
        mock_user_data = {
            'user_id': 'sleeper_user_123',
            'display_name': 'Test Sleeper User'
        }
        mock_get_user_data.return_value = mock_user_data
        
        # Test the integration
        user_data = self.platform_service.get_user_data('sleeper', 'sleeper_user_123')
        
        # Assertions
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data['user_id'], 'sleeper_user_123')
        self.assertEqual(user_data['display_name'], 'Test Sleeper User')
        mock_get_user_data.assert_called_once_with('sleeper_user_123')

if __name__ == '__main__':
    unittest.main()
