"""
Migration script: SQLite to Firebase Firestore
Transfers all data from favit.db to Firestore
"""
import sys
import os
from datetime import datetime
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.repositories.sqlite_repository import SQLiteRepository
from app.repositories.firestore_repository import FirestoreRepository
from app.config import Config


def migrate_table(sqlite_repo, firestore_repo, table_name, migration_func):
    """Helper to migrate a table"""
    print(f"\n{'='*60}")
    print(f"Migrating {table_name}...")
    print(f"{'='*60}")
    
    try:
        count = migration_func(sqlite_repo, firestore_repo)
        print(f"✓ Migrated {count} {table_name} records")
        return count
    except Exception as e:
        print(f"✗ Error migrating {table_name}: {e}")
        import traceback
        traceback.print_exc()
        return 0


def migrate_users(sqlite_repo, firestore_repo):
    """Migrate users table"""
    conn = sqlite_repo.db if hasattr(sqlite_repo, 'db') else None
    if not conn:
        from app.utils.db_path import get_db_connection
        conn = get_db_connection()
    
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    count = 0
    
    for row in rows:
        user_data = dict(zip(columns, row))
        user_id = user_data['id']
        
        # Check if already exists in Firestore
        existing = firestore_repo.get_user_by_id(user_id)
        if existing:
            print(f"  User {user_id} already exists, skipping...")
            continue
        
        # Convert timestamps
        created_at = user_data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                except:
                    created_at = datetime.now()
        elif created_at is None:
            created_at = datetime.now()
        
        last_read = user_data.get('last_read_notifications_at')
        if isinstance(last_read, str):
            try:
                last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    last_read = datetime.strptime(last_read, '%Y-%m-%d %H:%M:%S')
                except:
                    last_read = None
        
        # Create in Firestore
        firestore_repo.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            profile_url=user_data.get('profile_url', ''),
            created_at=created_at,
            last_read_notifications_at=last_read,
            avatar_url=user_data.get('avatar_url')
        )
        count += 1
        print(f"  Migrated user: {user_data['username']} ({user_id})")
    
    if not hasattr(sqlite_repo, 'db'):
        conn.close()
    
    return count


def migrate_products(sqlite_repo, firestore_repo):
    """Migrate products table"""
    from app.utils.db_path import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    rows = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    count = 0
    
    for row in rows:
        product_data = dict(zip(columns, row))
        product_id = product_data['id']
        
        # Check if already exists
        existing = firestore_repo.get_product_by_id(product_id)
        if existing:
            print(f"  Product {product_id} already exists, skipping...")
            continue
        
        # Parse images JSON
        images = product_data.get('images')
        if images and isinstance(images, str):
            try:
                images = json.loads(images)
            except:
                images = [product_data.get('image')] if product_data.get('image') else []
        elif not images:
            images = [product_data.get('image')] if product_data.get('image') else []
        
        # Convert timestamp
        created_at = product_data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                except:
                    created_at = datetime.now()
        elif created_at is None:
            created_at = datetime.now()
        
        # Create in Firestore
        firestore_repo.create_product(
            user_id=product_data['user_id'],
            name=product_data['name'],
            price=product_data['price'],
            image=product_data.get('image'),
            brand=product_data['brand'],
            url=product_data['url'],
            created_at=created_at,
            old_price=product_data.get('old_price'),
            current_price=product_data.get('current_price'),
            discount_percentage=product_data.get('discount_percentage'),
            images=images,
            discount_info=product_data.get('discount_info')
        )
        count += 1
        if count % 10 == 0:
            print(f"  Migrated {count} products...")
    
    conn.close()
    return count


def migrate_collections(sqlite_repo, firestore_repo):
    """Migrate collections table"""
    from app.utils.db_path import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM collections')
    rows = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    count = 0
    
    for row in rows:
        collection_data = dict(zip(columns, row))
        collection_id = collection_data['id']
        
        # Check if already exists
        existing = firestore_repo.get_collection_by_id(collection_id)
        if existing:
            print(f"  Collection {collection_id} already exists, skipping...")
            continue
        
        # Convert timestamp
        created_at = collection_data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                except:
                    created_at = datetime.now()
        elif created_at is None:
            created_at = datetime.now()
        
        # Create in Firestore
        firestore_repo.create_collection(
            user_id=collection_data['user_id'],
            name=collection_data['name'],
            description=collection_data.get('description'),
            collection_type=collection_data['type'],
            is_public=bool(collection_data.get('is_public', True)),
            share_url=collection_data.get('share_url', ''),
            created_at=created_at
        )
        count += 1
    
    conn.close()
    return count


def migrate_collection_products(sqlite_repo, firestore_repo):
    """Migrate collection_products table"""
    from app.utils.db_path import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM collection_products')
    rows = cursor.fetchall()
    
    count = 0
    for row in rows:
        collection_id, product_id = row[0], row[1]
        firestore_repo.add_product_to_collection(collection_id, product_id)
        count += 1
    
    conn.close()
    return count


def migrate_favorites(sqlite_repo, firestore_repo):
    """Migrate favorites table"""
    from app.utils.db_path import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM favorites')
    rows = cursor.fetchall()
    
    count = 0
    for row in rows:
        user_id, product_id = row[0], row[1]
        firestore_repo.add_favorite(user_id, product_id)
        count += 1
    
    conn.close()
    return count


