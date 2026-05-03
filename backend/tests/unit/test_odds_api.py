"""
Tests for Odds API client.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.api.clients.odds_api import OddsAPI, BettingOdds, GameWithOdds
from src.api.clients.base import APIError, AuthenticationError


class TestOddsAPI:
    """Test Odds API client functionality."""
    
    @pytest.fixture
    def odds_api(self):
        """Create Odds API client for testing."""
        return OddsAPI(api_key="test_key", timeout=5, max_retries=1, rate_limit=50)
    
    def test_initialization(self):
        """Test Odds API client initialization."""
        api = OddsAPI(api_key="test_key", timeout=10, max_retries=3, rate_limit=20)
        
        assert api.api_key == "test_key"
        assert api.base_url == "https://api.the-odds-api.com/v4"
        assert api.timeout == 10
        assert api.max_retries == 3
        assert api.rate_limiter.max_requests == 20
    
    def test_auth_headers(self, odds_api):
        """Test Odds API authentication headers (API key in params)."""
        headers = odds_api._get_auth_headers()
        
        # Odds API doesn't use headers for auth, uses query params
        assert headers == {}
    
    @pytest.mark.asyncio
    async def test_get_sports_success(self, odds_api):
        """Test successful sports retrieval."""
        mock_sports_response = [
            {"key": "basketball_nba", "title": "NBA", "group": "Basketball"},
            {"key": "soccer_epl", "title": "EPL", "group": "Soccer"}
        ]
        
        with patch.object(odds_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = mock_sports_response
            
            sports = await odds_api.get_sports()
            
            assert len(sports) == 2
            assert sports[0]["title"] == "NBA"
            assert sports[1]["title"] == "EPL"
            
            mock_request.assert_called_once_with(
                'GET', 
                'sports',
                params={'apiKey': 'test_key'}
            )
    
    @pytest.mark.asyncio
    async def test_get_sports_authentication_error(self, odds_api):
        """Test sports retrieval with invalid API key."""
        with patch.object(odds_api, '_make_request') as mock_request:
            mock_request.return_value.success = False
            mock_request.return_value.status_code = 401
            
            with pytest.raises(APIError):
                await odds_api.get_sports()
    
    @pytest.mark.asyncio
    async def test_get_odds_success(self, odds_api):
        """Test successful odds retrieval."""
        mock_odds_response = [{
            "id": "game123",
            "sport_key": "basketball_nba",
            "home_team": "Lakers",
            "away_team": "Warriors",
            "commence_time": "2024-01-01T20:00:00Z",
            "completed": False,
            "bookmakers": [{
                "key": "draftkings",
                "title": "DraftKings",
                "last_update": "2024-01-01T19:00:00Z",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Lakers", "price": 1.90},
                        {"name": "Warriors", "price": 1.95}
                    ]
                }, {
                    "key": "totals",
                    "outcomes": [
                        {"name": "Over", "price": 1.85, "point": 220.5},
                        {"name": "Under", "price": 1.95, "point": 220.5}
                    ]
                }]
            }]
        }]
        
        with patch.object(odds_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = mock_odds_response
            
            games_with_odds = await odds_api.get_odds("basketball_nba")
            
            assert len(games_with_odds) == 1
            game = games_with_odds[0]
            
            assert isinstance(game, GameWithOdds)
            assert game.game_id == "game123"
            assert game.home_team == "Lakers"
            assert game.away_team == "Warriors"
            assert game.sport == "basketball_nba"
            assert not game.completed
            
            # Check odds parsing
            assert len(game.odds) == 1
            betting_odds = game.odds[0]
            
            assert isinstance(betting_odds, BettingOdds)
            assert betting_odds.bookmaker == "DraftKings"
            assert betting_odds.home_odds == 1.90
            assert betting_odds.away_odds == 1.95
            assert betting_odds.over_under_line == 220.5
            assert betting_odds.over_odds == 1.85
            assert betting_odds.under_odds == 1.95
            
            mock_request.assert_called_once_with(
                'GET',
                'sports/basketball_nba/odds',
                params={
                    'apiKey': 'test_key',
                    'regions': 'us',
                    'markets': 'h2h,spreads,totals',
                    'dateFormat': 'iso'
                }
            )
    
    @pytest.mark.asyncio
    async def test_parse_game_odds_with_scores(self, odds_api):
        """Test parsing completed game with scores."""
        game_data = {
            "id": "completed_game",
            "sport_key": "basketball_nba",
            "home_team": "Lakers",
            "away_team": "Warriors",
            "commence_time": "2024-01-01T20:00:00Z",
            "completed": True,
            "scores": [
                {"name": "Lakers", "score": 110},
                {"name": "Warriors", "score": 105}
            ],
            "bookmakers": []
        }
        
        game_with_odds = odds_api._parse_game_odds(game_data)
        
        assert game_with_odds.completed
        assert game_with_odds.home_score == 110
        assert game_with_odds.away_score == 105
    
    @pytest.mark.asyncio
    async def test_parse_game_odds_with_draw(self, odds_api):
        """Test parsing odds with draw option (soccer)."""
        game_data = {
            "id": "soccer_game",
            "sport_key": "soccer_epl",
            "home_team": "Arsenal",
            "away_team": "Chelsea", 
            "commence_time": "2024-01-01T15:00:00Z",
            "completed": False,
            "bookmakers": [{
                "key": "bet365",
                "title": "Bet365",
                "last_update": "2024-01-01T14:00:00Z",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Arsenal", "price": 2.10},
                        {"name": "Chelsea", "price": 3.20},
                        {"name": "Draw", "price": 3.50}
                    ]
                }]
            }]
        }
        
        game_with_odds = odds_api._parse_game_odds(game_data)
        betting_odds = game_with_odds.odds[0]
        
        assert betting_odds.home_odds == 2.10
        assert betting_odds.away_odds == 3.20
        assert betting_odds.draw_odds == 3.50
    
    @pytest.mark.asyncio
    async def test_get_historical_odds(self, odds_api):
        """Test historical odds retrieval."""
        with patch.object(odds_api, '_make_request') as mock_request:
            mock_request.return_value.success = False
            mock_request.return_value.status_code = 401
            
            with pytest.raises(APIError) as exc_info:
                await odds_api.get_historical_odds("basketball_nba")
            
            assert "Historical odds require a paid subscription" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_games_from_odds(self, odds_api):
        """Test converting odds data to game format."""
        mock_odds_data = [{
            "id": "game456",
            "sport_key": "basketball_nba",
            "home_team": "Celtics",
            "away_team": "Heat",
            "commence_time": "2024-01-02T19:30:00Z",
            "completed": True,
            "scores": [
                {"name": "Celtics", "score": 108},
                {"name": "Heat", "score": 102}
            ],
            "bookmakers": []
        }]
        
        with patch.object(odds_api, 'get_odds') as mock_get_odds:
            mock_get_odds.return_value = [odds_api._parse_game_odds(mock_odds_data[0])]
            
            games = await odds_api.get_games()
            
            assert len(games) == 1
            game = games[0]
            
            assert game.id == "game456"
            assert game.home_team_id == "Celtics"
            assert game.away_team_id == "Heat"
            assert game.status == "finished"
            assert game.home_score == 108
            assert game.away_score == 102
    
    @pytest.mark.asyncio
    async def test_not_implemented_methods(self, odds_api):
        """Test that team/player methods raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await odds_api.get_teams()
        
        with pytest.raises(NotImplementedError):
            await odds_api.get_team("team123")
        
        with pytest.raises(NotImplementedError):
            await odds_api.get_players()
        
        with pytest.raises(NotImplementedError):
            await odds_api.get_player("player123")
        
        with pytest.raises(NotImplementedError):
            await odds_api.get_team_stats("team123")
        
        with pytest.raises(NotImplementedError):
            await odds_api.get_player_stats("player123")
    
    @pytest.mark.asyncio
    async def test_get_usage_info(self, odds_api):
        """Test API usage information retrieval."""
        with patch.object(odds_api, '_make_request') as mock_request:
            mock_response = AsyncMock()
            mock_response.success = True
            mock_response.data = []
            mock_response.headers = {
                'x-requests-remaining': '450',
                'x-requests-used': '50', 
                'x-requests-last': '1640995200'
            }
            mock_request.return_value = mock_response
            
            usage_info = await odds_api.get_usage_info()
            
            assert usage_info['requests_remaining'] == '450'
            assert usage_info['requests_used'] == '50'
            assert usage_info['requests_last'] == '1640995200'


