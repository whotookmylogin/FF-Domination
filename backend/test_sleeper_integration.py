#\!/usr/bin/env python3
"""Test Sleeper integration with user wtml"""

import asyncio
import aiohttp
import json
from datetime import datetime

SLEEPER_BASE_URL = "https://api.sleeper.app/v1"

async def test_sleeper_user(username):
    """Test fetching Sleeper user data"""
    async with aiohttp.ClientSession() as session:
        # Get user info
        async with session.get(f"{SLEEPER_BASE_URL}/user/{username}") as resp:
            if resp.status == 200:
                user_data = await resp.json()
                print(f"\n✅ Found Sleeper user: {user_data.get('display_name', username)}")
                print(f"   User ID: {user_data.get('user_id')}")
                print(f"   Avatar: {user_data.get('avatar', 'No avatar')}")
                return user_data.get('user_id')
            else:
                print(f"❌ Could not find user {username}")
                return None

async def test_sleeper_leagues(user_id, sport='nfl', season='2025'):
    """Test fetching user's Sleeper leagues"""
    async with aiohttp.ClientSession() as session:
        # Get user's leagues for the season
        async with session.get(f"{SLEEPER_BASE_URL}/user/{user_id}/leagues/{sport}/{season}") as resp:
            if resp.status == 200:
                leagues = await resp.json()
                print(f"\n📋 Found {len(leagues)} leagues for {season} season:")
                
                for league in leagues[:5]:  # Show first 5 leagues
                    print(f"\n   League: {league.get('name')}")
                    print(f"   League ID: {league.get('league_id')}")
                    print(f"   Total Teams: {league.get('total_rosters')}")
                    print(f"   Status: {league.get('status')}")
                    print(f"   Scoring: {league.get('scoring_settings', {}).get('rec', 'N/A')} PPR")
                
                if leagues:
                    return leagues[0].get('league_id')  # Return first league for testing
                return None
            else:
                print(f"❌ Could not fetch leagues")
                return None

async def test_sleeper_roster(user_id, league_id):
    """Test fetching user's roster in a specific league"""
    async with aiohttp.ClientSession() as session:
        # Get all rosters in the league
        async with session.get(f"{SLEEPER_BASE_URL}/league/{league_id}/rosters") as resp:
            if resp.status == 200:
                rosters = await resp.json()
                
                # Find user's roster
                user_roster = None
                for roster in rosters:
                    if roster.get('owner_id') == user_id:
                        user_roster = roster
                        break
                
                if user_roster:
                    print(f"\n🏈 Your roster in this league:")
                    print(f"   Roster ID: {user_roster.get('roster_id')}")
                    print(f"   Wins: {user_roster.get('settings', {}).get('wins', 0)}")
                    print(f"   Losses: {user_roster.get('settings', {}).get('losses', 0)}")
                    print(f"   Points For: {user_roster.get('settings', {}).get('fpts', 0)}")
                    
                    # Get players
                    players = user_roster.get('players', [])
                    if players:
                        print(f"   Players on roster: {len(players)}")
                        print(f"   Sample players: {players[:5]}")
                    
                    return user_roster
                else:
                    print("❌ Could not find your roster in this league")
                    return None
            else:
                print(f"❌ Could not fetch rosters")
                return None

async def test_sleeper_players():
    """Test fetching NFL players database"""
    async with aiohttp.ClientSession() as session:
        # This endpoint returns all NFL players
        print("\n📥 Testing player database access...")
        async with session.get(f"{SLEEPER_BASE_URL}/players/nfl") as resp:
            if resp.status == 200:
                players = await resp.json()
                print(f"✅ Successfully accessed player database")
                print(f"   Total players in database: {len(players)}")
                
                # Show a sample player
                sample_player_id = list(players.keys())[0]
                sample_player = players[sample_player_id]
                print(f"\n   Sample player data:")
                print(f"   Name: {sample_player.get('first_name')} {sample_player.get('last_name')}")
                print(f"   Position: {sample_player.get('position')}")
                print(f"   Team: {sample_player.get('team')}")
                return True
            else:
                print(f"❌ Could not fetch player database")
                return False

async def main():
    """Run all Sleeper integration tests"""
    print("="*60)
    print("🏈 SLEEPER INTEGRATION TEST - User: wtml")
    print("="*60)
    
    # Test 1: Get user info
    user_id = await test_sleeper_user("wtml")
    
    if user_id:
        # Test 2: Get user's leagues
        league_id = await test_sleeper_leagues(user_id)
        
        if league_id:
            # Test 3: Get user's roster in first league
            await test_sleeper_roster(user_id, league_id)
    
    # Test 4: Test player database access
    await test_sleeper_players()
    
    print("\n" + "="*60)
    print("✅ Sleeper integration test complete!")
    print("="*60)
    
    if user_id:
        print(f"\n📝 To complete integration, add to .env:")
        print(f"   SLEEPER_USERNAME=wtml")
        print(f"   SLEEPER_USER_ID={user_id}")

if __name__ == "__main__":
    asyncio.run(main())
