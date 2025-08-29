import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from platforms.sleeper import SleeperIntegration

class TestSleeperIntegration(unittest.TestCase):
    """Unit tests for Sleeper integration service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sleeper_integration = SleeperIntegration("dummy_token")
        
    @patch('platforms.sleeper.requests.get')
    def test_fetch_user_data_success(self, mock_get):
        """Test successful user data fetch."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'user_id': 'user123',
            'display_name': 'Test User',
            'avatar': 'avatar_hash'
        }
        mock_get.return_value = mock_response
        
        # Test the method
        user_data = self.sleeper_integration.fetch_user_data('user123')
        
        # Assertions
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data['user_id'], 'user123')
        self.assertEqual(user_data['display_name'], 'Test User')
        
    @patch('platforms.sleeper.requests.get')
    def test_fetch_user_data_failure(self, mock_get):
        """Test failed user data fetch."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Test the method
        user_data = self.sleeper_integration.fetch_user_data('invalid_user')
        
        # Assertions
        self.assertIsNone(user_data)
        
    @patch('platforms.sleeper.requests.get')
    def test_fetch_league_rosters_success(self, mock_get):
        """Test successful league rosters fetch."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'roster_id': 'roster1',
                'owner_id': 'user1',
                'players': ['player1', 'player2']
            },
            {
                'roster_id': 'roster2',
                'owner_id': 'user2',
                'players': ['player3', 'player4']
            }
        ]
        mock_get.return_value = mock_response
        
        # Test the method
        rosters = self.sleeper_integration.fetch_league_rosters('league123')
        
        # Assertions
        self.assertIsNotNone(rosters)
        self.assertEqual(len(rosters), 2)
        self.assertEqual(rosters[0]['roster_id'], 'roster1')
        
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Test that rate limiting is properly initialized
        self.assertIsNotNone(self.sleeper_integration.rate_limiter)
        self.assertEqual(self.sleeper_integration.rate_limiter.max_calls, 10)
        self.assertEqual(self.sleeper_integration.rate_limiter.period, 1)

if __name__ == '__main__':
    unittest.main()
