import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with common settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_123456789")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Handle DB URL mapping for SQLAlchemy (replacing postgres:// or postgresql:// with postgresql+psycopg://)
    raw_db_url = os.getenv("DATABASE_URL")
    if raw_db_url:
        if raw_db_url.startswith("postgres://"):
            raw_db_url = raw_db_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif raw_db_url.startswith("postgresql://"):
            raw_db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    SQLALCHEMY_DATABASE_URI = raw_db_url or "postgresql+psycopg://postgres:postgres@localhost:5432/smart_task_db"
    
    # Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS

class DevelopmentConfig(Config):
    """Development stage configurations."""
    DEBUG = True
    ENV = "development"

class TestingConfig(Config):
    """Testing stage configurations."""
    TESTING = True
    DEBUG = True
    LOGIN_DISABLED = False  # Ensure @login_required blocks unauthenticated requests in tests
    # In-memory SQLite or testing DB URL
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

class ProductionConfig(Config):
    """Production stage configurations."""
    DEBUG = False
    ENV = "production"
    SESSION_COOKIE_SECURE = True

# Helper dictionary to load config dynamic states
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}
