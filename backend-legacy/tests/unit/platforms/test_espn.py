import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from platforms.espn import ESPNIntegration

class TestESPNIntegration(unittest.TestCase):
    """Unit tests for ESPN integration service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.espn_integration = ESPNIntegration("dummy_cookie")
        
    @patch('platforms.espn.requests.get')
    def test_get_user_data_success(self, mock_get):
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
        user_data = self.espn_integration.get_user_data('user123')
        
        # Assertions
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data['user_id'], 'user123')
        self.assertEqual(user_data['display_name'], 'Test User')
        
    @patch('platforms.espn.requests.get')
    def test_get_user_data_failure(self, mock_get):
        """Test failed user data fetch."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Test the method
        user_data = self.espn_integration.get_user_data('invalid_user')
        
        # Assertions
        self.assertIsNone(user_data)
        
    @patch('platforms.espn.requests.get')
    def test_get_roster_data_success(self, mock_get):
        """Test successful roster data fetch."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'team123',
            'name': 'Test Team',
            'roster': {
                'entries': [
                    {
                        'playerId': 'player1',
                        'playerPoolEntry': {
                            'player': {
                                'fullName': 'John Smith',
                                'position': 'RB'
                            }
                        }
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Test the method
        roster_data = self.espn_integration.get_roster_data(2023, '12345')
        
        # Assertions
        self.assertIsNotNone(roster_data)
        self.assertEqual(len(roster_data['roster']['entries']), 1)
        
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Test that rate limiting is properly initialized
        self.assertIsNotNone(self.espn_integration.rate_limiter)
        self.assertEqual(self.espn_integration.rate_limiter.max_calls, 10)
        self.assertEqual(self.espn_integration.rate_limiter.period, 1)

if __name__ == '__main__':
    unittest.main()
