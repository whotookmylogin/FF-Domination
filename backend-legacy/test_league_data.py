#!/usr/bin/env python3
import requests
import json

# Test the league endpoint
response = requests.get("http://localhost:8000/user/league/83806")
data = response.json()

print("=== ESPN LEAGUE DATA TEST ===\n")
print(f"Status: {data.get('status')}")

if data.get('status') == 'success':
    league_data = data.get('data', {})
    
    # Check settings
    settings = league_data.get('settings', {})
    print(f"\nLeague Settings:")
    print(f"  Name: {settings.get('name', 'Not found')}")
    print(f"  Season: {settings.get('season_id', 'Not found')}")
    print(f"  Current Week: {settings.get('current_week', 'Not found')}")
    
    # Check teams
    teams = league_data.get('teams', [])
    print(f"\nTeams: {len(teams)} found")
    
    if teams and len(teams) > 0:
        print("\nFirst 3 teams:")
        for i, team in enumerate(teams[:3]):
            print(f"\nTeam {i+1}:")
            print(f"  Structure: {list(team.keys())[:5]}...")
            # Try different possible name fields
            name = team.get('name') or team.get('team_name') or team.get('location', '') + ' ' + team.get('nickname', '') or 'Unknown'
            print(f"  Name: {name}")
            print(f"  ID: {team.get('id', team.get('team_id', 'Unknown'))}")
            
else:
    print(f"Error: {data.get('message', 'Unknown error')}")