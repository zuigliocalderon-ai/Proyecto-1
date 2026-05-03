#!/usr/bin/env python3
"""
Test real API data integration for dashboard metrics and matches.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from src.services.data_service import DataService


async def test_dashboard_data():
    """Test dashboard metrics and matches with real API data."""
    print("🧪 Testing Real API Data Integration")
    print("=" * 50)
    
    async with DataService() as data_service:
        # Test metrics
        print("\n📊 Dashboard Metrics:")
        try:
            metrics = await data_service.get_dashboard_metrics()
            print(f"  ✅ Win Rate: {metrics.win_rate}%")
            print(f"  ✅ Current Balance: ${metrics.current_balance}")
            print(f"  ✅ Starting Balance: ${metrics.starting_balance}")
            print(f"  ✅ Total Profit: ${metrics.total_profit}")
            print(f"  ✅ Total Bets: {metrics.total_bets}")
            print(f"  ✅ Successful Bets: {metrics.successful_bets}")
            print(f"  ✅ Average Odds: {metrics.avg_odds}")
            print(f"  ✅ ROI: {metrics.roi}%")
        except Exception as e:
            print(f"  ❌ Metrics Error: {e}")
        
        # Test matches
        print("\n🏀 Dashboard Matches:")
        try:
            matches = await data_service.get_dashboard_matches()
            print(f"  ✅ Retrieved {len(matches)} matches")
            
            for i, match in enumerate(matches[:3]):  # Show first 3
                print(f"  🏆 Match {i+1}:")
                print(f"     Teams: {match.home_team} vs {match.away_team}")
                print(f"     Date: {match.date} at {match.time}")
                print(f"     Status: {match.status}")
                print(f"     Odds: {match.odds}")
                print(f"     Prediction: {match.prediction} ({match.confidence}%)")
                if match.home_score is not None:
                    print(f"     Score: {match.home_score} - {match.away_score}")
        except Exception as e:
            print(f"  ❌ Matches Error: {e}")
        
        # Test health check
        print("\n🏥 API Health Check:")
        try:
            health = await data_service.health_check()
            for api, status in health.items():
                status_emoji = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                print(f"  {status_emoji} {api}: {status}")
        except Exception as e:
            print(f"  ❌ Health Check Error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(test_dashboard_data())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()