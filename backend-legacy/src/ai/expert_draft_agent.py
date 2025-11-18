"""
Expert Draft Tool with 30-Year Fantasy Football Veteran AI Agent
Provides championship-level draft strategy and real-time guidance
"""

import openai
import requests
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
import json
from datetime import datetime

@dataclass
class DraftPick:
    """Represents a draft pick"""
    round: int
    pick: int
    overall_pick: int
    player_name: str
    position: str
    team: str
    adp: float  # Average Draft Position
    value_grade: str  # A+, A, B+, B, C+, C, D, F
    pick_analysis: str
    alternatives_considered: List[str]
    
@dataclass
class DraftStrategy:
    """Draft strategy for specific league"""
    league_settings: Dict[str, Any]
    draft_position: int
    total_teams: int
    strategy_name: str  # "Zero RB", "Hero RB", "Robust RB", "BPA", etc.
    round_by_round_plan: Dict[int, Dict[str, Any]]
    key_targets: List[Dict[str, Any]]
    avoid_list: List[Dict[str, Any]]
    handcuff_strategy: Dict[str, Any]
    
@dataclass
class LiveDraftState:
    """Current state of live draft"""
    current_round: int
    current_pick: int
    picks_made: List[DraftPick]
    available_players: List[Dict[str, Any]]
    user_roster: List[Dict[str, Any]]
    next_pick_in: int  # Picks until user's next turn
    
