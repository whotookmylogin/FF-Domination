import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import numpy as np

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from ai.scoring import SimpleScoringAlgorithm

class TestSimpleScoringAlgorithm(unittest.TestCase):
    """Unit tests for simple scoring algorithm."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scoring_algorithm = SimpleScoringAlgorithm()
        
    def test_positional_weighting(self):
        """Test positional weighting calculations."""
        # Test RB weighting
        rb_weight = self.scoring_algorithm._get_positional_weight('RB')
        self.assertEqual(rb_weight, 1.0)
        
        # Test QB weighting
        qb_weight = self.scoring_algorithm._get_positional_weight('QB')
        self.assertEqual(qb_weight, 1.0)
        
        # Test unknown position
        unknown_weight = self.scoring_algorithm._get_positional_weight('UNKNOWN')
        self.assertEqual(unknown_weight, 1.0)
        
    def test_matchup_factor(self):
        """Test matchup difficulty factor calculations."""
        # Test easy matchup
        easy_matchup = self.scoring_algorithm._calculate_matchup_factor(1)  # Easy defense
        self.assertGreater(easy_matchup, 1.0)
        
        # Test hard matchup
        hard_matchup = self.scoring_algorithm._calculate_matchup_factor(32)  # Hard defense
        self.assertLess(hard_matchup, 1.0)
        
        # Test average matchup
        avg_matchup = self.scoring_algorithm._calculate_matchup_factor(16)  # Average defense
        self.assertEqual(avg_matchup, 1.0)
        
    def test_weather_factor(self):
        """Test weather impact factor calculations."""
        # Test good weather
        good_weather = self.scoring_algorithm._calculate_weather_factor('sunny')
        self.assertEqual(good_weather, 1.0)
        
        # Test bad weather
        bad_weather = self.scoring_algorithm._calculate_weather_factor('rain')
        self.assertLess(bad_weather, 1.0)
        
    def test_trend_analysis(self):
        """Test performance trend analysis."""
        # Test improving trend
        recent_scores = [10, 12, 15, 18]
        trend_factor = self.scoring_algorithm._analyze_trends(recent_scores)
        self.assertGreaterEqual(trend_factor, 1.0)
        
        # Test declining trend
        recent_scores = [18, 15, 12, 10]
        trend_factor = self.scoring_algorithm._analyze_trends(recent_scores)
        self.assertLessEqual(trend_factor, 1.0)
        
        # Test stable trend
        recent_scores = [15, 15, 15, 15]
        trend_factor = self.scoring_algorithm._analyze_trends(recent_scores)
        self.assertEqual(trend_factor, 1.0)
        
    def test_project_player_score(self):
        """Test player score projection."""
        player_data = {
            'position': 'RB',
            'team': 'BUF',
            'opponent': 'NE',
            'recent_scores': [12, 15, 14, 16]
        }
        
        # Mock matchup difficulty (NE defense rank)
        with patch.object(self.scoring_algorithm, '_get_defense_rank', return_value=20):
            projected_score = self.scoring_algorithm.project_player_score(player_data, 'rain')
            
            # Should return a numeric score
            self.assertIsInstance(projected_score, (int, float))
            self.assertGreater(projected_score, 0)

if __name__ == '__main__':
    unittest.main()
