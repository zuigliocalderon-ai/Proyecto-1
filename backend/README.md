# Sports Predictions Backend

Industry-standard backend architecture for sports predictions platform with ML capabilities.

## 📁 Project Structure

```
backend/
├── src/                          # Source code
│   ├── api/                      # API layer
│   │   ├── clients/              # External API clients (ESPN, NBA)
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Base API client with rate limiting
│   │   │   ├── espn_api.py       # ESPN API client
│   │   │   └── nba_api.py        # NBA API client with fallback
│   │   └── app.py                # Flask web application
│   ├── core/                     # Core business logic
│   │   ├── __init__.py
│   │   ├── database.py           # Database configuration & connection
│   │   ├── models.py             # SQLAlchemy ORM models
│   │   └── seed_data.py          # Sample data creation
│   ├── services/                 # Business logic services
│   ├── utils/                    # Utility functions
│   └── schemas/                  # Data validation schemas
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   │   ├── test_base_api.py      # API client base tests
│   │   └── test_nba_api.py       # NBA API tests
│   ├── integration/              # Integration tests
│   └── conftest.py               # Pytest configuration
├── scripts/                      # Management scripts
│   ├── db_manager.py             # Database management CLI
│   ├── test_*.py                 # Test scripts
├── config/                       # Configuration files
├── migrations/                   # Alembic database migrations
├── pytest.ini                   # Test configuration
└── requirements.txt              # Python dependencies
```

## 🚀 Quick Start

### Database Management
```bash
# Initialize database with sample data
python scripts/db_manager.py init

# Check database status
python scripts/db_manager.py status

# Reset database
python scripts/db_manager.py reset
```

### Run Application
```bash
# From backend directory
python -m src.api.app
```

### Run Tests
```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# With coverage
pytest --cov=src
```

## 🏗️ Architecture Features

- **Extensible API clients** with consistent interfaces
- **Rate limiting** and **error handling**
- **Database connection pooling**
- **Migration system** with Alembic
- **Comprehensive testing** with pytest
- **Industry-standard structure** for scalability

## 📊 API Clients

### ESPN API (Primary)
- ✅ 30 NBA teams
- ✅ Player rosters
- ✅ Live game data
- ✅ Reliable and accessible

### NBA Stats API (Fallback)
- ✅ 30 NBA teams (fallback data)
- ✅ Complete team structure
- ✅ Graceful degradation

Both APIs implement the same interface for easy switching and future extensions.

## 🧪 Testing

- **Unit tests** for individual components
- **Integration tests** for API interactions
- **Mock data** for reliable testing
- **80% coverage requirement**

## 📈 Next Steps

1. Data transformation layer
2. ML feature engineering
3. Caching with Redis
4. API versioning
5. Production deployment