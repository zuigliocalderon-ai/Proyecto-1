from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import DatabaseConfig, create_engine_and_session
from .models import (
    Base, League, Season, Venue, Team, Player, Weather, Match,
    TeamStats, PlayerStats, MatchFeatures, Prediction, User, Bet
)

def create_seed_data():
    """Create sample data for all tables"""
    engine, Session = create_engine_and_session()
    session = Session()

    try:
        # Create all tables using SQLAlchemy ORM
        print("Creating database tables...")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        print("✓ Database tables created successfully")

        # Create sample data
        print("Creating sample data...")

        # NBA League
        nba = League(
            name='NBA',
            sport_type='basketball',
            country='USA',
            level=1
        )
        session.add(nba)
        session.flush()

        # Venues
        venues_data = [
            Venue(name='Staples Center', city='Los Angeles', country='USA', capacity=20000, is_indoor=True),
            Venue(name='Chase Center', city='San Francisco', country='USA', capacity=18064, is_indoor=True),
            Venue(name='TD Garden', city='Boston', country='USA', capacity=19580, is_indoor=True)
        ]
        session.add_all(venues_data)
        session.flush()

        # Season
        season = Season(
            league_id=nba.id,
            name='2024-25',
            start_date=datetime(2024, 10, 1),
            end_date=datetime(2025, 4, 15),
            is_current=True
        )
        session.add(season)
        session.flush()

        # Teams
        teams_data = [
            Team(name='Los Angeles Lakers', short_name='LAL', league_id=nba.id, home_venue_id=venues_data[0].id, founded_year=1948),
            Team(name='Golden State Warriors', short_name='GSW', league_id=nba.id, home_venue_id=venues_data[1].id, founded_year=1946),
            Team(name='Boston Celtics', short_name='BOS', league_id=nba.id, home_venue_id=venues_data[2].id, founded_year=1957)
        ]
        session.add_all(teams_data)
        session.flush()

        # Players
        players_data = [
            Player(first_name='LeBron', last_name='James', team_id=teams_data[0].id, position='SF', jersey_number=23, nationality='USA'),
            Player(first_name='Stephen', last_name='Curry', team_id=teams_data[1].id, position='PG', jersey_number=30, nationality='USA'),
            Player(first_name='Jayson', last_name='Tatum', team_id=teams_data[2].id, position='SF', jersey_number=0, nationality='USA')
        ]
        session.add_all(players_data)
        session.flush()

        # Weather
        weather = Weather(
            venue_id=venues_data[0].id,
            recorded_at=datetime.now(),
            temperature_celsius=22,
            humidity_percent=45,
            wind_speed_kmh=10,
            condition='Clear'
        )
        session.add(weather)
        session.flush()

        # Match
        match = Match(
            season_id=season.id,
            home_team_id=teams_data[0].id,
            away_team_id=teams_data[1].id,
            venue_id=venues_data[0].id,
            weather_id=weather.id,
            scheduled_at=datetime.now() + timedelta(days=1),
            status='scheduled'
        )
        session.add(match)
        session.flush()

        # Team Stats
        team_stats = TeamStats(
            team_id=teams_data[0].id,
            season_id=season.id,
            games_played=10,
            wins=8,
            losses=2,
            draws=0,
            points_for=1050.0,
            points_against=980.0,
            win_percentage=0.800
        )
        session.add(team_stats)

        # Player Stats
        player_stats = PlayerStats(
            player_id=players_data[0].id,
            season_id=season.id,
            games_played=10,
            games_started=10,
            minutes_played=360.0,
            efficiency_rating=28.5
        )
        session.add(player_stats)

        # Match Features
        match_features = MatchFeatures(
            match_id=match.id,
            home_team_ranking=3,
            away_team_ranking=5,
            home_team_form_last_5=0.8,
            away_team_form_last_5=0.6,
            home_win_odds=1.85,
            away_win_odds=2.05
        )
        session.add(match_features)

        # User
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password',
            starting_balance=1000.00,
            current_balance=1500.00,
            total_wagered=2000.00,
            total_winnings=2500.00
        )
        session.add(user)
        session.flush()

        # Prediction
        prediction = Prediction(
            match_id=match.id,
            model_name='baseline_model',
            model_version='1.0',
            predicted_winner='home',
            confidence_score=0.75,
            home_win_probability=0.75,
            away_win_probability=0.25
        )
        session.add(prediction)
        session.flush()

        # Bet
        bet = Bet(
            user_id=user.id,
            match_id=match.id,
            prediction_id=prediction.id,
            bet_type='moneyline',
            bet_amount=100.00,
            odds=1.85,
            potential_payout=185.00,
            selection='home'
        )
        session.add(bet)

        session.commit()
        print("✓ Sample data created successfully")
        return True

    except Exception as e:
        session.rollback()
        print(f"✗ Error creating seed data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()
