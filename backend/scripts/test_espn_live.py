#!/usr/bin/env python3
"""
Live test script for ESPN API client.

Tests ESPN API endpoints which are more accessible than NBA stats API.
"""

import asyncio
import logging
import sys
import os
from datetime import date, datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.api.clients.espn_api import ESPNAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_espn_api():
    """Test ESPN API client with live data."""
    print("🏀 Testing ESPN API Client...")
    print("=" * 50)
    
    async with ESPNAPI(rate_limit=100) as espn_api:  # ESPN is more permissive
        try:
            # Test 1: Get NBA Teams
            print("\n1. Testing get_teams() for NBA...")
            teams = await espn_api.get_teams('basketball')
            print(f"✅ Retrieved {len(teams)} NBA teams")
            
            if teams:
                first_team = teams[0]
                print(f"   Sample team: {first_team.name} ({first_team.short_name})")
                print(f"   City: {first_team.city}")
                print(f"   Logo URL: {first_team.logo_url}")
                print(f"   Venue: {first_team.venue}")
                
                # Test 2: Get Specific Team
                print(f"\n2. Testing get_team() for {first_team.name}...")
                try:
                    team_detail = await espn_api.get_team(first_team.id)
                    print(f"✅ Retrieved team details: {team_detail.name}")
                    print(f"   Colors: {team_detail.primary_color}")
                except Exception as e:
                    print(f"⚠️  Team details error: {e}")
                
                # Test 3: Get Players for Team
                print(f"\n3. Testing get_players() for {first_team.name}...")
                try:
                    players = await espn_api.get_players(first_team.id)
                    print(f"✅ Retrieved {len(players)} players")
                    
                    if players:
                        sample_player = players[0]
                        print(f"   Sample player: {sample_player.first_name} {sample_player.last_name}")
                        print(f"   Position: {sample_player.position}, Jersey: {sample_player.jersey_number}")
                        
                        # Test 4: Get Player Details
                        print(f"\n4. Testing get_player() for {sample_player.first_name} {sample_player.last_name}...")
                        try:
                            player_detail = await espn_api.get_player(sample_player.id)
                            print(f"✅ Retrieved player details: {player_detail.first_name} {player_detail.last_name}")
                            print(f"   Height: {player_detail.height}, Weight: {player_detail.weight}")
                        except Exception as e:
                            print(f"⚠️  Player details error: {e}")
                
                except Exception as e:
                    print(f"⚠️  Players error: {e}")
            
            # Test 5: Get Recent Games
            print(f"\n5. Testing get_games() for recent games...")
            try:
                games = await espn_api.get_games()
                print(f"✅ Retrieved {len(games)} recent games")
                
                if games:
                    sample_game = games[0]
                    print(f"   Sample game: {sample_game.id}")
                    print(f"   Teams: {sample_game.home_team_id} vs {sample_game.away_team_id}")
                    print(f"   Status: {sample_game.status}")
                    print(f"   Scores: {sample_game.home_score} - {sample_game.away_score}")
                    print(f"   Venue: {sample_game.venue}")
                    
                    # Test 6: Get Game Details
                    print(f"\n6. Testing get_game() for sample game...")
                    try:
                        game_detail = await espn_api.get_game(sample_game.id)
                        print(f"✅ Retrieved game details")
                        print(f"   Date: {game_detail.scheduled_at}")
                        print(f"   Attendance: {game_detail.attendance}")
                    except Exception as e:
                        print(f"⚠️  Game details error: {e}")
                
            except Exception as e:
                print(f"⚠️  Games error: {e}")
            
            # Test 7: Get Games with Date Filter
            print(f"\n7. Testing get_games() with date filter...")
            try:
                today = date.today()
                games = await espn_api.get_games(start_date=today)
                print(f"✅ Retrieved {len(games)} games for today")
                
            except Exception as e:
                print(f"⚠️  Date filtered games error: {e}")
            
        except Exception as e:
            print(f"❌ Major error: {e}")
            logger.exception("Detailed error information:")
    
    print("\n" + "=" * 50)
    print("🏀 ESPN API Test Complete!")


async def test_multiple_sports():
    """Test ESPN API with multiple sports."""
    print("\n🏈 Testing Multiple Sports...")
    
    sports = ['basketball', 'football']  # NBA and NFL
    
    async with ESPNAPI() as espn_api:
        for sport in sports:
            try:
                print(f"\n   Testing {sport.upper()}...")
                teams = await espn_api.get_teams(sport)
                print(f"   ✅ Retrieved {len(teams)} {sport} teams")
                
                if teams:
                    sample_team = teams[0]
                    print(f"      Sample: {sample_team.name}")
                
            except Exception as e:
                print(f"   ⚠️  {sport} error: {e}")


if __name__ == "__main__":
    try:
        # Run main ESPN API test
        asyncio.run(test_espn_api())
        
        # Test multiple sports
        asyncio.run(test_multiple_sports())
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.exception("Test failure details:")