#!/usr/bin/env python3
"""
Test NBA API client with fallback mechanism.
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.api.clients.nba_api import NBAAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_nba_with_fallback():
    """Test NBA API with graceful fallback."""
    print("🏀 Testing NBA API with Fallback")
    print("=" * 50)
    
    async with NBAAPI() as nba_api:
        try:
            # Test teams (should work with fallback)
            print("\n1. Testing get_teams()...")
            teams = await nba_api.get_teams()
            print(f"✅ Retrieved {len(teams)} NBA teams")
            
            if teams:
                # Show sample teams from different conferences
                east_teams = [t for t in teams if t.conference == 'East']
                west_teams = [t for t in teams if t.conference == 'West']
                
                print(f"   📊 Eastern Conference: {len(east_teams)} teams")
                print(f"   📊 Western Conference: {len(west_teams)} teams")
                
                if east_teams:
                    sample_east = east_teams[0]
                    print(f"   🏀 Sample East: {sample_east.name} ({sample_east.short_name})")
                    print(f"      Division: {sample_east.division}")
                    
                if west_teams:
                    sample_west = west_teams[0]
                    print(f"   🏀 Sample West: {sample_west.name} ({sample_west.short_name})")
                    print(f"      Division: {sample_west.division}")
                
                # Test specific team details
                print(f"\n2. Testing get_team() for {sample_east.name}...")
                try:
                    team_detail = await nba_api.get_team(sample_east.id)
                    print(f"✅ Retrieved team details: {team_detail.name}")
                    print(f"   Conference: {team_detail.conference}")
                    print(f"   Division: {team_detail.division}")
                except Exception as e:
                    print(f"⚠️  Team details not available: {e}")
                
                # Show complete team structure
                print(f"\n3. Team data structure:")
                print(f"   ✅ ID: {sample_east.id}")
                print(f"   ✅ Name: {sample_east.name}")
                print(f"   ✅ Short Name: {sample_east.short_name}")
                print(f"   ✅ City: {sample_east.city}")
                print(f"   ✅ League: {sample_east.league}")
                print(f"   ✅ Conference: {sample_east.conference}")
                print(f"   ✅ Division: {sample_east.division}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            logger.exception("Detailed error:")
    
    print("\n" + "=" * 50)
    print("✅ NBA API Test Complete!")


async def test_both_apis():
    """Test both ESPN and NBA APIs together."""
    print("\n🏆 Testing Both APIs Together")
    print("=" * 50)
    
    from api_clients.espn_api import ESPNAPI
    
    apis = [
        ("ESPN API", ESPNAPI()),
        ("NBA API (with fallback)", NBAAPI())
    ]
    
    results = {}
    
    for api_name, api_client in apis:
        print(f"\n📡 {api_name}...")
        
        async with api_client as api:
            try:
                teams = await api.get_teams('basketball')
                results[api_name] = len(teams)
                print(f"   ✅ {len(teams)} teams retrieved")
                
                if teams:
                    sample = teams[0]
                    print(f"   🏀 Sample: {sample.name} ({sample.short_name})")
                    
            except Exception as e:
                results[api_name] = 0
                print(f"   ❌ Failed: {e}")
    
    print(f"\n📊 Results Summary:")
    for api_name, count in results.items():
        status = "✅" if count > 0 else "❌"
        print(f"   {status} {api_name}: {count} teams")
    
    total_working = sum(1 for count in results.values() if count > 0)
    print(f"\n🎯 {total_working}/{len(apis)} APIs working successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(test_nba_with_fallback())
        asyncio.run(test_both_apis())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")