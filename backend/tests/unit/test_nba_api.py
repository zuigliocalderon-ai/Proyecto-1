"""
Tests for NBA API client.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, date

from src.api.clients.nba_api import NBAAPI
from src.api.clients.base import Team, Player, Game, APIError, DataNotFoundError


class TestNBAAAPI:
    """Test NBA API client functionality."""
    
    @pytest.fixture
    def nba_api(self):
        """Create NBA API client for testing."""
        return NBAAPI(timeout=5, max_retries=1, rate_limit=100)
    
    def test_initialization(self):
        """Test NBA API client initialization."""
        api = NBAAPI(timeout=10, max_retries=3, rate_limit=60)
        
        assert api.base_url == "https://stats.nba.com/stats"
        assert api.timeout == 10
        assert api.max_retries == 3
        assert api.rate_limiter.max_requests == 60
    
    def test_auth_headers(self, nba_api):
        """Test NBA API authentication headers."""
        headers = nba_api._get_auth_headers()
        
        assert "Host" in headers
        assert "Referer" in headers
        assert "x-nba-stats-origin" in headers
        assert "x-nba-stats-token" in headers
        assert headers["Host"] == "stats.nba.com"
    
    @pytest.mark.asyncio
    async def test_get_teams_success(self, nba_api, mock_nba_teams_response):
        """Test successful teams retrieval."""
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = mock_nba_teams_response
            
            teams = await nba_api.get_teams()
            
            assert len(teams) == 2
            assert isinstance(teams[0], Team)
            assert teams[0].name == "Atlanta Hawks"
            assert teams[0].short_name == "ATL"
            assert teams[0].city == "Atlanta"
            assert teams[0].league == "NBA"
            assert teams[0].conference == "East"
            
            mock_request.assert_called_once_with('GET', 'commonteamyears')
    
    @pytest.mark.asyncio
    async def test_get_teams_api_error(self, nba_api):
        """Test teams retrieval with API error."""
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = False
            mock_request.return_value.status_code = 500
            
            with pytest.raises(APIError):
                await nba_api.get_teams()
    
    @pytest.mark.asyncio
    async def test_get_team_success(self, nba_api):
        """Test successful team retrieval."""
        mock_team_response = {
            "resultSets": [{
                "headers": ["TEAM_ID", "TEAM_NAME", "ABBREVIATION", "TEAM_CITY", "TEAM_CONFERENCE", "TEAM_DIVISION"],
                "rowSet": [[1610612737, "Atlanta Hawks", "ATL", "Atlanta", "East", "Southeast"]]
            }]
        }
        
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = mock_team_response
            
            team = await nba_api.get_team("1610612737")
            
            assert isinstance(team, Team)
            assert team.id == "1610612737"
            assert team.name == "Atlanta Hawks"
            assert team.short_name == "ATL"
            assert team.city == "Atlanta"
            assert team.conference == "East"
            assert team.division == "Southeast"
            
            mock_request.assert_called_once_with('GET', 'teaminfocommon', params={'TeamID': '1610612737'})
    
    @pytest.mark.asyncio
    async def test_get_team_not_found(self, nba_api):
        """Test team retrieval when team not found."""
        mock_response = {
            "resultSets": [{
                "headers": [],
                "rowSet": []
            }]
        }
        
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = mock_response
            
            with pytest.raises(DataNotFoundError):
                await nba_api.get_team("invalid_id")
    
    @pytest.mark.asyncio
    async def test_get_players_success(self, nba_api):
        """Test successful players retrieval."""
        mock_players_response = {
            "resultSets": [{
                "headers": ["PERSON_ID", "DISPLAY_FIRST_LAST", "TEAM_ID"],
                "rowSet": [
                    [123, "John Doe", 1610612737],
                    [456, "Jane Smith", 1610612738]
                ]
            }]
        }
        
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = mock_players_response
            
            players = await nba_api.get_players()
            
            assert len(players) == 2
            assert isinstance(players[0], Player)
            assert players[0].id == "123"
            assert players[0].first_name == "John"
            assert players[0].last_name == "Doe"
            assert players[0].team_id == "1610612737"
            
            mock_request.assert_called_once_with(
                'GET', 
                'commonallplayers',
                params={'IsOnlyCurrentSeason': '1'}
            )
    
    @pytest.mark.asyncio
    async def test_get_players_with_team_filter(self, nba_api):
        """Test players retrieval filtered by team."""
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = {"resultSets": [{"headers": [], "rowSet": []}]}
            
            await nba_api.get_players(team_id="1610612737")
            
            mock_request.assert_called_once_with(
                'GET',
                'commonallplayers', 
                params={'IsOnlyCurrentSeason': '1', 'TeamID': '1610612737'}
            )
    
    @pytest.mark.asyncio
    async def test_get_player_success(self, nba_api):
        """Test successful player retrieval."""
        mock_player_response = {
            "resultSets": [{
                "headers": ["PERSON_ID", "FIRST_NAME", "LAST_NAME", "TEAM_ID", "POSITION", "JERSEY", "HEIGHT", "WEIGHT"],
                "rowSet": [[123, "John", "Doe", 1610612737, "PG", "23", "6-3", 200]]
            }]
        }
        
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = mock_player_response
            
            player = await nba_api.get_player("123")
            
            assert isinstance(player, Player)
            assert player.id == "123"
            assert player.first_name == "John"
            assert player.last_name == "Doe"
            assert player.team_id == "1610612737"
            assert player.position == "PG"
            assert player.jersey_number == "23"
            assert player.height == "6-3"
            assert player.weight == 200
            
            mock_request.assert_called_once_with('GET', 'commonplayerinfo', params={'PlayerID': '123'})
    
    @pytest.mark.asyncio
    async def test_get_games_success(self, nba_api):
        """Test successful games retrieval."""
        mock_games_response = {
            "resultSets": [{
                "headers": ["GAME_ID", "GAME_DATE", "TEAM_ID", "SEASON_ID", "WL", "PTS", "OPP_PTS"],
                "rowSet": [
                    ["0022300001", "2024-01-01T00:00:00", 1610612737, "22023", "W", 110, 105],
                    ["0022300002", "2024-01-02T00:00:00", 1610612738, "22023", "L", 95, 100]
                ]
            }]
        }
        
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = mock_games_response
            
            games = await nba_api.get_games()
            
            assert len(games) == 2
            assert isinstance(games[0], Game)
            assert games[0].id == "0022300001"
            assert games[0].home_team_id == "1610612737"
            assert games[0].season == "22023"
            assert games[0].home_score == 110
            assert games[0].away_score == 105
            
            mock_request.assert_called_once_with('GET', 'leaguegamefinder', params={})
    
    @pytest.mark.asyncio
    async def test_get_games_with_date_range(self, nba_api):
        """Test games retrieval with date range."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = {"resultSets": [{"headers": [], "rowSet": []}]}
            
            await nba_api.get_games(start_date=start_date, end_date=end_date)
            
            mock_request.assert_called_once_with(
                'GET',
                'leaguegamefinder',
                params={'DateFrom': '01/01/2024', 'DateTo': '01/31/2024'}
            )
    
    @pytest.mark.asyncio
    async def test_get_game_success(self, nba_api):
        """Test successful game retrieval."""
        mock_game_response = {
            "resultSets": [{
                "headers": ["GAME_ID", "GAME_DATE_EST", "HOME_TEAM_ID", "VISITOR_TEAM_ID", "SEASON", "HOME_TEAM_PTS", "VISITOR_TEAM_PTS", "ATTENDANCE"],
                "rowSet": [["0022300001", "2024-01-01T20:00:00", 1610612737, 1610612738, "2023-24", 110, 105, 18000]]
            }]
        }
        
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = mock_game_response
            
            game = await nba_api.get_game("0022300001")
            
            assert isinstance(game, Game)
            assert game.id == "0022300001"
            assert game.home_team_id == "1610612737"
            assert game.away_team_id == "1610612738"
            assert game.season == "2023-24"
            assert game.home_score == 110
            assert game.away_score == 105
            assert game.attendance == 18000
            
            mock_request.assert_called_once_with('GET', 'boxscoresummaryv2', params={'GameID': '0022300001'})
    
    @pytest.mark.asyncio
    async def test_get_team_stats_success(self, nba_api):
        """Test successful team stats retrieval."""
        mock_stats_response = {
            "resultSets": [{
                "headers": ["TEAM_ID", "GP", "W", "L", "WIN_PCT", "PTS", "REB", "AST"],
                "rowSet": [[1610612737, 82, 45, 37, 0.549, 112.5, 44.2, 25.8]]
            }]
        }
        
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = mock_stats_response
            
            stats = await nba_api.get_team_stats("1610612737", season="2023-24")
            
            assert isinstance(stats, dict)
            assert stats["TEAM_ID"] == 1610612737
            assert stats["GP"] == 82
            assert stats["WIN_PCT"] == 0.549
            
            mock_request.assert_called_once_with(
                'GET',
                'teamdashboardbygeneralsplits',
                params={'TeamID': '1610612737', 'Season': '2023-24'}
            )
    
    @pytest.mark.asyncio
    async def test_get_player_stats_success(self, nba_api):
        """Test successful player stats retrieval."""
        mock_stats_response = {
            "resultSets": [{
                "headers": ["PLAYER_ID", "GP", "MIN", "PTS", "REB", "AST", "FG_PCT"],
                "rowSet": [[123, 75, 35.2, 28.5, 8.1, 6.3, 0.485]]
            }]
        }
        
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.return_value.success = True
            mock_request.return_value.data = mock_stats_response
            
            stats = await nba_api.get_player_stats("123", season="2023-24")
            
            assert isinstance(stats, dict)
            assert stats["PLAYER_ID"] == 123
            assert stats["GP"] == 75
            assert stats["PTS"] == 28.5
            
            mock_request.assert_called_once_with(
                'GET',
                'playerdashboardbygeneralsplits',
                params={'PlayerID': '123', 'Season': '2023-24'}
            )
    
    @pytest.mark.asyncio
    async def test_exception_handling(self, nba_api):
        """Test exception handling in NBA API client."""
        with patch.object(nba_api, '_make_request') as mock_request:
            mock_request.side_effect = Exception("Network error")
            
            with pytest.raises(APIError) as exc_info:
                await nba_api.get_teams()
            
            assert "Failed to fetch NBA teams" in str(exc_info.value)
    
    @pytest.mark.asyncio 
    async def test_context_manager_usage(self, nba_api):
        """Test NBA API client as context manager."""
        async with nba_api as api:
            assert api._session is not None
            
            with patch.object(api, '_make_request') as mock_request:
                mock_request.return_value.success = True
                mock_request.return_value.data = {"resultSets": [{"headers": [], "rowSet": []}]}
                
                await api.get_teams()
                mock_request.assert_called_once()
        
        assert api._session.closed