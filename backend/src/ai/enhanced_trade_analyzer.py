"""
Enhanced AI-Powered Trade Analyzer
Analyzes trades across all teams in league using AI agents
"""

import requests
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import json
from itertools import combinations
try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False
    OpenAI = None

@dataclass
class TradeOpportunity:
    """Represents a potential trade opportunity"""
    team_a_id: str
    team_b_id: str
    team_a_gives: List[Dict[str, Any]]
    team_a_gets: List[Dict[str, Any]]
    team_b_gives: List[Dict[str, Any]]
    team_b_gets: List[Dict[str, Any]]
    fairness_score: float
    team_a_improvement: float
    team_b_improvement: float
    ai_analysis: str
    confidence_score: float
    urgency: str  # HIGH, MEDIUM, LOW
    bye_week_impact: Dict[str, Any]  # Impact on bye week coverage
    matchup_advantage: Dict[str, Any]  # Future matchup advantages
    timing_recommendation: str  # When to execute trade
    team_a_name: str = ""  # Team A name (e.g., "Trashy McTrash-Face")
    team_b_name: str = ""  # Team B name

class AITradeAnalyzer:
    """
    AI-powered trade analyzer that evaluates all possible trades across league
    """
    
    # Model configuration - easy to change
    MODELS = {
        "cheap": {
            "openai": "gpt-4o-mini",  # $0.15/1M input, $0.60/1M output
            "openrouter": "anthropic/claude-3-haiku"  # $0.25/1M input, $1.25/1M output
        },
        "balanced": {
            "openai": "gpt-4o-mini",  # Still very cost-effective
            "openrouter": "anthropic/claude-3-haiku"  # Best value for money
        },
        "premium": {
            "openai": "gpt-4",  # $30/1M input, $60/1M output (expensive!)
            "openrouter": "anthropic/claude-3.5-sonnet"  # $3/1M input, $15/1M output
        }
    }
    
    def __init__(self, openai_key: Optional[str] = None, openrouter_key: Optional[str] = None, quality: str = "balanced"):
        """Initialize with AI API keys
        
        Args:
            openai_key: OpenAI API key
            openrouter_key: OpenRouter API key
            quality: Model quality tier - "cheap", "balanced", or "premium"
        """
        self.openai_key = openai_key
        self.openrouter_key = openrouter_key
        self.client = None
        self.quality = quality
        self.selected_models = self.MODELS.get(quality, self.MODELS["balanced"])
        
        if openai_key and openai_available:
            self.client = OpenAI(api_key=openai_key)
        
        self.expert_prompt = self._load_expert_prompt()
        
        # Log selected models
        logging.info(f"AI Trade Analyzer initialized with {quality} quality tier")
        logging.info(f"Models: OpenAI={self.selected_models['openai']}, OpenRouter={self.selected_models['openrouter']}")
        
    def _load_expert_prompt(self) -> str:
        """Load the expert fantasy football agent prompt"""
        return """
You are a legendary fantasy football expert with 30 years of experience and a 90% winning ratio.

Your expertise includes:
- Advanced trade evaluation considering positional scarcity
- League-specific strategy optimization  
- Injury risk and playoff schedule analysis
- Team construction and roster balance
- Market inefficiency identification
- Psychological aspects of trading with opponents
- Bye week management and coverage strategy
- Upcoming matchup difficulty assessment
- Playoff schedule strength analysis

For each trade, provide:
1. Detailed analysis of value exchange
2. How this affects playoff chances for both teams  
3. Risk assessment (injury, schedule, etc.)
4. Strategic implications 
5. Negotiation leverage points
6. Overall recommendation with confidence level
7. Bye week coverage impact for both teams
8. Matchup advantages/disadvantages for next 4 weeks
9. Optimal timing for trade execution

Be specific, actionable, and consider all contextual factors including upcoming schedules.
"""

    def analyze_all_league_trades(self, league_id: str, platform_service, focus_team_id: str = None) -> List[TradeOpportunity]:
        """
        Analyze all possible beneficial trades across the entire league
        
        Args:
            league_id: League identifier
            platform_service: Platform integration service
            focus_team_id: Optional team to focus on (dramatically reduces scope)
            
        Returns:
            List of ranked trade opportunities
        """
        try:
            logging.info(f"Starting trade analysis for league {league_id}, focus_team: {focus_team_id}")
            
            # Get all team data from league
            all_teams = self._get_all_team_data(league_id, platform_service)
            logging.info(f"Retrieved {len(all_teams)} teams from league")
            
            if len(all_teams) < 2:
                logging.warning("Not enough teams found for trade analysis")
                return []
            
            # If focus_team specified, only analyze trades for that team
            if focus_team_id:
                focus_team = next((t for t in all_teams if t['team_id'] == focus_team_id), None)
                if not focus_team:
                    logging.error(f"Focus team {focus_team_id} not found")
                    return []
                    
                # Only analyze trades between focus team and others
                trade_opportunities = []
                for other_team in all_teams:
                    if other_team['team_id'] != focus_team_id:
                        two_team_trades = self._find_two_team_trades(focus_team, other_team)
                        trade_opportunities.extend(two_team_trades)
                        
                logging.info(f"Generated {len(trade_opportunities)} potential trades for team {focus_team_id}")
            else:
                # Find all possible trade combinations
                trade_opportunities = []
                
                # Analyze 2-team trades
                team_pairs = list(combinations(all_teams, 2))
                logging.info(f"Analyzing {len(team_pairs)} team pairs for trades")
                
                for team_a, team_b in team_pairs:
                    two_team_trades = self._find_two_team_trades(team_a, team_b)
                    trade_opportunities.extend(two_team_trades)
                
                logging.info(f"Generated {len(trade_opportunities)} potential 2-team trades")
                
                # Skip 3-team trades for now (too complex/slow)
                # if len(all_teams) >= 3:
                #     for team_combo in combinations(all_teams, 3):
                #         three_team_trades = self._find_three_team_trades(team_combo)
                #         trade_opportunities.extend(three_team_trades)
            
            # Limit number of trades to analyze with AI (top 5 most viable)
            viable_trades = [t for t in trade_opportunities if self._is_viable_trade(t)]
            logging.info(f"Found {len(viable_trades)} viable trades")
            
            # Sort by initial viability and take top 5
            viable_trades = viable_trades[:5]
            logging.info(f"Analyzing top {len(viable_trades)} trades with AI")
            
            # AI analysis of each trade
            enhanced_trades = []
            for i, trade in enumerate(viable_trades):
                logging.info(f"AI analyzing trade {i+1}/{len(viable_trades)}")
                ai_enhanced = self._ai_analyze_trade(trade)
                if ai_enhanced:
                    enhanced_trades.append(ai_enhanced)
                else:
                    logging.warning(f"AI analysis failed for trade {i+1}")
            
            # Rank by overall value and feasibility
            return self._rank_trade_opportunities(enhanced_trades)
            
        except Exception as e:
            logging.error(f"Error analyzing league trades: {e}")
            return []
    
    def _get_all_team_data(self, league_id: str, platform_service) -> List[Dict[str, Any]]:
        """Get roster and team data for all teams in league"""
        all_teams = []
        
        # ESPN leagues typically have team IDs 1-12
        for team_id in range(1, 13):  # Try team IDs 1-12
            try:
                team_data = platform_service.get_user_data("espn", str(team_id))
                roster_data = platform_service.get_roster_data("espn", str(team_id))
                
                if team_data and roster_data:
                    # Handle nested data structure
                    roster = roster_data.get('data', {})
                    if isinstance(roster, dict) and 'data' in roster:
                        roster = roster['data']
                    
                    team_info = {
                        'team_id': str(team_id),
                        'team_name': team_data.get('team_name', f'Team {team_id}'),
                        'wins': team_data.get('wins', 0),
                        'losses': team_data.get('losses', 0),
                        'points_for': team_data.get('points_for', 0),
                        'roster': roster if isinstance(roster, list) else []
                    }
                    all_teams.append(team_info)
                    
            except Exception as e:
                logging.debug(f"Could not get data for team {team_id}: {e}")
                continue
        
        logging.info(f"Successfully retrieved data for {len(all_teams)} teams")
        return all_teams
    
    def _player_to_dict(self, player: Any) -> Dict[str, Any]:
        """Convert player object to dictionary"""
        if isinstance(player, dict):
            return player
        
        # Convert player object to dict
        try:
            return {
                'name': getattr(player, 'name', 'Unknown'),
                'position': getattr(player, 'position', 'POS'),
                'team': getattr(player, 'proTeam', 'FA'),
                'injury_status': getattr(player, 'injuryStatus', None)
            }
        except:
            return {'name': str(player), 'position': 'POS', 'team': 'FA'}
    
    def _find_two_team_trades(self, team_a: Dict[str, Any], team_b: Dict[str, Any]) -> List[TradeOpportunity]:
        """Find beneficial 2-team trades"""
        trades = []
        
        # Analyze team needs
        team_a_needs = self._analyze_team_needs(team_a)
        team_b_needs = self._analyze_team_needs(team_b)
        
        # Find players that could address needs
        for position_needed in team_a_needs['weak_positions']:
            # Look for players in that position on team B
            available_players = [p for p in team_b['roster'] 
                               if p.get('position') == position_needed]
            
            for player in available_players:
                # Find suitable trade return for team B
                trade_return = self._find_trade_return(team_a, team_b_needs, player)
                
                if trade_return:
                    # Convert players to dicts
                    trade_return_dicts = [self._player_to_dict(p) for p in trade_return]
                    player_dict = self._player_to_dict(player)
                    
                    # Analyze bye week and matchup impacts
                    bye_impact = self._analyze_bye_week_impact(
                        team_a, team_b, trade_return_dicts, [player_dict]
                    )
                    matchup_adv = self._analyze_matchup_advantage(
                        team_a, team_b, trade_return_dicts, [player_dict]
                    )
                    
                    trade = TradeOpportunity(
                        team_a_id=team_a['team_id'],
                        team_b_id=team_b['team_id'],
                        team_a_name=team_a.get('team_name', f"Team {team_a['team_id']}"),
                        team_b_name=team_b.get('team_name', f"Team {team_b['team_id']}"),
                        team_a_gives=trade_return_dicts,
                        team_a_gets=[player_dict],
                        team_b_gives=[player_dict],
                        team_b_gets=trade_return_dicts,
                        fairness_score=0.0,  # Will be calculated
                        team_a_improvement=0.0,  # Will be calculated
                        team_b_improvement=0.0,  # Will be calculated
                        ai_analysis="",  # Will be filled by AI
                        confidence_score=0.0,
                        urgency="MEDIUM",
                        bye_week_impact=bye_impact,
                        matchup_advantage=matchup_adv,
                        timing_recommendation=self._determine_trade_timing(bye_impact, matchup_adv)
                    )
                    trades.append(trade)
        
        return trades
    
    def _analyze_team_needs(self, team: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze team's positional strengths and weaknesses"""
        roster = team.get('roster', [])
        
        # Count players by position
        position_counts = {}
        position_quality = {}
        
        for player in roster:
            pos = player.get('position', 'UNKNOWN')
            if pos not in position_counts:
                position_counts[pos] = 0
                position_quality[pos] = []
            
            position_counts[pos] += 1
            # Simple quality metric based on team (NFL team quality proxy)
            quality_score = self._estimate_player_quality(player)
            position_quality[pos].append(quality_score)
        
        # Identify weak positions
        weak_positions = []
        strong_positions = []
        
        # Standard roster requirements
        position_needs = {
            'QB': 1,    # Need at least 1 quality QB
            'RB': 2,    # Need at least 2 quality RBs  
            'WR': 2,    # Need at least 2 quality WRs
            'TE': 1,    # Need at least 1 quality TE
        }
        
        for pos, min_needed in position_needs.items():
            count = position_counts.get(pos, 0)
            avg_quality = sum(position_quality.get(pos, [0])) / max(1, count)
            
            if count < min_needed or avg_quality < 5.0:  # Below average quality
                weak_positions.append(pos)
            elif count > min_needed and avg_quality > 7.0:  # Above average
                strong_positions.append(pos)
        
        return {
            'weak_positions': weak_positions,
            'strong_positions': strong_positions,
            'position_counts': position_counts,
            'team_record': f"{team.get('wins', 0)}-{team.get('losses', 0)}"
        }
    
    def _estimate_player_quality(self, player: Dict[str, Any]) -> float:
        """Estimate player quality on 1-10 scale"""
        # This is a simplified quality estimation
        # In reality, would use advanced metrics, projections, etc.
        
        # Factors that increase quality
        quality = 5.0  # Base quality
        
        # NFL team quality (rough proxy)
        good_teams = ['BUF', 'KC', 'DAL', 'SF', 'PHI', 'MIA', 'CIN', 'BAL']
        if player.get('team') in good_teams:
            quality += 1.0
        
        # Position scarcity
        scarce_positions = ['RB', 'TE']
        if player.get('position') in scarce_positions:
            quality += 0.5
        
        # Injury status
        if player.get('injury_status') in ['QUESTIONABLE', 'DOUBTFUL']:
            quality -= 1.0
        elif player.get('injury_status') == 'OUT':
            quality -= 2.0
        
        return max(1.0, min(10.0, quality))
    
    def _find_trade_return(self, offering_team: Dict[str, Any], 
                          receiving_team_needs: Dict[str, Any], 
                          desired_player: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find appropriate players to offer in return"""
        
        # Look for players in positions the receiving team needs
        suitable_returns = []
        
        for need_position in receiving_team_needs['weak_positions']:
            candidates = [p for p in offering_team['roster'] 
                         if p.get('position') == need_position]
            
            if candidates:
                # Pick best candidate for that position
                best_candidate = max(candidates, key=self._estimate_player_quality)
                suitable_returns.append(best_candidate)
        
        # If no direct needs match, offer from strong positions
        if not suitable_returns:
            for strong_pos in receiving_team_needs['strong_positions']:
                candidates = [p for p in offering_team['roster'] 
                             if p.get('position') == strong_pos]
                if candidates:
                    suitable_returns.append(candidates[0])
                    break
        
        return suitable_returns[:1]  # Return single player for simple 1-for-1 trade
    
    def _find_three_team_trades(self, teams: Tuple[Dict[str, Any], ...]) -> List[TradeOpportunity]:
        """Find beneficial 3-team trades (more complex)"""
        # Simplified 3-team trade logic
        # In practice, this would be much more sophisticated
        return []  # Not implemented in this version
    
    def _is_viable_trade(self, trade: TradeOpportunity) -> bool:
        """Check if trade is worth analyzing further"""
        # Basic viability checks
        if not trade.team_a_gives or not trade.team_a_gets:
            return False
        
        if not trade.team_b_gives or not trade.team_b_gets:
            return False
        
        return True
    
    def _ai_analyze_trade(self, trade: TradeOpportunity) -> Optional[TradeOpportunity]:
        """Use AI to provide expert analysis of the trade"""
        
        if not (self.openai_key or self.openrouter_key):
            # Fallback to basic analysis if no AI keys
            trade.ai_analysis = "AI analysis not available - no API key provided"
            trade.confidence_score = 0.5
            return trade
        
        try:
            # Prepare trade context for AI
            trade_context = self._format_trade_for_ai(trade)
            
            # Make AI request
            response = None
            if self.openai_key:
                logging.info("Querying OpenAI for trade analysis...")
                response = self._query_openai(trade_context)
                if response:
                    logging.info("OpenAI analysis successful")
                else:
                    logging.warning("OpenAI query failed")
            
            if not response and self.openrouter_key:
                logging.info("Querying OpenRouter for trade analysis...")
                response = self._query_openrouter(trade_context)
                if response:
                    logging.info("OpenRouter analysis successful")
                else:
                    logging.warning("OpenRouter query failed")
            
            if response:
                trade.ai_analysis = response.get('analysis', '')
                trade.confidence_score = response.get('confidence', 0.5)
                trade.urgency = response.get('urgency', 'MEDIUM')
                
                # Extract fairness and improvement scores from AI response
                trade.fairness_score = response.get('fairness_score', 50.0)
                trade.team_a_improvement = response.get('team_a_improvement', 0.0)
                trade.team_b_improvement = response.get('team_b_improvement', 0.0)
                
                return trade
            
        except Exception as e:
            logging.error(f"AI analysis failed: {e}")
            trade.ai_analysis = f"AI analysis failed: {str(e)}"
            trade.confidence_score = 0.1
        
        return trade
    
    def _format_trade_for_ai(self, trade: TradeOpportunity) -> str:
        """Format trade details for AI analysis"""
        
        team_a_gives_str = ", ".join([p.get('name', 'Unknown') + f" ({p.get('position', 'POS')})" 
                                     for p in trade.team_a_gives])
        team_a_gets_str = ", ".join([p.get('name', 'Unknown') + f" ({p.get('position', 'POS')})" 
                                    for p in trade.team_a_gets])
        
        # Check if Team A is Team 7 (Trashy McTrash-Face)
        is_our_team = trade.team_a_id == "7"
        our_team_label = "Trashy McTrash-Face (Team 7)" if is_our_team else f"Team {trade.team_a_id}"
        other_team_label = f"Team {trade.team_b_id}"
        
        return f"""
Analyze this fantasy football trade from the perspective of {our_team_label}:

{our_team_label}:
- GIVES AWAY: {team_a_gives_str}
- RECEIVES: {team_a_gets_str}

{other_team_label}:
- GIVES AWAY: {", ".join([p.get('name', 'Unknown') + f" ({p.get('position', 'POS')})" for p in trade.team_b_gives])}
- RECEIVES: {", ".join([p.get('name', 'Unknown') + f" ({p.get('position', 'POS')})" for p in trade.team_b_gets])}

IMPORTANT: Focus your analysis on whether this trade helps Trashy McTrash-Face (Team 7) win their league.

Provide your analysis in PLAIN ENGLISH (not JSON) covering:
1. Why this trade helps or hurts Trashy McTrash-Face
2. The immediate impact on Team 7's starting lineup
3. How this affects Team 7's playoff chances (1-100 score)
4. Any risks Team 7 should consider
5. Your recommendation: STRONGLY ACCEPT, ACCEPT, CONSIDER, DECLINE, or STRONGLY DECLINE
6. One-sentence summary of why Team 7 should or shouldn't do this trade

Be conversational and explain in terms a casual fantasy player would understand. Focus on Team 7's benefit.
"""
    
    def _query_openai(self, trade_context: str) -> Optional[Dict[str, Any]]:
        """Query OpenAI for trade analysis"""
        if not self.client:
            logging.error("OpenAI client not initialized")
            return None
            
        try:
            response = self.client.chat.completions.create(
                model=self.selected_models['openai'],  # Uses configured model based on quality tier
                messages=[
                    {"role": "system", "content": self.expert_prompt},
                    {"role": "user", "content": trade_context}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse the response to extract key metrics
            analysis_text = ai_response
            
            # Try to extract scores and recommendation from the text
            fairness = 50.0
            improvement = 0.0
            urgency = 'MEDIUM'
            
            # Look for recommendation keywords
            if 'STRONGLY ACCEPT' in ai_response.upper():
                fairness = 85.0
                improvement = 15.0
                urgency = 'HIGH'
            elif 'ACCEPT' in ai_response.upper() and 'DECLINE' not in ai_response.upper():
                fairness = 70.0
                improvement = 8.0
                urgency = 'HIGH'
            elif 'CONSIDER' in ai_response.upper():
                fairness = 55.0
                improvement = 3.0
                urgency = 'MEDIUM'
            elif 'STRONGLY DECLINE' in ai_response.upper():
                fairness = 20.0
                improvement = -10.0
                urgency = 'LOW'
            elif 'DECLINE' in ai_response.upper():
                fairness = 35.0
                improvement = -5.0
                urgency = 'LOW'
            
            return {
                'analysis': analysis_text,
                'fairness_score': fairness,
                'team_a_improvement': improvement,
                'team_b_improvement': 0.0,
                'confidence': 0.8,
                'urgency': urgency
            }
                
        except Exception as e:
            logging.error(f"OpenAI query failed: {e}")
            return None
    
    def _query_openrouter(self, trade_context: str) -> Optional[Dict[str, Any]]:
        """Query OpenRouter for trade analysis"""
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.selected_models['openrouter'],  # Uses configured model based on quality tier
                    "messages": [
                        {"role": "system", "content": self.expert_prompt},
                        {"role": "user", "content": trade_context}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()['choices'][0]['message']['content']
                
                # Try to parse as JSON
                try:
                    return json.loads(ai_response)
                except json.JSONDecodeError:
                    return {
                        'analysis': ai_response,
                        'fairness_score': 50.0,
                        'team_a_improvement': 0.0,
                        'team_b_improvement': 0.0,
                        'confidence': 0.7,
                        'urgency': 'MEDIUM'
                    }
            
        except Exception as e:
            logging.error(f"OpenRouter query failed: {e}")
            return None
    
    def _rank_trade_opportunities(self, trades: List[TradeOpportunity]) -> List[TradeOpportunity]:
        """Rank trade opportunities by overall value"""
        
        def trade_score(trade):
            # Composite score considering multiple factors
            fairness_factor = 1.0 - abs(trade.fairness_score - 50.0) / 50.0  # Closer to 50 is better
            improvement_factor = max(0, trade.team_a_improvement)  # Your team's improvement
            confidence_factor = trade.confidence_score
            urgency_factor = {'HIGH': 1.0, 'MEDIUM': 0.7, 'LOW': 0.4}.get(trade.urgency, 0.5)
            
            return (fairness_factor * 0.3 + 
                   improvement_factor * 0.4 + 
                   confidence_factor * 0.2 + 
                   urgency_factor * 0.1)
        
        return sorted(trades, key=trade_score, reverse=True)
    
    def _analyze_bye_week_impact(
        self,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        team_a_gives: List[Dict[str, Any]],
        team_a_gets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze how trade affects bye week coverage for both teams
        """
        bye_impact = {
            "team_a": {"improves": False, "weeks_affected": [], "details": ""},
            "team_b": {"improves": False, "weeks_affected": [], "details": ""}
        }
        
        # Check bye weeks for players being traded
        for player in team_a_gives:
            bye_week = player.get("bye_week", 0)
            if bye_week > 0:
                position = player.get("position")
                # Check if team_a has other players at this position for bye week
                coverage = self._check_bye_coverage(team_a, position, bye_week, exclude_players=team_a_gives)
                if not coverage:
                    bye_impact["team_a"]["weeks_affected"].append(bye_week)
                    bye_impact["team_a"]["details"] += f"Losing {position} coverage for week {bye_week}. "
        
        for player in team_a_gets:
            bye_week = player.get("bye_week", 0)
            if bye_week > 0:
                position = player.get("position")
                # Check if this helps team_a's bye week issues
                existing_byes = self._get_position_bye_weeks(team_a, position)
                if bye_week not in existing_byes:
                    bye_impact["team_a"]["improves"] = True
                    bye_impact["team_a"]["details"] += f"Gaining {position} with different bye week ({bye_week}). "
        
        # Similar analysis for team_b (reverse of team_a)
        bye_impact["team_b"]["improves"] = not bye_impact["team_a"]["improves"]
        bye_impact["team_b"]["weeks_affected"] = bye_impact["team_a"]["weeks_affected"]
        
        return bye_impact
    
    def _analyze_matchup_advantage(
        self,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        team_a_gives: List[Dict[str, Any]],
        team_a_gets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze matchup advantages for next 4 weeks
        """
        matchup_advantage = {
            "team_a": {"weeks_improved": [], "strength_change": 0, "details": ""},
            "team_b": {"weeks_improved": [], "strength_change": 0, "details": ""}
        }
        
        # Simplified matchup analysis
        # In production, would use actual schedule and defensive rankings
        for player in team_a_gets:
            # Check upcoming matchups (placeholder logic)
            easy_matchups = self._get_easy_matchups(player)
            if easy_matchups:
                matchup_advantage["team_a"]["weeks_improved"].extend(easy_matchups)
                matchup_advantage["team_a"]["strength_change"] += len(easy_matchups) * 2
                matchup_advantage["team_a"]["details"] += f"{player.get('name')} has {len(easy_matchups)} favorable matchups. "
        
        for player in team_a_gives:
            hard_matchups = self._get_hard_matchups(player)
            if hard_matchups:
                matchup_advantage["team_a"]["strength_change"] -= len(hard_matchups)
                matchup_advantage["team_a"]["details"] += f"Losing {player.get('name')} avoids {len(hard_matchups)} tough matchups. "
        
        # Team B gets opposite impact
        matchup_advantage["team_b"]["strength_change"] = -matchup_advantage["team_a"]["strength_change"]
        
        return matchup_advantage
    
    def _determine_trade_timing(
        self,
        bye_impact: Dict[str, Any],
        matchup_advantage: Dict[str, Any]
    ) -> str:
        """
        Determine optimal timing for trade execution
        """
        # Check urgency based on bye weeks
        if bye_impact["team_a"]["weeks_affected"]:
            earliest_bye = min(bye_impact["team_a"]["weeks_affected"])
            if earliest_bye <= 2:  # Next 2 weeks
                return "EXECUTE IMMEDIATELY - Bye week coverage needed"
        
        # Check matchup advantages
        if matchup_advantage["team_a"]["strength_change"] > 5:
            return "EXECUTE THIS WEEK - Strong upcoming matchups"
        elif matchup_advantage["team_a"]["strength_change"] < -3:
            return "WAIT 1-2 WEEKS - Better matchups later"
        
        return "FLEXIBLE TIMING - Execute when convenient"
    
    def _check_bye_coverage(
        self,
        team: Dict[str, Any],
        position: str,
        bye_week: int,
        exclude_players: List[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if team has coverage for a position during bye week
        """
        exclude_ids = [p.get("player_id") for p in (exclude_players or [])]
        roster = team.get("roster", [])
        
        for player in roster:
            if (player.get("position") == position and 
                player.get("bye_week") != bye_week and
                player.get("player_id") not in exclude_ids):
                return True
        return False
    
    def _get_position_bye_weeks(self, team: Dict[str, Any], position: str) -> List[int]:
        """
        Get all bye weeks for a position on team
        """
        bye_weeks = []
        for player in team.get("roster", []):
            if player.get("position") == position:
                bye_week = player.get("bye_week", 0)
                if bye_week > 0:
                    bye_weeks.append(bye_week)
        return bye_weeks
    
    def _get_easy_matchups(self, player: Dict[str, Any]) -> List[int]:
        """
        Get weeks with easy matchups for player (placeholder)
        """
        # In production, would check actual schedule
        # For now, return random weeks as example
        import random
        if random.random() > 0.5:
            return [1, 3]  # Example easy matchup weeks
        return []
    
    def _get_hard_matchups(self, player: Dict[str, Any]) -> List[int]:
        """
        Get weeks with difficult matchups for player (placeholder)
        """
        # In production, would check actual schedule
        import random
        if random.random() > 0.5:
            return [2, 4]  # Example hard matchup weeks
        return []

# Example usage:
# analyzer = AITradeAnalyzer(openai_key="your_key", openrouter_key="your_key")  
# trades = analyzer.analyze_all_league_trades("83806", platform_service)