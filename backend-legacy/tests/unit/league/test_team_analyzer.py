import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from league.team_analyzer import TeamAnalyzer

class TestTeamAnalyzer(unittest.TestCase):
    """Unit tests for team analyzer service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.team_analyzer = TeamAnalyzer()
        
    def test_calculate_roster_strength(self):
        """Test roster strength calculation."""
        roster_data = [
            {'position': 'QB', 'projected_points': 18.5},
            {'position': 'RB', 'projected_points': 15.2},
            {'position': 'RB', 'projected_points': 12.8},
            {'position': 'WR', 'projected_points': 14.1},
            {'position': 'WR', 'projected_points': 11.9},
            {'position': 'TE', 'projected_points': 8.7}
        ]
        
        strength = self.team_analyzer._calculate_roster_strength(roster_data)
        
        # Should return a numeric strength score
        self.assertIsInstance(strength, (int, float))
        self.assertGreater(strength, 0)
        
    def test_calculate_positional_strength(self):
        """Test positional strength calculation."""
        roster_data = [
            {'position': 'QB', 'projected_points': 18.5},
            {'position': 'RB', 'projected_points': 15.2},
            {'position': 'RB', 'projected_points': 12.8},
            {'position': 'WR', 'projected_points': 14.1},
            {'position': 'WR', 'projected_points': 11.9},
            {'position': 'TE', 'projected_points': 8.7}
        ]
        
        positional_strength = self.team_analyzer._calculate_positional_strength(roster_data)
        
        # Should return a dictionary with positional strengths
        self.assertIsInstance(positional_strength, dict)
        self.assertIn('QB', positional_strength)
        self.assertIn('RB', positional_strength)
        self.assertIn('WR', positional_strength)
        self.assertIn('TE', positional_strength)
        
    def test_calculate_positional_depth(self):
        """Test positional depth calculation."""
        roster_data = [
            {'position': 'QB', 'projected_points': 18.5},
            {'position': 'QB', 'projected_points': 12.3},
            {'position': 'RB', 'projected_points': 15.2},
            {'position': 'RB', 'projected_points': 12.8},
            {'position': 'RB', 'projected_points': 10.5},
            {'position': 'WR', 'projected_points': 14.1},
            {'position': 'WR', 'projected_points': 11.9},
            {'position': 'WR', 'projected_points': 9.8},
            {'position': 'TE', 'projected_points': 8.7},
            {'position': 'TE', 'projected_points': 6.2}
        ]
        
        positional_depth = self.team_analyzer._calculate_positional_depth(roster_data)
        
        # Should return a dictionary with positional depths
        self.assertIsInstance(positional_depth, dict)
        self.assertIn('QB', positional_depth)
        self.assertIn('RB', positional_depth)
        self.assertIn('WR', positional_depth)
        self.assertIn('TE', positional_depth)
        
    def test_assess_injury_risk(self):
        """Test injury risk assessment."""
        roster_data = [
            {'player_id': 'player1', 'name': 'Player One', 'position': 'QB', 'injury_status': 0},
            {'player_id': 'player2', 'name': 'Player Two', 'position': 'RB', 'injury_status': 2},
            {'player_id': 'player3', 'name': 'Player Three', 'position': 'WR', 'injury_status': 3}
        ]
        
        injury_risk = self.team_analyzer._assess_injury_risk(roster_data)
        
        # Should return a risk score and detailed breakdown
        self.assertIsInstance(injury_risk, dict)
        self.assertIn('overall_risk_score', injury_risk)
        self.assertIn('high_risk_players', injury_risk)
        self.assertIn('injury_counts', injury_risk)
        
    def test_evaluate_bench_quality(self):
        """Test bench quality evaluation."""
        roster_data = [
            {'slot_type': 'STARTER', 'position': 'QB', 'projected_points': 18.5},
            {'slot_type': 'STARTER', 'position': 'RB', 'projected_points': 15.2},
            {'slot_type': 'BENCH', 'position': 'RB', 'projected_points': 12.8},
            {'slot_type': 'BENCH', 'position': 'WR', 'projected_points': 11.9},
            {'slot_type': 'BENCH', 'position': 'TE', 'projected_points': 8.7}
        ]
        
        bench_quality = self.team_analyzer._evaluate_bench_quality(roster_data)
        
        # Should return a quality score and detailed breakdown
        self.assertIsInstance(bench_quality, dict)
        self.assertIn('overall_bench_score', bench_quality)
        self.assertIn('bench_depth', bench_quality)
        
    def test_project_starter_performance(self):
        """Test starter performance projection."""
        roster_data = [
            {'slot_type': 'STARTER', 'position': 'QB', 'projected_points': 18.5},
            {'slot_type': 'STARTER', 'position': 'RB', 'projected_points': 15.2},
            {'slot_type': 'STARTER', 'position': 'RB', 'projected_points': 12.8},
            {'slot_type': 'STARTER', 'position': 'WR', 'projected_points': 14.1},
            {'slot_type': 'STARTER', 'position': 'WR', 'projected_points': 11.9},
            {'slot_type': 'STARTER', 'position': 'TE', 'projected_points': 8.7}
        ]
        
        performance_projection = self.team_analyzer._project_starter_performance(roster_data)
        
        # Should return a projection score
        self.assertIsInstance(performance_projection, (int, float))
        self.assertGreater(performance_projection, 0)
        
    def test_generate_recommendations(self):
        """Test AI recommendation generation."""
        analysis_data = {
            'overall_strength': 85.2,
            'positional_strength': {'QB': 90, 'RB': 80, 'WR': 75, 'TE': 60},
            'positional_depth': {'QB': 2, 'RB': 4, 'WR': 5, 'TE': 3},
            'injury_risk': {'overall_risk_score': 35},
            'bench_quality': {'overall_bench_score': 70}
        }
        
        recommendations = self.team_analyzer._generate_recommendations(analysis_data)
        
        # Should return a list of recommendations
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

if __name__ == '__main__':
    unittest.main()
