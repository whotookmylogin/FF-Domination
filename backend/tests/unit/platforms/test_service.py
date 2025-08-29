import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from platforms.service import PlatformIntegrationService

class TestPlatformIntegrationService(unittest.TestCase):
    """Unit tests for unified platform integration service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.platform_service = PlatformIntegrationService(espn_cookie="dummy_cookie", sleeper_token="dummy_token")
        
    @patch('platforms.service.ESPNIntegration')
    @patch('platforms.service.SleeperIntegration')
    def test_initialize_integrations(self, mock_sleeper, mock_espn):
        """Test that platform integrations are properly initialized."""
        # Assertions
        self.assertIsNotNone(self.platform_service.espn_integration)
        self.assertIsNotNone(self.platform_service.sleeper_integration)
        
    def test_get_league_data_espn(self):
        """Test ESPN league data fetch."""
        # Mock ESPN integration
        self.platform_service.espn_integration = MagicMock()
        mock_league_data = {'id': 'espn_league', 'name': 'ESPN League'}
        self.platform_service.espn_integration.get_roster_data.return_value = mock_league_data
        
        # Test the method
        league_data = self.platform_service.get_league_data('espn', 'espn_league_id')
        
        # Assertions
        self.platform_service.espn_integration.get_roster_data.assert_called_once_with(2023, 'espn_league_id')
        self.assertEqual(league_data['id'], 'espn_league')
        
    def test_get_league_data_sleeper(self):
        """Test Sleeper league data fetch."""
        # Mock Sleeper integration
        self.platform_service.sleeper_integration = MagicMock()
        mock_league_data = {'id': 'sleeper_league', 'name': 'Sleeper League'}
        self.platform_service.sleeper_integration.get_rosters_data.return_value = mock_league_data
        
        # Test the method
        league_data = self.platform_service.get_league_data('sleeper', 'sleeper_league_id')
        
        # Assertions
        self.platform_service.sleeper_integration.get_rosters_data.assert_called_once_with('sleeper_league_id')
        self.assertEqual(league_data['id'], 'sleeper_league')
        
    def test_get_user_data_espn(self):
        """Test ESPN user data fetch."""
        # Mock ESPN integration
        self.platform_service.espn_integration = MagicMock()
        mock_user_data = {'id': 'espn_user', 'username': 'ESPN User'}
        self.platform_service.espn_integration.get_user_data.return_value = mock_user_data
        
        # Test the method
        user_data = self.platform_service.get_user_data('espn', 'espn_user_id')
        
        # Assertions
        self.platform_service.espn_integration.get_user_data.assert_called_once_with('espn_user_id')
        self.assertEqual(user_data['username'], 'ESPN User')
        
    def test_get_user_data_sleeper(self):
        """Test Sleeper user data fetch."""
        # Mock Sleeper integration
        self.platform_service.sleeper_integration = MagicMock()
        mock_user_data = {'id': 'sleeper_user', 'username': 'Sleeper User'}
        self.platform_service.sleeper_integration.get_user_data.return_value = mock_user_data
        
        # Test the method
        user_data = self.platform_service.get_user_data('sleeper', 'sleeper_user_id')
        
        # Assertions
        self.platform_service.sleeper_integration.get_user_data.assert_called_once_with('sleeper_user_id')
        self.assertEqual(user_data['username'], 'Sleeper User')

if __name__ == '__main__':
    unittest.main()
