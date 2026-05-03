"""
Sports API clients package.

Provides extensible API clients for multiple sports data providers.
"""

from .base import (
    BaseSportsAPI, 
    APIError, 
    RateLimitError, 
    AuthenticationError, 
    DataNotFoundError,
    APIResponse,
    Team,
    Player,
    Game
)

from .odds_api import (
    OddsAPI,
    BettingOdds,
    GameWithOdds
)

__all__ = [
    'BaseSportsAPI',
    'APIError',
    'RateLimitError', 
    'AuthenticationError',
    'DataNotFoundError',
    'APIResponse',
    'Team',
    'Player',
    'Game',
    'OddsAPI',
    'BettingOdds',
    'GameWithOdds'
]