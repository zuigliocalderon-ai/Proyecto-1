"""
ESPN API client implementation.

Provides access to ESPN sports data using their public API endpoints.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
import logging
from .base import (
    BaseSportsAPI, Team, Player, Game,
    APIError, DataNotFoundError
)

logger = logging.getLogger(__name__)


class ESPNAPI(BaseSportsAPI):
    """ESPN API client using public ESPN API endpoints."""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 timeout: int = 10,
                 max_retries: int = 3,
                 rate_limit: int = 100):
        super().__init__(
            api_key=api_key,
            base_url="https://site.api.espn.com/apis/site/v2/sports",
            timeout=timeout,
            max_retries=max_retries,
            rate_limit=rate_limit
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """ESPN API headers (API key if provided)."""
        headers = {}
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers
    
    async def get_teams(self, league: Optional[str] = None) -> List[Team]:
        """Get teams from ESPN API."""
        sport = league.lower() if league else 'basketball'
        league_name = 'nba' if sport == 'basketball' else sport
        
        try:
            response = await self._make_request(
                'GET', 
                f'{sport}/{league_name}/teams'
            )
            
            if not response.success:
                raise APIError(f"Failed to fetch teams: {response.status_code}")
            
            sports_data = response.data.get('sports', [{}])[0]
            leagues_data = sports_data.get('leagues', [{}])[0]
            teams_data = leagues_data.get('teams', [])
            
            teams = []
            for team_data in teams_data:
                team_info = team_data.get('team', {})
                
                team = Team(
                    id=str(team_info.get('id', '')),
                    name=team_info.get('displayName', ''),
                    short_name=team_info.get('abbreviation', ''),
                    city=team_info.get('location', ''),
                    league=league_name.upper(),
                    logo_url=self._extract_logo_url(team_info.get('logos', [])),
                    primary_color=team_info.get('color', ''),
                    venue=self._extract_venue_name(team_info.get('venue', {}))
                )
                teams.append(team)
            
            logger.info(f"Retrieved {len(teams)} ESPN teams for {league_name}")
            return teams
            
        except Exception as e:
            logger.error(f"Error fetching ESPN teams: {e}")
            raise APIError(f"Failed to fetch ESPN teams: {e}")
    
    async def get_team(self, team_id: str) -> Team:
        """Get specific team details from ESPN."""
        try:
            response = await self._make_request(
                'GET',
                f'basketball/nba/teams/{team_id}'
            )
            
            if not response.success:
                raise DataNotFoundError(f"Team {team_id} not found")
            
            team_info = response.data.get('team', {})
            
            if not team_info:
                raise DataNotFoundError(f"Team {team_id} not found")
            
            return Team(
                id=str(team_info.get('id', '')),
                name=team_info.get('displayName', ''),
                short_name=team_info.get('abbreviation', ''),
                city=team_info.get('location', ''),
                league='NBA',
                logo_url=self._extract_logo_url(team_info.get('logos', [])),
                primary_color=team_info.get('color', ''),
                venue=self._extract_venue_name(team_info.get('venue', {}))
            )
            
        except Exception as e:
            logger.error(f"Error fetching ESPN team {team_id}: {e}")
            if isinstance(e, (DataNotFoundError, APIError)):
                raise
            raise APIError(f"Failed to fetch ESPN team {team_id}: {e}")
    
    async def get_players(self, team_id: Optional[str] = None) -> List[Player]:
        """Get players from ESPN API."""
        try:
            if team_id:
                response = await self._make_request(
                    'GET',
                    f'basketball/nba/teams/{team_id}/roster'
                )
            else:
                # ESPN doesn't have a general players endpoint, need to fetch per team
                teams = await self.get_teams('basketball')
                all_players = []
                
                for team in teams:
                    team_players = await self.get_players(team.id)
                    all_players.extend(team_players)
                
                return all_players
            
            if not response.success:
                raise APIError(f"Failed to fetch players: {response.status_code}")
            
            athletes_data = response.data.get('athletes', [])
            
            players = []
            for athlete_data in athletes_data:
                athlete_info = athlete_data.get('athlete', {})
                
                # Handle missing name fields - use displayName as fallback
                first_name = athlete_info.get('firstName', '')
                last_name = athlete_info.get('lastName', '')
                
                # If names are missing, try to parse from displayName
                if not first_name and not last_name:
                    display_name = athlete_info.get('displayName', '')
                    if display_name:
                        name_parts = display_name.split(' ', 1)
                        first_name = name_parts[0] if name_parts else ''
                        last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Skip players with no name data
                if not first_name and not last_name:
                    continue
                
                player = Player(
                    id=str(athlete_info.get('id', '')),
                    first_name=first_name,
                    last_name=last_name,
                    team_id=team_id or '',
                    position=athlete_info.get('position', {}).get('abbreviation', ''),
                    jersey_number=athlete_info.get('jersey', None),
                    height=athlete_info.get('height', None),
                    weight=athlete_info.get('weight', None),
                    date_of_birth=self._parse_birth_date(athlete_info.get('dateOfBirth'))
                )
                players.append(player)
            
            logger.info(f"Retrieved {len(players)} ESPN players")
            return players
            
        except Exception as e:
            logger.error(f"Error fetching ESPN players: {e}")
            raise APIError(f"Failed to fetch ESPN players: {e}")
    
    async def get_player(self, player_id: str) -> Player:
        """Get specific player details from ESPN."""
        try:
            response = await self._make_request(
                'GET',
                f'basketball/nba/athletes/{player_id}'
            )
            
            if not response.success:
                raise DataNotFoundError(f"Player {player_id} not found")
            
            athlete_info = response.data.get('athlete', {})
            
            if not athlete_info:
                raise DataNotFoundError(f"Player {player_id} not found")
            
            # Extract team ID from team data
            team_info = athlete_info.get('team', {})
            team_id = str(team_info.get('id', '')) if team_info else ''
            
            return Player(
                id=str(athlete_info.get('id', '')),
                first_name=athlete_info.get('firstName', ''),
                last_name=athlete_info.get('lastName', ''),
                team_id=team_id,
                position=athlete_info.get('position', {}).get('abbreviation', ''),
                jersey_number=athlete_info.get('jersey', None),
                height=athlete_info.get('height', None),
                weight=athlete_info.get('weight', None),
                date_of_birth=self._parse_birth_date(athlete_info.get('dateOfBirth'))
            )
            
        except Exception as e:
            logger.error(f"Error fetching ESPN player {player_id}: {e}")
            if isinstance(e, (DataNotFoundError, APIError)):
                raise
            raise APIError(f"Failed to fetch ESPN player {player_id}: {e}")
    
    async def get_games(self, 
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None,
                       team_id: Optional[str] = None) -> List[Game]:
        """Get games from ESPN API."""
        try:
            params = {}
            if start_date:
                params['dates'] = start_date.strftime('%Y%m%d')
            if end_date and start_date:
                end_str = end_date.strftime('%Y%m%d')
                params['dates'] = f"{params['dates']}-{end_str}"
            
            endpoint = 'basketball/nba/scoreboard'
            if team_id:
                endpoint = f'basketball/nba/teams/{team_id}/schedule'
            
            response = await self._make_request('GET', endpoint, params=params)
            
            if not response.success:
                raise APIError(f"Failed to fetch games: {response.status_code}")
            
            if team_id:
                events_data = response.data.get('events', [])
            else:
                events_data = response.data.get('events', [])
            
            games = []
            for event_data in events_data:
                competitions = event_data.get('competitions', [{}])
                if not competitions:
                    continue
                    
                competition = competitions[0]
                competitors = competition.get('competitors', [])
                
                home_team = next((c for c in competitors if c.get('homeAway') == 'home'), {})
                away_team = next((c for c in competitors if c.get('homeAway') == 'away'), {})
                
                # Parse date
                date_str = event_data.get('date', '')
                try:
                    scheduled_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    scheduled_at = datetime.now()
                
                game = Game(
                    id=str(event_data.get('id', '')),
                    home_team_id=str(home_team.get('team', {}).get('id', '')),
                    away_team_id=str(away_team.get('team', {}).get('id', '')),
                    scheduled_at=scheduled_at,
                    status=event_data.get('status', {}).get('type', {}).get('description', 'scheduled'),
                    season=str(event_data.get('season', {}).get('year', '')),
                    home_score=home_team.get('score', None),
                    away_score=away_team.get('score', None),
                    venue=competition.get('venue', {}).get('fullName', None)
                )
                games.append(game)
            
            logger.info(f"Retrieved {len(games)} ESPN games")
            return games
            
        except Exception as e:
            logger.error(f"Error fetching ESPN games: {e}")
            raise APIError(f"Failed to fetch ESPN games: {e}")
    
    async def get_game(self, game_id: str) -> Game:
        """Get specific game details from ESPN."""
        try:
            response = await self._make_request(
                'GET',
                f'basketball/nba/summary',
                params={'event': game_id}
            )
            
            if not response.success:
                raise DataNotFoundError(f"Game {game_id} not found")
            
            header_data = response.data.get('header', {})
            competition = header_data.get('competition', {})
            competitors = competition.get('competitors', [])
            
            if not competitors:
                raise DataNotFoundError(f"Game {game_id} not found")
            
            home_team = next((c for c in competitors if c.get('homeAway') == 'home'), {})
            away_team = next((c for c in competitors if c.get('homeAway') == 'away'), {})
            
            # Parse date
            date_str = header_data.get('date', '')
            try:
                scheduled_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                scheduled_at = datetime.now()
            
            return Game(
                id=game_id,
                home_team_id=str(home_team.get('team', {}).get('id', '')),
                away_team_id=str(away_team.get('team', {}).get('id', '')),
                scheduled_at=scheduled_at,
                status=header_data.get('status', {}).get('type', {}).get('description', 'scheduled'),
                season=str(header_data.get('season', {}).get('year', '')),
                home_score=home_team.get('score', None),
                away_score=away_team.get('score', None),
                venue=competition.get('venue', {}).get('fullName', None),
                attendance=competition.get('attendance', None)
            )
            
        except Exception as e:
            logger.error(f"Error fetching ESPN game {game_id}: {e}")
            if isinstance(e, (DataNotFoundError, APIError)):
                raise
            raise APIError(f"Failed to fetch ESPN game {game_id}: {e}")
    
    async def get_team_stats(self, team_id: str, season: Optional[str] = None) -> Dict[str, Any]:
        """Get team statistics from ESPN."""
        try:
            params = {}
            if season:
                params['season'] = season
            
            response = await self._make_request(
                'GET',
                f'basketball/nba/teams/{team_id}/statistics',
                params=params
            )
            
            if not response.success:
                raise APIError(f"Failed to fetch team stats: {response.status_code}")
            
            return response.data.get('stats', {})
            
        except Exception as e:
            logger.error(f"Error fetching ESPN team stats for {team_id}: {e}")
            raise APIError(f"Failed to fetch ESPN team stats: {e}")
    
    async def get_player_stats(self, player_id: str, season: Optional[str] = None) -> Dict[str, Any]:
        """Get player statistics from ESPN."""
        try:
            params = {}
            if season:
                params['season'] = season
            
            response = await self._make_request(
                'GET',
                f'basketball/nba/athletes/{player_id}/statistics',
                params=params
            )
            
            if not response.success:
                raise APIError(f"Failed to fetch player stats: {response.status_code}")
            
            return response.data.get('stats', {})
            
        except Exception as e:
            logger.error(f"Error fetching ESPN player stats for {player_id}: {e}")
            raise APIError(f"Failed to fetch ESPN player stats: {e}")
    
    # Helper methods
    def _extract_logo_url(self, logos: List[Dict]) -> Optional[str]:
        """Extract logo URL from logos array."""
        if not logos:
            return None
        
        # Prefer higher resolution logos
        for logo in logos:
            if logo.get('width', 0) >= 500:
                return logo.get('href')
        
        # Fallback to any available logo
        return logos[0].get('href') if logos else None
    
    def _extract_venue_name(self, venue: Dict) -> Optional[str]:
        """Extract venue name from venue object."""
        return venue.get('fullName') or venue.get('name')
    
    def _parse_birth_date(self, birth_date_str: Optional[str]) -> Optional[date]:
        """Parse birth date string to date object."""
        if not birth_date_str:
            return None
        
        try:
            return datetime.fromisoformat(birth_date_str.replace('Z', '+00:00')).date()
        except:
            return None