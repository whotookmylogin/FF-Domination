# Test ESPN-API Library
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    # Try to import the espn-api library
    from espn_api.football import League
    print("✓ ESPN-API library imported successfully")
    
    # Get ESPN credentials from environment
    espn_cookie = os.getenv("ESPN_COOKIE")
    if not espn_cookie:
        print("⚠ ESPN_COOKIE not found in environment variables")
        print("Please set ESPN_COOKIE in your .env file with your ESPN s2 cookie and SWID")
        exit(1)
    
    # Extract espn_s2 and SWID from the cookie
    # The cookie should be in the format: "espn_s2=...; SWID={...}"
    espn_s2 = None
    swid = None
    
    if "espn_s2=" in espn_cookie:
        # Extract espn_s2 value
        start = espn_cookie.find("espn_s2=") + len("espn_s2=")
        end = espn_cookie.find(";", start)
        if end == -1:  # If there's no semicolon after espn_s2, go to the end of string
            espn_s2 = espn_cookie[start:]
        else:
            espn_s2 = espn_cookie[start:end]
    
    if "SWID=" in espn_cookie:
        # Extract SWID value
        start = espn_cookie.find("SWID=") + len("SWID=")
        end = espn_cookie.find(";", start)
        if end == -1:  # If there's no semicolon after SWID, go to the end of string
            swid = espn_cookie[start:]
        else:
            swid = espn_cookie[start:end]
    
    if not espn_s2 or not swid:
        print("⚠ Could not extract espn_s2 and SWID from ESPN_COOKIE")
        print("Please ensure ESPN_COOKIE is in the format: espn_s2=...; SWID={...}")
        exit(1)
    
    print(f"✓ Extracted credentials: espn_s2 length={len(espn_s2)}, SWID={swid[:10]}...")
    
    # Test with your league ID (83806) and current year (2025)
    league_id = "83806"
    year = 2025
    
    print(f"\nTesting ESPN-API with league ID: {league_id}, year: {year}")
    
    # Try to create a League object
    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    
    print("✓ League object created successfully")
    
    # Test fetching league data
    print(f"\nLeague Size: {len(league.teams)} teams")
    
    # Show team names
    print("\nTeams:")
    for team in league.teams:
        print(f"  - {team.team_name} (ID: {team.team_id})")
    
    # Test fetching recent activity (transactions)
    print("\nRecent Activity (Transactions):")
    try:
        # Get recent activity
        activity = league.recent_activity()
        if activity:
            print(f"  Found {len(activity)} recent activities")
            # Show first few activities
            for i, act in enumerate(activity[:3]):
                print(f"  {i+1}. {act}")
        else:
            print("  No recent activity found")
    except Exception as e:
        print(f"  Could not fetch recent activity: {e}")
    
    # Test fetching box scores for current week
    print("\nCurrent Week Box Scores:")
    try:
        box_scores = league.box_scores()
        if box_scores:
            print(f"  Found {len(box_scores)} matchups")
            # Show first matchup
            if box_scores:
                first_matchup = box_scores[0]
                print(f"  First matchup: {first_matchup.home_team.team_name} vs {first_matchup.away_team.team_name}")
                print(f"  Score: {first_matchup.home_score} - {first_matchup.away_score}")
        else:
            print("  No box scores available")
    except Exception as e:
        print(f"  Could not fetch box scores: {e}")
    
    print("\n" + "=" * 50)
    print("ESPN-API Library Test Complete")
    print("=" * 50)
    
except ImportError as e:
    print("✗ ESPN-API library not installed or import failed")
    print(f"Error: {e}")
    print("Please install it with: pip install espn-api")
    
except Exception as e:
    print(f"✗ Error testing ESPN-API library: {e}")
    print("This might be due to invalid credentials, network issues, or ESPN API changes")
