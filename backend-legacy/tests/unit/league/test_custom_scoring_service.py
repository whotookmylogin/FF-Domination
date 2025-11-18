import unittest
from unittest.mock import Mock, patch
import logging
import json

from backend.src.league.custom_scoring_service import CustomScoringService
from backend.src.database.models import League, User

class TestCustomScoringService(unittest.TestCase):
    """Test cases for the CustomScoringService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.custom_scoring_service = CustomScoringService(db_session=self.mock_db_session)
        
    def test_init(self):
        """Test CustomScoringService initialization."""
        self.assertEqual(self.custom_scoring_service.db_session, self.mock_db_session)
        self.assertEqual(self.custom_scoring_service.service_version, "1.0")
        self.assertIsNotNone(self.custom_scoring_service.default_scoring)
        
    def test_get_league_scoring_settings_empty_session(self):
        """Test get_league_scoring_settings with empty database session."""
        # Create service without db session
        service = CustomScoringService()
        result = service.get_league_scoring_settings("league123")
        
        # Should return default settings
        self.assertIn("scoring_type", result)
        self.assertEqual(result["scoring_type"], "default")
        
    def test_get_league_scoring_settings_with_custom_settings(self):
        """Test get_league_scoring_settings with custom league settings."""
        # Mock league with custom scoring settings
        mock_league = Mock(spec=League)
        mock_league.scoring_settings = json.dumps({
            "scoring_type": "custom",
            "scoring_multipliers": {
                "passing_yards": 0.05,
                "passing_touchdowns": 5.0,
                "interceptions": -1.0
            }
        })
        
        # Configure mock database session
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_league
        
        result = self.custom_scoring_service.get_league_scoring_settings("league123")
        
        self.assertEqual(result["scoring_type"], "custom")
        self.assertEqual(result["scoring_multipliers"]["passing_yards"], 0.05)
        self.assertEqual(result["scoring_multipliers"]["passing_touchdowns"], 5.0)
        self.assertEqual(result["scoring_multipliers"]["interceptions"], -1.0)
        
    def test_get_league_scoring_settings_with_default_settings(self):
        """Test get_league_scoring_settings when league has no custom settings."""
        # Mock league without custom scoring settings
        mock_league = Mock(spec=League)
        mock_league.scoring_settings = None
        
        # Configure mock database session
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_league
        
        result = self.custom_scoring_service.get_league_scoring_settings("league123")
        
        # Should return default settings
        self.assertIn("scoring_type", result)
        self.assertEqual(result["scoring_type"], "default")
        
    def test_get_league_scoring_settings_league_not_found(self):
        """Test get_league_scoring_settings when league doesn't exist."""
        # Configure mock database session to return None
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.custom_scoring_service.get_league_scoring_settings("league123")
        
        # Should return default settings
        self.assertIn("scoring_type", result)
        self.assertEqual(result["scoring_type"], "default")
        
    def test_apply_custom_scoring_default(self):
        """Test apply_custom_scoring with default scoring settings."""
        # Mock player, matchup, and weather data
        player_data = {
            "position": "QB",
            "passing_yards": 250,
            "passing_touchdowns": 2,
            "interceptions": 1
        }
        
        matchup_data = {"difficulty": "average"}
        weather_data = {"conditions": "good"}
        
        # Mock league with default scoring
        mock_league = Mock(spec=League)
        mock_league.scoring_settings = json.dumps({"scoring_type": "default"})
        
        # Configure mock database session
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_league
        
        # Mock the default scoring algorithm
        with patch.object(self.custom_scoring_service.default_scoring, 'project_player_score', return_value=15.0):
            result = self.custom_scoring_service.apply_custom_scoring(
                player_data, matchup_data, weather_data, "league123"
            )
            
            self.assertEqual(result, 15.0)
            
    def test_apply_custom_scoring_custom(self):
        """Test apply_custom_scoring with custom scoring settings."""
        # Mock player data
        player_data = {
            "position": "QB",
            "passing_yards": 250,
            "passing_touchdowns": 2,
            "interceptions": 1
        }
        
        matchup_data = {"difficulty": "average"}
        weather_data = {"conditions": "good"}
        
        # Mock league with custom scoring settings
        mock_league = Mock(spec=League)
        mock_league.scoring_settings = json.dumps({
            "scoring_type": "custom",
            "scoring_multipliers": {
                "passing_yards": 0.05,
                "passing_touchdowns": 5.0,
                "interceptions": -1.0
            },
            "position_weights": {
                "QB": 1.1
            }
        })
        
        # Configure mock database session
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_league
        
        result = self.custom_scoring_service.apply_custom_scoring(
            player_data, matchup_data, weather_data, "league123"
        )
        
        # Expected calculation:
        # (250 * 0.05) + (2 * 5.0) + (1 * -1.0) = 12.5 + 10.0 - 1.0 = 21.5
        # Then apply QB position weight: 21.5 * 1.1 = 23.65
        self.assertAlmostEqual(result, 23.65, places=10)
        
    def test_apply_custom_scoring_league_not_found(self):
        """Test apply_custom_scoring when league is not found."""
        # Mock player, matchup, and weather data
        player_data = {
            "position": "QB",
            "passing_yards": 250,
            "passing_touchdowns": 2,
            "interceptions": 1
        }
        
        matchup_data = {"difficulty": "average"}
        weather_data = {"conditions": "good"}
        
        # Configure mock database session to return None for league query
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Mock the default scoring algorithm
        with patch.object(self.custom_scoring_service.default_scoring, 'project_player_score', return_value=15.0):
            result = self.custom_scoring_service.apply_custom_scoring(
                player_data, matchup_data, weather_data, "league123"
            )
            
            self.assertEqual(result, 15.0)
            
    def test_calculate_custom_score_with_position_weight(self):
        """Test _calculate_custom_score with position weighting."""
        player_data = {
            "position": "RB",
            "rushing_yards": 100,
            "rushing_touchdowns": 1
        }
        
        scoring_settings = {
            "scoring_multipliers": {
                "rushing_yards": 0.1,
                "rushing_touchdowns": 6.0
            },
            "position_weights": {
                "RB": 1.2
            }
        }
        
        result = self.custom_scoring_service._calculate_custom_score(player_data, scoring_settings)
        
        # Expected calculation:
        # (100 * 0.1) + (1 * 6.0) = 10.0 + 6.0 = 16.0
        # Then apply RB position weight: 16.0 * 1.2 = 19.2
        self.assertEqual(result, 19.2)
        
    def test_calculate_custom_score_without_position_weight(self):
        """Test _calculate_custom_score without position weighting."""
        player_data = {
            "position": "WR",
            "receiving_yards": 120,
            "receiving_touchdowns": 1
        }
        
        scoring_settings = {
            "scoring_multipliers": {
                "receiving_yards": 0.1,
                "receiving_touchdowns": 6.0
            },
            "position_weighting": False
        }
        
        result = self.custom_scoring_service._calculate_custom_score(player_data, scoring_settings)
        
        # Expected calculation:
        # (120 * 0.1) + (1 * 6.0) = 12.0 + 6.0 = 18.0
        # No position weighting applied
        self.assertEqual(result, 18.0)
        
    def test_update_league_scoring_settings_success(self):
        """Test successful update of league scoring settings."""
        # Mock league
        mock_league = Mock(spec=League)
        
        # Configure mock database session
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_league
        
        new_settings = {
            "scoring_type": "custom",
            "scoring_multipliers": {
                "passing_yards": 0.06
            }
        }
        
        result = self.custom_scoring_service.update_league_scoring_settings("league123", new_settings)
        
        self.assertTrue(result)
        # Check that the settings were converted to JSON string
        self.assertEqual(mock_league.scoring_settings, json.dumps(new_settings))
        self.mock_db_session.commit.assert_called_once()
        
    def test_update_league_scoring_settings_league_not_found(self):
        """Test update_league_scoring_settings when league is not found."""
        # Configure mock database session to return None
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        new_settings = {"scoring_type": "custom"}
        
        result = self.custom_scoring_service.update_league_scoring_settings("league123", new_settings)
        
        self.assertFalse(result)
        self.mock_db_session.commit.assert_not_called()
        
    def test_update_league_scoring_settings_db_error(self):
        """Test update_league_scoring_settings with database error."""
        # Mock league
        mock_league = Mock(spec=League)
        
        # Configure mock database session to raise exception
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_league
        self.mock_db_session.commit.side_effect = Exception("Database error")
        
        new_settings = {"scoring_type": "custom"}
        
        result = self.custom_scoring_service.update_league_scoring_settings("league123", new_settings)
        
        self.assertFalse(result)
        self.mock_db_session.rollback.assert_called_once()

if __name__ == '__main__':
    unittest.main()
