#!/usr/bin/env python3
"""
Live test script for NBA API client.

Tests actual NBA API endpoints to verify functionality.
"""

import asyncio
import logging
from datetime import date, datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.api.clients.nba_api import NBAAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_nba_api():
    """Test NBA API client with live data."""
    print("🏀 Testing NBA API Client...")
    print("=" * 50)
    
    async with NBAAPI(rate_limit=30) as nba_api:  # Lower rate limit for safety
        try:
            # Test 1: Get Teams
            print("\n1. Testing get_teams()...")
            teams = await nba_api.get_teams()
            print(f"✅ Retrieved {len(teams)} NBA teams")
            
            if teams:
                first_team = teams[0]
                print(f"   Sample team: {first_team.name} ({first_team.short_name})")
                print(f"   City: {first_team.city}, Conference: {first_team.conference}")
                
                # Test 2: Get Specific Team
                print(f"\n2. Testing get_team() for {first_team.name}...")
                team_detail = await nba_api.get_team(first_team.id)
                print(f"✅ Retrieved team details: {team_detail.name}")
                
                # Test 3: Get Team Stats
                print(f"\n3. Testing get_team_stats() for {first_team.name}...")
                try:
                    team_stats = await nba_api.get_team_stats(first_team.id)
                    print(f"✅ Retrieved team stats with {len(team_stats)} metrics")
                    # Show a few key stats
                    key_stats = {k: v for k, v in team_stats.items() if k in ['GP', 'W', 'L', 'WIN_PCT', 'PTS']}
                    print(f"   Key stats: {key_stats}")
                except Exception as e:
                    print(f"⚠️  Team stats error: {e}")
                
                # Test 4: Get Players for Team
                print(f"\n4. Testing get_players() for {first_team.name}...")
                try:
                    players = await nba_api.get_players(first_team.id)
                    print(f"✅ Retrieved {len(players)} players")
                    
                    if players:
                        sample_player = players[0]
                        print(f"   Sample player: {sample_player.first_name} {sample_player.last_name}")
                        
                        # Test 5: Get Player Details
                        print(f"\n5. Testing get_player() for {sample_player.first_name} {sample_player.last_name}...")
                        try:
                            player_detail = await nba_api.get_player(sample_player.id)
                            print(f"✅ Retrieved player details: {player_detail.first_name} {player_detail.last_name}")
                            print(f"   Position: {player_detail.position}, Jersey: {player_detail.jersey_number}")
                        except Exception as e:
                            print(f"⚠️  Player details error: {e}")
                        
                        # Test 6: Get Player Stats
                        print(f"\n6. Testing get_player_stats() for {sample_player.first_name} {sample_player.last_name}...")
                        try:
                            player_stats = await nba_api.get_player_stats(sample_player.id)
                            print(f"✅ Retrieved player stats with {len(player_stats)} metrics")
                            # Show a few key stats
                            key_stats = {k: v for k, v in player_stats.items() if k in ['GP', 'MIN', 'PTS', 'REB', 'AST']}
                            print(f"   Key stats: {key_stats}")
                        except Exception as e:
                            print(f"⚠️  Player stats error: {e}")
                
                except Exception as e:
                    print(f"⚠️  Players error: {e}")
            
            # Test 7: Get Recent Games
            print(f"\n7. Testing get_games() for recent games...")
            try:
                # Get games from last 7 days
                end_date = date.today()
                start_date = end_date - timedelta(days=7)
                
                games = await nba_api.get_games(start_date=start_date, end_date=end_date)
                print(f"✅ Retrieved {len(games)} games from last 7 days")
                
                if games:
                    sample_game = games[0]
                    print(f"   Sample game: {sample_game.id}")
                    print(f"   Teams: {sample_game.home_team_id} vs {sample_game.away_team_id}")
                    print(f"   Status: {sample_game.status}")
                    
                    # Test 8: Get Game Details
                    print(f"\n8. Testing get_game() for sample game...")
                    try:
                        game_detail = await nba_api.get_game(sample_game.id)
                        print(f"✅ Retrieved game details")
                        print(f"   Score: {game_detail.home_score} - {game_detail.away_score}")
                        print(f"   Date: {game_detail.scheduled_at}")
                    except Exception as e:
                        print(f"⚠️  Game details error: {e}")
                
            except Exception as e:
                print(f"⚠️  Games error: {e}")
            
        except Exception as e:
            print(f"❌ Major error: {e}")
            logger.exception("Detailed error information:")
    
    print("\n" + "=" * 50)
    print("🏀 NBA API Test Complete!")


async def test_api_rate_limiting():
    """Test rate limiting functionality."""
    print("\n🔄 Testing Rate Limiting...")
    
    async with NBAAPI(rate_limit=2) as nba_api:  # Very low rate limit
        start_time = datetime.now()
        
        # Make 3 requests quickly
        for i in range(3):
            try:
                await nba_api.get_teams()
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"   Request {i+1} completed at {elapsed:.2f}s")
            except Exception as e:
                print(f"   Request {i+1} failed: {e}")
        
        total_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ Rate limiting test completed in {total_time:.2f}s")


if __name__ == "__main__":
    try:
        # Run main NBA API test
        asyncio.run(test_nba_api())
        
        # Run rate limiting test
        asyncio.run(test_api_rate_limiting())
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.exception("Test failure details:")