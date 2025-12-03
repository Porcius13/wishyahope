# Firebase Firestore Migration Guide

This document describes the migration from SQLite to Firebase Firestore and how to use the new repository layer.

## Overview

The project now supports two database backends:
- **SQLite** (default): File-based database (`favit.db`)
- **Firebase Firestore**: Cloud-based NoSQL database

The migration uses a **repository pattern** to abstract database operations, allowing seamless switching between backends.

## Architecture

### Repository Layer

The repository layer provides a clean abstraction over database operations:

```
app/repositories/
├── __init__.py              # Factory exports
├── base_repository.py       # Abstract base class
├── sqlite_repository.py     # SQLite implementation
├── firestore_repository.py  # Firestore implementation
└── repository_factory.py   # Factory to get the right repository
```

### Key Components

1. **BaseRepository**: Abstract interface defining all database operations
2. **SQLiteRepository**: Wraps existing SQLite operations
3. **FirestoreRepository**: Implements Firestore operations
4. **Repository Factory**: Returns the appropriate repository based on `DB_BACKEND` config

## Configuration

### Environment Variables

Add these to your environment or `.env` file:

```bash
# Database backend: 'sqlite' or 'firestore'
DB_BACKEND=firestore

# Firebase Configuration
FIREBASE_PROJECT_ID=miayis
FIREBASE_CREDENTIALS_PATH=/path/to/service-account-key.json  # Optional
```

### Firebase Setup

1. **Install Firebase Admin SDK**:
   ```bash
   pip install firebase-admin
   ```

2. **Get Service Account Key** (optional):
   - Go to Firebase Console → Project Settings → Service Accounts
   - Generate a new private key
   - Save it as `service-account-key.json`
   - Set `FIREBASE_CREDENTIALS_PATH` to the file path

   **OR** use Application Default Credentials (recommended for production):
   ```bash
   gcloud auth application-default login
   ```

3. **Update Config**:
   The config is automatically loaded from `app/config.py`:
   ```python
   DB_BACKEND = os.environ.get('DB_BACKEND', 'sqlite')
   FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', 'miayis')
   ```

## Migration Process

### Step 1: Run Migration Script

The migration script transfers all data from SQLite to Firestore:

```bash
python scripts/migrate_to_firestore.py
```

This will:
- Read all data from `favit.db`
- Create corresponding documents in Firestore
- Skip existing records (idempotent)
- Show progress for each table

### Step 2: Switch to Firestore

Set the environment variable:
```bash
export DB_BACKEND=firestore
```

Or update `app/config.py`:
```python
DB_BACKEND = 'firestore'
```

### Step 3: Restart Application

Restart your Flask application. It will automatically use Firestore.

## Using the Repository

### Getting a Repository Instance

```python
from app.repositories import get_repository

repo = get_repository()  # Returns SQLiteRepository or FirestoreRepository
```

### Example Operations

```python
# User operations
user = repo.get_user_by_id(user_id)
user = repo.get_user_by_username(username)
user_id = repo.create_user(username, email, password_hash, ...)

# Product operations
product = repo.get_product_by_id(product_id)
products = repo.get_products_by_user_id(user_id)
product_id = repo.create_product(user_id, name, price, ...)

# And so on for all entities...
```

## Data Model Mapping

### SQLite → Firestore

| SQLite Table | Firestore Collection | Notes |
|-------------|---------------------|-------|
| `users` | `users` | Direct mapping |
| `products` | `products` | Direct mapping |
| `collections` | `collections` | Direct mapping |
| `collection_products` | `collection_products` | Junction table → collection |
| `favorites` | `favorites` | Junction table → collection |
| `price_tracking` | `price_tracking` | Direct mapping |
| `price_history` | `price_history` | Direct mapping |
| `notifications` | `notifications` | Direct mapping |
| `product_import_issues` | `product_import_issues` | Direct mapping |

### Timestamp Handling

- SQLite stores timestamps as strings or datetime objects
- Firestore uses Firestore Timestamp objects
- The repository layer handles conversion automatically

### JSON Fields

- SQLite stores JSON as TEXT (e.g., `images` field)
- Firestore stores JSON as native arrays/objects
- The repository layer handles serialization/deserialization

## Backward Compatibility

The existing `models.py` file still works with SQLite. To fully migrate:

1. **Option A**: Gradually refactor models to use repository pattern
2. **Option B**: Keep models.py for SQLite, use repository directly in new code
3. **Option C**: Create adapter layer in models.py that uses repository

## Testing

### Test with SQLite (default)
```bash
# No changes needed, works as before
python run_local.py
```

### Test with Firestore
```bash
export DB_BACKEND=firestore
python run_local.py
```

## Troubleshooting

### Firebase Authentication Errors

**Error**: `DefaultCredentialsError`

**Solution**: 
- Set `FIREBASE_CREDENTIALS_PATH` to your service account key file
- OR run `gcloud auth application-default login`

### Migration Errors

**Error**: "User already exists"

**Solution**: The migration is idempotent. It skips existing records. This is normal.

### Performance Issues

**Issue**: Slow queries in Firestore

**Solution**:
- Add composite indexes in Firebase Console
- Use pagination for large collections
- Consider caching frequently accessed data

## Next Steps

1. ✅ Repository layer created
2. ✅ Migration script created
3. ⏳ Refactor `models.py` to use repository (optional)
4. ⏳ Update routes to use repository directly (optional)
5. ⏳ Add Firestore indexes for better performance
6. ⏳ Set up Firebase security rules

## Firestore Security Rules

Example security rules (add in Firebase Console):

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users: users can read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Products: users can read/write their own products
    match /products/{productId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Add similar rules for other collections...
  }
}
```

## Support

For issues or questions:
1. Check Firebase Console for errors
2. Review migration script logs
3. Verify environment variables are set correctly
4. Check Firestore indexes are created