class ExpertDraftAgent:
    """
    AI-powered draft tool with 30 years of fantasy football expertise
    """
    
    def __init__(self, openai_key: Optional[str] = None, openrouter_key: Optional[str] = None):
        """Initialize with AI API keys"""
        self.openai_key = openai_key
        self.openrouter_key = openrouter_key
        
        if openai_key:
            openai.api_key = openai_key
            
        self.expert_persona = self._load_expert_persona()
        self.draft_strategies = self._load_draft_strategies()
        
    def _load_expert_persona(self) -> str:
        """Load the 30-year expert persona prompt"""
        return """
You are a legendary fantasy football draft expert with 30 years of experience and a 90% championship winning ratio.

Your expertise spans:

**Draft Philosophy:**
- "Championship teams are built, not drafted" - focus on upside and ceiling
- Value over consensus - find market inefficiencies 
- Positional scarcity understanding across all formats
- Roster construction balance and complementary pieces
- Late-round lottery tickets that win championships

**30 Years of Winning Strategies:**
- Zero RB: Wait on RB, load up on WR/TE elite talent early
- Hero RB: Take one elite RB early, then wait and diversify  
- Robust RB: Secure RB depth early, they get hurt most
- BPA (Best Player Available): Always take highest value regardless of position
- Contrarian: Zig when others zag, find overlooked value

**Advanced Concepts:**
- ADP manipulation and reaching vs. value
- Handcuff identification and lottery ticket strategy
- Rookie vs. veteran risk/reward profiles
- Injury history analysis and risk mitigation
- Playoff schedule strength (weeks 15-17)
- Bye week stacking and roster management

**Draft Day Execution:**
- Read the room - adapt to how others are drafting
- Target identification 2-3 rounds ahead
- Tier breaks and when to reach vs. wait
- Trade up/down opportunities mid-draft
- Stream vs. draft approach for K/DEF

Your advice is:
- Confident and decisive (you've seen it all)
- Contextual to specific league settings
- Strategic with detailed reasoning
- Actionable with specific player recommendations
- Championship-focused, not season-long mediocrity

You speak with the authority of someone who has dominated fantasy football for three decades.
"""

    def _load_draft_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined draft strategies"""
        return {
            "zero_rb": {
                "name": "Zero RB",
                "description": "Wait on RB, dominate WR/TE early",
                "early_rounds": ["WR", "WR", "WR/TE", "QB/TE"],
                "rb_targets": "rounds 5-8",
                "best_for": "PPR leagues, deep benches"
            },
            "hero_rb": {
                "name": "Hero RB", 
                "description": "One elite RB, then diversify",
                "early_rounds": ["RB", "WR", "WR", "RB/WR"],
                "rb_targets": "1 elite early, depth late",
                "best_for": "Standard scoring, shallow benches"
            },
            "robust_rb": {
                "name": "Robust RB",
                "description": "Secure RB depth early and often",
                "early_rounds": ["RB", "RB", "RB/WR", "RB/WR"],
                "rb_targets": "3-4 in first 6 rounds",
                "best_for": "Standard scoring, injury-prone position"
            },
            "bpa": {
                "name": "Best Player Available",
                "description": "Pure value regardless of position",
                "early_rounds": ["BPA", "BPA", "BPA", "BPA"],
                "rb_targets": "as value dictates",
                "best_for": "Experienced drafters, trade-active leagues"
            }
        }
    
    def create_draft_strategy(self, league_settings: Dict[str, Any], 
                            draft_position: int, total_teams: int) -> DraftStrategy:
        """
        Create customized draft strategy for specific league
        
        Args:
            league_settings: League scoring, roster, bench settings
            draft_position: User's draft position (1-12 typically)
            total_teams: Number of teams in league
            
        Returns:
            Customized DraftStrategy object
        """
        
        # Analyze league settings to determine best strategy
        strategy_name = self._determine_optimal_strategy(league_settings, draft_position)
        
        # Create round-by-round plan
        round_plan = self._create_round_plan(strategy_name, draft_position, total_teams, league_settings)
        
        # Generate key targets and avoid list
        targets = self._generate_targets(league_settings, strategy_name)
        avoid_list = self._generate_avoid_list(league_settings)
        
        # Handcuff strategy
        handcuff_plan = self._create_handcuff_strategy(strategy_name)
        
        return DraftStrategy(
            league_settings=league_settings,
            draft_position=draft_position,
            total_teams=total_teams,
            strategy_name=strategy_name,
            round_by_round_plan=round_plan,
            key_targets=targets,
            avoid_list=avoid_list,
            handcuff_strategy=handcuff_plan
        )
    
    def analyze_draft_pick(self, draft_state: LiveDraftState, 
                          player_under_consideration: Dict[str, Any],
                          league_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a specific draft pick in real-time
        
        Args:
            draft_state: Current state of the draft
            player_under_consideration: Player being considered
            league_settings: League configuration
            
        Returns:
            Detailed pick analysis with recommendation
        """
        
        analysis_context = self._format_pick_context(
            draft_state, player_under_consideration, league_settings
        )
        
        if self.openai_key or self.openrouter_key:
            ai_analysis = self._get_ai_pick_analysis(analysis_context)
        else:
            ai_analysis = self._fallback_pick_analysis(
                draft_state, player_under_consideration
            )
        
        return ai_analysis
    
    def get_draft_recommendations(self, draft_state: LiveDraftState,
                                 league_settings: Dict[str, Any],
                                 num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """
        Get top draft recommendations for current situation
        
        Args:
            draft_state: Current draft state
            league_settings: League settings
            num_recommendations: Number of players to recommend
            
        Returns:
            List of recommended players with analysis
        """
        
        # Filter available players by positional need
        positional_needs = self._assess_positional_needs(draft_state.user_roster, league_settings)
        
        # Get top available players
        top_available = self._rank_available_players(
            draft_state.available_players, positional_needs, draft_state.current_round
        )
        
        recommendations = []
        for player in top_available[:num_recommendations]:
            analysis = self.analyze_draft_pick(draft_state, player, league_settings)
            recommendations.append({
                'player': player,
                'analysis': analysis,
                'recommendation_strength': analysis.get('recommendation_strength', 'MEDIUM')
            })
        
        return recommendations
    
    def post_draft_analysis(self, final_roster: List[Dict[str, Any]], 
                           all_picks: List[DraftPick],
                           league_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive post-draft analysis and recommendations
        
        Args:
            final_roster: User's final drafted team
            all_picks: All picks made during draft
            league_settings: League configuration
            
        Returns:
            Complete draft analysis with grades and recommendations
        """
        
        analysis = {
            'overall_grade': self._grade_draft(final_roster, all_picks),
            'positional_grades': self._grade_by_position(final_roster),
            'best_picks': self._identify_best_picks(all_picks),
            'questionable_picks': self._identify_questionable_picks(all_picks),
            'roster_strengths': self._analyze_strengths(final_roster),
            'roster_weaknesses': self._analyze_weaknesses(final_roster),
            'immediate_trade_targets': self._suggest_trade_targets(final_roster),
            'waiver_wire_priorities': self._suggest_waiver_priorities(final_roster),
            'season_outlook': self._predict_season_outcome(final_roster, league_settings)
        }
        
        # Add AI-enhanced analysis if available
        if self.openai_key or self.openrouter_key:
            ai_enhanced = self._get_ai_post_draft_analysis(final_roster, all_picks, league_settings)
            analysis['expert_analysis'] = ai_enhanced
        
        return analysis
    
    def _determine_optimal_strategy(self, league_settings: Dict[str, Any], draft_position: int) -> str:
        """Determine best draft strategy for league settings and position"""
        
        scoring = league_settings.get('scoring_type', 'standard')
        roster_size = league_settings.get('roster_size', 16)
        
        # PPR leagues favor WR-heavy strategies
        if scoring in ['ppr', 'half_ppr']:
            if draft_position <= 4:
                return "hero_rb"  # Get elite RB early
            else:
                return "zero_rb"  # Wait on RB in PPR
        
        # Standard scoring favors RB
        else:
            if draft_position <= 6:
                return "robust_rb"  # RB early and often
            else:
                return "bpa"  # Take best value available
    
    def _create_round_plan(self, strategy: str, draft_pos: int, 
                          total_teams: int, league_settings: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
        """Create detailed round-by-round draft plan"""
        
        rounds_plan = {}
        
        for round_num in range(1, 16):  # Plan first 15 rounds
            pick_in_round = draft_pos if round_num % 2 == 1 else (total_teams - draft_pos + 1)
            overall_pick = (round_num - 1) * total_teams + pick_in_round
            
            round_info = {
                'round': round_num,
                'pick_in_round': pick_in_round,
                'overall_pick': overall_pick,
                'target_positions': self._get_round_targets(strategy, round_num),
                'strategy_notes': self._get_round_notes(strategy, round_num, draft_pos)
            }
            
            rounds_plan[round_num] = round_info
        
        return rounds_plan
    
    def _get_round_targets(self, strategy: str, round_num: int) -> List[str]:
        """Get target positions for specific round based on strategy"""
        
        strategy_targets = {
            "zero_rb": {
                1: ["WR"], 2: ["WR"], 3: ["WR", "TE"], 4: ["QB", "TE"],
                5: ["RB"], 6: ["RB"], 7: ["RB"], 8: ["WR"], 9: ["RB"]
            },
            "hero_rb": {
                1: ["RB"], 2: ["WR"], 3: ["WR"], 4: ["RB", "WR"],
                5: ["WR", "TE"], 6: ["QB"], 7: ["RB"], 8: ["WR"], 9: ["RB"]
            },
            "robust_rb": {
                1: ["RB"], 2: ["RB"], 3: ["RB", "WR"], 4: ["RB", "WR"],
                5: ["WR"], 6: ["WR", "TE"], 7: ["QB"], 8: ["WR"], 9: ["RB"]
            },
            "bpa": {
                1: ["RB", "WR"], 2: ["RB", "WR"], 3: ["RB", "WR"], 4: ["RB", "WR", "TE"],
                5: ["RB", "WR", "TE"], 6: ["QB", "WR", "TE"], 7: ["RB", "WR"], 8: ["RB", "WR"], 9: ["RB", "WR"]
            }
        }
        
        # Default late round targets
        if round_num >= 10:
            return ["RB", "WR", "QB", "TE", "K", "DEF"]
        
        return strategy_targets.get(strategy, {}).get(round_num, ["RB", "WR"])
    
    def _get_round_notes(self, strategy: str, round_num: int, draft_pos: int) -> str:
        """Get strategic notes for specific round"""
        
        notes = {
            1: f"Round 1 (Pick {draft_pos}): Set the foundation. In {strategy}, prioritize tier 1 players.",
            2: "Round 2: Complement Round 1 pick. Look for positional balance or double down on strength.",
            3: "Round 3: Address biggest need or take best available. Tier breaks matter here.",
            4: "Round 4: Last chance for premium players. Consider QB/TE if elite options available.",
            5: "Round 5: Value hunting begins. Target high-upside players with defined roles.",
            6: "Round 6: Depth and handcuffs. Shore up starting lineup weaknesses.",
            7: "Round 7: Lottery tickets and sleepers. Look for situation over talent sometimes.",
            8: "Round 8: Last starting lineup spots. Don't reach, trust your prep.",
            9: "Round 9: Bench depth begins. Target specific handcuffs and upside.",
            10: "Round 10+: Swing for the fences. Rookies, injury returns, situation changes."
        }
        
        return notes.get(round_num, f"Round {round_num}: Continue building depth and targeting upside.")
    
    def _generate_targets(self, league_settings: Dict[str, Any], strategy: str) -> List[Dict[str, Any]]:
        """Generate key target players based on strategy"""
        
        # This would be populated with current year player data
        # For now, using example structure
        
        targets = [
            {
                'name': 'Example Elite RB',
                'position': 'RB',
                'target_rounds': [1, 2],
                'reasoning': 'Tier 1 RB with massive workload and TD upside'
            },
            {
                'name': 'Example WR1',
                'position': 'WR', 
                'target_rounds': [2, 3],
                'reasoning': 'Target volume in high-powered offense'
            }
        ]
        
        return targets
    
    def _generate_avoid_list(self, league_settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate players to avoid based on expert analysis"""
        
        avoid_list = [
            {
                'name': 'Example Injury Risk',
                'position': 'RB',
                'reasoning': 'Extensive injury history, age concerns, heavy workload risk'
            }
        ]
        
        return avoid_list
    
    def _create_handcuff_strategy(self, strategy: str) -> Dict[str, Any]:
        """Create handcuff and lottery ticket strategy"""
        
        return {
            'handcuff_priority': 'HIGH' if strategy == 'robust_rb' else 'MEDIUM',
            'target_rounds': [8, 9, 10, 11],
            'approach': 'Target handcuffs of your RBs and elite RBs on other teams',
            'lottery_tickets': 'Focus on rookie WRs and RBs in good situations'
        }
    
    def _format_pick_context(self, draft_state: LiveDraftState, 
                           player: Dict[str, Any], 
                           league_settings: Dict[str, Any]) -> str:
        """Format draft context for AI analysis"""
        
        current_roster = [f"{p.get('name', 'Unknown')} ({p.get('position', 'POS')})" 
                         for p in draft_state.user_roster]
        
        return f"""
DRAFT SITUATION ANALYSIS:

Current Round: {draft_state.current_round}
Current Pick: {draft_state.current_pick}
Next Pick In: {draft_state.next_pick_in} picks

PLAYER UNDER CONSIDERATION:
Name: {player.get('name', 'Unknown')}
Position: {player.get('position', 'Unknown')}
Team: {player.get('team', 'Unknown')}
ADP: {player.get('adp', 'Unknown')}

CURRENT ROSTER:
{', '.join(current_roster) if current_roster else 'No players drafted yet'}

LEAGUE SETTINGS:
Scoring: {league_settings.get('scoring_type', 'Standard')}
Roster Size: {league_settings.get('roster_size', 16)}
Starting Lineup: {league_settings.get('starting_lineup', 'Standard')}

ANALYSIS REQUEST:
Should I draft this player now? Consider:
1. Value vs ADP 
2. Positional need
3. Tier breaks and future availability
4. Overall draft strategy fit
5. Championship upside

Provide grade (A+ to F) and detailed reasoning.
"""
    
    def _get_ai_pick_analysis(self, context: str) -> Dict[str, Any]:
        """Get AI analysis of draft pick"""
        
        try:
            if self.openai_key:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.expert_persona},
                        {"role": "user", "content": context}
                    ],
                    max_tokens=800,
                    temperature=0.8
                )
                
                ai_response = response.choices[0].message.content
                
            elif self.openrouter_key:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3-sonnet",
                        "messages": [
                            {"role": "system", "content": self.expert_persona},
                            {"role": "user", "content": context}
                        ],
                        "max_tokens": 800,
                        "temperature": 0.8
                    }
                )
                
                ai_response = response.json()['choices'][0]['message']['content']
            
            # Parse response for grade and recommendation
            grade = self._extract_grade(ai_response)
            recommendation = self._extract_recommendation(ai_response)
            
            return {
                'grade': grade,
                'analysis': ai_response,
                'recommendation': recommendation,
                'recommendation_strength': self._get_recommendation_strength(grade),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"AI analysis failed: {e}")
            return self._fallback_pick_analysis(None, {})
    
    def _fallback_pick_analysis(self, draft_state: Optional[LiveDraftState], 
                               player: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        
        return {
            'grade': 'B',
            'analysis': 'AI analysis not available. Consider value vs ADP and positional need.',
            'recommendation': 'CONSIDER',
            'recommendation_strength': 'MEDIUM',
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_grade(self, ai_response: str) -> str:
        """Extract grade from AI response"""
        grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F']
        
        for grade in grades:
            if grade in ai_response:
                return grade
        
        return 'B'  # Default grade
    
    def _extract_recommendation(self, ai_response: str) -> str:
        """Extract recommendation from AI response"""
        if any(word in ai_response.lower() for word in ['excellent', 'great pick', 'draft him', 'take him']):
            return 'STRONG_YES'
        elif any(word in ai_response.lower() for word in ['good pick', 'solid', 'recommend']):
            return 'YES'
        elif any(word in ai_response.lower() for word in ['consider', 'decent', 'okay']):
            return 'CONSIDER'
        elif any(word in ai_response.lower() for word in ['pass', 'avoid', 'wait']):
            return 'NO'
        else:
            return 'CONSIDER'
    
    def _get_recommendation_strength(self, grade: str) -> str:
        """Convert grade to recommendation strength"""
        if grade in ['A+', 'A']:
            return 'VERY_HIGH'
        elif grade in ['A-', 'B+']:
            return 'HIGH'  
        elif grade in ['B', 'B-']:
            return 'MEDIUM'
        elif grade in ['C+', 'C']:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def _assess_positional_needs(self, current_roster: List[Dict[str, Any]], 
                               league_settings: Dict[str, Any]) -> Dict[str, int]:
        """Assess positional needs based on current roster"""
        
        # Count current positions
        position_counts = {}
        for player in current_roster:
            pos = player.get('position', 'UNKNOWN')
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        # Standard roster requirements
        position_needs = {
            'QB': 2,    # 1 starter + 1 backup
            'RB': 4,    # 2-3 starters + handcuffs  
            'WR': 5,    # 2-3 starters + depth
            'TE': 2,    # 1 starter + 1 backup
            'K': 1,     # 1 starter
            'DEF': 1    # 1 starter
        }
        
        # Calculate remaining needs
        remaining_needs = {}
        for pos, need in position_needs.items():
            current = position_counts.get(pos, 0)
            remaining_needs[pos] = max(0, need - current)
        
        return remaining_needs
    
    def _rank_available_players(self, available_players: List[Dict[str, Any]], 
                              positional_needs: Dict[str, int],
                              current_round: int) -> List[Dict[str, Any]]:
        """Rank available players by draft value"""
        
        def player_value(player):
            # Simple ranking algorithm
            # In reality, would use sophisticated projections
            
            base_value = 100 - player.get('adp', 100)  # Lower ADP = higher value
            
            # Boost for positional need
            pos = player.get('position', 'UNKNOWN')
            need_boost = positional_needs.get(pos, 0) * 5
            
            # Penalty for late round QB/K/DEF if taken early
            if current_round <= 8 and pos in ['QB', 'K', 'DEF']:
                base_value -= 20
            
            return base_value + need_boost
        
        return sorted(available_players, key=player_value, reverse=True)
    
    def _grade_draft(self, final_roster: List[Dict[str, Any]], 
                    all_picks: List[DraftPick]) -> str:
        """Grade overall draft performance"""
        
        # Simplified grading based on value picks
        total_value = 0
        for pick in all_picks:
            grade_values = {'A+': 4.0, 'A': 3.7, 'A-': 3.3, 'B+': 3.0, 'B': 2.7, 
                          'B-': 2.3, 'C+': 2.0, 'C': 1.7, 'C-': 1.3, 'D': 1.0, 'F': 0.0}
            total_value += grade_values.get(pick.value_grade, 2.0)
        
        avg_value = total_value / len(all_picks) if all_picks else 2.0
        
        if avg_value >= 3.5:
            return 'A'
        elif avg_value >= 3.0:
            return 'B+'
        elif avg_value >= 2.5:
            return 'B'
        elif avg_value >= 2.0:
            return 'C+'
        else:
            return 'C'
    
    def _grade_by_position(self, final_roster: List[Dict[str, Any]]) -> Dict[str, str]:
        """Grade roster by position"""
        
        # Simplified positional grading
        position_grades = {}
        
        for pos in ['QB', 'RB', 'WR', 'TE']:
            players_at_pos = [p for p in final_roster if p.get('position') == pos]
            
            if not players_at_pos:
                position_grades[pos] = 'F'
            elif len(players_at_pos) == 1:
                position_grades[pos] = 'C'
            elif len(players_at_pos) >= 2:
                position_grades[pos] = 'B'
            else:
                position_grades[pos] = 'B+'
        
        return position_grades
    
    # Additional helper methods for post-draft analysis...
    def _identify_best_picks(self, all_picks: List[DraftPick]) -> List[DraftPick]:
        """Identify the best picks from the draft"""
        return [pick for pick in all_picks if pick.value_grade in ['A+', 'A', 'A-']]
    
    def _identify_questionable_picks(self, all_picks: List[DraftPick]) -> List[DraftPick]:
        """Identify questionable picks from the draft"""
        return [pick for pick in all_picks if pick.value_grade in ['D', 'F']]
    
    def _analyze_strengths(self, final_roster: List[Dict[str, Any]]) -> List[str]:
        """Analyze roster strengths"""
        return ["Example strength: Deep WR corps", "Strong RB handcuffs"]
    
    def _analyze_weaknesses(self, final_roster: List[Dict[str, Any]]) -> List[str]:
        """Analyze roster weaknesses"""
        return ["Example weakness: Lack of elite TE", "Questionable QB depth"]
    
    def _suggest_trade_targets(self, final_roster: List[Dict[str, Any]]) -> List[str]:
        """Suggest immediate trade targets"""
        return ["Target: Elite TE for depth WR", "Target: RB1 for WR package"]
    
    def _suggest_waiver_priorities(self, final_roster: List[Dict[str, Any]]) -> List[str]:
        """Suggest waiver wire priorities"""
        return ["Priority: Handcuff RBs", "Priority: High-upside WRs"]
    
    def _predict_season_outcome(self, final_roster: List[Dict[str, Any]], 
                              league_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Predict season outcome"""
        return {
            'playoff_probability': 75,
            'championship_probability': 15,
            'projected_record': '9-5',
            'key_factors': ['RB health', 'WR breakout potential', 'QB consistency']
        }
    
    def _get_ai_post_draft_analysis(self, final_roster: List[Dict[str, Any]],
                                  all_picks: List[DraftPick],
                                  league_settings: Dict[str, Any]) -> str:
        """Get comprehensive AI post-draft analysis"""
        
        roster_summary = ", ".join([f"{p.get('name', 'Unknown')} ({p.get('position', 'POS')})" 
                                   for p in final_roster])
        
        context = f"""
FINAL DRAFT ANALYSIS:

ROSTER: {roster_summary}

LEAGUE SETTINGS: {json.dumps(league_settings, indent=2)}

DRAFT PICKS: {len(all_picks)} total picks made

Provide a comprehensive post-draft analysis including:
1. Overall draft grade and reasoning
2. Biggest strengths and weaknesses
3. Best and worst picks
4. Championship potential (1-100)
5. Immediate action items (trades, waivers)
6. Season outlook and key factors for success

Use your 30 years of experience to provide championship-level insights.
"""
        
        try:
            if self.openai_key:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.expert_persona},
                        {"role": "user", "content": context}
                    ],
                    max_tokens=1500,
                    temperature=0.8
                )
                return response.choices[0].message.content
                
            elif self.openrouter_key:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3-sonnet",
                        "messages": [
                            {"role": "system", "content": self.expert_persona},
                            {"role": "user", "content": context}
                        ],
                        "max_tokens": 1500,
                        "temperature": 0.8
                    }
                )
                return response.json()['choices'][0]['message']['content']
                
        except Exception as e:
            logging.error(f"AI post-draft analysis failed: {e}")
            return "AI analysis not available. Review draft picks and assess positional balance."

# Example usage:
# expert = ExpertDraftAgent(openai_key="your_key")
# strategy = expert.create_draft_strategy(league_settings, draft_position=7, total_teams=12)
# recommendations = expert.get_draft_recommendations(draft_state, league_settings)