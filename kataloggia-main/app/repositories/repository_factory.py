"""
Repository factory
Returns the appropriate repository implementation based on configuration
"""
import os
from flask import current_app
from app.repositories.sqlite_repository import SQLiteRepository
from app.repositories.firestore_repository import FirestoreRepository
from app.config import Config


# Singleton instance
_repository_instance = None


def get_repository():
    """
    Get the repository instance based on DB_BACKEND configuration.
    Returns a singleton instance.
    """
    global _repository_instance
    
    # Get DB_BACKEND - prioritize environment variable over config
    env_db_backend = os.environ.get('DB_BACKEND')
    try:
        # Try to get from Flask app context first
        app_db_backend = current_app.config.get('DB_BACKEND', Config.DB_BACKEND)
    except RuntimeError:
        # No app context, use Config directly
        app_db_backend = Config.DB_BACKEND
    
    # Environment variable takes precedence
    db_backend = env_db_backend if env_db_backend else app_db_backend
    
    # Debug logging
    print(f"[DEBUG get_repository] DB_BACKEND: {db_backend}")
    print(f"[DEBUG get_repository] Environment: {os.environ.get('DB_BACKEND', 'NOT SET')}")
    print(f"[DEBUG get_repository] Config: {Config.DB_BACKEND}")
    
    # Check if we need to recreate the repository (backend changed)
    if _repository_instance is not None:
        # Check if backend matches
        current_backend = 'firestore' if isinstance(_repository_instance, FirestoreRepository) else 'sqlite'
        print(f"[DEBUG get_repository] Current repository: {current_backend}, Required: {db_backend}")
        if current_backend == db_backend:
            return _repository_instance
        else:
            # Backend changed, reset and recreate
            print(f"[WARNING] DB_BACKEND changed from {current_backend} to {db_backend}, recreating repository...")
            _repository_instance = None
    
    # Create appropriate repository
    print(f"[INFO] Creating repository for backend: {db_backend}")
    if db_backend == 'firestore':
        _repository_instance = FirestoreRepository()
        print(f"[INFO] FirestoreRepository created successfully")
    else:
        # Default to SQLite
        _repository_instance = SQLiteRepository()
        print(f"[WARNING] SQLiteRepository created (DB_BACKEND={db_backend}, Firestore expected!)")
    
    return _repository_instance


def reset_repository():
    """Reset the repository singleton (useful for testing)"""
    global _repository_instance
    _repository_instance = None

