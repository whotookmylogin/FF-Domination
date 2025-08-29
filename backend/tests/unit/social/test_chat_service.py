import unittest
from unittest.mock import Mock, patch
import logging
import json
from datetime import datetime

from backend.src.social.chat_service import LeagueChatService
from backend.src.database.models import League, Team, User

class TestLeagueChatService(unittest.TestCase):
    """Test cases for the LeagueChatService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.chat_service = LeagueChatService(db_session=self.mock_db_session)
        
    def test_init(self):
        """Test LeagueChatService initialization."""
        self.assertEqual(self.chat_service.db_session, self.mock_db_session)
        self.assertEqual(self.chat_service.service_version, "1.0")
        
    def test_send_message_success(self):
        """Test successful message sending."""
        # Mock league
        mock_league = Mock(spec=League)
        
        # Configure mock database session
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_league
        
        message_content = "Hello league!"
        
        with patch('backend.src.social.chat_service.uuid.uuid4', return_value="test-message-id"), \
             patch('backend.src.social.chat_service.datetime') as mock_datetime:
            
            mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
            
            result = self.chat_service.send_message("league123", "user456", message_content)
            
            self.assertEqual(result["status"], "sent")
            self.assertEqual(result["id"], "test-message-id")
            self.assertEqual(result["league_id"], "league123")
            self.assertEqual(result["user_id"], "user456")
            self.assertEqual(result["content"], message_content)
            
    def test_send_message_league_not_found(self):
        """Test message sending when league is not found."""
        # Configure mock database session to return None
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.chat_service.send_message("league123", "user456", "Hello league!")
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "League not found")
        
    def test_send_message_no_db_session(self):
        """Test message sending with no database session."""
        # Create service without db session
        service = LeagueChatService()
        result = service.send_message("league123", "user456", "Hello league!")
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "No database session provided")
        
    def test_get_league_messages_success(self):
        """Test successful retrieval of league messages."""
        # Mock league
        mock_league = Mock(spec=League)
        
        # Configure mock database session
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_league
        
        result = self.chat_service.get_league_messages("league123")
        
        # Should return empty list (placeholder implementation)
        self.assertEqual(result, [])
        
    def test_get_league_messages_league_not_found(self):
        """Test message retrieval when league is not found."""
        # Configure mock database session to return None
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.chat_service.get_league_messages("league123")
        
        # Should return empty list
        self.assertEqual(result, [])
        
    def test_get_league_messages_no_db_session(self):
        """Test message retrieval with no database session."""
        # Create service without db session
        service = LeagueChatService()
        result = service.get_league_messages("league123")
        
        # Should return empty list
        self.assertEqual(result, [])
        
    def test_get_user_league_chats_success(self):
        """Test successful retrieval of user league chats."""
        # Mock leagues
        mock_league1 = Mock(spec=League)
        mock_league1.id = "league1"
        mock_league1.league_name = "Test League 1"
        mock_league1.platform = "ESPN"
        
        mock_league2 = Mock(spec=League)
        mock_league2.id = "league2"
        mock_league2.league_name = "Test League 2"
        mock_league2.platform = "Sleeper"
        
        mock_team1 = Mock(spec=Team)
        mock_team1.id = "team1"
        mock_team1.team_name = "Test Team 1"
        
        mock_team2 = Mock(spec=Team)
        mock_team2.id = "team2"
        mock_team2.team_name = "Test Team 2"
        
        # Configure mock database session
        # Mock the query chain for leagues
        leagues_query_mock = Mock()
        leagues_query_mock.all.return_value = [mock_league1, mock_league2]
        leagues_query_mock.filter.return_value = leagues_query_mock
        
        # Mock the query chain for teams
        teams_query_mock = Mock()
        teams_query_mock.filter.return_value = teams_query_mock
        teams_query_mock.all.side_effect = [
            [mock_team1],  # Teams for league1
            [mock_team1, mock_team2]  # Teams for league2
        ]
        
        # Configure the mock to handle different query calls properly
        def query_side_effect(model):
            if model == League:
                return leagues_query_mock
            elif model == Team:
                return teams_query_mock
            else:
                return Mock()
        
        self.mock_db_session.query.side_effect = query_side_effect
        
        result = self.chat_service.get_user_league_chats("user456")
        
        self.assertEqual(len(result), 2)
        
        # Check first league chat
        self.assertEqual(result[0]["league_id"], "league1")
        self.assertEqual(result[0]["league_name"], "Test League 1")
        self.assertEqual(result[0]["platform"], "ESPN")
        self.assertEqual(len(result[0]["participants"]), 1)
        self.assertEqual(result[0]["participants"][0]["id"], "team1")
        self.assertEqual(result[0]["participants"][0]["name"], "Test Team 1")
        
        # Check second league chat
        self.assertEqual(result[1]["league_id"], "league2")
        self.assertEqual(result[1]["league_name"], "Test League 2")
        self.assertEqual(result[1]["platform"], "Sleeper")
        self.assertEqual(len(result[1]["participants"]), 2)
        
    def test_get_user_league_chats_no_db_session(self):
        """Test league chat retrieval with no database session."""
        # Create service without db session
        service = LeagueChatService()
        result = service.get_user_league_chats("user456")
        
        # Should return empty list
        self.assertEqual(result, [])
        
    def test_get_user_league_chats_db_error(self):
        """Test league chat retrieval with database error."""
        # Configure mock database session to raise exception
        self.mock_db_session.query.return_value.filter.return_value.all.side_effect = Exception("Database error")
        
        result = self.chat_service.get_user_league_chats("user456")
        
        # Should return empty list
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