class TestBettingOdds:
    """Test BettingOdds data structure."""
    
    def test_betting_odds_creation(self):
        """Test BettingOdds object creation."""
        odds = BettingOdds(
            game_id="game123",
            bookmaker="DraftKings",
            home_team="Lakers",
            away_team="Warriors",
            home_odds=1.90,
            away_odds=1.95,
            over_under_line=220.5,
            over_odds=1.85,
            under_odds=1.95,
            last_update=datetime.now()
        )
        
        assert odds.game_id == "game123"
        assert odds.bookmaker == "DraftKings"
        assert odds.home_team == "Lakers"
        assert odds.away_team == "Warriors"
        assert odds.home_odds == 1.90
        assert odds.away_odds == 1.95
        assert odds.over_under_line == 220.5


class TestGameWithOdds:
    """Test GameWithOdds data structure."""
    
    def test_game_with_odds_creation(self):
        """Test GameWithOdds object creation."""
        game = GameWithOdds(
            game_id="game123",
            home_team="Lakers",
            away_team="Warriors", 
            sport="basketball_nba",
            commence_time=datetime.now(),
            completed=False
        )
        
        assert game.game_id == "game123"
        assert game.home_team == "Lakers"
        assert game.away_team == "Warriors"
        assert game.sport == "basketball_nba"
        assert not game.completed
        assert game.odds == []  # Should initialize empty list
    
    def test_game_with_odds_with_odds_list(self):
        """Test GameWithOdds with betting odds."""
        betting_odds = BettingOdds(
            game_id="game123",
            bookmaker="DraftKings",
            home_team="Lakers",
            away_team="Warriors"
        )
        
        game = GameWithOdds(
            game_id="game123",
            home_team="Lakers",
            away_team="Warriors",
            sport="basketball_nba", 
            commence_time=datetime.now(),
            odds=[betting_odds]
        )
        
        assert len(game.odds) == 1
        assert game.odds[0].bookmaker == "DraftKings"