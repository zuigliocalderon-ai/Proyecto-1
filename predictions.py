import requests
import os
from datetime import datetime, timedelta

ISPORTS_API_KEY = os.getenv("ISPORTS_API_KEY", "")
API_SPORTS_KEY = os.getenv("API_SPORTS_KEY", "")
API_SPORTS_BASE_URL = "https://v3.football.api-sports.io"
REQUEST_TIMEOUT = 5

def get_team_stats_from_api_sports(team_id):
    if not API_SPORTS_KEY:
        return {"avg_goals": 0, "avg_goals_against": 0, "win_pct": 0, "form": "N/A"}
    try:
        headers = {"x-apisports-key": API_SPORTS_KEY}
        response = requests.get(f"{API_SPORTS_BASE_URL}/teams/statistics", params={"team": team_id, "season": 2024}, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json().get("response", {})
        return {"avg_goals": data.get("goals", {}).get("for", {}).get("average", 0), "avg_goals_against": data.get("goals", {}).get("against", {}).get("average", 0), "win_pct": data.get("fixtures", {}).get("wins", {}).get("pct", 0) or 0, "form": data.get("form", "N/A")}
    except Exception as e:
        return {"avg_goals": 0, "avg_goals_against": 0, "win_pct": 0, "form": "N/A"}

def calculate_prediction_confidence(team1_stats, team2_stats):
    try:
        team1_score = 0
        team2_score = 0
        if team1_stats["avg_goals"] > team2_stats["avg_goals"]:
            team1_score += 0.35
        else:
            team2_score += 0.35
        if team1_stats["avg_goals_against"] < team2_stats["avg_goals_against"]:
            team1_score += 0.25
        else:
            team2_score += 0.25
        if team1_stats["win_pct"] > team2_stats["win_pct"]:
            team1_score += 0.40
        else:
            team2_score += 0.40
        if team1_score > team2_score:
            return {"winner": 1, "confidence": min(int(team1_score * 100), 99)}
        else:
            return {"winner": 2, "confidence": min(int(team2_score * 100), 99)}
    except:
        return {"winner": 1, "confidence": 50}

def get_upcoming_fixtures():
    if not API_SPORTS_KEY:
        return []
    try:
        headers = {"x-apisports-key": API_SPORTS_KEY}
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        response = requests.get(f"{API_SPORTS_BASE_URL}/fixtures", params={"dateFrom": today, "dateTo": future, "league": 39, "season": 2024}, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json().get("response", [])
    except:
        return []

def get_enhanced_predictions():
    fixtures = get_upcoming_fixtures()
    if not fixtures:
        return get_mock_predictions()
    predictions = []
    for fixture in fixtures[:3]:
        try:
            fixture_info = fixture.get("fixture", {})
            teams = fixture.get("teams", {})
            league = fixture.get("league", {})
            home_team = teams.get("home", {})
            away_team = teams.get("away", {})
            home_stats = get_team_stats_from_api_sports(home_team.get("id"))
            away_stats = get_team_stats_from_api_sports(away_team.get("id"))
            prediction = calculate_prediction_confidence(home_stats, away_stats)
            match_date = fixture_info.get("date", "")
            match_time = match_date.split("T")[1][:5] if "T" in match_date else "19:30"
            match_date_only = match_date.split("T")[0] if "T" in match_date else datetime.now().strftime("%Y-%m-%d")
            winner_name = home_team.get("name") if prediction["winner"] == 1 else away_team.get("name")
            predictions.append({"id": fixture_info.get("id"), "team1": home_team.get("name", "Unknown"), "team2": away_team.get("name", "Unknown"), "date": match_date_only, "time": match_time, "league": league.get("name", "Unknown"), "prediction": {"winner": winner_name, "confidence": prediction["confidence"], "odds": {"home": round(1.5 + (prediction["confidence"] / 100) * 0.5, 2), "away": round(2.5 - (prediction["confidence"] / 100) * 0.5, 2)}}, "stats": {"team1_avg_points": round(home_stats["avg_goals"] * 10, 1), "team2_avg_points": round(away_stats["avg_goals"] * 10, 1), "team1_win_pct": int(home_stats["win_pct"]), "team2_win_pct": int(away_stats["win_pct"])}})
        except:
            pass
    return predictions if predictions else get_mock_predictions()

def get_live_scores():
    if not API_SPORTS_KEY:
        return get_mock_live_matches()
    try:
        headers = {"x-apisports-key": API_SPORTS_KEY}
        response = requests.get(f"{API_SPORTS_BASE_URL}/fixtures", params={"live": "all", "league": 39, "season": 2024}, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        fixtures = response.json().get("response", [])
        live_matches = []
        for fixture in fixtures:
            fixture_info = fixture.get("fixture", {})
            teams = fixture.get("teams", {})
            goals = fixture.get("goals", {})
            status = fixture_info.get("status", {})
            live_matches.append({"id": fixture_info.get("id"), "team1": teams.get("home", {}).get("name", "Unknown"), "team2": teams.get("away", {}).get("name", "Unknown"), "score1": goals.get("home", 0), "score2": goals.get("away", 0), "status": status.get("short", "NS"), "elapsed": status.get("elapsed", 0), "date": fixture_info.get("date", "").split("T")[0], "start_time": fixture_info.get("date", "").split("T")[1][:5] if "T" in fixture_info.get("date", "") else "00:00"})
        return live_matches
    except:
        return get_mock_live_matches()

