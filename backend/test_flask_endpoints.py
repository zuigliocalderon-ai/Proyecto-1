#!/usr/bin/env python3
"""
Test Flask endpoints with real API data.
"""

import sys
import os
import json
from flask import Flask

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from src.api.app import app


def test_flask_endpoints():
    """Test all Flask endpoints with real data."""
    print("🌐 Testing Flask Endpoints with Real Data")
    print("=" * 50)
    
    with app.test_client() as client:
        # Test metrics endpoint
        print("\n📊 Testing /api/metrics")
        try:
            response = client.get('/api/metrics')
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"  ✅ Win Rate: {data['win_rate']}%")
                print(f"  ✅ Current Balance: ${data['current_balance']}")
                print(f"  ✅ Total Profit: ${data['total_profit']}")
                print(f"  ✅ Total Bets: {data['total_bets']}")
                print(f"  ✅ ROI: {data['roi']}%")
            else:
                print(f"  ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")
        
        # Test matches endpoint
        print("\n🏀 Testing /api/matches")
        try:
            response = client.get('/api/matches')
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"  ✅ Matches Retrieved: {len(data)}")
                
                if data:
                    match = data[0]
                    print(f"  🏆 Sample Match:")
                    print(f"     Teams: {match['team1']} vs {match['team2']}")
                    print(f"     Date: {match['date']} at {match['time']}")
                    print(f"     Status: {match['status']}")
                    print(f"     Odds: {match['odds']}")
                    print(f"     Prediction: {match['prediction']} ({match['confidence']}%)")
            else:
                print(f"  ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")
        
        # Test teams endpoint
        print("\n👥 Testing /api/teams")
        try:
            response = client.get('/api/teams')
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"  ✅ Teams Retrieved: {len(data)}")
                
                if data:
                    team = data[0]
                    print(f"  🏀 Sample Team: {team['name']} ({team['short_name']})")
                    print(f"     City: {team['city']}")
                    print(f"     League: {team['league']}")
            else:
                print(f"  ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")
        
        # Test health endpoint
        print("\n🏥 Testing /api/health")
        try:
            response = client.get('/api/health')
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print("  ✅ Health Status:")
                for api, status in data.items():
                    if api != 'stats':
                        status_emoji = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                        print(f"     {status_emoji} {api}: {status}")
            else:
                print(f"  ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    print(f"\n🎉 Flask endpoint testing complete!")


if __name__ == "__main__":
    test_flask_endpoints()