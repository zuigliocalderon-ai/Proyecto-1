from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class SportType(enum.Enum):
    BASKETBALL = "basketball"
    SOCCER = "soccer"
    FOOTBALL = "football"
    BASEBALL = "baseball"
    CRICKET = "cricket"

class MatchStatus(enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live" 
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"

class WeatherCondition(enum.Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"
    WIND = "wind"

class BetType(enum.Enum):
    MONEYLINE = "moneyline"  # Win/loss bet
    SPREAD = "spread"        # Point spread bet
    OVER_UNDER = "over_under"  # Total points over/under
    PROP = "prop"           # Proposition bet

class BetStatus(enum.Enum):
    PENDING = "pending"     # Bet placed, game not finished
    WON = "won"            # Bet won
    LOST = "lost"          # Bet lost
    PUSH = "push"          # Tie/refunded
    CANCELLED = "cancelled" # Bet cancelled

class League(Base):
    __tablename__ = 'leagues'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    sport_type = Column(Enum(SportType), nullable=False)
    country = Column(String(50), nullable=False)
    level = Column(Integer, default=1)  # 1 = top tier, 2 = second tier, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teams = relationship("Team", back_populates="league")
    seasons = relationship("Season", back_populates="league")

class Season(Base):
    __tablename__ = 'seasons'
    
    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    name = Column(String(20), nullable=False)  # e.g., "2023-24"
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    league = relationship("League", back_populates="seasons")
    matches = relationship("Match", back_populates="season")

class Venue(Base):
    __tablename__ = 'venues'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    capacity = Column(Integer)
    surface_type = Column(String(20))  # grass, turf, hardwood, etc.
    is_indoor = Column(Boolean, default=False)
    latitude = Column(Float)
    longitude = Column(Float)
    timezone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teams = relationship("Team", back_populates="home_venue")
    matches = relationship("Match", back_populates="venue")

class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    short_name = Column(String(10))
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    home_venue_id = Column(Integer, ForeignKey('venues.id'))
    founded_year = Column(Integer)
    is_active = Column(Boolean, default=True)
    logo_url = Column(String(255))
    primary_color = Column(String(7))  # hex color
    secondary_color = Column(String(7))  # hex color
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    league = relationship("League", back_populates="teams")
    home_venue = relationship("Venue", back_populates="teams")
    players = relationship("Player", back_populates="team")
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    team_stats = relationship("TeamStats", back_populates="team")

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'))
    position = Column(String(20))
    jersey_number = Column(Integer)
    date_of_birth = Column(DateTime)
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    nationality = Column(String(50))
    is_active = Column(Boolean, default=True)
    contract_start = Column(DateTime)
    contract_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="players")
    player_stats = relationship("PlayerStats", back_populates="player")

class Weather(Base):
    __tablename__ = 'weather'
    
    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    temperature_celsius = Column(Float)
    humidity_percent = Column(Float)
    wind_speed_kmh = Column(Float)
    wind_direction = Column(String(10))  # N, NE, E, SE, S, SW, W, NW
    precipitation_mm = Column(Float, default=0.0)
    condition = Column(Enum(WeatherCondition))
    visibility_km = Column(Float)
    pressure_hpa = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    venue = relationship("Venue")
    matches = relationship("Match", back_populates="weather")

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey('seasons.id'), nullable=False)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False)
    weather_id = Column(Integer, ForeignKey('weather.id'))
    scheduled_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    status = Column(Enum(MatchStatus), default=MatchStatus.SCHEDULED)
    
    # Scores
    home_score = Column(Integer)
    away_score = Column(Integer)
    home_score_periods = Column(Text)  # JSON string for period-by-period scores
    away_score_periods = Column(Text)  # JSON string for period-by-period scores
    
    # Match details
    attendance = Column(Integer)
    referee = Column(String(100))
    round_number = Column(Integer)
    week_number = Column(Integer)
    is_playoff = Column(Boolean, default=False)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    season = relationship("Season", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    venue = relationship("Venue", back_populates="matches")
    weather = relationship("Weather", back_populates="matches")
    match_features = relationship("MatchFeatures", back_populates="match")
    predictions = relationship("Prediction", back_populates="match")

class TeamStats(Base):
    __tablename__ = 'team_stats'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), nullable=False)
    
    # General stats
    games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    points_for = Column(Float, default=0.0)
    points_against = Column(Float, default=0.0)
    
    # Advanced metrics
    win_percentage = Column(Float, default=0.0)
    points_per_game = Column(Float, default=0.0)
    points_allowed_per_game = Column(Float, default=0.0)
    point_differential = Column(Float, default=0.0)
    
    # Home/Away splits
    home_wins = Column(Integer, default=0)
    home_losses = Column(Integer, default=0)
    away_wins = Column(Integer, default=0)
    away_losses = Column(Integer, default=0)
    
    # Recent form (last 5 games)
    last_5_wins = Column(Integer, default=0)
    last_5_losses = Column(Integer, default=0)
    
    # Streak data
    current_streak_type = Column(String(1))  # W or L
    current_streak_length = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="team_stats")
    season = relationship("Season")

