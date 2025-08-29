"""
Enhanced AI-Powered Trade Analyzer
Analyzes trades across all teams in league using AI agents
"""

import openai
import requests
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import json
from itertools import combinations

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

class AITradeAnalyzer:
    """
    AI-powered trade analyzer that evaluates all possible trades across league
    """
    
    def __init__(self, openai_key: Optional[str] = None, openrouter_key: Optional[str] = None):
        """Initialize with AI API keys"""
        self.openai_key = openai_key
        self.openrouter_key = openrouter_key
        
        if openai_key:
            openai.api_key = openai_key
        
        self.expert_prompt = self._load_expert_prompt()
        
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

For each trade, provide:
1. Detailed analysis of value exchange
2. How this affects playoff chances for both teams  
3. Risk assessment (injury, schedule, etc.)
4. Strategic implications 
5. Negotiation leverage points
6. Overall recommendation with confidence level

Be specific, actionable, and consider all contextual factors.
"""

    def analyze_all_league_trades(self, league_id: str, platform_service) -> List[TradeOpportunity]:
        """
        Analyze all possible beneficial trades across the entire league
        
        Args:
            league_id: League identifier
            platform_service: Platform integration service
            
        Returns:
            List of ranked trade opportunities
        """
        try:
            # Get all team data from league
            all_teams = self._get_all_team_data(league_id, platform_service)
            
            if len(all_teams) < 2:
                logging.warning("Not enough teams found for trade analysis")
                return []
            
            # Find all possible trade combinations
            trade_opportunities = []
            
            # Analyze 2-team trades
            for team_a, team_b in combinations(all_teams, 2):
                two_team_trades = self._find_two_team_trades(team_a, team_b)
                trade_opportunities.extend(two_team_trades)
            
            # Analyze 3-team trades (more complex)
            if len(all_teams) >= 3:
                for team_combo in combinations(all_teams, 3):
                    three_team_trades = self._find_three_team_trades(team_combo)
                    trade_opportunities.extend(three_team_trades)
            
            # AI analysis of each trade
            enhanced_trades = []
            for trade in trade_opportunities:
                if self._is_viable_trade(trade):
                    ai_enhanced = self._ai_analyze_trade(trade)
                    if ai_enhanced:
                        enhanced_trades.append(ai_enhanced)
            
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
                    trade = TradeOpportunity(
                        team_a_id=team_a['team_id'],
                        team_b_id=team_b['team_id'],
                        team_a_gives=trade_return,
                        team_a_gets=[player],
                        team_b_gives=[player],
                        team_b_gets=trade_return,
                        fairness_score=0.0,  # Will be calculated
                        team_a_improvement=0.0,  # Will be calculated
                        team_b_improvement=0.0,  # Will be calculated
                        ai_analysis="",  # Will be filled by AI
                        confidence_score=0.0,
                        urgency="MEDIUM"
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
            if self.openai_key:
                response = self._query_openai(trade_context)
            else:
                response = self._query_openrouter(trade_context)
            
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
        
        return f"""
Analyze this fantasy football trade:

Team A (ID: {trade.team_a_id}):
- Gives: {team_a_gives_str}
- Gets: {team_a_gets_str}

Team B (ID: {trade.team_b_id}):
- Gives: {", ".join([p.get('name', 'Unknown') + f" ({p.get('position', 'POS')})" for p in trade.team_b_gives])}
- Gets: {", ".join([p.get('name', 'Unknown') + f" ({p.get('position', 'POS')})" for p in trade.team_b_gets])}

Provide detailed analysis including:
1. Trade fairness (1-100 scale)
2. Impact on each team's playoff chances
3. Risk assessment
4. Overall recommendation
5. Confidence level (0-1)
6. Urgency (HIGH/MEDIUM/LOW)

Format as JSON with fields: analysis, fairness_score, team_a_improvement, team_b_improvement, confidence, urgency
"""
    
    def _query_openai(self, trade_context: str) -> Optional[Dict[str, Any]]:
        """Query OpenAI for trade analysis"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.expert_prompt},
                    {"role": "user", "content": trade_context}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback to text analysis
                return {
                    'analysis': ai_response,
                    'fairness_score': 50.0,
                    'team_a_improvement': 0.0,
                    'team_b_improvement': 0.0,
                    'confidence': 0.7,
                    'urgency': 'MEDIUM'
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
                    "model": "anthropic/claude-3-sonnet",
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

# Example usage:
# analyzer = AITradeAnalyzer(openai_key="your_key", openrouter_key="your_key")  
# trades = analyzer.analyze_all_league_trades("83806", platform_service)