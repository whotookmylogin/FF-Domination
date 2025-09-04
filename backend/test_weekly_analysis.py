#!/usr/bin/env python3
"""
Test script for weekly matchup analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.matchup.weekly_analyzer import WeeklyMatchupAnalyzer
import json

def test_weekly_analysis():
    """Test the weekly matchup analysis without full server"""
    print("Testing Weekly Matchup Analysis...")
    
    # Initialize analyzer without platform service (will use mock data)
    analyzer = WeeklyMatchupAnalyzer(platform_service=None)
    
    # Test analysis for league 83806, team 7
    result = analyzer.analyze_weekly_matchup(
        league_id="83806",
        team_id="7",
        week=1
    )
    
    # Print results
    if result.get("status") == "success":
        print("\n✅ Analysis successful!\n")
        matchup = result.get("matchup", {})
        
        # User team summary
        user_team = matchup.get("user_team", {})
        print(f"Your Team: {user_team.get('team_name', 'Unknown')}")
        print(f"Projected Total: {user_team.get('projected_total', 0):.1f} points")
        print(f"Strengths: {', '.join(user_team.get('strengths', []))}")
        
        # Opponent summary
        opponent = matchup.get("opponent_team", {})
        print(f"\nOpponent: {opponent.get('team_name', 'Unknown')}")
        print(f"Projected Total: {opponent.get('projected_total', 0):.1f} points")
        
        # Head to head
        h2h = matchup.get("head_to_head", {})
        print(f"\nProjected Difference: {h2h.get('projected_difference', 0):.1f} points")
        print(f"Overall Advantage: {h2h.get('overall_advantage', 'Unknown')}")
        
        # Recommendations
        recommendations = matchup.get("recommendations", [])
        if recommendations:
            print("\n📋 Recommendations:")
            for rec in recommendations[:3]:
                print(f"  • {rec}")
    else:
        print(f"\n❌ Analysis failed: {result.get('message', 'Unknown error')}")
    
    print("\n" + "="*50 + "\n")
    print("Full JSON output (first 1000 chars):")
    json_output = json.dumps(result, indent=2)
    print(json_output[:1000])

if __name__ == "__main__":
    test_weekly_analysis()