class PlayerStats(Base):
    __tablename__ = 'player_stats'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), nullable=False)
    
    # General stats
    games_played = Column(Integer, default=0)
    games_started = Column(Integer, default=0)
    minutes_played = Column(Float, default=0.0)
    
    # Sport-specific stats stored as JSON-like text for flexibility
    stats_data = Column(Text)  # JSON string with sport-specific statistics
    
    # Performance metrics
    efficiency_rating = Column(Float)
    plus_minus = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    player = relationship("Player", back_populates="player_stats")
    season = relationship("Season")

class MatchFeatures(Base):
    __tablename__ = 'match_features'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    
    # Pre-match features
    home_team_ranking = Column(Integer)
    away_team_ranking = Column(Integer)
    home_team_form_last_5 = Column(Float)  # Win percentage in last 5 games
    away_team_form_last_5 = Column(Float)
    head_to_head_home_wins = Column(Integer)
    head_to_head_away_wins = Column(Integer)
    head_to_head_draws = Column(Integer)
    days_since_last_match_home = Column(Integer)
    days_since_last_match_away = Column(Integer)
    
    # Betting odds
    home_win_odds = Column(Float)
    away_win_odds = Column(Float)
    draw_odds = Column(Float)
    over_under_line = Column(Float)
    over_odds = Column(Float)
    under_odds = Column(Float)
    
    # Advanced features
    strength_of_schedule_home = Column(Float)
    strength_of_schedule_away = Column(Float)
    home_advantage_factor = Column(Float)
    injury_impact_home = Column(Float)
    injury_impact_away = Column(Float)
    
    # Additional features as JSON for flexibility
    additional_features = Column(Text)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    match = relationship("Match", back_populates="match_features")

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    model_name = Column(String(50), nullable=False)
    model_version = Column(String(20), nullable=False)
    
    # Predictions
    predicted_winner = Column(String(10))  # home, away, draw
    confidence_score = Column(Float)
    predicted_home_score = Column(Float)
    predicted_away_score = Column(Float)
    predicted_total_score = Column(Float)
    
    # Probabilities
    home_win_probability = Column(Float)
    away_win_probability = Column(Float)
    draw_probability = Column(Float)
    
    # Actual outcomes (filled after match)
    actual_winner = Column(String(10))
    actual_home_score = Column(Integer)
    actual_away_score = Column(Integer)
    actual_total_score = Column(Integer)
    
    # Accuracy metrics
    prediction_correct = Column(Boolean)
    score_prediction_error = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    match = relationship("Match", back_populates="predictions")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255))  # For future authentication
    
    # Betting profile
    starting_balance = Column(Numeric(10, 2), default=100.00)
    current_balance = Column(Numeric(10, 2), default=100.00)
    total_wagered = Column(Numeric(10, 2), default=0.00)
    total_winnings = Column(Numeric(10, 2), default=0.00)
    
    # Account status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bets = relationship("Bet", back_populates="user")

class Bet(Base):
    __tablename__ = 'bets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    prediction_id = Column(Integer, ForeignKey('predictions.id'))  # Optional link to ML prediction
    
    # Bet details
    bet_type = Column(Enum(BetType), nullable=False)
    bet_amount = Column(Numeric(10, 2), nullable=False)
    odds = Column(Float, nullable=False)  # Decimal odds (e.g., 2.5 = +150)
    potential_payout = Column(Numeric(10, 2), nullable=False)  # bet_amount * odds
    
    # Bet selection
    selection = Column(String(20), nullable=False)  # "home", "away", "over", "under", etc.
    line_value = Column(Float)  # For spread/over-under bets
    
    # Result
    status = Column(Enum(BetStatus), default=BetStatus.PENDING)
    actual_payout = Column(Numeric(10, 2), default=0.00)
    profit_loss = Column(Numeric(10, 2), default=0.00)  # actual_payout - bet_amount
    
    # Metadata
    placed_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="bets")
    match = relationship("Match")
    prediction = relationship("Prediction")