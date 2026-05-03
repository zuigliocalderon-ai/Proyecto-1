#!/usr/bin/env python3
"""
Database Management Script for Sports Predictions Platform

Usage:
    python db_manager.py init          # Initialize database with tables and seed data
    python db_manager.py reset         # Drop all tables and recreate
    python db_manager.py migrate       # Run pending migrations
    python db_manager.py seed          # Add sample data only
    python db_manager.py backup        # Create database backup
    python db_manager.py test          # Test database connection
"""

import sys
import os
import argparse
from datetime import datetime
from sqlalchemy import create_engine, text

# Add parent directory to path to import src modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import test_db_connection, create_engine_and_session
from src.core.seed_data import create_seed_data

def init_database():
    """Initialize database with tables and seed data"""
    print("🚀 Initializing database...")
    
    if not test_db_connection():
        print("❌ Database connection failed")
        return False
        
    success = create_seed_data()
    if success:
        print("✅ Database initialized successfully!")
        return True
    else:
        print("❌ Database initialization failed")
        return False

def reset_database():
    """Drop all tables and recreate with seed data"""
    print("🔄 Resetting database...")
    
    engine, Session = create_engine_and_session()
    session = Session()
    
    try:
        # Drop all tables
        print("Dropping existing tables...")
        session.execute(text("""
            DROP TABLE IF EXISTS bets CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
            DROP TABLE IF EXISTS predictions CASCADE;
            DROP TABLE IF EXISTS match_features CASCADE;
            DROP TABLE IF EXISTS player_stats CASCADE;
            DROP TABLE IF EXISTS team_stats CASCADE;
            DROP TABLE IF EXISTS matches CASCADE;
            DROP TABLE IF EXISTS weather CASCADE;
            DROP TABLE IF EXISTS players CASCADE;
            DROP TABLE IF EXISTS teams CASCADE;
            DROP TABLE IF EXISTS seasons CASCADE;
            DROP TABLE IF EXISTS venues CASCADE;
            DROP TABLE IF EXISTS leagues CASCADE;
        """))
        session.commit()
        print("✓ Tables dropped")
        
        session.close()
        
        # Recreate with seed data
        success = create_seed_data()
        if success:
            print("✅ Database reset successfully!")
            return True
        else:
            print("❌ Database reset failed")
            return False
            
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def run_migrations():
    """Run pending database migrations"""
    print("🔄 Running database migrations...")
    import subprocess
    try:
        result = subprocess.run([
            'python3', '-m', 'flask', 'db', 'upgrade'
        ], env={'FLASK_APP': 'app.py'}, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully!")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def seed_database():
    """Add sample data to existing database"""
    print("🌱 Seeding database...")
    
    engine, Session = create_engine_and_session()
    session = Session()
    
    try:
        # Check if data already exists
        result = session.execute(text("SELECT COUNT(*) FROM leagues"))
        count = result.scalar()
        
        if count > 0:
            print(f"Database already has {count} leagues. Use reset to start fresh.")
            return False
            
        session.close()
        
        # Create seed data
        success = create_seed_data()
        if success:
            print("✅ Database seeded successfully!")
            return True
        else:
            print("❌ Database seeding failed")
            return False
            
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return False
    finally:
        session.close()

def backup_database():
    """Create database backup"""
    print("💾 Creating database backup...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.sql"
    
    try:
        import subprocess
        import os
        
        database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/sports_predictions')
        
        result = subprocess.run([
            'pg_dump', database_url, '-f', backup_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Database backup created: {backup_file}")
            return True
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def test_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    if test_db_connection():
        print("✅ Database connection successful!")
        return True
    else:
        print("❌ Database connection failed!")
        return False

def show_status():
    """Show database status"""
    print("📊 Database Status:")
    
    engine, Session = create_engine_and_session()
    session = Session()
    
    try:
        tables = [
            'leagues', 'venues', 'seasons', 'teams', 'players',
            'weather', 'matches', 'team_stats', 'player_stats',
            'match_features', 'predictions', 'users', 'bets'
        ]
        
        for table in tables:
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Table not found or error")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False
    finally:
        session.close()

def main():
    parser = argparse.ArgumentParser(description='Database Management for Sports Predictions Platform')
    parser.add_argument('command', choices=[
        'init', 'reset', 'migrate', 'seed', 'backup', 'test', 'status'
    ], help='Database operation to perform')
    
    args = parser.parse_args()
    
    commands = {
        'init': init_database,
        'reset': reset_database,
        'migrate': run_migrations,
        'seed': seed_database,
        'backup': backup_database,
        'test': test_connection,
        'status': show_status
    }
    
    if args.command in commands:
        success = commands[args.command]()
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

if __name__ == "__main__":
    main()