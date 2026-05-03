from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .database import DatabaseConfig, create_engine_and_session
from .models import (
    Base, League, Season, Venue, Team, Player, Weather, Match, 
    TeamStats, PlayerStats, MatchFeatures, Prediction, User, Bet,
    SportType, MatchStatus, WeatherCondition, BetType, BetStatus
)

def create_seed_data():
    """Create sample data for all tables"""
    engine, Session = create_engine_and_session()
    session = Session()
    
    try:
        # Create all tables manually (bypassing enum issues)
        print("Creating database tables...")
        
        # Drop existing tables first
        Base.metadata.drop_all(engine)
        
        # Create tables without enums
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS leagues (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                sport_type VARCHAR(20) NOT NULL,
                country VARCHAR(50) NOT NULL,
                level INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS venues (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                city VARCHAR(50) NOT NULL,
                country VARCHAR(50) NOT NULL,
                capacity INTEGER,
                surface_type VARCHAR(20),
                is_indoor BOOLEAN DEFAULT FALSE,
                latitude FLOAT,
                longitude FLOAT,
                timezone VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS seasons (
                id SERIAL PRIMARY KEY,
                league_id INTEGER REFERENCES leagues(id),
                name VARCHAR(20) NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                is_current BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS teams (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                short_name VARCHAR(10),
                league_id INTEGER REFERENCES leagues(id),
                home_venue_id INTEGER REFERENCES venues(id),
                founded_year INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                logo_url VARCHAR(255),
                primary_color VARCHAR(7),
                secondary_color VARCHAR(7),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                team_id INTEGER REFERENCES teams(id),
                position VARCHAR(20),
                jersey_number INTEGER,
                date_of_birth TIMESTAMP,
                height_cm INTEGER,
                weight_kg INTEGER,
                nationality VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE,
                contract_start TIMESTAMP,
                contract_end TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS weather (
                id SERIAL PRIMARY KEY,
                venue_id INTEGER REFERENCES venues(id),
                recorded_at TIMESTAMP NOT NULL,
                temperature_celsius FLOAT,
                humidity_percent FLOAT,
                wind_speed_kmh FLOAT,
                wind_direction VARCHAR(10),
                precipitation_mm FLOAT DEFAULT 0.0,
                condition VARCHAR(20),
                visibility_km FLOAT,
                pressure_hpa FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS matches (
                id SERIAL PRIMARY KEY,
                season_id INTEGER REFERENCES seasons(id),
                home_team_id INTEGER REFERENCES teams(id),
                away_team_id INTEGER REFERENCES teams(id),
                venue_id INTEGER REFERENCES venues(id),
                weather_id INTEGER REFERENCES weather(id),
                scheduled_at TIMESTAMP NOT NULL,
                started_at TIMESTAMP,
                finished_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'scheduled',
                home_score INTEGER,
                away_score INTEGER,
                home_score_periods TEXT,
                away_score_periods TEXT,
                attendance INTEGER,
                referee VARCHAR(100),
                round_number INTEGER,
                week_number INTEGER,
                is_playoff BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS team_stats (
                id SERIAL PRIMARY KEY,
                team_id INTEGER REFERENCES teams(id),
                season_id INTEGER REFERENCES seasons(id),
                games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                points_for FLOAT DEFAULT 0.0,
                points_against FLOAT DEFAULT 0.0,
                win_percentage FLOAT DEFAULT 0.0,
                points_per_game FLOAT DEFAULT 0.0,
                points_allowed_per_game FLOAT DEFAULT 0.0,
                point_differential FLOAT DEFAULT 0.0,
                home_wins INTEGER DEFAULT 0,
                home_losses INTEGER DEFAULT 0,
                away_wins INTEGER DEFAULT 0,
                away_losses INTEGER DEFAULT 0,
                last_5_wins INTEGER DEFAULT 0,
                last_5_losses INTEGER DEFAULT 0,
                current_streak_type VARCHAR(1),
                current_streak_length INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS player_stats (
                id SERIAL PRIMARY KEY,
                player_id INTEGER REFERENCES players(id),
                season_id INTEGER REFERENCES seasons(id),
                games_played INTEGER DEFAULT 0,
                games_started INTEGER DEFAULT 0,
                minutes_played FLOAT DEFAULT 0.0,
                stats_data TEXT,
                efficiency_rating FLOAT,
                plus_minus FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS match_features (
                id SERIAL PRIMARY KEY,
                match_id INTEGER REFERENCES matches(id),
                home_team_ranking INTEGER,
                away_team_ranking INTEGER,
                home_team_form_last_5 FLOAT,
                away_team_form_last_5 FLOAT,
                head_to_head_home_wins INTEGER,
                head_to_head_away_wins INTEGER,
                head_to_head_draws INTEGER,
                days_since_last_match_home INTEGER,
                days_since_last_match_away INTEGER,
                home_win_odds FLOAT,
                away_win_odds FLOAT,
                draw_odds FLOAT,
                over_under_line FLOAT,
                over_odds FLOAT,
                under_odds FLOAT,
                strength_of_schedule_home FLOAT,
                strength_of_schedule_away FLOAT,
                home_advantage_factor FLOAT,
                injury_impact_home FLOAT,
                injury_impact_away FLOAT,
                additional_features TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                match_id INTEGER REFERENCES matches(id),
                model_name VARCHAR(50) NOT NULL,
                model_version VARCHAR(20) NOT NULL,
                predicted_winner VARCHAR(10),
                confidence_score FLOAT,
                predicted_home_score FLOAT,
                predicted_away_score FLOAT,
                predicted_total_score FLOAT,
                home_win_probability FLOAT,
                away_win_probability FLOAT,
                draw_probability FLOAT,
                actual_winner VARCHAR(10),
                actual_home_score INTEGER,
                actual_away_score INTEGER,
                actual_total_score INTEGER,
                prediction_correct BOOLEAN,
                score_prediction_error FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255),
                starting_balance NUMERIC(10, 2) DEFAULT 100.00,
                current_balance NUMERIC(10, 2) DEFAULT 100.00,
                total_wagered NUMERIC(10, 2) DEFAULT 0.00,
                total_winnings NUMERIC(10, 2) DEFAULT 0.00,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS bets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                match_id INTEGER REFERENCES matches(id),
                prediction_id INTEGER REFERENCES predictions(id),
                bet_type VARCHAR(20) NOT NULL,
                bet_amount NUMERIC(10, 2) NOT NULL,
                odds FLOAT NOT NULL,
                potential_payout NUMERIC(10, 2) NOT NULL,
                selection VARCHAR(20) NOT NULL,
                line_value FLOAT,
                status VARCHAR(20) DEFAULT 'pending',
                actual_payout NUMERIC(10, 2) DEFAULT 0.00,
                profit_loss NUMERIC(10, 2) DEFAULT 0.00,
                placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                settled_at TIMESTAMP,
                notes TEXT
            );
        """))
        
        session.commit()
        print("✓ Database tables created successfully")
        
        # Create sample data
        print("Creating sample data...")
        
        # NBA League
        nba = {
            'name': 'NBA',
            'sport_type': 'basketball',
            'country': 'USA',
            'level': 1
        }
        session.execute(text("INSERT INTO leagues (name, sport_type, country, level) VALUES (:name, :sport_type, :country, :level)"), nba)
        
        # Venues
        venues_data = [
            {'name': 'Staples Center', 'city': 'Los Angeles', 'country': 'USA', 'capacity': 20000, 'is_indoor': True},
            {'name': 'Chase Center', 'city': 'San Francisco', 'country': 'USA', 'capacity': 18064, 'is_indoor': True},
            {'name': 'TD Garden', 'city': 'Boston', 'country': 'USA', 'capacity': 19580, 'is_indoor': True}
        ]
        
        for venue in venues_data:
            session.execute(text("""
                INSERT INTO venues (name, city, country, capacity, is_indoor) 
                VALUES (:name, :city, :country, :capacity, :is_indoor)
            """), venue)
        
        # Season
        season_data = {
            'league_id': 1,
            'name': '2024-25',
            'start_date': '2024-10-01',
            'end_date': '2025-04-15',
            'is_current': True
        }
        session.execute(text("""
            INSERT INTO seasons (league_id, name, start_date, end_date, is_current) 
            VALUES (:league_id, :name, :start_date, :end_date, :is_current)
        """), season_data)
        
        # Teams
        teams_data = [
            {'name': 'Los Angeles Lakers', 'short_name': 'LAL', 'league_id': 1, 'home_venue_id': 1, 'founded_year': 1947},
            {'name': 'Golden State Warriors', 'short_name': 'GSW', 'league_id': 1, 'home_venue_id': 2, 'founded_year': 1946},
            {'name': 'Boston Celtics', 'short_name': 'BOS', 'league_id': 1, 'home_venue_id': 3, 'founded_year': 1946}
        ]
        
        for team in teams_data:
            session.execute(text("""
                INSERT INTO teams (name, short_name, league_id, home_venue_id, founded_year) 
                VALUES (:name, :short_name, :league_id, :home_venue_id, :founded_year)
            """), team)
        
        # Sample players
        players_data = [
            {'first_name': 'LeBron', 'last_name': 'James', 'team_id': 1, 'position': 'F', 'jersey_number': 23},
            {'first_name': 'Stephen', 'last_name': 'Curry', 'team_id': 2, 'position': 'G', 'jersey_number': 30},
            {'first_name': 'Jayson', 'last_name': 'Tatum', 'team_id': 3, 'position': 'F', 'jersey_number': 0}
        ]
        
        for player in players_data:
            session.execute(text("""
                INSERT INTO players (first_name, last_name, team_id, position, jersey_number) 
                VALUES (:first_name, :last_name, :team_id, :position, :jersey_number)
            """), player)
        
        # Sample match
        match_data = {
            'season_id': 1,
            'home_team_id': 1,
            'away_team_id': 2,
            'venue_id': 1,
            'scheduled_at': '2024-12-25 20:00:00',
            'status': 'scheduled'
        }
        session.execute(text("""
            INSERT INTO matches (season_id, home_team_id, away_team_id, venue_id, scheduled_at, status) 
            VALUES (:season_id, :home_team_id, :away_team_id, :venue_id, :scheduled_at, :status)
        """), match_data)
        
        # Create default user
        user_data = {
            'id': 1,
            'username': 'demo_user',
            'email': 'demo@example.com',
            'starting_balance': 100.00,
            'current_balance': 100.00
        }
        session.execute(text("""
            INSERT INTO users (id, username, email, starting_balance, current_balance) 
            VALUES (:id, :username, :email, :starting_balance, :current_balance)
        """), user_data)
        
        session.commit()
        print("✓ Sample data created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating seed data: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = create_seed_data()
    if success:
        print("Database setup completed successfully!")
    else:
        print("Database setup failed!")