"""
NBA API client implementation.

Provides access to NBA stats and data using the official NBA stats API
and nba_api Python package endpoints.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
import logging
from .base import (
    BaseSportsAPI, Team, Player, Game, 
    APIError, DataNotFoundError
)

logger = logging.getLogger(__name__)


class NBAAPI(BaseSportsAPI):
    """NBA API client using stats.nba.com endpoints."""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 timeout: int = 15,  # Longer timeout for NBA API
                 max_retries: int = 3,
                 rate_limit: int = 30):  # More conservative rate limit
        super().__init__(
            api_key=api_key,
            base_url="https://stats.nba.com/stats",
            timeout=timeout,
            max_retries=max_retries,
            rate_limit=rate_limit
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """NBA API doesn't require authentication but needs specific headers."""
        return {
            'Host': 'stats.nba.com',
            'Referer': 'https://www.nba.com/',
            'Origin': 'https://www.nba.com',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }
    
    async def get_teams(self, league: Optional[str] = None) -> List[Team]:
        """Get all NBA teams using a simpler approach."""
        try:
            # Use a more basic endpoint that's more reliable
            response = await self._make_request('GET', 'teamdetails', params={'TeamID': '1610612737'})
            
            if not response.success:
                # Fallback: Use hardcoded NBA team data if API fails
                logger.warning("NBA API not accessible, using fallback team data")
                return self._get_fallback_teams()
            
            # If we get here, API is working, so try the real endpoint
            response = await self._make_request('GET', 'commonteamyears', params={'LeagueID': '00'})
            
            if not response.success:
                logger.warning("NBA teams endpoint failed, using fallback")
                return self._get_fallback_teams()
            
            teams_data = response.data.get('resultSets', [{}])[0].get('rowSet', [])
            headers = response.data.get('resultSets', [{}])[0].get('headers', [])
            
            teams = []
            # Filter for current teams only (most recent year)
            if teams_data:
                current_year = max(row[1] for row in teams_data if len(row) > 1)
                
                for team_row in teams_data:
                    if len(team_row) > 1 and team_row[1] == current_year:
                        team_dict = dict(zip(headers, team_row))
                        
                        team = Team(
                            id=str(team_dict.get('TEAM_ID', '')),
                            name=team_dict.get('TEAM_NAME', ''),
                            short_name=team_dict.get('ABBREVIATION', ''),
                            city=team_dict.get('TEAM_CITY', ''),
                            league='NBA',
                            conference=team_dict.get('CONFERENCE', ''),
                            division=team_dict.get('DIVISION', '')
                        )
                        teams.append(team)
            
            if not teams:
                logger.warning("No teams parsed from NBA API, using fallback")
                return self._get_fallback_teams()
            
            logger.info(f"Retrieved {len(teams)} NBA teams")
            return teams
            
        except Exception as e:
            logger.warning(f"NBA API error: {e}, using fallback teams")
            return self._get_fallback_teams()
    
    def _get_fallback_teams(self) -> List[Team]:
        """Fallback NBA team data when API is not accessible."""
        fallback_teams = [
            # Eastern Conference - Atlantic
            {"id": "1610612738", "name": "Boston Celtics", "short_name": "BOS", "city": "Boston", "conference": "East", "division": "Atlantic"},
            {"id": "1610612751", "name": "Brooklyn Nets", "short_name": "BKN", "city": "Brooklyn", "conference": "East", "division": "Atlantic"},
            {"id": "1610612752", "name": "New York Knicks", "short_name": "NYK", "city": "New York", "conference": "East", "division": "Atlantic"},
            {"id": "1610612755", "name": "Philadelphia 76ers", "short_name": "PHI", "city": "Philadelphia", "conference": "East", "division": "Atlantic"},
            {"id": "1610612761", "name": "Toronto Raptors", "short_name": "TOR", "city": "Toronto", "conference": "East", "division": "Atlantic"},
            
            # Eastern Conference - Central
            {"id": "1610612741", "name": "Chicago Bulls", "short_name": "CHI", "city": "Chicago", "conference": "East", "division": "Central"},
            {"id": "1610612739", "name": "Cleveland Cavaliers", "short_name": "CLE", "city": "Cleveland", "conference": "East", "division": "Central"},
            {"id": "1610612765", "name": "Detroit Pistons", "short_name": "DET", "city": "Detroit", "conference": "East", "division": "Central"},
            {"id": "1610612754", "name": "Indiana Pacers", "short_name": "IND", "city": "Indiana", "conference": "East", "division": "Central"},
            {"id": "1610612749", "name": "Milwaukee Bucks", "short_name": "MIL", "city": "Milwaukee", "conference": "East", "division": "Central"},
            
            # Eastern Conference - Southeast
            {"id": "1610612737", "name": "Atlanta Hawks", "short_name": "ATL", "city": "Atlanta", "conference": "East", "division": "Southeast"},
            {"id": "1610612766", "name": "Charlotte Hornets", "short_name": "CHA", "city": "Charlotte", "conference": "East", "division": "Southeast"},
            {"id": "1610612748", "name": "Miami Heat", "short_name": "MIA", "city": "Miami", "conference": "East", "division": "Southeast"},
            {"id": "1610612753", "name": "Orlando Magic", "short_name": "ORL", "city": "Orlando", "conference": "East", "division": "Southeast"},
            {"id": "1610612764", "name": "Washington Wizards", "short_name": "WAS", "city": "Washington", "conference": "East", "division": "Southeast"},
            
            # Western Conference - Northwest  
            {"id": "1610612743", "name": "Denver Nuggets", "short_name": "DEN", "city": "Denver", "conference": "West", "division": "Northwest"},
            {"id": "1610612750", "name": "Minnesota Timberwolves", "short_name": "MIN", "city": "Minnesota", "conference": "West", "division": "Northwest"},
            {"id": "1610612760", "name": "Oklahoma City Thunder", "short_name": "OKC", "city": "Oklahoma City", "conference": "West", "division": "Northwest"},
            {"id": "1610612757", "name": "Portland Trail Blazers", "short_name": "POR", "city": "Portland", "conference": "West", "division": "Northwest"},
            {"id": "1610612762", "name": "Utah Jazz", "short_name": "UTA", "city": "Utah", "conference": "West", "division": "Northwest"},
            
            # Western Conference - Pacific
            {"id": "1610612744", "name": "Golden State Warriors", "short_name": "GSW", "city": "Golden State", "conference": "West", "division": "Pacific"},
            {"id": "1610612746", "name": "LA Clippers", "short_name": "LAC", "city": "Los Angeles", "conference": "West", "division": "Pacific"},
            {"id": "1610612747", "name": "Los Angeles Lakers", "short_name": "LAL", "city": "Los Angeles", "conference": "West", "division": "Pacific"},
            {"id": "1610612756", "name": "Phoenix Suns", "short_name": "PHX", "city": "Phoenix", "conference": "West", "division": "Pacific"},
            {"id": "1610612758", "name": "Sacramento Kings", "short_name": "SAC", "city": "Sacramento", "conference": "West", "division": "Pacific"},
            
            # Western Conference - Southwest
            {"id": "1610612742", "name": "Dallas Mavericks", "short_name": "DAL", "city": "Dallas", "conference": "West", "division": "Southwest"},
            {"id": "1610612745", "name": "Houston Rockets", "short_name": "HOU", "city": "Houston", "conference": "West", "division": "Southwest"},
            {"id": "1610612763", "name": "Memphis Grizzlies", "short_name": "MEM", "city": "Memphis", "conference": "West", "division": "Southwest"},
            {"id": "1610612740", "name": "New Orleans Pelicans", "short_name": "NOP", "city": "New Orleans", "conference": "West", "division": "Southwest"},
            {"id": "1610612759", "name": "San Antonio Spurs", "short_name": "SAS", "city": "San Antonio", "conference": "West", "division": "Southwest"},
        ]
        
        teams = []
        for team_data in fallback_teams:
            team = Team(
                id=team_data["id"],
                name=team_data["name"],
                short_name=team_data["short_name"],
                city=team_data["city"],
                league="NBA",
                conference=team_data["conference"],
                division=team_data["division"]
            )
            teams.append(team)
        
        logger.info(f"Using fallback data: {len(teams)} NBA teams")
        return teams
    
    async def get_team(self, team_id: str) -> Team:
        """Get specific NBA team details."""
        try:
            response = await self._make_request(
                'GET', 
                'teaminfocommon',
                params={'TeamID': team_id}
            )
            
            if not response.success:
                raise DataNotFoundError(f"Team {team_id} not found")
            
            team_data = response.data.get('resultSets', [{}])[0].get('rowSet', [[]])[0]
            headers = response.data.get('resultSets', [{}])[0].get('headers', [])
            
            if not team_data:
                raise DataNotFoundError(f"Team {team_id} not found")
            
            team_dict = dict(zip(headers, team_data))
            
            return Team(
                id=str(team_dict.get('TEAM_ID', '')),
                name=team_dict.get('TEAM_NAME', ''),
                short_name=team_dict.get('ABBREVIATION', ''),
                city=team_dict.get('TEAM_CITY', ''),
                league='NBA',
                conference=team_dict.get('TEAM_CONFERENCE', ''),
                division=team_dict.get('TEAM_DIVISION', '')
            )
            
        except Exception as e:
            logger.error(f"Error fetching NBA team {team_id}: {e}")
            if isinstance(e, (DataNotFoundError, APIError)):
                raise
            raise APIError(f"Failed to fetch NBA team {team_id}: {e}")
    
    async def get_players(self, team_id: Optional[str] = None) -> List[Player]:
        """Get NBA players, optionally filtered by team."""
        try:
            params = {}
            if team_id:
                params['TeamID'] = team_id
            
            response = await self._make_request(
                'GET', 
                'commonallplayers',
                params={'IsOnlyCurrentSeason': '1', **params}
            )
            
            if not response.success:
                raise APIError(f"Failed to fetch players: {response.status_code}")
            
            players_data = response.data.get('resultSets', [{}])[0].get('rowSet', [])
            headers = response.data.get('resultSets', [{}])[0].get('headers', [])
            
            players = []
            for player_row in players_data:
                player_dict = dict(zip(headers, player_row))
                
                # Split name if available
                full_name = player_dict.get('DISPLAY_FIRST_LAST', '')
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0] if name_parts else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                player = Player(
                    id=str(player_dict.get('PERSON_ID', '')),
                    first_name=first_name,
                    last_name=last_name,
                    team_id=str(player_dict.get('TEAM_ID', '')),
                    position='',  # Position not in commonallplayers
                    jersey_number=None
                )
                players.append(player)
            
            logger.info(f"Retrieved {len(players)} NBA players")
            return players
            
        except Exception as e:
            logger.error(f"Error fetching NBA players: {e}")
            raise APIError(f"Failed to fetch NBA players: {e}")
    
    async def get_player(self, player_id: str) -> Player:
        """Get specific NBA player details."""
        try:
            response = await self._make_request(
                'GET',
                'commonplayerinfo',
                params={'PlayerID': player_id}
            )
            
            if not response.success:
                raise DataNotFoundError(f"Player {player_id} not found")
            
            player_data = response.data.get('resultSets', [{}])[0].get('rowSet', [[]])[0]
            headers = response.data.get('resultSets', [{}])[0].get('headers', [])
            
            if not player_data:
                raise DataNotFoundError(f"Player {player_id} not found")
            
            player_dict = dict(zip(headers, player_data))
            
            return Player(
                id=str(player_dict.get('PERSON_ID', '')),
                first_name=player_dict.get('FIRST_NAME', ''),
                last_name=player_dict.get('LAST_NAME', ''),
                team_id=str(player_dict.get('TEAM_ID', '')),
                position=player_dict.get('POSITION', ''),
                jersey_number=player_dict.get('JERSEY', None),
                height=player_dict.get('HEIGHT', None),
                weight=player_dict.get('WEIGHT', None)
            )
            
        except Exception as e:
            logger.error(f"Error fetching NBA player {player_id}: {e}")
            if isinstance(e, (DataNotFoundError, APIError)):
                raise
            raise APIError(f"Failed to fetch NBA player {player_id}: {e}")
    
    async def get_games(self, 
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None,
                       team_id: Optional[str] = None) -> List[Game]:
        """Get NBA games for date range or team."""
        try:
            params = {}
            
            if start_date:
                params['DateFrom'] = start_date.strftime('%m/%d/%Y')
            if end_date:
                params['DateTo'] = end_date.strftime('%m/%d/%Y')
            if team_id:
                params['TeamID'] = team_id
            
            response = await self._make_request(
                'GET',
                'leaguegamefinder',
                params=params
            )
            
            if not response.success:
                raise APIError(f"Failed to fetch games: {response.status_code}")
            
            games_data = response.data.get('resultSets', [{}])[0].get('rowSet', [])
            headers = response.data.get('resultSets', [{}])[0].get('headers', [])
            
            games = []
            processed_game_ids = set()
            
            for game_row in games_data:
                game_dict = dict(zip(headers, game_row))
                game_id = str(game_dict.get('GAME_ID', ''))
                
                # Avoid duplicates (API returns home and away records)
                if game_id in processed_game_ids:
                    continue
                processed_game_ids.add(game_id)
                
                # Parse game date
                game_date_str = game_dict.get('GAME_DATE', '')
                try:
                    scheduled_at = datetime.strptime(game_date_str, '%Y-%m-%dT%H:%M:%S')
                except:
                    scheduled_at = datetime.now()
                
                game = Game(
                    id=game_id,
                    home_team_id=str(game_dict.get('TEAM_ID', '')),  # This needs improvement
                    away_team_id='',  # Need to fetch opponent
                    scheduled_at=scheduled_at,
                    status='finished' if game_dict.get('WL') else 'scheduled',
                    season=str(game_dict.get('SEASON_ID', '')),
                    home_score=game_dict.get('PTS', None),
                    away_score=game_dict.get('OPP_PTS', None)
                )
                games.append(game)
            
            logger.info(f"Retrieved {len(games)} NBA games")
            return games
            
        except Exception as e:
            logger.error(f"Error fetching NBA games: {e}")
            raise APIError(f"Failed to fetch NBA games: {e}")
    
    async def get_game(self, game_id: str) -> Game:
        """Get specific NBA game details."""
        try:
            response = await self._make_request(
                'GET',
                'boxscoresummaryv2',
                params={'GameID': game_id}
            )
            
            if not response.success:
                raise DataNotFoundError(f"Game {game_id} not found")
            
            # Extract game summary data
            game_summary = response.data.get('resultSets', [{}])[0].get('rowSet', [[]])[0]
            headers = response.data.get('resultSets', [{}])[0].get('headers', [])
            
            if not game_summary:
                raise DataNotFoundError(f"Game {game_id} not found")
            
            game_dict = dict(zip(headers, game_summary))
            
            return Game(
                id=game_id,
                home_team_id=str(game_dict.get('HOME_TEAM_ID', '')),
                away_team_id=str(game_dict.get('VISITOR_TEAM_ID', '')),
                scheduled_at=datetime.strptime(
                    game_dict.get('GAME_DATE_EST', ''), 
                    '%Y-%m-%dT%H:%M:%S'
                ),
                status='finished',  # Improve status mapping
                season=str(game_dict.get('SEASON', '')),
                home_score=game_dict.get('HOME_TEAM_PTS', None),
                away_score=game_dict.get('VISITOR_TEAM_PTS', None),
                attendance=game_dict.get('ATTENDANCE', None)
            )
            
        except Exception as e:
            logger.error(f"Error fetching NBA game {game_id}: {e}")
            if isinstance(e, (DataNotFoundError, APIError)):
                raise
            raise APIError(f"Failed to fetch NBA game {game_id}: {e}")
    
    async def get_team_stats(self, team_id: str, season: Optional[str] = None) -> Dict[str, Any]:
        """Get NBA team statistics."""
        try:
            params = {'TeamID': team_id}
            if season:
                params['Season'] = season
            
            response = await self._make_request(
                'GET',
                'teamdashboardbygeneralsplits',
                params=params
            )
            
            if not response.success:
                raise APIError(f"Failed to fetch team stats: {response.status_code}")
            
            stats_data = response.data.get('resultSets', [{}])[0].get('rowSet', [[]])[0]
            headers = response.data.get('resultSets', [{}])[0].get('headers', [])
            
            return dict(zip(headers, stats_data))
            
        except Exception as e:
            logger.error(f"Error fetching NBA team stats for {team_id}: {e}")
            raise APIError(f"Failed to fetch NBA team stats: {e}")
    
    async def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Dict[str, Any]:
        """Get NBA player statistics."""
        try:
            params = {'PlayerID': player_id}
            if season:
                params['Season'] = season
            
            response = await self._make_request(
                'GET',
                'playerdashboardbygeneralsplits',
                params=params
            )
            
            if not response.success:
                raise APIError(f"Failed to fetch player stats: {response.status_code}")
            
            stats_data = response.data.get('resultSets', [{}])[0].get('rowSet', [[]])[0]
            headers = response.data.get('resultSets', [{}])[0].get('headers', [])
            
            return dict(zip(headers, stats_data))
            
        except Exception as e:
            logger.error(f"Error fetching NBA player stats for {player_id}: {e}")
            raise APIError(f"Failed to fetch NBA player stats: {e}")