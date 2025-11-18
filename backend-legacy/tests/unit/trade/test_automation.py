import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from trade.automation import TradeAutomationService

class TestTradeAutomationService(unittest.TestCase):
    """Unit tests for trade automation service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trade_service = TradeAutomationService()
        
    @patch('trade.automation.AIRecommendationEngine')
    def test_generate_trade_proposal_success(self, mock_ai_engine):
        """Test successful trade proposal generation."""
        # Mock AI engine response
        mock_ai_engine_instance = MagicMock()
        mock_ai_engine_instance.evaluate_trade.return_value = {
            'recommendation': 'ACCEPT',
            'confidence': 'HIGH',
            'fairness_score': 75.5,
            'win_probability_delta': 0.05
        }
        self.trade_service.ai_engine = mock_ai_engine_instance
        
        # Mock team data
        team1_roster = [
            {'player_id': 'player1', 'name': 'Player One', 'position': 'QB', 'projected_points': 18.5},
            {'player_id': 'player2', 'name': 'Player Two', 'position': 'RB', 'projected_points': 12.3}
        ]
        
        team2_roster = [
            {'player_id': 'player3', 'name': 'Player Three', 'position': 'WR', 'projected_points': 15.2},
            {'player_id': 'player4', 'name': 'Player Four', 'position': 'TE', 'projected_points': 10.1}
        ]
        
        # Test the method
        trade_proposal = self.trade_service.generate_trade_proposal(
            'team123', 'team456', team1_roster, team2_roster
        )
        
        # Assertions
        self.assertIsNotNone(trade_proposal)
        self.assertIn('recommendation', trade_proposal)
        self.assertIn('fairness_score', trade_proposal)
        self.assertIn('win_probability_delta', trade_proposal)
        
    def test_calculate_roster_impact(self):
        """Test roster impact calculation."""
        team_roster = [
            {'position': 'QB', 'projected_points': 18.5},
            {'position': 'RB', 'projected_points': 12.3},
            {'position': 'RB', 'projected_points': 10.1},
            {'position': 'WR', 'projected_points': 15.2},
            {'position': 'WR', 'projected_points': 11.7},
            {'position': 'TE', 'projected_points': 8.9}
        ]
        
        acquire_players = [
            {'position': 'RB', 'projected_points': 16.8},
            {'position': 'WR', 'projected_points': 13.4}
        ]
        
        offer_players = [
            {'position': 'RB', 'projected_points': 10.1},
            {'position': 'TE', 'projected_points': 8.9}
        ]
        
        impact = self.trade_service._calculate_roster_impact(
            team_roster, acquire_players, offer_players
        )
        
        # Should return impact metrics
        self.assertIn('total_points_delta', impact)
        self.assertIn('position_changes', impact)
        self.assertIn('roster_strength_delta', impact)
        
    def test_filter_relevant_trades(self):
        """Test filtering of relevant trades."""
        # Mock trade proposals
        trade_proposals = [
            {'fairness_score': 85, 'win_probability_delta': 0.08},
            {'fairness_score': 45, 'win_probability_delta': -0.02},
            {'fairness_score': 72, 'win_probability_delta': 0.03}
        ]
        
        # Test filtering with threshold
        relevant_trades = self.trade_service._filter_relevant_trades(trade_proposals, min_fairness=70)
        
        # Should only return trades with fairness >= 70
        self.assertEqual(len(relevant_trades), 2)
        for trade in relevant_trades:
            self.assertGreaterEqual(trade['fairness_score'], 70)
            
    @patch('trade.automation.NotificationService')
    def test_send_trade_notification(self, mock_notification_service):
        """Test sending trade notification."""
        # Mock notification service
        mock_notification_instance = MagicMock()
        mock_notification_instance.send_trade_proposal_notification.return_value = True
        self.trade_service.notification_service = mock_notification_instance
        
        # Mock trade proposal
        trade_proposal = {
            'team1_id': 'team123',
            'team2_id': 'team456',
            'recommendation': 'ACCEPT',
            'fairness_score': 75.5
        }
        
        # Test the method
        success = self.trade_service._send_trade_notification(trade_proposal)
        
        # Assertions
        self.assertTrue(success)
        mock_notification_instance.send_trade_proposal_notification.assert_called_once()

if __name__ == '__main__':
    unittest.main()
