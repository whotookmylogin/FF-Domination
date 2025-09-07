#!/usr/bin/env python3
"""
Test Gridiron Guru with actual API calls
Requires OPENAI_API_KEY or OPENROUTER_API_KEY environment variable
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai.expert_draft_agent import ExpertDraftAgent, DraftPick, LiveDraftState
from src.ai.enhanced_trade_analyzer import AITradeAnalyzer, TradeOpportunity

def test_with_openai():
    """Test using OpenAI API"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    print("\n🤖 Testing with OpenAI API...")
    
    # Test Draft Agent
    agent = ExpertDraftAgent(openai_key=api_key)
    
    # Create a mock draft state
    draft_state = LiveDraftState(
        current_round=2,
        current_pick=5,
        picks_made=[],
        available_players=[
            {"name": "Tyreek Hill", "position": "WR", "adp": 5.2},
            {"name": "Amon-Ra St. Brown", "position": "WR", "adp": 8.1},
            {"name": "Travis Etienne", "position": "RB", "adp": 15.3}
        ],
        user_roster=[
            {"name": "Christian McCaffrey", "position": "RB"}
        ],
        next_pick_in=14
    )
    
    player = {"name": "Tyreek Hill", "position": "WR", "adp": 5.2, "team": "MIA"}
    league_settings = {"scoring_type": "ppr", "roster_size": 16}
    
    print("\nAsking Gridiron Guru about drafting Tyreek Hill in round 2...")
    analysis = agent.analyze_draft_pick(draft_state, player, league_settings)
    
    print("\n🏈 GRIDIRON GURU SAYS:")
    print("-" * 40)
    print(f"Grade: {analysis.get('grade', 'N/A')}")
    print(f"Recommendation: {analysis.get('recommendation', 'N/A')}")
    print(f"\nAnalysis:\n{analysis.get('analysis', 'No analysis available')}")

def test_with_openrouter():
    """Test using OpenRouter API"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        print("Set it with: export OPENROUTER_API_KEY='your-key-here'")
        return
    
    print("\n🤖 Testing with OpenRouter API...")
    
    # Test Trade Analyzer
    analyzer = AITradeAnalyzer(openrouter_key=api_key)
    
    # Create a mock trade
    trade = TradeOpportunity(
        team_a_id="team1",
        team_b_id="team2",
        team_a_name="Your Team",
        team_b_name="Opponent",
        team_a_gives=[{"name": "Justin Jefferson", "position": "WR"}],
        team_a_gets=[{"name": "Bijan Robinson", "position": "RB"}, 
                     {"name": "Mike Evans", "position": "WR"}],
        team_b_gives=[{"name": "Bijan Robinson", "position": "RB"},
                      {"name": "Mike Evans", "position": "WR"}],
        team_b_gets=[{"name": "Justin Jefferson", "position": "WR"}],
        fairness_score=0,
        team_a_improvement=0,
        team_b_improvement=0,
        ai_analysis="",
        confidence_score=0,
        urgency="MEDIUM",
        bye_week_impact={},
        matchup_advantage={},
        timing_recommendation=""
    )
    
    print("\nAsking Gridiron Guru about trading Jefferson for Bijan + Evans...")
    
    # This would normally be called internally, but we can simulate
    trade_context = f"""
    Trade Analysis Request:
    Team A gives: Justin Jefferson (WR)
    Team A gets: Bijan Robinson (RB) + Mike Evans (WR)
    
    League: 12-team PPR
    Team A needs RB help and has WR depth.
    
    Should Team A accept this trade?
    """
    
    result = analyzer._query_openrouter(trade_context)
    
    if result:
        print("\n🏈 GRIDIRON GURU SAYS:")
        print("-" * 40)
        print(f"Fairness Score: {result.get('fairness_score', 'N/A')}/100")
        print(f"Urgency: {result.get('urgency', 'N/A')}")
        print(f"\nAnalysis:\n{result.get('analysis', 'No analysis available')}")

def main():
    print("🏈" * 30)
    print("GRIDIRON GURU API TEST")
    print("Test with real AI responses")
    print("🏈" * 30)
    
    # Check for API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))
    
    if not has_openai and not has_openrouter:
        print("\n⚠️  No API keys found!")
        print("\nTo test with real AI responses, set one of these:")
        print("  export OPENAI_API_KEY='your-openai-key'")
        print("  export OPENROUTER_API_KEY='your-openrouter-key'")
        print("\nGet keys from:")
        print("  OpenAI: https://platform.openai.com/api-keys")
        print("  OpenRouter: https://openrouter.ai/keys")
        return
    
    if has_openai:
        test_with_openai()
    
    if has_openrouter:
        test_with_openrouter()
    
    print("\n🏆 API tests completed!")

if __name__ == "__main__":
    main()