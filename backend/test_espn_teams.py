#!/usr/bin/env python3
"""Test script to check available teams in ESPN league"""

import os
import sys
from dotenv import load_dotenv

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

from platforms.espn_api_integration import ESPNAPIIntegration

# Get ESPN credentials
espn_s2 = os.getenv("ESPN_S2")
espn_swid = os.getenv("ESPN_SWID")
league_id = os.getenv("ESPN_LEAGUE_ID", "83806")
year = int(os.getenv("ESPN_SEASON_YEAR", "2025"))

print(f"Testing ESPN API with league_id={league_id}, year={year}")
print(f"ESPN_S2 available: {bool(espn_s2)}")
print(f"ESPN_SWID available: {bool(espn_swid)}")

# Initialize ESPN API
espn_api = ESPNAPIIntegration(league_id, year, espn_s2, espn_swid)

if espn_api.connect():
    print(f"\nConnection successful! Mock mode: {espn_api.use_mock_data}")
    
    if not espn_api.use_mock_data and espn_api.league:
        print(f"\nLeague Name: {espn_api.league.name if hasattr(espn_api.league, 'name') else 'Unknown'}")
        print(f"Number of teams: {len(espn_api.league.teams)}")
        print("\nAvailable teams:")
        for team in espn_api.league.teams:
            print(f"  - Team ID: {team.team_id}, Name: {team.team_name}, Owner: {getattr(team, 'owner', 'Unknown')}")
    else:
        print("\nUsing mock data mode - no real teams available")
        print("To use real data, please set ESPN_S2 and ESPN_SWID environment variables")
else:
    print("Failed to connect to ESPN API")