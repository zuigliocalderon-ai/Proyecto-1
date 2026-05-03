import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from .models import Base

load_dotenv()

# Database configuration
class DatabaseConfig:
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/sports_predictions')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }

# Global database instances
db = SQLAlchemy()
migrate = Migrate()

def init_database(app):
    """Initialize database with Flask app"""
    app.config.from_object(DatabaseConfig)
    db.init_app(app)
    migrate.init_app(app, db)
    return db

def create_engine_and_session():
    """Create SQLAlchemy engine and session for standalone usage"""
    engine = create_engine(DatabaseConfig.DATABASE_URL, **DatabaseConfig.SQLALCHEMY_ENGINE_OPTIONS)
    Session = sessionmaker(bind=engine)
    return engine, Session

def test_db_connection():
    """Test database connection"""
    try:
        engine, Session = create_engine_and_session()
        session = Session()
        
        # Test basic query
        result = session.execute(text('SELECT version();'))
        version = result.fetchone()[0]
        print(f"✓ Database connected: {version}")
        
        # Test pgvector extension
        try:
            session.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
            print("✓ pgvector extension available")
        except Exception as e:
            print(f"⚠ pgvector not available: {e}")
        
        # Test TimescaleDB extension
        try:
            session.execute(text('CREATE EXTENSION IF NOT EXISTS timescaledb;'))
            print("✓ TimescaleDB extension available")
        except Exception as e:
            print(f"⚠ TimescaleDB not available: {e}")
        
        session.commit()
        session.close()
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def create_all_tables():
    """Create all tables in the database"""
    try:
        engine, _ = create_engine_and_session()
        Base.metadata.create_all(engine)
        print("✓ All tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        return False