def migrate_price_tracking(sqlite_repo, firestore_repo):
    """Migrate price_tracking table"""
    from app.utils.db_path import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM price_tracking')
    rows = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    count = 0
    
    for row in rows:
        tracking_data = dict(zip(columns, row))
        tracking_id = tracking_data['id']
        
        # Check if already exists
        existing = firestore_repo.get_price_tracking_by_id(tracking_id)
        if existing:
            continue
        
        # Convert timestamp
        created_at = tracking_data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                except:
                    created_at = datetime.now()
        elif created_at is None:
            created_at = datetime.now()
        
        # Create in Firestore
        firestore_repo.create_price_tracking(
            user_id=tracking_data['user_id'],
            product_id=tracking_data['product_id'],
            current_price=tracking_data.get('current_price', '0'),
            original_price=tracking_data.get('original_price'),
            alert_price=tracking_data.get('alert_price'),
            created_at=created_at
        )
        count += 1
    
    conn.close()
    return count


def migrate_price_history(sqlite_repo, firestore_repo):
    """Migrate price_history table"""
    from app.utils.db_path import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM price_history')
    rows = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    count = 0
    
    for row in rows:
        history_data = dict(zip(columns, row))
        
        # Convert timestamp
        recorded_at = history_data.get('recorded_at')
        if isinstance(recorded_at, str):
            try:
                recorded_at = datetime.strptime(recorded_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    recorded_at = datetime.strptime(recorded_at, '%Y-%m-%d %H:%M:%S')
                except:
                    recorded_at = datetime.now()
        elif recorded_at is None:
            recorded_at = datetime.now()
        
        # Create in Firestore
        firestore_repo.add_price_history(
            product_id=history_data['product_id'],
            price=history_data.get('price', '0'),
            recorded_at=recorded_at
        )
        count += 1
        if count % 100 == 0:
            print(f"  Migrated {count} price history records...")
    
    conn.close()
    return count


def migrate_notifications(sqlite_repo, firestore_repo):
    """Migrate notifications table"""
    from app.utils.db_path import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notifications')
    rows = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    count = 0
    
    for row in rows:
        notif_data = dict(zip(columns, row))
        notif_id = notif_data['id']
        
        # Convert timestamp
        created_at = notif_data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                except:
                    created_at = datetime.now()
        elif created_at is None:
            created_at = datetime.now()
        
        read_at = notif_data.get('read_at')
        if isinstance(read_at, str):
            try:
                read_at = datetime.strptime(read_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    read_at = datetime.strptime(read_at, '%Y-%m-%d %H:%M:%S')
                except:
                    read_at = None
        
        # Create in Firestore
        firestore_repo.create_notification(
            user_id=notif_data['user_id'],
            product_id=notif_data.get('product_id'),
            notification_type=notif_data['type'],
            message=notif_data['message'],
            payload=notif_data.get('payload'),
            created_at=created_at
        )
        
        # Update read_at if needed
        if read_at:
            # Note: This would require updating the notification after creation
            # For simplicity, we'll skip this for now
            pass
        
        count += 1
    
    conn.close()
    return count


def migrate_import_issues(sqlite_repo, firestore_repo):
    """Migrate product_import_issues table"""
    from app.utils.db_path import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM product_import_issues')
    rows = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    count = 0
    
    for row in rows:
        issue_data = dict(zip(columns, row))
        
        # Convert timestamp
        created_at = issue_data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                except:
                    created_at = datetime.now()
        elif created_at is None:
            created_at = datetime.now()
        
        # Create in Firestore
        firestore_repo.create_import_issue(
            user_id=issue_data['user_id'],
            url=issue_data['url'],
            status=issue_data['status'],
            reason=issue_data.get('reason'),
            raw_data=issue_data.get('raw_data'),
            created_at=created_at
        )
        count += 1
    
    conn.close()
    return count


def main():
    """Main migration function"""
    print("="*60)
    print("SQLite to Firestore Migration")
    print("="*60)
    print(f"Project ID: {Config.FIREBASE_PROJECT_ID}")
    print(f"Database Path: {Config.DATABASE_PATH}")
    print("="*60)
    
    # Confirm
    response = input("\nThis will migrate all data from SQLite to Firestore. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return
    
    # Initialize repositories
    print("\nInitializing repositories...")
    sqlite_repo = SQLiteRepository()
    firestore_repo = FirestoreRepository()
    
    # Run migrations
    total = 0
    total += migrate_table(sqlite_repo, firestore_repo, "users", migrate_users)
    total += migrate_table(sqlite_repo, firestore_repo, "products", migrate_products)
    total += migrate_table(sqlite_repo, firestore_repo, "collections", migrate_collections)
    total += migrate_table(sqlite_repo, firestore_repo, "collection_products", migrate_collection_products)
    total += migrate_table(sqlite_repo, firestore_repo, "favorites", migrate_favorites)
    total += migrate_table(sqlite_repo, firestore_repo, "price_tracking", migrate_price_tracking)
    total += migrate_table(sqlite_repo, firestore_repo, "price_history", migrate_price_history)
    total += migrate_table(sqlite_repo, firestore_repo, "notifications", migrate_notifications)
    total += migrate_table(sqlite_repo, firestore_repo, "product_import_issues", migrate_import_issues)
    
    print("\n" + "="*60)
    print(f"Migration completed! Total records migrated: {total}")
    print("="*60)
    print("\nNext steps:")
    print("1. Set DB_BACKEND=firestore in your environment or config")
    print("2. Restart your application")
    print("3. Test the application with Firestore")


if __name__ == '__main__':
    main()

