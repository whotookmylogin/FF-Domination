import logging
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class ESPNTeamAnalyzer:
    """
    Team analyzer that works directly with ESPN API data.
    Provides comprehensive team analysis without requiring database persistence.
    """
    
    def __init__(self, espn_service=None):
        """
        Initialize the ESPN Team Analyzer.
        
        Args:
            espn_service: ESPN API service instance
        """
        self.espn_service = espn_service
        
    def analyze_team(self, league_id: str, team_id: str, cookies: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a team using ESPN data.
        
        Args:
            league_id: ESPN league ID
            team_id: ESPN team ID
            cookies: ESPN authentication cookies
            
        Returns:
            Comprehensive team analysis
        """
        try:
            # Get team roster from ESPN
            roster_data = self._get_team_roster(league_id, team_id, cookies)
            if not roster_data:
                return {
                    "status": "error",
                    "message": "Could not fetch team roster"
                }
            
            # Transform ESPN data to our analysis format
            team_data = self._transform_espn_data(roster_data)
            
            # Perform analysis
            analysis = {
                "team_id": team_id,
                "team_name": roster_data.get("team_name", f"Team {team_id}"),
                "overallStrength": self._calculate_overall_strength(team_data),
                "positionalStrengths": self._analyze_positional_strengths(team_data),
                "positionalDepth": self._analyze_positional_depth(team_data),
                "injuryRisk": self._assess_injury_risk(team_data),
                "benchQuality": self._evaluate_bench_quality(team_data),
                "startersPerformance": self._calculate_starters_performance(team_data),
                "recommendations": [],
                "status": "success"
            }
            
            # Generate recommendations based on analysis
            analysis["recommendations"] = self._generate_recommendations(analysis, team_data)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing team {team_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _get_team_roster(self, league_id: str, team_id: str, cookies: Optional[Dict] = None) -> Optional[Dict]:
        """
        Get team roster from ESPN API.
        """
        if not self.espn_service:
            # Return mock data for testing
            return self._get_mock_roster(team_id)
        
        try:
            # Get roster from ESPN service using get_roster_data
            roster_data = self.espn_service.get_roster_data(str(team_id))
            
            if not roster_data:
                logger.warning(f"No roster data returned for team {team_id}, using mock data")
                return self._get_mock_roster(team_id)
            
            # Also try to get the league to get team name and more player details
            team_name = f"Team {team_id}"
            try:
                if hasattr(self.espn_service, 'league') and self.espn_service.league:
                    for team in self.espn_service.league.teams:
                        if str(team.team_id) == str(team_id):
                            team_name = team.team_name
                            # Get more detailed player info from team.roster
                            enhanced_roster = []
                            for player in team.roster:
                                player_data = {
                                    "name": player.name,
                                    "position": player.position if player.position != "D/ST" else "DEF",
                                    "projected_points": getattr(player, 'projected_points', getattr(player, 'points', 0)),
                                    "injury_status": getattr(player, 'injuryStatus', "ACTIVE"),
                                    "starter": getattr(player, 'lineupSlot', "BE") not in ["BE", "IR"],
                                    "pro_team": getattr(player, 'proTeam', "")
                                }
                                enhanced_roster.append(player_data)
                            
                            if enhanced_roster:
                                return {
                                    "team_name": team_name,
                                    "players": enhanced_roster
                                }
                            break
            except Exception as e:
                logger.warning(f"Could not get enhanced roster data: {e}")
            
            # Transform basic roster data to our format
            players = []
            for player in roster_data:
                position = player.get("position", "")
                if position == "D/ST":
                    position = "DEF"
                    
                players.append({
                    "name": player.get("name", "Unknown"),
                    "position": position,
                    "projected_points": player.get("projected_points", player.get("points", 0)),
                    "injury_status": player.get("injury_status", "ACTIVE"),
                    "starter": True  # Default to starter since we don't have lineup slot info
                })
            
            return {
                "team_name": team_name,
                "players": players
            }
        except Exception as e:
            logger.error(f"Error fetching ESPN roster: {e}")
            return self._get_mock_roster(team_id)
    
    def _get_mock_roster(self, team_id: str) -> Dict:
        """
        Get mock roster data for testing.
        """
        return {
            "team_name": f"Team {team_id}",
            "players": [
                {"name": "Josh Allen", "position": "QB", "projected_points": 22.5, "injury_status": "ACTIVE", "starter": True},
                {"name": "Saquon Barkley", "position": "RB", "projected_points": 18.2, "injury_status": "ACTIVE", "starter": True},
                {"name": "Derrick Henry", "position": "RB", "projected_points": 16.8, "injury_status": "ACTIVE", "starter": True},
                {"name": "CeeDee Lamb", "position": "WR", "projected_points": 17.5, "injury_status": "ACTIVE", "starter": True},
                {"name": "Tyreek Hill", "position": "WR", "projected_points": 19.2, "injury_status": "QUESTIONABLE", "starter": True},
                {"name": "Travis Kelce", "position": "TE", "projected_points": 14.3, "injury_status": "ACTIVE", "starter": True},
                {"name": "Justin Tucker", "position": "K", "projected_points": 8.5, "injury_status": "ACTIVE", "starter": True},
                {"name": "Baltimore Ravens", "position": "DEF", "projected_points": 9.2, "injury_status": "ACTIVE", "starter": True},
                {"name": "Tony Pollard", "position": "RB", "projected_points": 12.1, "injury_status": "ACTIVE", "starter": False},
                {"name": "DeAndre Hopkins", "position": "WR", "projected_points": 11.8, "injury_status": "ACTIVE", "starter": False},
                {"name": "George Kittle", "position": "TE", "projected_points": 12.5, "injury_status": "OUT", "starter": False},
                {"name": "Jared Goff", "position": "QB", "projected_points": 18.3, "injury_status": "ACTIVE", "starter": False}
            ]
        }
    
    def _transform_espn_data(self, roster_data: Dict) -> Dict:
        """
        Transform ESPN roster data to our analysis format.
        """
        players = []
        for player in roster_data.get("players", []):
            # Normalize position names
            position = player.get("position", "")
            if position == "D/ST":
                position = "DEF"
            
            # Determine if player is injured
            injury_status = player.get("injury_status", "ACTIVE")
            injury_value = 0
            if injury_status == "OUT":
                injury_value = 3
            elif injury_status == "DOUBTFUL":
                injury_value = 2
            elif injury_status == "QUESTIONABLE":
                injury_value = 1
            
            players.append({
                "name": player.get("name", "Unknown"),
                "position": position,
                "projected_score": player.get("projected_points", 0),
                "injury_status": injury_value,
                "starter": player.get("starter", False),
                "bench": not player.get("starter", False)
            })
        
        return {"players": players}
    
    def _calculate_overall_strength(self, team_data: Dict) -> float:
        """
        Calculate overall team strength score (0-100).
        """
        players = team_data.get("players", [])
        if not players:
            return 0
        
        # Calculate based on projected points of starters
        starters = [p for p in players if p.get("starter", False)]
        if not starters:
            starters = players[:8]  # Use top 8 players if no starters marked
        
        total_projected = sum(p.get("projected_score", 0) for p in starters)
        
        # Normalize to 0-100 scale (assuming 120 points is excellent)
        strength_score = min(100, (total_projected / 120) * 100)
        
        return round(strength_score, 1)
    
    def _analyze_positional_strengths(self, team_data: Dict) -> Dict[str, float]:
        """
        Analyze strength at each position (0-10 scale).
        """
        players = team_data.get("players", [])
        positions = ["QB", "RB", "WR", "TE", "K", "DEF"]
        
        # Define what's considered a strong score for each position
        position_benchmarks = {
            "QB": 20,   # 20+ points is strong for QB
            "RB": 15,   # 15+ points is strong for RB
            "WR": 14,   # 14+ points is strong for WR
            "TE": 10,   # 10+ points is strong for TE
            "K": 8,     # 8+ points is strong for K
            "DEF": 8    # 8+ points is strong for DEF
        }
        
        positional_strengths = {}
        
        for position in positions:
            position_players = [
                p for p in players 
                if p.get("position") == position
            ]
            
            if position_players:
                # Get the best player at this position
                best_score = max(p.get("projected_score", 0) for p in position_players)
                benchmark = position_benchmarks.get(position, 10)
                
                # Calculate strength on 0-10 scale
                strength = min(10, (best_score / benchmark) * 10)
                positional_strengths[position] = round(strength, 1)
            else:
                positional_strengths[position] = 0
        
        return positional_strengths
    
    def _analyze_positional_depth(self, team_data: Dict) -> Dict[str, Dict]:
        """
        Analyze depth at each position.
        """
        players = team_data.get("players", [])
        positions = ["QB", "RB", "WR", "TE", "K", "DEF"]
        
        depth_analysis = {}
        
        for position in positions:
            position_players = [
                p for p in players 
                if p.get("position") == position
            ]
            
            # Sort by projected score
            position_players.sort(key=lambda x: x.get("projected_score", 0), reverse=True)
            
            # Determine depth quality
            count = len(position_players)
            quality = self._assess_depth_quality(position, count, position_players)
            
            depth_analysis[position] = {
                "count": count,
                "quality": quality
            }
        
        return depth_analysis
    
    def _assess_depth_quality(self, position: str, count: int, players: List[Dict]) -> str:
        """
        Assess the quality of depth at a position.
        """
        # Define ideal counts for each position
        ideal_counts = {
            "QB": 2,
            "RB": 4,
            "WR": 5,
            "TE": 2,
            "K": 1,
            "DEF": 1
        }
        
        ideal = ideal_counts.get(position, 2)
        
        if count == 0:
            return "CRITICAL"
        elif count < ideal - 1:
            return "POOR"
        elif count < ideal:
            return "FAIR"
        elif count == ideal:
            return "GOOD"
        else:
            return "EXCELLENT"
    
    def _assess_injury_risk(self, team_data: Dict) -> float:
        """
        Assess overall injury risk (0-10 scale).
        """
        players = team_data.get("players", [])
        if not players:
            return 0
        
        # Count injured players and their severity
        injury_score = 0
        key_position_multiplier = 1.5
        
        for player in players:
            injury_status = player.get("injury_status", 0)
            if injury_status > 0:
                score = injury_status
                
                # Increase risk for key positions
                if player.get("position") in ["QB", "RB", "WR"] and player.get("starter", False):
                    score *= key_position_multiplier
                
                injury_score += score
        
        # Normalize to 0-10 scale
        risk = min(10, injury_score / 2)
        
        return round(risk, 1)
    
    def _evaluate_bench_quality(self, team_data: Dict) -> float:
        """
        Evaluate bench quality (0-100 scale).
        """
        players = team_data.get("players", [])
        bench_players = [p for p in players if p.get("bench", False)]
        
        if not bench_players:
            return 50  # Neutral if no bench identified
        
        # Calculate average projected score of bench
        avg_bench_score = np.mean([p.get("projected_score", 0) for p in bench_players])
        
        # Normalize to 0-100 (assuming 10 points average is good bench quality)
        bench_quality = min(100, (avg_bench_score / 10) * 100)
        
        return round(bench_quality, 1)
    
    def _calculate_starters_performance(self, team_data: Dict) -> float:
        """
        Calculate projected performance of starting lineup.
        """
        players = team_data.get("players", [])
        starters = [p for p in players if p.get("starter", False)]
        
        if not starters:
            # Use top 8 players if no starters marked
            players_sorted = sorted(players, key=lambda x: x.get("projected_score", 0), reverse=True)
            starters = players_sorted[:8]
        
        total_projected = sum(p.get("projected_score", 0) for p in starters)
        
        return round(total_projected, 1)
    
    def _generate_recommendations(self, analysis: Dict, team_data: Dict) -> List[str]:
        """
        Generate actionable recommendations based on analysis.
        """
        recommendations = []
        
        # Overall strength recommendations
        overall = analysis.get("overallStrength", 0)
        if overall < 50:
            recommendations.append("⚠️ Your team strength is below average - consider making trades to upgrade key positions")
        elif overall < 70:
            recommendations.append("📈 Your team is solid but has room for improvement - target high-upside waiver pickups")
        else:
            recommendations.append("💪 Your team is strong - maintain your roster and watch for injury updates")
        
        # Position-specific recommendations
        strengths = analysis.get("positionalStrengths", {})
        depth = analysis.get("positionalDepth", {})
        
        for position, strength in strengths.items():
            if strength < 5:
                recommendations.append(f"🔴 Weak at {position} - prioritize acquiring a starter via trade or waivers")
            
            pos_depth = depth.get(position, {})
            if pos_depth.get("quality") in ["CRITICAL", "POOR"]:
                recommendations.append(f"📊 Poor depth at {position} - add backup players for bye weeks and injuries")
        
        # Injury risk recommendations
        injury_risk = analysis.get("injuryRisk", 0)
        if injury_risk > 7:
            recommendations.append("🏥 High injury risk detected - handcuff your injured RBs and monitor status closely")
        elif injury_risk > 4:
            recommendations.append("⚕️ Moderate injury concerns - have backup plans ready for game-time decisions")
        
        # Bench quality recommendations
        bench = analysis.get("benchQuality", 0)
        if bench < 40:
            recommendations.append("📉 Weak bench detected - drop underperformers for high-upside lottery tickets")
        
        # Limit to top 5 most important recommendations
        return recommendations[:5]