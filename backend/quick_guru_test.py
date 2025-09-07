#!/usr/bin/env python3
"""
Quick interactive test of the Gridiron Guru system
Run this to see the Guru in action!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai.gridiron_guru_prompt import GridironGuru
from src.ai.expert_draft_agent import ExpertDraftAgent
from src.ai.enhanced_trade_analyzer import AITradeAnalyzer

def test_guru_quick_takes():
    """Test quick takes on various topics"""
    print("\n" + "="*60)
    print("GRIDIRON GURU QUICK TAKES")
    print("="*60)
    
    topics = {
        "zero_rb": "Zero RB Strategy",
        "handcuffs": "Handcuff Strategy", 
        "streaming": "Streaming Strategy",
        "trades": "Trade Timing",
        "rookies": "Rookie Evaluation",
        "dynasty": "Dynasty Strategy",
        "injuries": "Injury Management"
    }
    
    for key, title in topics.items():
        print(f"\n📌 {title}:")
        print(GridironGuru.get_quick_take(key))

def test_guru_draft_advice():
    """Test draft advice"""
    print("\n" + "="*60)
    print("GRIDIRON GURU DRAFT ADVICE")
    print("="*60)
    
    questions = [
        "Should I draft a RB or WR with the 5th pick in PPR?",
        "Is it worth reaching for an elite TE in round 2?",
        "When should I draft a QB in superflex?",
        "Should I handcuff my first round RB?"
    ]
    
    for q in questions:
        print(f"\n❓ Question: {q}")
        prompt = GridironGuru.get_context_prompt(
            query=q,
            context={"league_settings": "12-team PPR"}
        )
        # Show just the question part and first bit of response setup
        print("🏈 Guru Analysis Context Created:")
        print(f"   - Prompt length: {len(prompt)} characters")
        print(f"   - Context type: Draft analysis")
        print(f"   - Confidence: Based on 35 years of experience")

def test_guru_trade_evaluation():
    """Test trade evaluation"""
    print("\n" + "="*60)
    print("GRIDIRON GURU TRADE EVALUATION")
    print("="*60)
    
    trade_scenarios = [
        {
            "give": "Justin Jefferson",
            "get": "Bijan Robinson + Mike Evans",
            "context": "I'm weak at RB in PPR"
        },
        {
            "give": "Josh Allen",
            "get": "Lamar Jackson + Rachaad White",
            "context": "Superflex league, need RB depth"
        },
        {
            "give": "Travis Kelce + James Conner",
            "get": "Sam LaPorta + Breece Hall",
            "context": "Dynasty league"
        }
    ]
    
    for trade in trade_scenarios:
        print(f"\n💱 Trade Scenario:")
        print(f"   Give: {trade['give']}")
        print(f"   Get: {trade['get']}")
        print(f"   Context: {trade['context']}")
        
        query = f"Should I trade {trade['give']} for {trade['get']}? {trade['context']}"
        prompt = GridironGuru.get_context_prompt(
            query=query,
            context={"analysis_type": "trade"}
        )
        print(f"🏈 Guru Analysis Prepared ({len(prompt)} chars)")

def test_agent_integration():
    """Test that agents are using Gridiron Guru"""
    print("\n" + "="*60)
    print("TESTING AGENT INTEGRATION")
    print("="*60)
    
    # Test Draft Agent
    print("\n1. Expert Draft Agent:")
    agent = ExpertDraftAgent()
    print(f"   ✅ Persona loaded: {'Gridiron Guru' in agent.expert_persona}")
    print(f"   ✅ Strategies available: {list(agent.draft_strategies.keys())}")
    
    # Test Trade Analyzer
    print("\n2. AI Trade Analyzer:")
    analyzer = AITradeAnalyzer()
    print(f"   ✅ Guru prompt loaded: {'Gridiron Guru' in analyzer.expert_prompt}")
    print(f"   ✅ Quality tier: {analyzer.quality}")
    print(f"   ✅ Models configured: {analyzer.selected_models}")

def interactive_mode():
    """Interactive mode to ask the Guru questions"""
    print("\n" + "="*60)
    print("INTERACTIVE MODE - Ask the Gridiron Guru!")
    print("Type 'quit' to exit")
    print("="*60)
    
    while True:
        print("\n" + "-"*40)
        question = input("Your fantasy football question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Thanks for consulting the Gridiron Guru!")
            break
            
        if not question:
            continue
            
        # Determine context type
        if any(word in question.lower() for word in ['draft', 'pick', 'round']):
            context_type = "draft"
        elif any(word in question.lower() for word in ['trade', 'offer', 'give', 'get']):
            context_type = "trade"
        elif any(word in question.lower() for word in ['waiver', 'pickup', 'add', 'drop']):
            context_type = "waiver"
        else:
            context_type = "general"
        
        print(f"\n🏈 Gridiron Guru Analysis (Context: {context_type})")
        print("-"*40)
        
        # Create the prompt
        prompt = GridironGuru.get_context_prompt(
            query=question,
            context={"analysis_type": context_type}
        )
        
        print(f"Analysis prepared with {len(prompt)} characters of expertise.")
        print("(To see actual AI responses, you'd need to connect an AI API)")
        
        # Show what type of analysis would be done
        print(f"\nThe Guru would analyze this as a {context_type} question")
        print("Drawing from 35 years of fantasy football experience including:")
        
        if context_type == "draft":
            print("  • Draft strategy and positional value")
            print("  • ADP analysis and tier breaks")
            print("  • Format-specific adjustments")
        elif context_type == "trade":
            print("  • Trade fairness and value exchange")
            print("  • Team context and needs")
            print("  • Buy-low/sell-high timing")
        elif context_type == "waiver":
            print("  • FAAB bidding strategy")
            print("  • Pickup priority and timing")
            print("  • Drop candidate evaluation")
        else:
            print("  • All areas of fantasy expertise")
            print("  • Historical patterns and trends")
            print("  • Championship-winning strategies")

def main():
    """Run all tests"""
    print("\n" + "🏈"*30)
    print("GRIDIRON GURU TEST SUITE")
    print("Testing the 35-Year Fantasy Football Veteran System")
    print("🏈"*30)
    
    while True:
        print("\n" + "="*60)
        print("SELECT A TEST:")
        print("="*60)
        print("1. Quick Takes - See instant expert opinions")
        print("2. Draft Advice - Test draft questions")
        print("3. Trade Evaluation - Test trade scenarios")
        print("4. Agent Integration - Verify system integration")
        print("5. Interactive Mode - Ask your own questions")
        print("6. Run All Tests")
        print("0. Exit")
        print("-"*60)
        
        choice = input("Enter your choice (0-6): ").strip()
        
        if choice == "0":
            print("\n🏆 Thanks for testing the Gridiron Guru!")
            break
        elif choice == "1":
            test_guru_quick_takes()
        elif choice == "2":
            test_guru_draft_advice()
        elif choice == "3":
            test_guru_trade_evaluation()
        elif choice == "4":
            test_agent_integration()
        elif choice == "5":
            interactive_mode()
        elif choice == "6":
            test_guru_quick_takes()
            test_guru_draft_advice()
            test_guru_trade_evaluation()
            test_agent_integration()
            print("\n🏆 All tests completed!")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()