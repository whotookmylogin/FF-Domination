"""
Weekly Matchup Analyzer for Fantasy Football
Provides comprehensive analysis comparing user roster vs opponent
"""

import os
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
import re

logger = logging.getLogger(__name__)

@dataclass
class PlayerMatchup:
    player_name: str
    position: str
    team: str
    opponent: str
    projected_points: float
    weather_impact: str
    defense_rating: float
    qb_analysis: Optional[str]
    advantage_factors: List[str]
    disadvantage_factors: List[str]
    overall_rating: float

@dataclass
class TeamMatchupAnalysis:
    team_id: str
    team_name: str
    projected_total: float
    roster: List[PlayerMatchup]
    strengths: List[str]
    weaknesses: List[str]
    key_advantages: List[str]

class WeeklyMatchupAnalyzer:
    """Analyzes weekly matchups with weather, defense, and performance factors"""
    
    def __init__(self, platform_service=None, perplexity_api_key: Optional[str] = None):
        self.platform_service = platform_service
        self.perplexity_api_key = perplexity_api_key or os.getenv("PERPLEXITY_API_KEY")
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        
        # Defense rankings cache (will be updated periodically)
        self._defense_rankings = {}
        self._last_defense_update = None
        
        # QB performance data cache
        self._qb_data = {}
        self._last_qb_update = None
        
    def analyze_weekly_matchup(self, league_id: str, team_id: str, week: Optional[int] = None, platform: str = "ESPN") -> Dict[str, Any]:
        """
        Analyze the weekly matchup for a team against their opponent
        
        Args:
            league_id: The league identifier
            team_id: The user's team ID
            week: The week number (None for current week)
            platform: The platform being used (ESPN or Sleeper)
        
        Returns:
            Comprehensive matchup analysis
        """
        try:
            # Get current week if not specified
            if week is None:
                week = self._get_current_week()
            
            logger.info(f"Analyzing matchup for team {team_id} in {platform} league {league_id} for week {week}")
            
            # Get matchup data from platform
            matchup_data = self._get_matchup_data(league_id, team_id, week, platform)
            if not matchup_data:
                return {
                    "status": "error",
                    "message": f"Could not find matchup for team {team_id} in week {week}"
                }
            
            # Get both rosters
            user_roster = matchup_data.get("user_roster", [])
            opponent_roster = matchup_data.get("opponent_roster", [])
            
            # Update defense rankings and QB data if needed
            self._update_defense_rankings()
            self._update_qb_performance_data()
            
            # Analyze each player on both teams
            user_analysis = self._analyze_roster(user_roster)
            opponent_analysis = self._analyze_roster(opponent_roster)
            
            # Get head-to-head advantages
            h2h_analysis = self._compare_rosters(user_analysis, opponent_analysis)
            
            # Get AI-powered insights if available
            ai_insights = self._get_ai_insights(user_analysis, opponent_analysis, h2h_analysis)
            
            return {
                "status": "success",
                "week": week,
                "matchup": {
                    "user_team": {
                        "team_id": team_id,
                        "team_name": matchup_data.get("user_team_name", f"Team {team_id}"),
                        "projected_total": sum(p.projected_points for p in user_analysis),
                        "roster_analysis": [self._player_to_dict(p) for p in user_analysis],
                        "strengths": self._identify_strengths(user_analysis),
                        "weaknesses": self._identify_weaknesses(user_analysis),
                        "weather_advantages": self._get_weather_advantages(user_analysis),
                    },
                    "opponent_team": {
                        "team_id": matchup_data.get("opponent_id"),
                        "team_name": matchup_data.get("opponent_name", "Opponent"),
                        "projected_total": sum(p.projected_points for p in opponent_analysis),
                        "roster_analysis": [self._player_to_dict(p) for p in opponent_analysis],
                        "strengths": self._identify_strengths(opponent_analysis),
                        "weaknesses": self._identify_weaknesses(opponent_analysis),
                        "weather_advantages": self._get_weather_advantages(opponent_analysis),
                    },
                    "head_to_head": h2h_analysis,
                    "ai_insights": ai_insights,
                    "recommendations": self._generate_recommendations(user_analysis, opponent_analysis, h2h_analysis),
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing matchup: {e}")
            return {
                "status": "error",
                "message": f"Failed to analyze matchup: {str(e)}"
            }
    
    def _get_current_week(self) -> int:
        """Get the current NFL week number"""
        # 2025 NFL season starts September 4, 2025 (first Thursday of September)
        season_start = datetime(2025, 9, 4)
        current_date = datetime.now()
        
        # If before season start, return week 1
        if current_date < season_start:
            return 1
        
        # Calculate weeks passed since season start
        days_passed = (current_date - season_start).days
        weeks_passed = days_passed // 7
        
        # NFL regular season is 18 weeks (17 games + 1 bye week)
        # Week 1 starts when days_passed = 0-6, Week 2 when days_passed = 7-13, etc.
        current_week = min(weeks_passed + 1, 18)
        
        # Since today is Sept 3, 2025, which is before Sept 4, we should be at Week 1
        return current_week
    
    def _get_matchup_data(self, league_id: str, team_id: str, week: int, platform: str = "ESPN") -> Optional[Dict[str, Any]]:
        """Get matchup data from platform API"""
        try:
            # Handle Sleeper platform
            if platform.upper() == "SLEEPER":
                return self._get_sleeper_matchup_data(league_id, team_id, week)
            
            # Try to get real data from ESPN first
            if self.platform_service and hasattr(self.platform_service, 'espn_api_integration'):
                # Get the league object
                league = self.platform_service.espn_api_integration.league
                if not league:
                    logger.warning("League data not available")
                    return self._get_mock_matchup_data(team_id, week)
                
                # Find the user's team
                user_team = None
                for team in league.teams:
                    if str(team.team_id) == str(team_id):
                        user_team = team
                        break
                
                if not user_team:
                    logger.warning(f"Team {team_id} not found in league")
                    return self._get_mock_matchup_data(team_id, week)
                
                # Get matchup for the week - with timeout protection
                try:
                    matchups = league.box_scores(week)
                except Exception as e:
                    logger.warning(f"Failed to get box scores: {e}")
                    matchups = []
                
                user_matchup = None
                opponent_team = None
                
                for matchup in matchups:
                    if hasattr(matchup, 'home_team') and matchup.home_team.team_id == user_team.team_id:
                        user_matchup = matchup
                        opponent_team = matchup.away_team
                        break
                    elif hasattr(matchup, 'away_team') and matchup.away_team.team_id == user_team.team_id:
                        user_matchup = matchup
                        opponent_team = matchup.home_team
                        break
                
                if not user_matchup or not opponent_team:
                    logger.warning(f"No matchup found for team {team_id} in week {week}")
                    return None
                
                # Extract roster data
                user_roster = []
                opponent_roster = []
                
                # Get user's lineup
                for player in user_team.roster:
                    if player.lineupSlot not in ['BE', 'IR']:  # Only active players
                        # Get weekly projections properly
                        proj_points = 0
                        
                        # Check for week-specific projections first
                        if hasattr(player, 'stats') and week in player.stats:
                            week_stats = player.stats[week]
                            if 'projected_points' in week_stats:
                                proj_points = week_stats['projected_points']
                            elif 'points' in week_stats:
                                proj_points = week_stats['points']
                        
                        # Fall back to general projections
                        if proj_points == 0:
                            if hasattr(player, 'projected_points'):
                                proj_points = player.projected_points
                            elif hasattr(player, 'projected_total_points'):
                                proj_points = player.projected_total_points
                            elif hasattr(player, 'points'):
                                proj_points = player.points
                        
                        # If projection seems to be season total (>40 for non-QB, >60 for QB), divide by 17
                        if player.position == 'QB' and proj_points > 60:
                            proj_points = round(proj_points / 17, 1)
                        elif player.position != 'QB' and proj_points > 40:
                            proj_points = round(proj_points / 17, 1)
                        
                        # If still 0, use position-based estimates
                        if proj_points == 0:
                            position_averages = {
                                'QB': 18, 'RB': 12, 'WR': 10, 'TE': 8, 
                                'K': 8, 'D/ST': 9, 'DEF': 9
                            }
                            proj_points = position_averages.get(player.position, 5)
                        
                        user_roster.append({
                            'name': player.name,
                            'position': player.position,
                            'team': player.proTeam,
                            'opponent': self._get_opponent_team(player.proTeam, week),
                            'projected_points': proj_points
                        })
                
                # Get opponent's lineup
                for player in opponent_team.roster:
                    if player.lineupSlot not in ['BE', 'IR']:  # Only active players
                        # Get weekly projections properly
                        proj_points = 0
                        
                        # Check for week-specific projections first
                        if hasattr(player, 'stats') and week in player.stats:
                            week_stats = player.stats[week]
                            if 'projected_points' in week_stats:
                                proj_points = week_stats['projected_points']
                            elif 'points' in week_stats:
                                proj_points = week_stats['points']
                        
                        # Fall back to general projections
                        if proj_points == 0:
                            if hasattr(player, 'projected_points'):
                                proj_points = player.projected_points
                            elif hasattr(player, 'projected_total_points'):
                                proj_points = player.projected_total_points
                            elif hasattr(player, 'points'):
                                proj_points = player.points
                        
                        # If projection seems to be season total (>40 for non-QB, >60 for QB), divide by 17
                        if player.position == 'QB' and proj_points > 60:
                            proj_points = round(proj_points / 17, 1)
                        elif player.position != 'QB' and proj_points > 40:
                            proj_points = round(proj_points / 17, 1)
                        
                        # If still 0, use position-based estimates
                        if proj_points == 0:
                            position_averages = {
                                'QB': 18, 'RB': 12, 'WR': 10, 'TE': 8,
                                'K': 8, 'D/ST': 9, 'DEF': 9
                            }
                            proj_points = position_averages.get(player.position, 5)
                        
                        opponent_roster.append({
                            'name': player.name,
                            'position': player.position,
                            'team': player.proTeam,
                            'opponent': self._get_opponent_team(player.proTeam, week),
                            'projected_points': proj_points
                        })
                
                return {
                    'user_team_name': user_team.team_name,
                    'user_roster': user_roster,
                    'opponent_id': str(opponent_team.team_id),
                    'opponent_name': opponent_team.team_name,
                    'opponent_roster': opponent_roster
                }
            else:
                # Fall back to mock data if ESPN is not available
                logger.info("ESPN API not available, using mock data")
                return self._get_mock_matchup_data(team_id, week)
            
        except Exception as e:
            logger.error(f"Error getting matchup data: {e}")
            return None
    
    def _get_sleeper_matchup_data(self, league_id: str, team_id: str, week: int) -> Optional[Dict[str, Any]]:
        """Get matchup data from Sleeper API"""
        try:
            if not self.platform_service or not hasattr(self.platform_service, 'sleeper_api_integration'):
                logger.warning("Sleeper API integration not available")
                return self._get_mock_matchup_data(team_id, week)
            
            sleeper = self.platform_service.sleeper_api_integration
            
            # Get league data
            league_data = sleeper.get_league_info()
            if not league_data:
                logger.warning("Could not fetch Sleeper league data")
                return self._get_mock_matchup_data(team_id, week)
            
            # Get rosters
            rosters = sleeper.get_rosters()
            if not rosters:
                logger.warning("Could not fetch Sleeper rosters")
                return self._get_mock_matchup_data(team_id, week)
            
            # Get matchups for the week
            matchups = sleeper.get_matchups(week)
            if not matchups:
                logger.warning(f"Could not fetch Sleeper matchups for week {week}")
                return self._get_mock_matchup_data(team_id, week)
            
            # Get users to map team names
            users = sleeper.get_users()
            user_map = {u['user_id']: u.get('display_name', u.get('username', 'Unknown')) for u in users} if users else {}
            
            # Map rosters to users
            roster_map = {}
            for roster in rosters:
                roster_id = str(roster['roster_id'])
                owner_id = roster.get('owner_id')
                roster_map[roster_id] = {
                    'owner_id': owner_id,
                    'team_name': user_map.get(owner_id, f"Team {roster_id}"),
                    'players': roster.get('players', []),
                    'starters': roster.get('starters', [])
                }
            
            # Find user's matchup
            user_matchup = None
            opponent_matchup = None
            user_matchup_id = None
            
            for matchup in matchups:
                if str(matchup['roster_id']) == str(team_id):
                    user_matchup = matchup
                    user_matchup_id = matchup.get('matchup_id')
                    break
            
            if not user_matchup:
                logger.warning(f"Could not find matchup for team {team_id}")
                return self._get_mock_matchup_data(team_id, week)
            
            # Find opponent matchup
            for matchup in matchups:
                if matchup.get('matchup_id') == user_matchup_id and str(matchup['roster_id']) != str(team_id):
                    opponent_matchup = matchup
                    break
            
            if not opponent_matchup:
                logger.warning("Could not find opponent matchup")
                return self._get_mock_matchup_data(team_id, week)
            
            # Get player data
            players = sleeper.get_nfl_players()
            
            # Build roster data for both teams
            def build_roster(matchup, roster_info):
                roster_players = []
                starters = roster_info.get('starters', [])
                
                for player_id in starters:
                    if player_id and str(player_id) in players:
                        player = players[str(player_id)]
                        points = matchup.get('players_points', {}).get(str(player_id), 0)
                        
                        roster_players.append({
                            'name': player.get('full_name', 'Unknown'),
                            'position': player.get('position', 'FLEX'),
                            'team': player.get('team', 'FA'),
                            'opponent': '',  # Would need schedule data
                            'projected_points': points if points > 0 else self._estimate_projection(player)
                        })
                
                return roster_players
            
            user_roster_info = roster_map.get(str(team_id), {})
            opponent_roster_info = roster_map.get(str(opponent_matchup['roster_id']), {})
            
            return {
                'user_team_name': user_roster_info.get('team_name', f'Team {team_id}'),
                'user_roster': build_roster(user_matchup, user_roster_info),
                'opponent_id': str(opponent_matchup['roster_id']),
                'opponent_name': opponent_roster_info.get('team_name', 'Opponent'),
                'opponent_roster': build_roster(opponent_matchup, opponent_roster_info)
            }
            
        except Exception as e:
            logger.error(f"Error getting Sleeper matchup data: {e}")
            return self._get_mock_matchup_data(team_id, week)
    
    def _estimate_projection(self, player: Dict[str, Any]) -> float:
        """Estimate projection for a Sleeper player"""
        position = player.get('position', 'FLEX')
        # Basic projection by position
        projections = {
            'QB': 18.0, 'RB': 12.0, 'WR': 11.0, 'TE': 8.0,
            'K': 7.0, 'DEF': 8.0, 'D/ST': 8.0
        }
        return projections.get(position, 5.0)
    
    def _get_mock_matchup_data(self, team_id: str, week: int) -> Dict[str, Any]:
        """Generate mock matchup data for testing"""
        return {
            'user_team_name': f'Team {team_id}',
            'user_roster': [
                {'name': 'Patrick Mahomes', 'position': 'QB', 'team': 'KC', 'opponent': 'BUF', 'projected_points': 24.5},
                {'name': 'Christian McCaffrey', 'position': 'RB', 'team': 'SF', 'opponent': 'DAL', 'projected_points': 18.2},
                {'name': 'Saquon Barkley', 'position': 'RB', 'team': 'PHI', 'opponent': 'WAS', 'projected_points': 15.8},
                {'name': 'Tyreek Hill', 'position': 'WR', 'team': 'MIA', 'opponent': 'NYJ', 'projected_points': 16.3},
                {'name': 'CeeDee Lamb', 'position': 'WR', 'team': 'DAL', 'opponent': 'SF', 'projected_points': 14.7},
                {'name': 'Travis Kelce', 'position': 'TE', 'team': 'KC', 'opponent': 'BUF', 'projected_points': 12.5},
                {'name': 'Harrison Butker', 'position': 'K', 'team': 'KC', 'opponent': 'BUF', 'projected_points': 8.2},
                {'name': 'Ravens DST', 'position': 'D/ST', 'team': 'BAL', 'opponent': 'HOU', 'projected_points': 9.5}
            ],
            'opponent_id': '3',
            'opponent_name': 'Opponent Team',
            'opponent_roster': [
                {'name': 'Josh Allen', 'position': 'QB', 'team': 'BUF', 'opponent': 'KC', 'projected_points': 23.8},
                {'name': 'Derrick Henry', 'position': 'RB', 'team': 'BAL', 'opponent': 'HOU', 'projected_points': 16.5},
                {'name': 'Nick Chubb', 'position': 'RB', 'team': 'CLE', 'opponent': 'CIN', 'projected_points': 14.2},
                {'name': 'Justin Jefferson', 'position': 'WR', 'team': 'MIN', 'opponent': 'GB', 'projected_points': 17.1},
                {'name': 'A.J. Brown', 'position': 'WR', 'team': 'PHI', 'opponent': 'WAS', 'projected_points': 15.3},
                {'name': 'Mark Andrews', 'position': 'TE', 'team': 'BAL', 'opponent': 'HOU', 'projected_points': 10.8},
                {'name': 'Justin Tucker', 'position': 'K', 'team': 'BAL', 'opponent': 'HOU', 'projected_points': 8.5},
                {'name': '49ers DST', 'position': 'D/ST', 'team': 'SF', 'opponent': 'DAL', 'projected_points': 10.2}
            ]
        }
    
    def _get_opponent_team(self, team: str, week: int) -> str:
        """Get the opponent for a given team in a specific week"""
        # This would need NFL schedule data
        # For now, return a placeholder
        return "OPP"
    
    def _analyze_roster(self, roster: List[Dict[str, Any]]) -> List[PlayerMatchup]:
        """Analyze each player in the roster"""
        analyzed_players = []
        
        for player in roster:
            weather_impact = self._analyze_weather_impact(player['team'], player.get('opponent', ''))
            defense_rating = self._get_defense_rating(player['position'], player.get('opponent', ''))
            qb_analysis = self._analyze_qb_performance(player) if player['position'] == 'QB' else None
            
            advantage_factors = []
            disadvantage_factors = []
            
            # Check weather advantages
            if weather_impact in ['favorable', 'dome']:
                advantage_factors.append(f"Good weather conditions: {weather_impact}")
            elif weather_impact in ['rain', 'wind', 'snow']:
                disadvantage_factors.append(f"Poor weather: {weather_impact}")
            
            # Check defense matchup
            if defense_rating < 15:  # Top half defenses
                disadvantage_factors.append(f"Tough matchup vs #{int(defense_rating)} defense")
            elif defense_rating > 20:  # Bottom third defenses
                advantage_factors.append(f"Favorable matchup vs #{int(defense_rating)} defense")
            
            # Position-specific analysis
            if player['position'] == 'RB' and defense_rating > 25:
                advantage_factors.append("Weak run defense")
            elif player['position'] in ['WR', 'TE'] and defense_rating > 25:
                advantage_factors.append("Weak pass defense")
            
            # Calculate overall rating (0-100)
            base_rating = 50
            base_rating += (32 - defense_rating) * 1.5  # Defense impact
            if weather_impact == 'favorable':
                base_rating += 5
            elif weather_impact in ['rain', 'wind', 'snow']:
                base_rating -= 10
            
            # Cap at 0-100
            overall_rating = max(0, min(100, base_rating))
            
            analyzed_players.append(PlayerMatchup(
                player_name=player['name'],
                position=player['position'],
                team=player['team'],
                opponent=player.get('opponent', 'OPP'),
                projected_points=player.get('projected_points', 0),
                weather_impact=weather_impact,
                defense_rating=defense_rating,
                qb_analysis=qb_analysis,
                advantage_factors=advantage_factors,
                disadvantage_factors=disadvantage_factors,
                overall_rating=overall_rating
            ))
        
        return analyzed_players
    
    def _analyze_weather_impact(self, team: str, opponent: str) -> str:
        """Analyze weather conditions for the game"""
        # For now, return simulated weather data
        # In production, this would call a weather API
        import random
        weather_conditions = ['favorable', 'dome', 'rain', 'wind', 'snow', 'cold']
        return random.choice(weather_conditions[:3])  # Bias towards better conditions
    
    def _get_defense_rating(self, position: str, opponent: str) -> float:
        """Get defense rating against position (1-32, lower is better)"""
        # In production, this would use real defense rankings
        import random
        return random.uniform(1, 32)
    
    def _analyze_qb_performance(self, player: Dict[str, Any]) -> str:
        """Analyze QB performance factors"""
        # In production, this would use real QB stats
        analyses = [
            "Strong arm, good in cold weather",
            "Mobile QB, can extend plays",
            "Accurate passer, limited by O-line",
            "Veteran presence, consistent performer",
            "Young talent, high upside but inconsistent"
        ]
        import random
        return random.choice(analyses)
    
    def _update_defense_rankings(self):
        """Update defense rankings from external source"""
        try:
            # Check if update is needed (update daily)
            if self._last_defense_update:
                time_since_update = datetime.now() - self._last_defense_update
                if time_since_update < timedelta(hours=24):
                    return
            
            # Use Perplexity to get current defense rankings
            if self.perplexity_api_key:
                rankings = self._fetch_defense_rankings_from_ai()
                if rankings:
                    self._defense_rankings = rankings
                    self._last_defense_update = datetime.now()
                    logger.info("Updated defense rankings")
            
        except Exception as e:
            logger.error(f"Error updating defense rankings: {e}")
    
    def _fetch_defense_rankings_from_ai(self) -> Optional[Dict[str, Any]]:
        """Fetch current NFL defense rankings using AI"""
        try:
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "user",
                        "content": "What are the current NFL defense rankings for fantasy football? List top defenses against the run and pass."
                    }
                ]
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Parse the response and extract rankings
                # This is simplified - would need proper parsing
                return {"updated": datetime.now().isoformat()}
            
        except Exception as e:
            logger.error(f"Error fetching defense rankings from AI: {e}")
            return None
    
    def _update_qb_performance_data(self):
        """Update QB performance data"""
        try:
            # Similar to defense rankings, update daily
            if self._last_qb_update:
                time_since_update = datetime.now() - self._last_qb_update
                if time_since_update < timedelta(hours=24):
                    return
            
            # Fetch QB data
            if self.perplexity_api_key:
                qb_data = self._fetch_qb_data_from_ai()
                if qb_data:
                    self._qb_data = qb_data
                    self._last_qb_update = datetime.now()
                    logger.info("Updated QB performance data")
            
        except Exception as e:
            logger.error(f"Error updating QB data: {e}")
    
    def _fetch_qb_data_from_ai(self) -> Optional[Dict[str, Any]]:
        """Fetch current QB performance data using AI"""
        try:
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "user",
                        "content": "What are the current NFL QB performance stats and trends for fantasy football? Include completion percentage, TD/INT ratio, and recent form."
                    }
                ]
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {"updated": datetime.now().isoformat()}
            
        except Exception as e:
            logger.error(f"Error fetching QB data from AI: {e}")
            return None
    
    def _compare_rosters(self, user_roster: List[PlayerMatchup], opponent_roster: List[PlayerMatchup]) -> Dict[str, Any]:
        """Compare rosters head-to-head"""
        comparison = {
            "projected_difference": sum(p.projected_points for p in user_roster) - sum(p.projected_points for p in opponent_roster),
            "position_advantages": [],
            "position_disadvantages": [],
            "key_matchups": [],
            "overall_advantage": None
        }
        
        # Compare by position
        positions = ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']
        for pos in positions:
            user_pos_total = sum(p.projected_points for p in user_roster if p.position == pos)
            opp_pos_total = sum(p.projected_points for p in opponent_roster if p.position == pos)
            
            diff = user_pos_total - opp_pos_total
            if diff > 5:
                comparison["position_advantages"].append(f"{pos}: +{diff:.1f} points projected advantage")
            elif diff < -5:
                comparison["position_disadvantages"].append(f"{pos}: -{abs(diff):.1f} points projected disadvantage")
        
        # Identify key matchups
        top_user_players = sorted(user_roster, key=lambda x: x.projected_points, reverse=True)[:3]
        top_opp_players = sorted(opponent_roster, key=lambda x: x.projected_points, reverse=True)[:3]
        
        for player in top_user_players:
            comparison["key_matchups"].append({
                "player": player.player_name,
                "impact": f"Key player: {player.projected_points:.1f} projected points",
                "factors": player.advantage_factors[:2] if player.advantage_factors else []
            })
        
        # Overall advantage
        if comparison["projected_difference"] > 10:
            comparison["overall_advantage"] = "Strong advantage to user"
        elif comparison["projected_difference"] > 0:
            comparison["overall_advantage"] = "Slight advantage to user"
        elif comparison["projected_difference"] < -10:
            comparison["overall_advantage"] = "Strong advantage to opponent"
        elif comparison["projected_difference"] < 0:
            comparison["overall_advantage"] = "Slight advantage to opponent"
        else:
            comparison["overall_advantage"] = "Even matchup"
        
        return comparison
    
    def _get_ai_insights(self, user_roster: List[PlayerMatchup], opponent_roster: List[PlayerMatchup], h2h_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get AI-powered insights about the matchup"""
        if not self.perplexity_api_key:
            return None
        
        try:
            # Build context for AI
            user_key_players = [p.player_name for p in sorted(user_roster, key=lambda x: x.projected_points, reverse=True)[:3]]
            opp_key_players = [p.player_name for p in sorted(opponent_roster, key=lambda x: x.projected_points, reverse=True)[:3]]
            
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Analyze this fantasy football matchup for Week {self._get_current_week()}:
                        User's key players: {', '.join(user_key_players)}
                        Opponent's key players: {', '.join(opp_key_players)}
                        Projected difference: {h2h_analysis['projected_difference']:.1f} points
                        
                        Provide specific insights about player injuries, recent form, and matchup advantages."""
                    }
                ]
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                json=payload,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Parse insights from response
                insights = {
                    "summary": content[:200],
                    "key_insights": self._extract_insights_from_text(content),
                    "recommendations": self._extract_recommendations_from_text(content),
                    "injury_updates": self._extract_injury_info(content),
                    "generated_at": datetime.now().isoformat()
                }
                
                return insights
                
        except Exception as e:
            logger.error(f"Error getting AI insights: {e}")
            return None
    
    def _extract_insights_from_text(self, text: str) -> List[str]:
        """Extract key insights from AI response"""
        insights = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (
                'advantage' in line.lower() or
                'strong' in line.lower() or
                'weak' in line.lower() or
                'trend' in line.lower() or
                'matchup' in line.lower()
            ):
                insights.append(line)
                if len(insights) >= 3:
                    break
        
        return insights
    
    def _extract_recommendations_from_text(self, text: str) -> List[str]:
        """Extract recommendations from AI response"""
        recommendations = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (
                'should' in line.lower() or
                'recommend' in line.lower() or
                'consider' in line.lower() or
                'watch' in line.lower()
            ):
                recommendations.append(line)
                if len(recommendations) >= 2:
                    break
        
        return recommendations
    
    def _extract_injury_info(self, text: str) -> List[str]:
        """Extract injury information from AI response"""
        injuries = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (
                'injur' in line.lower() or
                'questionable' in line.lower() or
                'doubtful' in line.lower() or
                'out' in line.lower()
            ):
                injuries.append(line)
        
        return injuries[:3]  # Limit to 3 injury updates
    
    def _identify_strengths(self, roster: List[PlayerMatchup]) -> List[str]:
        """Identify team strengths"""
        strengths = []
        
        # Check for high-scoring positions
        position_totals = {}
        for player in roster:
            if player.position not in position_totals:
                position_totals[player.position] = 0
            position_totals[player.position] += player.projected_points
        
        for pos, total in position_totals.items():
            if total > 20:  # Threshold for strength
                strengths.append(f"Strong {pos} group ({total:.1f} projected points)")
        
        # Check for favorable matchups
        favorable_matchups = [p for p in roster if p.defense_rating > 20]
        if len(favorable_matchups) >= 3:
            strengths.append(f"{len(favorable_matchups)} players with favorable defensive matchups")
        
        # Check for weather advantages
        good_weather = [p for p in roster if p.weather_impact in ['favorable', 'dome']]
        if len(good_weather) >= 3:
            strengths.append(f"{len(good_weather)} players in good weather conditions")
        
        return strengths[:3]  # Top 3 strengths
    
    def _identify_weaknesses(self, roster: List[PlayerMatchup]) -> List[str]:
        """Identify team weaknesses"""
        weaknesses = []
        
        # Check for low-scoring positions
        position_totals = {}
        for player in roster:
            if player.position not in position_totals:
                position_totals[player.position] = 0
            position_totals[player.position] += player.projected_points
        
        for pos, total in position_totals.items():
            if total < 10:  # Threshold for weakness
                weaknesses.append(f"Weak {pos} group ({total:.1f} projected points)")
        
        # Check for tough matchups
        tough_matchups = [p for p in roster if p.defense_rating < 10]
        if len(tough_matchups) >= 3:
            weaknesses.append(f"{len(tough_matchups)} players facing top-10 defenses")
        
        # Check for weather disadvantages
        bad_weather = [p for p in roster if p.weather_impact in ['rain', 'wind', 'snow']]
        if len(bad_weather) >= 3:
            weaknesses.append(f"{len(bad_weather)} players in poor weather conditions")
        
        return weaknesses[:3]  # Top 3 weaknesses
    
    def _get_weather_advantages(self, roster: List[PlayerMatchup]) -> List[str]:
        """Get weather-based advantages"""
        advantages = []
        
        for player in roster:
            if player.weather_impact == 'dome':
                advantages.append(f"{player.player_name}: Playing in dome (no weather impact)")
            elif player.weather_impact == 'favorable':
                advantages.append(f"{player.player_name}: Good weather conditions")
            elif player.position == 'RB' and player.weather_impact in ['rain', 'snow']:
                advantages.append(f"{player.player_name}: RB in bad weather (more rushing attempts)")
        
        return advantages[:3]
    
    def _generate_recommendations(self, user_roster: List[PlayerMatchup], opponent_roster: List[PlayerMatchup], h2h_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check projected difference
        diff = h2h_analysis.get('projected_difference', 0)
        if diff < -10:
            recommendations.append("Consider looking for high-upside plays on waivers")
            recommendations.append("Monitor injury reports closely for opponent's players")
        elif diff > 10:
            recommendations.append("You're projected to win - ensure all players are active")
            recommendations.append("Consider safer floor plays over boom/bust options")
        
        # Check for specific weaknesses
        for player in user_roster:
            if player.defense_rating < 5:
                recommendations.append(f"Monitor {player.player_name} - facing top-5 defense")
            if player.weather_impact in ['snow', 'heavy rain']:
                recommendations.append(f"Consider benching {player.player_name} - severe weather expected")
        
        # Check for advantages to exploit
        for player in user_roster:
            if player.defense_rating > 28:
                recommendations.append(f"{player.player_name} has excellent matchup - ensure they're starting")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _player_to_dict(self, player: PlayerMatchup) -> Dict[str, Any]:
        """Convert PlayerMatchup to dictionary"""
        return {
            "name": player.player_name,
            "position": player.position,
            "team": player.team,
            "opponent": player.opponent,
            "projected_points": player.projected_points,
            "weather_impact": player.weather_impact,
            "defense_rating": player.defense_rating,
            "qb_analysis": player.qb_analysis,
            "advantage_factors": player.advantage_factors,
            "disadvantage_factors": player.disadvantage_factors,
            "overall_rating": player.overall_rating
        }