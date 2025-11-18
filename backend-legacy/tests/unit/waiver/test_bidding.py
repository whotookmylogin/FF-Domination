import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from waiver.services.bidding import WaiverBiddingService

class TestWaiverBiddingService(unittest.TestCase):
    """Unit tests for waiver bidding service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.waiver_service = WaiverBiddingService()
        
    def test_evaluate_waiver_claim_conditions(self):
        """Test waiver claim condition evaluation."""
        # Mock player and team data
        player_data = {
            'name': 'Test Player',
            'position': 'RB',
            'projected_points': 15.5,
            'injury_status': 0,
            'news_urgency': 4
        }
        
        team_needs = {
            'positional_strength': {'RB': 65, 'WR': 80, 'QB': 90},
            'positional_depth': {'RB': 2, 'WR': 4, 'QB': 1}
        }
        
        faab_budget = 50.0
        
        conditions = self.waiver_service._evaluate_waiver_claim_conditions(
            player_data, team_needs, faab_budget
        )
        
        # Should return condition metrics
        self.assertIsInstance(conditions, dict)
        self.assertIn('news_urgency_factor', conditions)
        self.assertIn('team_need_score', conditions)
        self.assertIn('projected_value', conditions)
        
    def test_calculate_team_need_score(self):
        """Test team need score calculation."""
        player_position = 'RB'
        team_needs = {
            'positional_strength': {'RB': 65, 'WR': 80, 'QB': 90},
            'positional_depth': {'RB': 2, 'WR': 4, 'QB': 1}
        }
        
        need_score = self.waiver_service._calculate_team_need_score(player_position, team_needs)
        
        # Should return a numeric need score
        self.assertIsInstance(need_score, (int, float))
        self.assertGreaterEqual(need_score, 0)
        self.assertLessEqual(need_score, 100)
        
    def test_estimate_required_bid(self):
        """Test required bid estimation."""
        player_data = {
            'name': 'Test Player',
            'position': 'RB',
            'projected_points': 15.5,
            'injury_status': 0,
            'news_urgency': 4
        }
        
        team_needs = {
            'positional_strength': {'RB': 65, 'WR': 80, 'QB': 90},
            'positional_depth': {'RB': 2, 'WR': 4, 'QB': 1}
        }
        
        faab_budget = 50.0
        
        bid_amount = self.waiver_service._estimate_required_bid(player_data, team_needs, faab_budget)
        
        # Should return a numeric bid amount
        self.assertIsInstance(bid_amount, (int, float))
        self.assertGreaterEqual(bid_amount, 0)
        
    def test_generate_bidding_recommendation(self):
        """Test bidding recommendation generation."""
        # Mock player data
        player_data = {
            'name': 'Test Player',
            'position': 'RB',
            'projected_points': 15.5,
            'injury_status': 1,  # questionable
            'news_urgency': 4
        }
        
        # Mock team needs
        team_needs = {
            'positional_strength': {'RB': 65, 'WR': 80, 'QB': 90},
            'positional_depth': {'RB': 2, 'WR': 4, 'QB': 1}
        }
        
        faab_budget = 50.0
        
        recommendation = self.waiver_service.generate_bidding_recommendation(
            player_data, team_needs, faab_budget
        )
        
        # Should return a recommendation with all required fields
        self.assertIsInstance(recommendation, dict)
        self.assertIn('should_claim', recommendation)
        self.assertIn('recommended_bid', recommendation)
        self.assertIn('confidence_level', recommendation)
        self.assertIn('reasoning', recommendation)
        
    def test_get_competitive_bid_probability(self):
        """Test competitive bid probability calculation."""
        recommended_bid = 25.0
        player_value = 15.5
        faab_budget = 50.0
        
        probability = self.waiver_service._get_competitive_bid_probability(
            recommended_bid, player_value, faab_budget
        )
        
        # Should return a probability between 0 and 1
        self.assertIsInstance(probability, float)
        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)

if __name__ == '__main__':
    unittest.main()
