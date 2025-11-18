#!/usr/bin/env python3
"""Test the AI Trade Engine"""

import os
import sys
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Check if OpenAI key is set
openai_key = os.getenv("OPENAI_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

if not openai_key or openai_key == "your-openai-api-key":
    print("❌ OpenAI API key not configured!")
    print("\nTo use the AI trade engine, you need to:")
    print("1. Edit the file: backend/.env")
    print("2. Replace 'your-openai-api-key' with your actual OpenAI API key")
    print("3. Save the file and restart the backend")
    sys.exit(1)

print(f"✅ OpenAI API key found: {openai_key[:20]}...")
if openrouter_key:
    print(f"✅ OpenRouter API key found: {openrouter_key[:20]}...")

# Now test the trade engine
from src.platforms.service import PlatformIntegrationService
from src.ai.enhanced_trade_analyzer import AITradeAnalyzer

# Initialize services
espn_s2 = os.getenv("ESPN_S2")
espn_swid = os.getenv("ESPN_SWID")

print("\n🏈 Initializing Fantasy Football Trade Engine...")
print(f"League: Sir Biffington's Revenge (ID: 83806)")
print(f"Your Team: Trashy McTrash-Face (ID: 7)")

# Initialize platform service
platform_service = PlatformIntegrationService(espn_s2=espn_s2, espn_swid=espn_swid)

# Initialize AI trade analyzer with both keys
trade_analyzer = AITradeAnalyzer(openai_key=openai_key, openrouter_key=openrouter_key)

print("\n🤖 AI Trade Analyzer initialized!")
print("Analyzing all possible trades in your league...")
print("This may take a moment as the AI evaluates each potential trade...\n")

try:
    # Analyze trades for your league
    trade_opportunities = trade_analyzer.analyze_all_league_trades("83806", platform_service)
    
    if trade_opportunities:
        print(f"✅ Found {len(trade_opportunities)} potential trades!\n")
        
        # Show top 3 trades
        print("🔥 TOP 3 TRADE OPPORTUNITIES FOR YOUR TEAM:\n")
        print("=" * 60)
        
        your_trades = [t for t in trade_opportunities if str(t.team_a_id) == "7" or str(t.team_b_id) == "7"]
        
        if your_trades:
            for i, trade in enumerate(your_trades[:3], 1):
                print(f"\n📊 TRADE #{i}")
                print("-" * 40)
                
                if str(trade.team_a_id) == "7":
                    # Format player names properly
                    gives = [f"{p.get('name', 'Unknown')} ({p.get('position', 'POS')})" if isinstance(p, dict) else str(p) for p in trade.team_a_gives]
                    gets = [f"{p.get('name', 'Unknown')} ({p.get('position', 'POS')})" if isinstance(p, dict) else str(p) for p in trade.team_a_gets]
                    
                    print(f"You Give: {', '.join(gives)}")
                    print(f"You Get:  {', '.join(gets)}")
                    print(f"Trade Partner: Team {trade.team_b_id}")
                    print(f"Your Improvement: {trade.team_a_improvement:.1f}%")
                else:
                    gives = [f"{p.get('name', 'Unknown')} ({p.get('position', 'POS')})" if isinstance(p, dict) else str(p) for p in trade.team_b_gives]
                    gets = [f"{p.get('name', 'Unknown')} ({p.get('position', 'POS')})" if isinstance(p, dict) else str(p) for p in trade.team_b_gets]
                    
                    print(f"You Give: {', '.join(gives)}")
                    print(f"You Get:  {', '.join(gets)}")
                    print(f"Trade Partner: Team {trade.team_a_id}")
                    print(f"Your Improvement: {trade.team_b_improvement:.1f}%")
                
                print(f"Fairness Score: {trade.fairness_score:.0f}/100")
                print(f"Confidence: {trade.confidence_score:.1f}/1.0")
                print(f"Urgency: {trade.urgency}")
                
                if trade.ai_analysis:
                    print(f"\n🤖 AI Analysis:\n{trade.ai_analysis[:300]}...")
        else:
            print("No trades found specifically for your team.")
            print("\nShowing general league trades:")
            for i, trade in enumerate(trade_opportunities[:2], 1):
                print(f"\nTrade {i}: Team {trade.team_a_id} ↔️ Team {trade.team_b_id}")
                print(f"  Fairness: {trade.fairness_score:.0f}/100")
                if trade.ai_analysis:
                    print(f"  Analysis: {trade.ai_analysis[:100]}...")
    else:
        print("❌ No viable trade opportunities found.")
        print("This could mean:")
        print("  - The AI couldn't connect to analyze trades")
        print("  - No beneficial trades exist currently")
        print("  - The OpenAI API key might not be working")
        
except Exception as e:
    print(f"❌ Error analyzing trades: {e}")
    import traceback
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("1. Make sure your OpenAI API key is valid")
    print("2. Check that you have API credits remaining")
    print("3. Ensure the backend is running")