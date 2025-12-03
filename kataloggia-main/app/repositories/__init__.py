"""
Repository layer for database abstraction
Supports SQLite and Firebase Firestore backends
"""
from app.repositories.repository_factory import get_repository, reset_repository
from app.repositories.base_repository import BaseRepository
from app.repositories.sqlite_repository import SQLiteRepository
from app.repositories.firestore_repository import FirestoreRepository

__all__ = ['get_repository', 'reset_repository', 'BaseRepository', 'SQLiteRepository', 'FirestoreRepository']

