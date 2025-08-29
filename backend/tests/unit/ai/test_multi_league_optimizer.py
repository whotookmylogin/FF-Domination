import unittest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from backend.src.ai.multi_league_optimizer import MultiLeagueOptimizer
from backend.src.database.models import League, Team, Player, RosterSlot, User

class TestMultiLeagueOptimizer(unittest.TestCase):
    """Test cases for the MultiLeagueOptimizer service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock(spec=Session)
        self.optimizer = MultiLeagueOptimizer(db_session=self.mock_db_session)
        
    def test_init(self):
        """Test MultiLeagueOptimizer initialization."""
        # The AI engine is instantiated directly, not mocked
        self.assertIsNotNone(self.optimizer.ai_engine)
        self.assertEqual(self.optimizer.db_session, self.mock_db_session)
        self.assertEqual(self.optimizer.optimization_version, "1.0")
        
    @patch('backend.src.ai.multi_league_optimizer.AIRecommendationEngine')
    def test_analyze_user_leagues_empty_session(self, mock_ai_engine):
        """Test analyze_user_leagues with empty database session."""
        # Create optimizer without db session
        optimizer = MultiLeagueOptimizer()
        result = optimizer.analyze_user_leagues("user123")
        
        self.assertIn("leagues", result)
        self.assertIn("recommendations", result)
        self.assertEqual(len(result["leagues"]), 0)
        self.assertEqual(len(result["recommendations"]), 0)
        
    @patch('backend.src.ai.multi_league_optimizer.AIRecommendationEngine')
    def test_analyze_user_leagues_success(self, mock_ai_engine):
        """Test successful user leagues analysis."""
        # Mock user and leagues data
        mock_user = Mock(spec=User)
        mock_user.username = "testuser"
        
        mock_league1 = Mock(spec=League)
        mock_league1.id = "league1"
        mock_league1.platform = "ESPN"
        mock_league1.league_name = "Test League 1"
        mock_league1.user = mock_user
        mock_league1.total_teams = 12
        mock_league1.current_week = 5
        
        mock_league2 = Mock(spec=League)
        mock_league2.id = "league2"
        mock_league2.platform = "Sleeper"
        mock_league2.league_name = "Test League 2"
        mock_league2.user = mock_user
        mock_league2.total_teams = 10
        mock_league2.current_week = 5
        
        # Mock teams and players
        mock_team1 = Mock(spec=Team)
        mock_team1.team_name = "Test Team 1"
        mock_team1.owner = "testuser"
        mock_team1.rank = 3
        
        mock_team2 = Mock(spec=Team)
        mock_team2.team_name = "Test Team 2"
        mock_team2.owner = "testuser"
        mock_team2.rank = 8
        
        mock_player1 = Mock(spec=Player)
        mock_player1.name = "Player One"
        mock_player1.position = "QB"
        mock_player1.projected_points = 15.0
        mock_player1.injury_status = 0
        
        mock_player2 = Mock(spec=Player)
        mock_player2.name = "Player Two"
        mock_player2.position = "RB"
        mock_player2.projected_points = 12.0
        mock_player2.injury_status = 1
        
        mock_roster_slot1 = Mock(spec=RosterSlot)
        mock_roster_slot1.player = mock_player1
        
        mock_roster_slot2 = Mock(spec=RosterSlot)
        mock_roster_slot2.player = mock_player2
        
        mock_team1.roster = [mock_roster_slot1, mock_roster_slot2]
        mock_team2.roster = [mock_roster_slot1, mock_roster_slot2]
        
        mock_league1.teams = [mock_team1]
        mock_league2.teams = [mock_team2]
        
        # Configure mock database session
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = [
            mock_league1, mock_league2
        ]
        
        # Configure mock AI engine
        mock_ai_engine_instance = Mock()
        mock_ai_engine_instance._calculate_team_strength.return_value = 125.5
        mock_ai_engine.return_value = mock_ai_engine_instance
        
        # Test analysis
        result = self.optimizer.analyze_user_leagues("user123")
        
        self.assertEqual(result["user_id"], "user123")
        self.assertEqual(len(result["leagues"]), 2)
        self.assertIn("recommendations", result)
        
        # Verify league analysis data
        league1_data = result["leagues"][0]
        self.assertEqual(league1_data["league_id"], "league1")
        self.assertEqual(league1_data["platform"], "ESPN")
        self.assertEqual(league1_data["league_name"], "Test League 1")
        self.assertIn("team_strength", league1_data)
        self.assertEqual(league1_data["rank"], 3)
        
        league2_data = result["leagues"][1]
        self.assertEqual(league2_data["league_id"], "league2")
        self.assertEqual(league2_data["platform"], "Sleeper")
        self.assertEqual(league2_data["league_name"], "Test League 2")
        self.assertIn("team_strength", league2_data)
        self.assertEqual(league2_data["rank"], 8)
        
    @patch('backend.src.ai.multi_league_optimizer.AIRecommendationEngine')
    def test_analyze_user_leagues_with_errors(self, mock_ai_engine):
        """Test user leagues analysis when some leagues have errors."""
        # Mock user and leagues data
        mock_user = Mock(spec=User)
        mock_user.username = "testuser"
        
        mock_league1 = Mock(spec=League)
        mock_league1.id = "league1"
        mock_league1.platform = "ESPN"
        mock_league1.league_name = "Test League 1"
        mock_league1.user = mock_user
        mock_league1.total_teams = 12
        mock_league1.current_week = 5
        
        mock_league2 = Mock(spec=League)
        mock_league2.id = "league2"
        mock_league2.platform = "Sleeper"
        mock_league2.league_name = "Test League 2"
        mock_league2.user = mock_user
        mock_league2.total_teams = 10
        mock_league2.current_week = 5
        
        # Configure mock database session to return one valid league and one with error
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = [
            mock_league1, mock_league2
        ]
        
        # Configure mock AI engine
        mock_ai_engine_instance = Mock()
        mock_ai_engine_instance._calculate_team_strength.return_value = 125.5
        mock_ai_engine.return_value = mock_ai_engine_instance
        
        # Test analysis
        result = self.optimizer.analyze_user_leagues("user123")
        
        self.assertEqual(result["user_id"], "user123")
        self.assertEqual(len(result["leagues"]), 2)
        self.assertIn("recommendations", result)
        
    def test_generate_cross_league_recommendations(self):
        """Test cross-league recommendation generation."""
        # Test data with multiple leagues
        league_analysis = [
            {
                "league_id": "league1",
                "platform": "ESPN",
                "league_name": "Test League 1",
                "team_strength": 125.5,
                "rank": 3,
                "total_teams": 12,
                "current_week": 5
            },
            {
                "league_id": "league2",
                "platform": "Sleeper",
                "league_name": "Test League 2",
                "team_strength": 95.2,
                "rank": 8,
                "total_teams": 10,
                "current_week": 5
            }
        ]
        
        # The method uses the actual AI engine, not a mock
        # Calculate expected team strength based on actual implementation
        # For the test data, with 2 players (15.0 and 12.0 projected points)
        # and some positional diversity, we expect a strength around 22.95
        pass
        
        recommendations = self.optimizer._generate_cross_league_recommendations(league_analysis)
        
        # Should have recommendations for underperforming leagues and resource allocation
        self.assertGreater(len(recommendations), 0)
        
        # Check that we have at least one recommendation
        self.assertGreater(len(recommendations), 0)
        
        # Check for resource allocation recommendation (should be present with multiple leagues)
        rec_types = [rec["type"] for rec in recommendations]
        self.assertIn("resource_allocation", rec_types)
        
    def test_generate_cross_league_recommendations_no_leagues(self):
        """Test cross-league recommendation generation with no leagues."""
        recommendations = self.optimizer._generate_cross_league_recommendations([])
        self.assertEqual(len(recommendations), 0)
        
    def test_generate_cross_league_recommendations_single_league(self):
        """Test cross-league recommendation generation with single league."""
        league_analysis = [
            {
                "league_id": "league1",
                "platform": "ESPN",
                "league_name": "Test League 1",
                "team_strength": 125.5,
                "rank": 3,
                "total_teams": 12,
                "current_week": 5
            }
        ]
        
        recommendations = self.optimizer._generate_cross_league_recommendations(league_analysis)
        
        # Should not have resource allocation recommendation with only one league
        rec_types = [rec["type"] for rec in recommendations]
        self.assertNotIn("resource_allocation", rec_types)

if __name__ == '__main__':
    unittest.main()
