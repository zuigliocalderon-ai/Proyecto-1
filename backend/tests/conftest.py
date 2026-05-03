"""
Pytest configuration and fixtures for testing.
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

from api_clients.base import APIResponse


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_session():
    """Mock aiohttp session for testing."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    yield session


@pytest.fixture
def sample_api_response():
    """Sample API response for testing."""
    return APIResponse(
        data={"test": "data"},
        status_code=200,
        headers={"Content-Type": "application/json"},
        response_time=0.5
    )


@pytest.fixture
def sample_team_data():
    """Sample team data for testing."""
    return {
        "id": "1",
        "name": "Test Team",
        "short_name": "TT",
        "city": "Test City",
        "league": "NBA",
        "conference": "Eastern",
        "division": "Atlantic"
    }


@pytest.fixture
def sample_player_data():
    """Sample player data for testing."""
    return {
        "id": "1",
        "first_name": "John",
        "last_name": "Doe",
        "team_id": "1",
        "position": "PG",
        "jersey_number": 23
    }


@pytest.fixture
def sample_game_data():
    """Sample game data for testing."""
    return {
        "id": "1",
        "home_team_id": "1",
        "away_team_id": "2",
        "scheduled_at": "2024-01-01T20:00:00",
        "status": "scheduled",
        "season": "2024",
        "home_score": None,
        "away_score": None
    }


@pytest.fixture
def mock_nba_teams_response():
    """Mock NBA teams API response."""
    return {
        "resultSets": [{
            "headers": ["TEAM_ID", "TEAM_NAME", "ABBREVIATION", "TEAM_CITY", "CONFERENCE", "DIVISION"],
            "rowSet": [
                [1610612737, "Atlanta Hawks", "ATL", "Atlanta", "East", "Southeast"],
                [1610612738, "Boston Celtics", "BOS", "Boston", "East", "Atlantic"]
            ]
        }]
    }


@pytest.fixture
def mock_espn_teams_response():
    """Mock ESPN teams API response."""
    return {
        "sports": [{
            "leagues": [{
                "teams": [{
                    "team": {
                        "id": "1",
                        "displayName": "Atlanta Hawks",
                        "abbreviation": "ATL",
                        "location": "Atlanta",
                        "logos": [{"href": "http://example.com/logo.png", "width": 500}],
                        "color": "#E03A3E",
                        "venue": {"fullName": "State Farm Arena"}
                    }
                }]
            }]
        }]
    }


@pytest.fixture 
def mock_http_error():
    """Mock HTTP error response."""
    mock_response = MagicMock()
    mock_response.status = 404
    mock_response.text = AsyncMock(return_value="Not Found")
    mock_response.json = AsyncMock(side_effect=Exception("Invalid JSON"))
    mock_response.headers = {}
    return mock_response