import anthropic
import os
from datetime import datetime

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAX_CALLS_PER_SESSION = 20

def check_call_limit(session_calls):
    return session_calls >= MAX_CALLS_PER_SESSION

def analyze_match_prediction(match_data, session_calls):
    if not ANTHROPIC_API_KEY:
        return None
    if check_call_limit(session_calls):
        return {"error": "Call limit reached", "message": f"Limite de {MAX_CALLS_PER_SESSION} consultas alcanzado", "remaining_calls": 0}
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        team1 = match_data.get("team1", "Team 1")
        team2 = match_data.get("team2", "Team 2")
        winner = match_data.get("prediction", {}).get("winner", "Unknown")
        confidence = match_data.get("prediction", {}).get("confidence", 0)
        prompt = f"Analiza esta prediccion deportiva: {team1} vs {team2}. Prediccion: {winner} con {confidence}% confianza. Proporciona insights breves."
        message = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=300, messages=[{"role": "user", "content": prompt}])
        return {"success": True, "analysis": message.content[0].text, "match": f"{team1} vs {team2}", "remaining_calls": MAX_CALLS_PER_SESSION - (session_calls + 1)}
    except Exception as e:
        return {"error": str(e), "message": "Error en analisis", "remaining_calls": MAX_CALLS_PER_SESSION - session_calls}

def generate_betting_strategy(matches, session_calls):
    if not ANTHROPIC_API_KEY:
        return None
    if check_call_limit(session_calls):
        return {"error": "Call limit reached", "remaining_calls": 0}
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        matches_text = ", ".join([f"{m.get('team1')} vs {m.get('team2')}" for m in matches[:5]])
        prompt = f"Genera una estrategia de apuestas para estos partidos: {matches_text}. Proporciona recomendaciones breves y concisas."
        message = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=400, messages=[{"role": "user", "content": prompt}])
        return {"success": True, "strategy": message.content[0].text, "matches_analyzed": len(matches), "remaining_calls": MAX_CALLS_PER_SESSION - (session_calls + 1)}
    except Exception as e:
        return {"error": str(e), "message": "Error en estrategia", "remaining_calls": MAX_CALLS_PER_SESSION - session_calls}

def get_remaining_calls(session_calls):
    return max(0, MAX_CALLS_PER_SESSION - session_calls)
