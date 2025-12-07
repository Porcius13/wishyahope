"""
Repository layer for database abstraction
Supports SQLite (deprecated) and Firebase Firestore backends
"""
from app.repositories.repository_factory import get_repository, reset_repository
from app.repositories.base_repository import BaseRepository
from app.repositories.firestore_repository import FirestoreRepository

# SQLite repository is optional (deprecated)
try:
    from app.repositories.sqlite_repository import SQLiteRepository
    __all__ = ['get_repository', 'reset_repository', 'BaseRepository', 'SQLiteRepository', 'FirestoreRepository']
except ImportError:
    SQLiteRepository = None
    __all__ = ['get_repository', 'reset_repository', 'BaseRepository', 'FirestoreRepository']

