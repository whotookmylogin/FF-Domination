import unittest
from unittest.mock import Mock, patch
import logging
import json
from datetime import datetime

from backend.src.analytics.advanced_analytics_service import AdvancedAnalyticsService
from backend.src.database.models import League, Team, Player, RosterSlot

class TestAdvancedAnalyticsService(unittest.TestCase):
    """Test cases for the AdvancedAnalyticsService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.analytics_service = AdvancedAnalyticsService(db_session=self.mock_db_session)
        
    def test_init(self):
        """Test AdvancedAnalyticsService initialization."""
        self.assertEqual(self.analytics_service.db_session, self.mock_db_session)
        self.assertEqual(self.analytics_service.service_version, "1.0")
        
    def test_get_league_analytics_success(self):
        """Test successful league analytics retrieval."""
        # Mock league
        mock_league = Mock(spec=League)
        mock_league.id = "league123"
        
        # Mock teams
        mock_team1 = Mock(spec=Team)
        mock_team1.id = "team1"
        mock_team1.team_name = "Test Team 1"
        mock_team1.wins = 5
        mock_team1.losses = 3
        mock_team1.ties = 0
        mock_team1.rank = 1
        
        mock_team2 = Mock(spec=Team)
        mock_team2.id = "team2"
        mock_team2.team_name = "Test Team 2"
        mock_team2.wins = 4
        mock_team2.losses = 4
        mock_team2.ties = 0
        mock_team2.rank = 2
        
        # Configure mock database session
        league_query_mock = Mock()
        league_query_mock.first.return_value = mock_league
        self.mock_db_session.query.return_value.filter.return_value = league_query_mock
        
        teams_query_mock = Mock()
        teams_query_mock.all.return_value = [mock_team1, mock_team2]
        self.mock_db_session.query.return_value.filter.return_value = teams_query_mock
        
        # Configure the mock to handle different query calls properly
        query_calls = []
        
        def query_side_effect(model):
            query_mock = Mock()
            if model == League:
                query_mock.filter.return_value.first.return_value = mock_league
            elif model == Team:
                query_mock.filter.return_value.all.return_value = [mock_team1, mock_team2]
            else:
                query_mock.filter.return_value.all.return_value = []
            query_calls.append(model)
            return query_mock
        
        self.mock_db_session.query.side_effect = query_side_effect
        
        result = self.analytics_service.get_league_analytics("league123")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["league_id"], "league123")
        self.assertEqual(len(result["team_rankings"]), 2)
        self.assertEqual(result["team_rankings"][0]["team_id"], "team1")
        self.assertEqual(result["team_rankings"][0]["rank"], 1)
        self.assertEqual(result["team_rankings"][1]["team_id"], "team2")
        self.assertEqual(result["team_rankings"][1]["rank"], 2)
        
    def test_get_league_analytics_league_not_found(self):
        """Test league analytics retrieval when league is not found."""
        # Configure mock database session to return None for league query
        league_query_mock = Mock()
        league_query_mock.first.return_value = None
        self.mock_db_session.query.return_value.filter.return_value = league_query_mock
        
        result = self.analytics_service.get_league_analytics("league123")
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "League not found")
        
    def test_get_league_analytics_no_db_session(self):
        """Test league analytics retrieval with no database session."""
        # Create service without db session
        service = AdvancedAnalyticsService()
        result = service.get_league_analytics("league123")
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "No database session provided")
        
    def test_get_team_analytics_success(self):
        """Test successful team analytics retrieval."""
        # Mock team
        mock_team = Mock(spec=Team)
        mock_team.id = "team123"
        mock_team.team_name = "Test Team"
        
        # Mock player
        mock_player = Mock(spec=Player)
        mock_player.id = "player1"
        mock_player.name = "Test Player"
        mock_player.position = "QB"
        mock_player.projected_points = 15.5
        mock_player.injury_status = 0
        
        # Mock roster slot
        mock_roster_slot = Mock(spec=RosterSlot)
        mock_roster_slot.player = mock_player
        mock_roster_slot.position = "QB"
        
        # Configure mock database session
        team_query_mock = Mock()
        team_query_mock.first.return_value = mock_team
        self.mock_db_session.query.return_value.filter.return_value = team_query_mock
        
        roster_query_mock = Mock()
        roster_query_mock.all.return_value = [mock_roster_slot]
        self.mock_db_session.query.return_value.filter.return_value = roster_query_mock
        
        # Configure the mock to handle different query calls properly
        query_call_count = 0
        
        def query_side_effect(model):
            query_mock = Mock()
            if model == Team:
                query_mock.filter.return_value.first.return_value = mock_team
            elif model == RosterSlot:
                query_mock.filter.return_value.all.return_value = [mock_roster_slot]
            else:
                query_mock.filter.return_value.all.return_value = []
            return query_mock
        
        self.mock_db_session.query.side_effect = query_side_effect
        
        result = self.analytics_service.get_team_analytics("team123")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["team_id"], "team123")
        self.assertEqual(result["team_name"], "Test Team")
        self.assertEqual(len(result["player_projections"]), 1)
        self.assertEqual(result["player_projections"][0]["player_id"], "player1")
        self.assertEqual(result["player_projections"][0]["projected_points"], 15.5)
        
    def test_get_team_analytics_team_not_found(self):
        """Test team analytics retrieval when team is not found."""
        # Configure mock database session to return None for team query
        team_query_mock = Mock()
        team_query_mock.first.return_value = None
        self.mock_db_session.query.return_value.filter.return_value = team_query_mock
        
        result = self.analytics_service.get_team_analytics("team123")
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Team not found")
        
    def test_get_team_analytics_no_db_session(self):
        """Test team analytics retrieval with no database session."""
        # Create service without db session
        service = AdvancedAnalyticsService()
        result = service.get_team_analytics("team123")
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "No database session provided")
        
    def test_calculate_team_rankings(self):
        """Test team rankings calculation."""
        # Mock teams
        mock_team1 = Mock(spec=Team)
        mock_team1.id = "team1"
        mock_team1.team_name = "Test Team 1"
        mock_team1.wins = 5
        mock_team1.losses = 3
        mock_team1.ties = 0
        mock_team1.rank = 1
        
        mock_team2 = Mock(spec=Team)
        mock_team2.id = "team2"
        mock_team2.team_name = "Test Team 2"
        mock_team2.wins = 4
        mock_team2.losses = 4
        mock_team2.ties = 0
        mock_team2.rank = 2
        
        teams = [mock_team1, mock_team2]
        
        result = self.analytics_service._calculate_team_rankings(teams)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["team_id"], "team1")
        self.assertEqual(result[0]["wins"], 5)
        self.assertEqual(result[0]["losses"], 3)
        self.assertEqual(result[0]["rank"], 1)
        self.assertAlmostEqual(result[0]["win_percentage"], 5/8)
        
    def test_analyze_roster_composition(self):
        """Test roster composition analysis."""
        # Mock roster slots
        mock_slot1 = Mock(spec=RosterSlot)
        mock_slot1.position = "QB"
        
        mock_slot2 = Mock(spec=RosterSlot)
        mock_slot2.position = "RB"
        
        mock_slot3 = Mock(spec=RosterSlot)
        mock_slot3.position = "WR"
        
        mock_slot4 = Mock(spec=RosterSlot)
        mock_slot4.position = "Bench"
        
        roster_slots = [mock_slot1, mock_slot2, mock_slot3, mock_slot4]
        
        result = self.analytics_service._analyze_roster_composition(roster_slots)
        
        self.assertEqual(result["total_players"], 4)
        self.assertEqual(result["position_distribution"]["QB"], 1)
        self.assertEqual(result["position_distribution"]["RB"], 1)
        self.assertEqual(result["position_distribution"]["WR"], 1)
        self.assertEqual(result["position_distribution"]["Bench"], 1)
        
    def test_get_player_projections(self):
        """Test player projections retrieval."""
        # Mock players
        mock_player1 = Mock(spec=Player)
        mock_player1.id = "player1"
        mock_player1.name = "Player One"
        mock_player1.position = "QB"
        mock_player1.projected_points = 18.5
        mock_player1.injury_status = 0
        
        mock_player2 = Mock(spec=Player)
        mock_player2.id = "player2"
        mock_player2.name = "Player Two"
        mock_player2.position = "RB"
        mock_player2.projected_points = 12.3
        mock_player2.injury_status = 1  # Questionable
        
        # Mock roster slots
        mock_slot1 = Mock(spec=RosterSlot)
        mock_slot1.player = mock_player1
        
        mock_slot2 = Mock(spec=RosterSlot)
        mock_slot2.player = mock_player2
        
        roster_slots = [mock_slot1, mock_slot2]
        
        result = self.analytics_service._get_player_projections(roster_slots)
        
        self.assertEqual(len(result), 2)
        # Should be sorted by projected points (descending)
        self.assertEqual(result[0]["player_id"], "player1")
        self.assertEqual(result[0]["projected_points"], 18.5)
        self.assertEqual(result[1]["player_id"], "player2")
        self.assertEqual(result[1]["projected_points"], 12.3)

if __name__ == '__main__':
    unittest.main()
