"""
The Odds API client implementation.

Provides access to betting odds data for sports predictions.
Free tier: 500 requests/month
API Documentation: https://the-odds-api.com/
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
import logging
from dataclasses import dataclass
from .base import (
    BaseSportsAPI, Team, Player, Game,
    APIError, DataNotFoundError, APIResponse
)

logger = logging.getLogger(__name__)


@dataclass
class BettingOdds:
    """Standardized betting odds data structure."""
    game_id: str
    bookmaker: str
    home_team: str
    away_team: str
    home_odds: Optional[float] = None
    away_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    over_under_line: Optional[float] = None
    over_odds: Optional[float] = None
    under_odds: Optional[float] = None
    last_update: Optional[datetime] = None


@dataclass
class GameWithOdds:
    """Game data enhanced with betting odds."""
    game_id: str
    home_team: str
    away_team: str
    sport: str
    commence_time: datetime
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    completed: bool = False
    odds: List[BettingOdds] = None
    
    def __post_init__(self):
        if self.odds is None:
            self.odds = []


class OddsAPI(BaseSportsAPI):
    """The Odds API client for betting odds data."""
    
    def __init__(self, 
                 api_key: str,
                 timeout: int = 10,
                 max_retries: int = 3,
                 rate_limit: int = 20):  # Conservative rate limit for free tier
        super().__init__(
            api_key=api_key,
            base_url="https://api.the-odds-api.com/v4",
            timeout=timeout,
            max_retries=max_retries,
            rate_limit=rate_limit
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Odds API uses API key in query params, not headers."""
        return {}
    
    async def get_sports(self) -> List[Dict[str, str]]:
        """Get available sports from Odds API."""
        try:
            response = await self._make_request(
                'GET', 
                'sports',
                params={'apiKey': self.api_key}
            )
            
            if not response.success:
                raise APIError(f"Failed to fetch sports: {response.status_code}")
            
            sports = response.data
            logger.info(f"Retrieved {len(sports)} available sports")
            return sports
            
        except Exception as e:
            logger.error(f"Error fetching available sports: {e}")
            raise APIError(f"Failed to fetch sports: {e}")
    
    async def get_odds(self, 
                      sport: str = "basketball_nba",
                      regions: str = "us",
                      markets: str = "h2h,spreads,totals",
                      date_format: str = "iso") -> List[GameWithOdds]:
        """Get betting odds for a specific sport."""
        try:
            params = {
                'apiKey': self.api_key,
                'regions': regions,
                'markets': markets,
                'dateFormat': date_format
            }
            
            response = await self._make_request(
                'GET',
                f'sports/{sport}/odds',
                params=params
            )
            
            if not response.success:
                raise APIError(f"Failed to fetch odds: {response.status_code}")
            
            games_data = response.data
            games_with_odds = []
            
            for game_data in games_data:
                game = self._parse_game_odds(game_data)
                games_with_odds.append(game)
            
            logger.info(f"Retrieved odds for {len(games_with_odds)} games")
            return games_with_odds
            
        except Exception as e:
            logger.error(f"Error fetching odds for {sport}: {e}")
            raise APIError(f"Failed to fetch odds: {e}")
    
    async def get_historical_odds(self,
                                 sport: str = "basketball_nba",
                                 start_date: Optional[date] = None,
                                 end_date: Optional[date] = None) -> List[GameWithOdds]:
        """Get historical odds data (requires paid plan)."""
        try:
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': 'h2h,spreads,totals'
            }
            
            if start_date:
                params['dateFrom'] = start_date.isoformat()
            if end_date:
                params['dateTo'] = end_date.isoformat()
            
            response = await self._make_request(
                'GET',
                f'historical/sports/{sport}/odds',
                params=params
            )
            
            if not response.success:
                if response.status_code == 401:
                    raise APIError("Historical odds require a paid subscription")
                raise APIError(f"Failed to fetch historical odds: {response.status_code}")
            
            games_data = response.data
            games_with_odds = []
            
            for game_data in games_data:
                game = self._parse_game_odds(game_data)
                games_with_odds.append(game)
            
            logger.info(f"Retrieved historical odds for {len(games_with_odds)} games")
            return games_with_odds
            
        except Exception as e:
            logger.error(f"Error fetching historical odds: {e}")
            raise APIError(f"Failed to fetch historical odds: {e}")
    
    def _parse_game_odds(self, game_data: Dict) -> GameWithOdds:
        """Parse game data with odds from API response."""
        # Parse basic game info
        game_id = game_data.get('id', '')
        home_team = game_data.get('home_team', '')
        away_team = game_data.get('away_team', '')
        sport = game_data.get('sport_key', '')
        
        # Parse commence time
        commence_time_str = game_data.get('commence_time', '')
        try:
            commence_time = datetime.fromisoformat(commence_time_str.replace('Z', '+00:00'))
        except:
            commence_time = datetime.now()
        
        # Parse scores if completed
        scores = game_data.get('scores')
        home_score = None
        away_score = None
        completed = game_data.get('completed', False)
        
        if scores:
            for score_data in scores:
                if score_data.get('name') == home_team:
                    home_score = score_data.get('score')
                elif score_data.get('name') == away_team:
                    away_score = score_data.get('score')
        
        # Parse bookmaker odds
        odds_list = []
        bookmakers = game_data.get('bookmakers', [])
        
        for bookmaker_data in bookmakers:
            bookmaker_name = bookmaker_data.get('title', '')
            last_update_str = bookmaker_data.get('last_update', '')
            
            try:
                last_update = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
            except:
                last_update = None
            
            # Parse different market types
            markets = bookmaker_data.get('markets', [])
            
            # Initialize odds object
            betting_odds = BettingOdds(
                game_id=game_id,
                bookmaker=bookmaker_name,
                home_team=home_team,
                away_team=away_team,
                last_update=last_update
            )
            
            for market in markets:
                market_key = market.get('key')
                outcomes = market.get('outcomes', [])
                
                if market_key == 'h2h':  # Head-to-head (moneyline)
                    for outcome in outcomes:
                        name = outcome.get('name')
                        price = outcome.get('price')
                        
                        if name == home_team:
                            betting_odds.home_odds = price
                        elif name == away_team:
                            betting_odds.away_odds = price
                        else:  # Draw (for sports that have it)
                            betting_odds.draw_odds = price
                
                elif market_key == 'totals':  # Over/Under
                    for outcome in outcomes:
                        name = outcome.get('name')
                        price = outcome.get('price')
                        point = outcome.get('point')
                        
                        if name == 'Over':
                            betting_odds.over_odds = price
                            betting_odds.over_under_line = point
                        elif name == 'Under':
                            betting_odds.under_odds = price
                            if not betting_odds.over_under_line:
                                betting_odds.over_under_line = point
            
            odds_list.append(betting_odds)
        
        return GameWithOdds(
            game_id=game_id,
            home_team=home_team,
            away_team=away_team,
            sport=sport,
            commence_time=commence_time,
            home_score=home_score,
            away_score=away_score,
            completed=completed,
            odds=odds_list
        )
    
    # Implement required abstract methods from BaseSportsAPI
    async def get_teams(self, league: Optional[str] = None) -> List[Team]:
        """Get teams (not directly supported by Odds API)."""
        raise NotImplementedError("Odds API doesn't provide team listings. Use ESPN or NBA API.")
    
    async def get_team(self, team_id: str) -> Team:
        """Get team details (not supported by Odds API)."""
        raise NotImplementedError("Odds API doesn't provide team details. Use ESPN or NBA API.")
    
    async def get_players(self, team_id: Optional[str] = None) -> List[Player]:
        """Get players (not supported by Odds API)."""
        raise NotImplementedError("Odds API doesn't provide player data. Use ESPN or NBA API.")
    
    async def get_player(self, player_id: str) -> Player:
        """Get player details (not supported by Odds API)."""
        raise NotImplementedError("Odds API doesn't provide player data. Use ESPN or NBA API.")
    
    async def get_games(self, 
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None,
                       team_id: Optional[str] = None) -> List[Game]:
        """Get games with basic info (adapted from odds data)."""
        try:
            games_with_odds = await self.get_odds()
            
            games = []
            for game_with_odds in games_with_odds:
                game = Game(
                    id=game_with_odds.game_id,
                    home_team_id=game_with_odds.home_team,  # Team name as ID
                    away_team_id=game_with_odds.away_team,  # Team name as ID
                    scheduled_at=game_with_odds.commence_time,
                    status='finished' if game_with_odds.completed else 'scheduled',
                    season='2024-25',  # Default season
                    home_score=game_with_odds.home_score,
                    away_score=game_with_odds.away_score
                )
                games.append(game)
            
            return games
            
        except Exception as e:
            logger.error(f"Error converting odds to games: {e}")
            raise APIError(f"Failed to get games from odds API: {e}")
    
    async def get_game(self, game_id: str) -> Game:
        """Get specific game details."""
        games = await self.get_games()
        
        for game in games:
            if game.id == game_id:
                return game
        
        raise DataNotFoundError(f"Game {game_id} not found")
    
    async def get_team_stats(self, team_id: str, season: Optional[str] = None) -> Dict[str, Any]:
        """Get team stats (not supported by Odds API)."""
        raise NotImplementedError("Odds API doesn't provide team stats. Use ESPN or NBA API.")
    
    async def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Dict[str, Any]:
        """Get player stats (not supported by Odds API)."""
        raise NotImplementedError("Odds API doesn't provide player stats. Use ESPN or NBA API.")
    
    async def get_usage_info(self) -> Dict[str, Any]:
        """Get API usage information."""
        try:
            response = await self._make_request(
                'GET',
                'sports',
                params={'apiKey': self.api_key}
            )
            
            usage_info = {
                'requests_remaining': response.headers.get('x-requests-remaining'),
                'requests_used': response.headers.get('x-requests-used'),
                'requests_last': response.headers.get('x-requests-last'),
            }
            
            return usage_info
            
        except Exception as e:
            logger.error(f"Error getting usage info: {e}")
            return {}