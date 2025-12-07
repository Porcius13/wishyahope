"""
Configuration settings
Central place for secrets, database paths/URLs and future Redis/Celery config.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration"""

    # Core secret
    SECRET_KEY = os.environ.get('SECRET_KEY', 'favit-secret-key-2025')

    # Database backend: 'sqlite' or 'firestore'
    # Default is now 'firestore' - SQLite support is deprecated
    DB_BACKEND = os.environ.get('DB_BACKEND', 'firestore')

    # Database path for raw sqlite3 usage (non-SQLAlchemy code)
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'favit.db')

    # SQLAlchemy URL: prefer DATABASE_URL, fall back to sqlite with DATABASE_PATH
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{DATABASE_PATH}',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Firebase Configuration
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', 'miayis')
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', None)
    # If FIREBASE_CREDENTIALS_PATH is not set, Firebase Admin SDK will use Application Default Credentials

    # Redis / Celery (for future use)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 3600
    
    # Scraping settings
    SCRAPING_TIMEOUT = 60
    SCRAPING_RETRY_COUNT = 3
    
    # JWT settings (gelecekte kullanılacak)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    # Note: SQLite in-memory database is still used for testing
    # If you want to use Firestore for testing, set DB_BACKEND=firestore
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

