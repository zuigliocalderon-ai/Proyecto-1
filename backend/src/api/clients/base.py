"""
Base API client for sports data providers.

Provides extensible foundation for multiple sports APIs with consistent interface,
error handling, rate limiting, and response transformation.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, date
import asyncio
import aiohttp
import time
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    pass


class AuthenticationError(APIError):
    """Raised when API authentication fails."""
    pass


class DataNotFoundError(APIError):
    """Raised when requested data is not found."""
    pass


@dataclass
class APIResponse:
    """Standardized API response wrapper."""
    data: Any
    status_code: int
    headers: Dict[str, str]
    response_time: float
    cached: bool = False
    
    @property
    def success(self) -> bool:
        return 200 <= self.status_code < 300


@dataclass
class Team:
    """Standardized team data structure."""
    id: str
    name: str
    short_name: str
    city: str
    league: str
    conference: Optional[str] = None
    division: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    venue: Optional[str] = None


@dataclass
class Player:
    """Standardized player data structure."""
    id: str
    first_name: str
    last_name: str
    team_id: str
    position: str
    jersey_number: Optional[int] = None
    height: Optional[str] = None
    weight: Optional[int] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None


@dataclass
class Game:
    """Standardized game data structure."""
    id: str
    home_team_id: str
    away_team_id: str
    scheduled_at: datetime
    status: str
    season: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    venue: Optional[str] = None
    attendance: Optional[int] = None


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """Wait if necessary to respect rate limits."""
        now = time.time()
        
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
                return await self.acquire()
        
        self.requests.append(now)


class BaseSportsAPI(ABC):
    """Abstract base class for sports data API clients."""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 base_url: str = "",
                 timeout: int = 10,
                 max_retries: int = 3,
                 rate_limit: int = 60):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limiter = RateLimiter(rate_limit)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers=self._get_default_headers()
            )
    
    async def close(self):
        """Close aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        headers = {
            'User-Agent': 'Sports-Predictions-Platform/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        if self.api_key:
            headers.update(self._get_auth_headers())
        
        return headers
    
    @abstractmethod
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers. Override in subclasses."""
        pass
    
    async def _make_request(self, 
                           method: str,
                           endpoint: str,
                           params: Optional[Dict] = None,
                           data: Optional[Dict] = None) -> APIResponse:
        """Make HTTP request with error handling and retries."""
        await self._ensure_session()
        await self.rate_limiter.acquire()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = time.time()
        
        for attempt in range(self.max_retries + 1):
            try:
                async with self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data
                ) as response:
                    response_time = time.time() - start_time
                    content = await response.text()
                    
                    # Handle different response types
                    try:
                        json_data = await response.json() if content else {}
                    except:
                        json_data = {'raw_content': content}
                    
                    api_response = APIResponse(
                        data=json_data,
                        status_code=response.status,
                        headers=dict(response.headers),
                        response_time=response_time
                    )
                    
                    # Handle HTTP errors
                    if response.status == 401:
                        raise AuthenticationError(f"Authentication failed: {content}")
                    elif response.status == 404:
                        raise DataNotFoundError(f"Data not found: {content}")
                    elif response.status == 429:
                        raise RateLimitError(f"Rate limit exceeded: {content}")
                    elif response.status >= 400:
                        raise APIError(f"API error {response.status}: {content}")
                    
                    logger.debug(f"{method} {url} completed in {response_time:.2f}s")
                    return api_response
                    
            except aiohttp.ClientError as e:
                if attempt == self.max_retries:
                    raise APIError(f"Request failed after {self.max_retries} retries: {e}")
                
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
    
    # Abstract methods that subclasses must implement
    @abstractmethod
    async def get_teams(self, league: Optional[str] = None) -> List[Team]:
        """Get list of teams."""
        pass
    
    @abstractmethod
    async def get_team(self, team_id: str) -> Team:
        """Get specific team details."""
        pass
    
    @abstractmethod
    async def get_players(self, team_id: Optional[str] = None) -> List[Player]:
        """Get list of players."""
        pass
    
    @abstractmethod
    async def get_player(self, player_id: str) -> Player:
        """Get specific player details."""
        pass
    
    @abstractmethod
    async def get_games(self, 
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None,
                       team_id: Optional[str] = None) -> List[Game]:
        """Get list of games."""
        pass
    
    @abstractmethod
    async def get_game(self, game_id: str) -> Game:
        """Get specific game details."""
        pass
    
    @abstractmethod
    async def get_team_stats(self, team_id: str, season: Optional[str] = None) -> Dict[str, Any]:
        """Get team statistics."""
        pass
    
    @abstractmethod
    async def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Dict[str, Any]:
        """Get player statistics."""
        pass