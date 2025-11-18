import unittest
from unittest.mock import Mock, patch
import logging

from backend.src.league.dynasty_service import DynastyLeagueService
from backend.src.database.models import League, Team, Player, RosterSlot, User

class TestDynastyLeagueService(unittest.TestCase):
    """Test cases for the DynastyLeagueService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.dynasty_service = DynastyLeagueService(db_session=self.mock_db_session)
        
    def test_init(self):
        """Test DynastyLeagueService initialization."""
        self.assertEqual(self.dynasty_service.db_session, self.mock_db_session)
        self.assertEqual(self.dynasty_service.service_version, "1.0")
        
    def test_get_rookie_rankings_empty_session(self):
        """Test get_rookie_rankings with empty database session."""
        # Create service without db session
        service = DynastyLeagueService()
        result = service.get_rookie_rankings("league123")
        
        self.assertEqual(result, [])
        
    def test_get_long_term_projections_empty_session(self):
        """Test get_long_term_projections with empty database session."""
        # Create service without db session
        service = DynastyLeagueService()
        result = service.get_long_term_projections("league123")
        
        self.assertEqual(result, [])
        
    def test_get_player_value_assessments_empty_session(self):
        """Test get_player_value_assessments with empty database session."""
        # Create service without db session
        service = DynastyLeagueService()
        result = service.get_player_value_assessments("league123")
        
        self.assertEqual(result, [])
        
    def test_get_rookie_rankings_success(self):
        """Test successful rookie rankings retrieval."""
        # Mock players
        mock_player1 = Mock(spec=Player)
        mock_player1.id = "player1"
        mock_player1.name = "Rookie Player One"
        mock_player1.position = "QB"
        mock_player1.team = "BUF"
        mock_player1.projected_points = 15.0
        
        mock_player2 = Mock(spec=Player)
        mock_player2.id = "player2"
        mock_player2.name = "Veteran Player Two"
        mock_player2.position = "RB"
        mock_player2.team = "KC"
        mock_player2.projected_points = 22.5
        
        mock_player3 = Mock(spec=Player)
        mock_player3.id = "player3"
        mock_player3.name = "Rookie Player Three"
        mock_player3.position = "WR"
        mock_player3.team = "SF"
        mock_player3.projected_points = 12.0
        
        # Configure mock database session
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = [
            mock_player1, mock_player2, mock_player3
        ]
        
        # Mock the private methods
        with patch.object(self.dynasty_service, '_is_rookie_player', side_effect=[True, False, True]), \
             patch.object(self.dynasty_service, '_calculate_dynasty_value', side_effect=[18.0, 14.4]):
            
            result = self.dynasty_service.get_rookie_rankings("league123")
            
            # Should have 2 rookies
            self.assertEqual(len(result), 2)
            
            # Should be sorted by dynasty value (highest first)
            self.assertEqual(result[0]["player_id"], "player1")
            self.assertEqual(result[0]["dynasty_value"], 18.0)
            self.assertEqual(result[1]["player_id"], "player3")
            self.assertEqual(result[1]["dynasty_value"], 14.4)
            
    def test_get_long_term_projections_success(self):
        """Test successful long-term projections retrieval."""
        # Mock players
        mock_player1 = Mock(spec=Player)
        mock_player1.id = "player1"
        mock_player1.name = "Player One"
        mock_player1.position = "QB"
        mock_player1.team = "BUF"
        mock_player1.projected_points = 15.0
        
        mock_player2 = Mock(spec=Player)
        mock_player2.id = "player2"
        mock_player2.name = "Player Two"
        mock_player2.position = "RB"
        mock_player2.team = "KC"
        mock_player2.projected_points = 22.5
        
        mock_player3 = Mock(spec=Player)
        mock_player3.id = "player3"
        mock_player3.name = "Player Three"
        mock_player3.position = "WR"
        mock_player3.team = "SF"
        mock_player3.projected_points = 12.0
        
        # Configure mock database session
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = [
            mock_player1, mock_player2, mock_player3
        ]
        
        # Mock the private methods
        with patch.object(self.dynasty_service, '_calculate_long_term_projection', side_effect=[16.5, 24.8, 13.2]), \
             patch.object(self.dynasty_service, '_get_player_trend', side_effect=[0.1, 0.2, 0.1]):
            
            result = self.dynasty_service.get_long_term_projections("league123")
            
            # Should have all 3 players
            self.assertEqual(len(result), 3)
            
            # Should be sorted by long-term projection (highest first)
            self.assertEqual(result[0]["player_id"], "player2")
            self.assertEqual(result[0]["long_term_projection"], 24.8)
            self.assertEqual(result[1]["player_id"], "player1")
            self.assertEqual(result[1]["long_term_projection"], 16.5)
            self.assertEqual(result[2]["player_id"], "player3")
            self.assertEqual(result[2]["long_term_projection"], 13.2)
            
    def test_get_player_value_assessments_success(self):
        """Test successful player value assessments retrieval."""
        # Mock players
        mock_player1 = Mock(spec=Player)
        mock_player1.id = "player1"
        mock_player1.name = "Player One"
        mock_player1.position = "QB"
        mock_player1.team = "BUF"
        mock_player1.projected_points = 15.0
        
        mock_player2 = Mock(spec=Player)
        mock_player2.id = "player2"
        mock_player2.name = "Player Two"
        mock_player2.position = "RB"
        mock_player2.team = "KC"
        mock_player2.projected_points = 22.5
        
        mock_player3 = Mock(spec=Player)
        mock_player3.id = "player3"
        mock_player3.name = "Player Three"
        mock_player3.position = "WR"
        mock_player3.team = "SF"
        mock_player3.projected_points = 12.0
        
        # Configure mock database session
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = [
            mock_player1, mock_player2, mock_player3
        ]
        
        # Mock the private methods
        with patch.object(self.dynasty_service, '_calculate_dynasty_value', side_effect=[19.5, 24.8, 14.4]), \
             patch.object(self.dynasty_service, '_get_player_age', side_effect=[24, 26, 25]), \
             patch.object(self.dynasty_service, '_get_contract_years', side_effect=[3, 2, 4]):
            
            result = self.dynasty_service.get_player_value_assessments("league123")
            
            # Should have all 3 players
            self.assertEqual(len(result), 3)
            
            # Should be sorted by dynasty value (highest first)
            self.assertEqual(result[0]["player_id"], "player2")
            self.assertEqual(result[0]["dynasty_value"], 24.8)
            self.assertEqual(result[0]["short_term_value"], 22.5)
            self.assertEqual(result[1]["player_id"], "player1")
            self.assertEqual(result[1]["dynasty_value"], 19.5)
            self.assertEqual(result[1]["short_term_value"], 15.0)
            self.assertEqual(result[2]["player_id"], "player3")
            self.assertEqual(result[2]["dynasty_value"], 14.4)
            self.assertEqual(result[2]["short_term_value"], 12.0)
            
    def test_is_rookie_player(self):
        """Test rookie player identification."""
        mock_player1 = Mock(spec=Player)
        mock_player1.name = "Rookie Player"
        mock_player1.projected_points = 3.0
        
        mock_player2 = Mock(spec=Player)
        mock_player2.name = "Veteran Player"
        mock_player2.projected_points = 18.0
        
        # Player with "Rookie" in name should be identified as rookie
        self.assertTrue(self.dynasty_service._is_rookie_player(mock_player1))
        
        # Player with high projected points should not be identified as rookie
        self.assertFalse(self.dynasty_service._is_rookie_player(mock_player2))
        
    def test_calculate_dynasty_value(self):
        """Test dynasty value calculation."""
        mock_player = Mock(spec=Player)
        mock_player.projected_points = 15.0
        mock_player.position = "QB"
        
        # Mock the private methods
        with patch.object(self.dynasty_service, '_get_player_age', return_value=24), \
             patch.object(self.dynasty_service, '_get_contract_years', return_value=3):
            
            value = self.dynasty_service._calculate_dynasty_value(mock_player)
            
            # Expected calculation: 15.0 (base) * 1.2 (age factor) * 1.3 (QB position factor) * 1.3 (contract factor)
            expected_value = 15.0 * 1.2 * 1.3 * 1.3
            self.assertEqual(value, expected_value)
            
    def test_calculate_long_term_projection(self):
        """Test long-term projection calculation."""
        mock_player = Mock(spec=Player)
        mock_player.projected_points = 15.0
        
        # Mock the private methods
        with patch.object(self.dynasty_service, '_get_player_trend', return_value=0.2):
            projection = self.dynasty_service._calculate_long_term_projection(mock_player, 16)
            
            # Expected calculation: 15.0 (base) * 1.02 (trend factor)
            expected_projection = 15.0 * 1.02
            self.assertEqual(projection, expected_projection)
            
    def test_get_player_age(self):
        """Test player age retrieval."""
        mock_player = Mock(spec=Player)
        age = self.dynasty_service._get_player_age(mock_player)
        self.assertEqual(age, 25)  # Placeholder value
        
    def test_get_contract_years(self):
        """Test contract years retrieval."""
        mock_player = Mock(spec=Player)
        years = self.dynasty_service._get_contract_years(mock_player)
        self.assertEqual(years, 3)  # Placeholder value
        
    def test_get_player_trend(self):
        """Test player trend retrieval."""
        mock_player = Mock(spec=Player)
        trend = self.dynasty_service._get_player_trend(mock_player)
        self.assertEqual(trend, 0.0)  # Placeholder value

if __name__ == '__main__':
    unittest.main()
