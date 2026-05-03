"""Initial migration: create all tables

Revision ID: 804eecf99e26
Revises: 
Create Date: 2025-06-27 14:12:36.382033

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '804eecf99e26'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create enums only if they don't exist
    connection = op.get_bind()
    
    # Check and create sporttype enum
    result = connection.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'sporttype'"))
    if not result.fetchone():
        op.execute("CREATE TYPE sporttype AS ENUM ('basketball', 'soccer', 'football', 'baseball', 'cricket')")
    
    # Check and create matchstatus enum  
    result = connection.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'matchstatus'"))
    if not result.fetchone():
        op.execute("CREATE TYPE matchstatus AS ENUM ('scheduled', 'live', 'finished', 'postponed', 'cancelled')")
    
    # Check and create weathercondition enum
    result = connection.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'weathercondition'"))
    if not result.fetchone():
        op.execute("CREATE TYPE weathercondition AS ENUM ('clear', 'cloudy', 'rain', 'snow', 'fog', 'wind')")
    
    # Create leagues table
    op.create_table('leagues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('sport_type', sa.Enum('BASKETBALL', 'SOCCER', 'FOOTBALL', 'BASEBALL', 'CRICKET', name='sporttype'), nullable=False),
        sa.Column('country', sa.String(length=50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create seasons table
    op.create_table('seasons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('league_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=20), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create venues table
    op.create_table('venues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('city', sa.String(length=50), nullable=False),
        sa.Column('country', sa.String(length=50), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('surface_type', sa.String(length=20), nullable=True),
        sa.Column('is_indoor', sa.Boolean(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create teams table
    op.create_table('teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('short_name', sa.String(length=10), nullable=True),
        sa.Column('league_id', sa.Integer(), nullable=False),
        sa.Column('home_venue_id', sa.Integer(), nullable=True),
        sa.Column('founded_year', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('logo_url', sa.String(length=255), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True),
        sa.Column('secondary_color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['home_venue_id'], ['venues.id'], ),
        sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create players table
    op.create_table('players',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('position', sa.String(length=20), nullable=True),
        sa.Column('jersey_number', sa.Integer(), nullable=True),
        sa.Column('date_of_birth', sa.DateTime(), nullable=True),
        sa.Column('height_cm', sa.Integer(), nullable=True),
        sa.Column('weight_kg', sa.Integer(), nullable=True),
        sa.Column('nationality', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('contract_start', sa.DateTime(), nullable=True),
        sa.Column('contract_end', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create weather table
    op.create_table('weather',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('venue_id', sa.Integer(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('temperature_celsius', sa.Float(), nullable=True),
        sa.Column('humidity_percent', sa.Float(), nullable=True),
        sa.Column('wind_speed_kmh', sa.Float(), nullable=True),
        sa.Column('wind_direction', sa.String(length=10), nullable=True),
        sa.Column('precipitation_mm', sa.Float(), nullable=True),
        sa.Column('condition', sa.Enum('CLEAR', 'CLOUDY', 'RAIN', 'SNOW', 'FOG', 'WIND', name='weathercondition'), nullable=True),
        sa.Column('visibility_km', sa.Float(), nullable=True),
        sa.Column('pressure_hpa', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create matches table
    op.create_table('matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('season_id', sa.Integer(), nullable=False),
        sa.Column('home_team_id', sa.Integer(), nullable=False),
        sa.Column('away_team_id', sa.Integer(), nullable=False),
        sa.Column('venue_id', sa.Integer(), nullable=False),
        sa.Column('weather_id', sa.Integer(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('SCHEDULED', 'LIVE', 'FINISHED', 'POSTPONED', 'CANCELLED', name='matchstatus'), nullable=True),
        sa.Column('home_score', sa.Integer(), nullable=True),
        sa.Column('away_score', sa.Integer(), nullable=True),
        sa.Column('home_score_periods', sa.Text(), nullable=True),
        sa.Column('away_score_periods', sa.Text(), nullable=True),
        sa.Column('attendance', sa.Integer(), nullable=True),
        sa.Column('referee', sa.String(length=100), nullable=True),
        sa.Column('round_number', sa.Integer(), nullable=True),
        sa.Column('week_number', sa.Integer(), nullable=True),
        sa.Column('is_playoff', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['away_team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['home_team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ),
        sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], ),
        sa.ForeignKeyConstraint(['weather_id'], ['weather.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create team_stats table
    op.create_table('team_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('season_id', sa.Integer(), nullable=False),
        sa.Column('games_played', sa.Integer(), nullable=True),
        sa.Column('wins', sa.Integer(), nullable=True),
        sa.Column('losses', sa.Integer(), nullable=True),
        sa.Column('draws', sa.Integer(), nullable=True),
        sa.Column('points_for', sa.Float(), nullable=True),
        sa.Column('points_against', sa.Float(), nullable=True),
        sa.Column('win_percentage', sa.Float(), nullable=True),
        sa.Column('points_per_game', sa.Float(), nullable=True),
        sa.Column('points_allowed_per_game', sa.Float(), nullable=True),
        sa.Column('point_differential', sa.Float(), nullable=True),
        sa.Column('home_wins', sa.Integer(), nullable=True),
        sa.Column('home_losses', sa.Integer(), nullable=True),
        sa.Column('away_wins', sa.Integer(), nullable=True),
        sa.Column('away_losses', sa.Integer(), nullable=True),
        sa.Column('last_5_wins', sa.Integer(), nullable=True),
        sa.Column('last_5_losses', sa.Integer(), nullable=True),
        sa.Column('current_streak_type', sa.String(length=1), nullable=True),
        sa.Column('current_streak_length', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create player_stats table
    op.create_table('player_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('season_id', sa.Integer(), nullable=False),
        sa.Column('games_played', sa.Integer(), nullable=True),
        sa.Column('games_started', sa.Integer(), nullable=True),
        sa.Column('minutes_played', sa.Float(), nullable=True),
        sa.Column('stats_data', sa.Text(), nullable=True),
        sa.Column('efficiency_rating', sa.Float(), nullable=True),
        sa.Column('plus_minus', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create match_features table
    op.create_table('match_features',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('home_team_ranking', sa.Integer(), nullable=True),
        sa.Column('away_team_ranking', sa.Integer(), nullable=True),
        sa.Column('home_team_form_last_5', sa.Float(), nullable=True),
        sa.Column('away_team_form_last_5', sa.Float(), nullable=True),
        sa.Column('head_to_head_home_wins', sa.Integer(), nullable=True),
        sa.Column('head_to_head_away_wins', sa.Integer(), nullable=True),
        sa.Column('head_to_head_draws', sa.Integer(), nullable=True),
        sa.Column('days_since_last_match_home', sa.Integer(), nullable=True),
        sa.Column('days_since_last_match_away', sa.Integer(), nullable=True),
        sa.Column('home_win_odds', sa.Float(), nullable=True),
        sa.Column('away_win_odds', sa.Float(), nullable=True),
        sa.Column('draw_odds', sa.Float(), nullable=True),
        sa.Column('over_under_line', sa.Float(), nullable=True),
        sa.Column('over_odds', sa.Float(), nullable=True),
        sa.Column('under_odds', sa.Float(), nullable=True),
        sa.Column('strength_of_schedule_home', sa.Float(), nullable=True),
        sa.Column('strength_of_schedule_away', sa.Float(), nullable=True),
        sa.Column('home_advantage_factor', sa.Float(), nullable=True),
        sa.Column('injury_impact_home', sa.Float(), nullable=True),
        sa.Column('injury_impact_away', sa.Float(), nullable=True),
        sa.Column('additional_features', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create predictions table
    op.create_table('predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(length=50), nullable=False),
        sa.Column('model_version', sa.String(length=20), nullable=False),
        sa.Column('predicted_winner', sa.String(length=10), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('predicted_home_score', sa.Float(), nullable=True),
        sa.Column('predicted_away_score', sa.Float(), nullable=True),
        sa.Column('predicted_total_score', sa.Float(), nullable=True),
        sa.Column('home_win_probability', sa.Float(), nullable=True),
        sa.Column('away_win_probability', sa.Float(), nullable=True),
        sa.Column('draw_probability', sa.Float(), nullable=True),
        sa.Column('actual_winner', sa.String(length=10), nullable=True),
        sa.Column('actual_home_score', sa.Integer(), nullable=True),
        sa.Column('actual_away_score', sa.Integer(), nullable=True),
        sa.Column('actual_total_score', sa.Integer(), nullable=True),
        sa.Column('prediction_correct', sa.Boolean(), nullable=True),
        sa.Column('score_prediction_error', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('predictions')
    op.drop_table('match_features')
    op.drop_table('player_stats')
    op.drop_table('team_stats')
    op.drop_table('matches')
    op.drop_table('weather')
    op.drop_table('players')
    op.drop_table('teams')
    op.drop_table('venues')
    op.drop_table('seasons')
    op.drop_table('leagues')
    op.execute('DROP TYPE IF EXISTS weathercondition')
    op.execute('DROP TYPE IF EXISTS matchstatus')
    op.execute('DROP TYPE IF EXISTS sporttype')
