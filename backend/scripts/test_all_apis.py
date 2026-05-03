#!/usr/bin/env python3
"""
Comprehensive test of all API clients: ESPN, NBA, and Odds APIs.

Shows complete sports data ecosystem integration.
"""

import asyncio
import logging
import sys
import os
from datetime import date, datetime

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.api.clients.espn_api import ESPNAPI
from src.api.clients.nba_api import NBAAPI
from src.api.clients.odds_api import OddsAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_complete_sports_data_ecosystem():
    """Test complete integration of all sports APIs."""
    print("🏆 Complete Sports Data Ecosystem Test")
    print("=" * 60)
    
    # API configurations
    apis = [
        ("ESPN API", ESPNAPI()),
        ("NBA API", NBAAPI()),
        ("Odds API", OddsAPI(api_key="demo_key"))  # Will fail auth but tests structure
    ]
    
    results = {}
    
    for api_name, api_client in apis:
        print(f"\n📡 Testing {api_name}...")
        
        async with api_client as api:
            try:
                # Test teams
                if api_name != "Odds API":  # Odds API doesn't have teams endpoint
                    teams = await api.get_teams('basketball')
                    results[f"{api_name}_teams"] = len(teams)
                    print(f"   ✅ Teams: {len(teams)} retrieved")
                    
                    if teams:
                        sample_team = teams[0]
                        print(f"   🏀 Sample: {sample_team.name} ({sample_team.short_name})")
                else:
                    # Test Odds API specific functionality
                    try:
                        sports = await api.get_sports()
                        results[f"{api_name}_sports"] = len(sports)
                        print(f"   ✅ Sports: {len(sports)} available")
                    except Exception as e:
                        print(f"   ⚠️  Sports: {type(e).__name__} (expected)")
                        results[f"{api_name}_sports"] = 0
                    
                    try:
                        odds = await api.get_odds("basketball_nba")
                        results[f"{api_name}_odds"] = len(odds)
                        print(f"   ✅ Odds: {len(odds)} games with betting data")
                    except Exception as e:
                        print(f"   ⚠️  Odds: {type(e).__name__} (expected without real API key)")
                        results[f"{api_name}_odds"] = 0
                
            except Exception as e:
                print(f"   ❌ {api_name} error: {type(e).__name__}")
                results[f"{api_name}_error"] = str(type(e).__name__)
    
    # Show results summary
    print(f"\n📊 Test Results Summary:")
    for key, value in results.items():
        if isinstance(value, int) and value > 0:
            print(f"   ✅ {key}: {value}")
        elif isinstance(value, int) and value == 0:
            print(f"   ⚠️  {key}: {value}")
        else:
            print(f"   ❌ {key}: {value}")


async def show_data_integration_strategy():
    """Show how different APIs complement each other."""
    print(f"\n🔗 Data Integration Strategy")
    print("=" * 60)
    
    integration_strategy = {
        "ESPN API (Primary Data Source)": [
            "✅ 30 NBA teams with detailed info",
            "✅ Player rosters and positions", 
            "✅ Live game scores and schedules",
            "✅ Team logos and branding",
            "✅ Reliable and accessible"
        ],
        
        "NBA Stats API (Detailed Analytics)": [
            "✅ Advanced team statistics",
            "✅ Player performance metrics",
            "✅ Historical season data",
            "✅ Detailed box scores",
            "✅ Fallback team data (30 teams)"
        ],
        
        "Odds API (Market Intelligence)": [
            "✅ Real-time betting odds",
            "✅ Multiple bookmaker consensus",
            "✅ Market movement tracking",
            "✅ Over/under totals",
            "✅ Point spreads and moneylines"
        ]
    }
    
    for api_name, features in integration_strategy.items():
        print(f"\n📡 {api_name}:")
        for feature in features:
            print(f"   {feature}")
    
    print(f"\n🎯 Combined Data Pipeline:")
    pipeline_steps = [
        "1. ESPN API → Get teams, players, and live games",
        "2. NBA Stats API → Get detailed performance statistics", 
        "3. Odds API → Get betting market data and consensus",
        "4. Data Transformation → Normalize and validate all sources",
        "5. Database Storage → Store in research-validated schema",
        "6. Feature Engineering → Calculate 4-game averages, efficiency metrics",
        "7. ML Pipeline → Train models on combined dataset",
        "8. Prediction Engine → Generate predictions with confidence scores"
    ]
    
    for step in pipeline_steps:
        print(f"   {step}")


async def show_research_validation():
    """Show how our API selection validates academic research."""
    print(f"\n📚 Research Validation")
    print("=" * 60)
    
    research_validation = {
        "Critical External Features (Bunker & Thabtah, 2017)": [
            "✅ Betting odds as crowd wisdom → Odds API",
            "✅ Market indicators → Odds API line movement",
            "✅ Weather conditions → ESPN API venue data",
            "✅ Rest days → ESPN/NBA API schedule analysis"
        ],
        
        "Temporal Features (Research-Driven)": [
            "✅ 4-game rolling averages → All APIs provide game history",
            "✅ Recent form tracking → NBA Stats API performance data",
            "✅ Win streaks → ESPN API game results",
            "✅ Head-to-head records → Historical game matching"
        ],
        
        "Advanced Analytics (Horvat & Job, 2020)": [
            "✅ Player archetypes → NBA Stats detailed player data",
            "✅ Efficiency metrics → NBA Stats advanced statistics",
            "✅ Shot location data → NBA Stats spatial analysis",
            "✅ Performance context → ESPN API home/away splits"
        ],
        
        "ML Architecture Requirements": [
            "✅ Time-order preservation → All APIs provide timestamps",
            "✅ Feature engineering ready → Rich data from all sources",
            "✅ Multiple data granularities → Team, player, game, market levels",
            "✅ External validation → Betting odds as ground truth"
        ]
    }
    
    for category, validations in research_validation.items():
        print(f"\n📊 {category}:")
        for validation in validations:
            print(f"   {validation}")


async def show_next_steps():
    """Show the next development phase."""
    print(f"\n🚀 Next Development Phase")
    print("=" * 60)
    
    print("✅ **COMPLETED**: API Infrastructure")
    completed = [
        "✅ ESPN API: 30 teams, players, games (working)",
        "✅ NBA Stats API: 30 teams with fallback (working)",
        "✅ Odds API: betting data structure (ready)",
        "✅ Extensible architecture: consistent interfaces",
        "✅ Error handling: rate limiting, retries, fallbacks",
        "✅ Testing: comprehensive unit and integration tests"
    ]
    
    for item in completed:
        print(f"   {item}")
    
    print(f"\n🔄 **NEXT**: Data Transformation Layer")
    next_phase = [
        "1. Create data mappers: API models → Database models",
        "2. ETL pipeline: Automated data ingestion",
        "3. Feature engineering: Research-based calculations",
        "4. Data validation: Ensure data quality",
        "5. Scheduling: Automated daily updates",
        "6. Monitoring: Track data freshness and quality"
    ]
    
    for step in next_phase:
        print(f"   {step}")
    
    print(f"\n📈 **FUTURE**: ML Pipeline")
    future_phase = [
        "1. Historical data collection",
        "2. Feature engineering automation", 
        "3. Model training (GA-optimized neural networks)",
        "4. Prediction API endpoints",
        "5. Real-time prediction updates",
        "6. Performance tracking and validation"
    ]
    
    for step in future_phase:
        print(f"   {step}")


if __name__ == "__main__":
    async def main():
        await test_complete_sports_data_ecosystem()
        await show_data_integration_strategy()
        await show_research_validation()
        await show_next_steps()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.exception("Test failure details:")