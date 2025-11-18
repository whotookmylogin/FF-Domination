import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import numpy as np

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from ai.recommendation_engine import AIRecommendationEngine

class TestAIRecommendationEngine(unittest.TestCase):
    """Unit tests for AI recommendation engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ai_engine = AIRecommendationEngine()
        
    def test_calculate_positional_weights(self):
        """Test positional weight calculations based on league settings."""
        league_settings = {
            'roster_positions': {
                'QB': 1,
                'RB': 2,
                'WR': 2,
                'TE': 1
            }
        }
        
        weights = self.ai_engine._calculate_positional_weights(league_settings)
        
        # All positions should have weights
        self.assertIn('QB', weights)
        self.assertIn('RB', weights)
        self.assertIn('WR', weights)
        self.assertIn('TE', weights)
        
        # RB and WR should have higher weights due to multiple slots
        self.assertGreaterEqual(weights['RB'], weights['QB'])
        self.assertGreaterEqual(weights['WR'], weights['QB'])
        
    @patch('ai.recommendation_engine.RandomForestRegressor')
    def test_train_model_success(self, mock_rf):
        """Test successful model training."""
        # Mock the RandomForestRegressor
        mock_model = MagicMock()
        mock_rf.return_value = mock_model
        
        # Mock training data
        training_data = {
            'features': np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
            'targets': np.array([10, 20, 30])
        }
        
        # Test the method
        success = self.ai_engine.train_model(training_data)
        
        # Assertions
        self.assertTrue(success)
        mock_rf.assert_called_once_with(n_estimators=100, random_state=42)
        mock_model.fit.assert_called_once_with(training_data['features'], training_data['targets'])
        
    def test_predict_player_performance_success(self):
        """Test successful player performance prediction."""
        # Mock trained model
        self.ai_engine.model = MagicMock()
        self.ai_engine.model.predict.return_value = np.array([15.5])
        
        # Mock player features
        player_features = [1, 2, 3, 4, 5]
        
        # Test the method
        prediction = self.ai_engine.predict_player_performance(player_features)
        
        # Assertions
        self.assertIsNotNone(prediction)
        self.assertEqual(prediction['predicted_score'], 15.5)
        self.assertIn('confidence_interval', prediction)
        
    def test_predict_player_performance_no_model(self):
        """Test player performance prediction when no model is trained."""
        # No model set up
        self.ai_engine.model = None
        
        # Mock player features
        player_features = [1, 2, 3, 4, 5]
        
        # Test the method
        prediction = self.ai_engine.predict_player_performance(player_features)
        
        # Assertions
        self.assertIsNone(prediction)
        
    def test_evaluate_trade_fairness(self):
        """Test trade fairness evaluation."""
        team_id = "team123"
        acquire_players = [
            {"projected_score": 18.5},
            {"projected_score": 12.3}
        ]
        offer_players = [
            {"projected_score": 15.2},
            {"projected_score": 10.1}
        ]
        
        fairness_score = self.ai_engine._evaluate_trade_fairness(
            team_id, acquire_players, offer_players
        )
        
        # Should return a score between 1-100
        self.assertIsInstance(fairness_score, (int, float))
        self.assertGreaterEqual(fairness_score, 1)
        self.assertLessEqual(fairness_score, 100)
        
    def test_calculate_win_probability_delta(self):
        """Test win probability delta calculation."""
        current_win_prob = 0.65
        projected_win_prob = 0.72
        
        delta = self.ai_engine._calculate_win_probability_delta(
            current_win_prob, projected_win_prob
        )
        
        # Should return the difference
        self.assertEqual(delta, 0.07)

if __name__ == '__main__':
    unittest.main()
