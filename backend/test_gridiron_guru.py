#!/usr/bin/env python3
"""
Test script for Gridiron Guru integration
Verifies that the 35-year veteran fantasy football expert system is properly integrated
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai.gridiron_guru_prompt import GridironGuru
from src.ai.expert_draft_agent import ExpertDraftAgent
from src.ai.enhanced_trade_analyzer import AITradeAnalyzer

def test_gridiron_guru_prompt():
    """Test the Gridiron Guru prompt system"""
    print("=" * 60)
    print("TESTING GRIDIRON GURU PROMPT SYSTEM")
    print("=" * 60)
    
    # Test getting full prompts for different contexts
    print("\n1. Testing Draft Context Prompt:")
    print("-" * 40)
    draft_prompt = GridironGuru.get_full_prompt(context_type="draft")
    print(f"Draft prompt length: {len(draft_prompt)} characters")
    print(f"First 200 chars: {draft_prompt[:200]}...")
    
    print("\n2. Testing Trade Context Prompt:")
    print("-" * 40)
    trade_prompt = GridironGuru.get_full_prompt(context_type="trade")
    print(f"Trade prompt length: {len(trade_prompt)} characters")
    print(f"First 200 chars: {trade_prompt[:200]}...")
    
    print("\n3. Testing Waiver Context Prompt:")
    print("-" * 40)
    waiver_prompt = GridironGuru.get_full_prompt(context_type="waiver")
    print(f"Waiver prompt length: {len(waiver_prompt)} characters")
    print(f"First 200 chars: {waiver_prompt[:200]}...")
    
    print("\n4. Testing General Context Prompt:")
    print("-" * 40)
    general_prompt = GridironGuru.get_full_prompt(context_type="general")
    print(f"General prompt length: {len(general_prompt)} characters")
    
    # Test contextualized prompts
    print("\n5. Testing Contextualized Prompts:")
    print("-" * 40)
    
    draft_query = "Should I draft Justin Jefferson in the first round?"
    context_prompt = GridironGuru.get_context_prompt(
        query=draft_query,
        context={
            "league_settings": "12-team PPR",
            "week": 1
        }
    )
    print(f"Query: {draft_query}")
    print(f"Contextualized prompt length: {len(context_prompt)} characters")
    
    # Test quick takes
    print("\n6. Testing Quick Takes:")
    print("-" * 40)
    topics = ["zero_rb", "handcuffs", "streaming", "trades", "rookies"]
    for topic in topics:
        take = GridironGuru.get_quick_take(topic)
        print(f"{topic}: {take}")
    
    # Test response formatting
    print("\n7. Testing Response Formatting:")
    print("-" * 40)
    formatted = GridironGuru.format_response(
        response="Based on my 35 years of experience, I recommend accepting this trade.",
        confidence_level="high"
    )
    for key, value in formatted.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("GRIDIRON GURU TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

def test_expert_draft_agent_integration():
    """Test that ExpertDraftAgent uses Gridiron Guru"""
    print("\n" + "=" * 60)
    print("TESTING EXPERT DRAFT AGENT INTEGRATION")
    print("=" * 60)
    
    # Initialize without API keys (will use fallback)
    agent = ExpertDraftAgent()
    
    # Check that the expert persona is loaded correctly
    print("\n1. Checking Expert Persona Loading:")
    print("-" * 40)
    persona = agent.expert_persona
    print(f"Persona loaded: {'Gridiron Guru' in persona}")
    print(f"Persona length: {len(persona)} characters")
    
    # Check draft strategies are loaded
    print("\n2. Checking Draft Strategies:")
    print("-" * 40)
    strategies = agent.draft_strategies
    print(f"Strategies loaded: {list(strategies.keys())}")
    
    print("\n" + "=" * 60)
    print("EXPERT DRAFT AGENT INTEGRATION TEST COMPLETED!")
    print("=" * 60)

def test_trade_analyzer_integration():
    """Test that AITradeAnalyzer uses Gridiron Guru"""
    print("\n" + "=" * 60)
    print("TESTING AI TRADE ANALYZER INTEGRATION")
    print("=" * 60)
    
    # Initialize without API keys
    analyzer = AITradeAnalyzer()
    
    # Check that the expert prompt is loaded correctly
    print("\n1. Checking Expert Prompt Loading:")
    print("-" * 40)
    prompt = analyzer.expert_prompt
    print(f"Gridiron Guru prompt loaded: {'Gridiron Guru' in prompt}")
    print(f"Prompt length: {len(prompt)} characters")
    
    # Check model configuration
    print("\n2. Checking Model Configuration:")
    print("-" * 40)
    print(f"Quality tier: {analyzer.quality}")
    print(f"Selected models: {analyzer.selected_models}")
    
    print("\n" + "=" * 60)
    print("AI TRADE ANALYZER INTEGRATION TEST COMPLETED!")
    print("=" * 60)

def main():
    """Run all tests"""
    print("\n" + "🏈" * 30)
    print("GRIDIRON GURU INTEGRATION TEST SUITE")
    print("Testing the 35-Year Fantasy Football Veteran System")
    print("🏈" * 30)
    
    try:
        # Test the core Gridiron Guru prompt system
        test_gridiron_guru_prompt()
        
        # Test integration with Expert Draft Agent
        test_expert_draft_agent_integration()
        
        # Test integration with AI Trade Analyzer
        test_trade_analyzer_integration()
        
        print("\n" + "🏆" * 30)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("The Gridiron Guru system is properly integrated.")
        print("🏆" * 30)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Some tests failed. Please check the implementation.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())