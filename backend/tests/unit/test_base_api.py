"""
Tests for base API client functionality.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

from src.api.clients.base import (
    BaseSportsAPI, RateLimiter, APIResponse,
    APIError, RateLimitError, AuthenticationError, DataNotFoundError
)


class TestRateLimiter:
    """Test rate limiter functionality."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_allows_requests_within_limit(self):
        """Test that rate limiter allows requests within the limit."""
        limiter = RateLimiter(max_requests=5, time_window=60)
        
        # Should allow 5 requests without delay
        for _ in range(5):
            await limiter.acquire()
        
        assert len(limiter.requests) == 5
    
    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_excess_requests(self):
        """Test that rate limiter blocks requests exceeding the limit."""
        limiter = RateLimiter(max_requests=2, time_window=1)
        
        # First 2 requests should be immediate
        await limiter.acquire()
        await limiter.acquire()
        
        # Third request should be delayed
        start_time = time.time()
        await limiter.acquire()
        elapsed = time.time() - start_time
        
        assert elapsed >= 0.9  # Should have waited almost 1 second
    
    @pytest.mark.asyncio
    async def test_rate_limiter_cleanup_old_requests(self):
        """Test that rate limiter cleans up old requests."""
        limiter = RateLimiter(max_requests=2, time_window=1)
        
        # Add requests and wait for time window to pass
        await limiter.acquire()
        await limiter.acquire()
        
        # Wait for requests to expire
        await asyncio.sleep(1.1)
        
        # Should allow new request immediately
        start_time = time.time()
        await limiter.acquire()
        elapsed = time.time() - start_time
        
        assert elapsed < 0.1  # Should be immediate


class TestBaseSportsAPI:
    """Test base sports API client."""
    
    class MockSportsAPI(BaseSportsAPI):
        """Mock implementation for testing."""
        
        def _get_auth_headers(self):
            return {"Authorization": "Bearer test-token"}
        
        async def get_teams(self, league=None):
            return []
        
        async def get_team(self, team_id):
            return None
        
        async def get_players(self, team_id=None):
            return []
        
        async def get_player(self, player_id):
            return None
        
        async def get_games(self, start_date=None, end_date=None, team_id=None):
            return []
        
        async def get_game(self, game_id):
            return None
        
        async def get_team_stats(self, team_id, season=None):
            return {}
        
        async def get_player_stats(self, player_id, season=None):
            return {}
    
    def test_initialization(self):
        """Test API client initialization."""
        api = self.MockSportsAPI(
            api_key="test-key",
            base_url="https://api.test.com",
            timeout=15,
            max_retries=5,
            rate_limit=100
        )
        
        assert api.api_key == "test-key"
        assert api.base_url == "https://api.test.com"
        assert api.timeout == 15
        assert api.max_retries == 5
        assert api.rate_limiter.max_requests == 100
    
    def test_default_headers(self):
        """Test default headers generation."""
        api = self.MockSportsAPI(api_key="test-key")
        headers = api._get_default_headers()
        
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token"
    
    @pytest.mark.asyncio
    async def test_session_management(self):
        """Test session creation and cleanup."""
        api = self.MockSportsAPI()
        
        # Session should not exist initially
        assert api._session is None
        
        # Session should be created when needed
        await api._ensure_session()
        assert api._session is not None
        
        # Session should be closed properly
        await api.close()
        assert api._session.closed
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        async with self.MockSportsAPI() as api:
            assert api._session is not None
            assert not api._session.closed
        
        # Session should be closed after context exit
        assert api._session.closed
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, mock_session):
        """Test successful API request."""
        api = self.MockSportsAPI()
        api._session = mock_session
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"data": "test"}')
        mock_response.json = AsyncMock(return_value={"data": "test"})
        mock_response.headers = {"Content-Type": "application/json"}
        
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        with patch('time.time', side_effect=[0, 0.5]):  # Mock timing
            response = await api._make_request('GET', '/test')
        
        assert response.success
        assert response.status_code == 200
        assert response.data == {"data": "test"}
        assert response.response_time == 0.5
    
    @pytest.mark.asyncio
    async def test_make_request_authentication_error(self, mock_session):
        """Test API request with authentication error."""
        api = self.MockSportsAPI()
        api._session = mock_session
        
        # Mock 401 response
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value="Unauthorized")
        mock_response.json = AsyncMock(side_effect=Exception("Invalid JSON"))
        mock_response.headers = {}
        
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(AuthenticationError):
            await api._make_request('GET', '/test')
    
    @pytest.mark.asyncio
    async def test_make_request_not_found_error(self, mock_session):
        """Test API request with not found error."""
        api = self.MockSportsAPI()
        api._session = mock_session
        
        # Mock 404 response
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Not Found")
        mock_response.json = AsyncMock(side_effect=Exception("Invalid JSON"))
        mock_response.headers = {}
        
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(DataNotFoundError):
            await api._make_request('GET', '/test')
    
    @pytest.mark.asyncio
    async def test_make_request_rate_limit_error(self, mock_session):
        """Test API request with rate limit error."""
        api = self.MockSportsAPI()
        api._session = mock_session
        
        # Mock 429 response
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.text = AsyncMock(return_value="Rate Limit Exceeded")
        mock_response.json = AsyncMock(side_effect=Exception("Invalid JSON"))
        mock_response.headers = {}
        
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(RateLimitError):
            await api._make_request('GET', '/test')
    
    @pytest.mark.asyncio
    async def test_make_request_retry_logic(self, mock_session):
        """Test API request retry logic."""
        api = self.MockSportsAPI(max_retries=2)
        api._session = mock_session
        
        # Mock failing then successful response
        mock_response_fail = AsyncMock()
        mock_response_fail.status = 500
        mock_response_fail.text = AsyncMock(return_value="Server Error")
        
        mock_response_success = AsyncMock()
        mock_response_success.status = 200
        mock_response_success.text = AsyncMock(return_value='{"data": "test"}')
        mock_response_success.json = AsyncMock(return_value={"data": "test"})
        mock_response_success.headers = {}
        
        # First call fails, second succeeds
        mock_session.request.return_value.__aenter__.side_effect = [
            Exception("Network error"),
            mock_response_success
        ]
        
        with patch('asyncio.sleep'):  # Mock sleep to speed up test
            with patch('time.time', side_effect=[0, 0.5]):
                response = await api._make_request('GET', '/test')
        
        assert response.success
        assert mock_session.request.call_count == 2


class TestAPIResponse:
    """Test APIResponse functionality."""
    
    def test_api_response_creation(self):
        """Test APIResponse object creation."""
        response = APIResponse(
            data={"test": "data"},
            status_code=200,
            headers={"Content-Type": "application/json"},
            response_time=0.5,
            cached=False
        )
        
        assert response.data == {"test": "data"}
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.response_time == 0.5
        assert response.cached is False
    
    def test_success_property(self):
        """Test success property for different status codes."""
        # Successful responses
        assert APIResponse({}, 200, {}, 0.5).success
        assert APIResponse({}, 201, {}, 0.5).success
        assert APIResponse({}, 299, {}, 0.5).success
        
        # Error responses
        assert not APIResponse({}, 400, {}, 0.5).success
        assert not APIResponse({}, 404, {}, 0.5).success
        assert not APIResponse({}, 500, {}, 0.5).success