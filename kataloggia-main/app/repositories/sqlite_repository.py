"""
SQLite repository implementation
Wraps existing SQLite database operations
"""
import sqlite3
import uuid
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.repositories.base_repository import BaseRepository
from app.utils.db_path import get_db_connection


class SQLiteRepository(BaseRepository):
    """SQLite implementation of the repository interface"""
    
    def init_db(self):
        """Initialize SQLite database schema"""
        from models import init_db
        init_db()
    
    # User operations
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row)) if columns else None
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row)) if columns else None
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row)) if columns else None
        return None
    
    def get_user_by_profile_url(self, profile_url: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE profile_url = ?', (profile_url,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row)) if columns else None
        return None
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?', (limit, offset))
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        if rows and cursor.description:
            columns = [desc[0] for desc in cursor.description]
            for row in rows:
                users.append(dict(zip(columns, row)))
        return users
    
    def create_user(self, username: str, email: str, password_hash: str, 
                   profile_url: str, created_at: datetime, 
                   last_read_notifications_at: Optional[datetime] = None,
                   avatar_url: Optional[str] = None) -> str:
        user_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Add new columns if they don't exist (for backward compatibility)
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN email_verification_token TEXT')
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN email_verification_token_expires_at TIMESTAMP')
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN locked_until REAL')
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            conn.commit()
            
            # Insert user with new fields
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash, profile_url, created_at, 
                                 last_read_notifications_at, avatar_url, email_verified,
                                 email_verification_token, email_verification_token_expires_at, locked_until)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, email, password_hash, profile_url, created_at, 
                  last_read_notifications_at, avatar_url, 1, None, None, None))
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            conn.rollback()
            raise Exception("Bu kullanıcı adı veya email zaten kullanılıyor")
        finally:
            conn.close()
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        allowed_fields = ['username', 'email', 'password_hash', 'profile_url', 
                         'last_read_notifications_at', 'avatar_url', 'email_verified',
                         'email_verification_token', 'email_verification_token_expires_at', 'locked_until']
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            conn.close()
            return False
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        try:
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] User update error: {e}")
            return False
        finally:
            conn.close()
    
    # Product operations
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row)) if columns else None
        return None
    
    def get_product_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Get product by URL (returns the most recent one if multiple exist)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        # Normalize URL - remove trailing slashes for better matching
        normalized_url = url.strip().rstrip('/')
        # Try exact match first, then try original URL
        cursor.execute('SELECT * FROM products WHERE url = ? OR url = ? ORDER BY created_at DESC LIMIT 1', 
                      (normalized_url, url))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row)) if columns else None
        return None
    
    def get_products_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in rows] if columns else []
    
    def create_product(self, user_id: str, name: str, price: str, image: Optional[str],
                      brand: str, url: str, created_at: datetime,
                      old_price: Optional[str] = None,
                      current_price: Optional[str] = None,
                      discount_percentage: Optional[str] = None,
                      images: Optional[List[str]] = None,
                      discount_info: Optional[str] = None) -> str:
        product_id = str(uuid.uuid4())
        images_json = json.dumps(images) if images else (json.dumps([image]) if image else None)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (id, user_id, name, price, image, brand, url, old_price, current_price, discount_percentage, images, discount_info, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product_id, user_id, name, price, image, brand, url, old_price, current_price, discount_percentage, images_json, discount_info, created_at))
        conn.commit()
        conn.close()
        
        return product_id
    
    def update_product(self, product_id: str, user_id: str, **kwargs) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        allowed_fields = ['name', 'price', 'image', 'brand', 'url', 'old_price', 
                         'current_price', 'discount_percentage', 'images', 'discount_info']
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                if field == 'images' and isinstance(value, list):
                    value = json.dumps(value)
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            conn.close()
            return False
        
        values.extend([product_id, user_id])
        query = f"UPDATE products SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
        
        try:
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Product update error: {e}")
            return False
        finally:
            conn.close()
    
    def delete_product(self, product_id: str, user_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id FROM products WHERE id = ? AND user_id = ?', (product_id, user_id))
            if not cursor.fetchone():
                return False
            
            cursor.execute('DELETE FROM collection_products WHERE product_id = ?', (product_id,))
            cursor.execute('DELETE FROM price_tracking WHERE product_id = ?', (product_id,))
            cursor.execute('DELETE FROM price_history WHERE product_id = ?', (product_id,))
            cursor.execute('DELETE FROM favorites WHERE product_id = ?', (product_id,))
            cursor.execute('DELETE FROM products WHERE id = ? AND user_id = ?', (product_id, user_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Product delete error: {e}")
            return False
        finally:
            conn.close()
    
    # Collection operations
    def get_collection_by_id(self, collection_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM collections WHERE id = ?', (collection_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row)) if columns else None
        return None
    
    def get_collection_by_share_url(self, share_url: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM collections WHERE share_url = ?', (share_url,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row)) if columns else None
        return None
    
    def get_collections_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM collections WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in rows] if columns else []
    
    def create_collection(self, user_id: str, name: str, description: Optional[str],
                         collection_type: str, is_public: bool, share_url: str,
                         created_at: datetime, cover_image: Optional[str] = None) -> str:
        collection_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO collections (id, user_id, name, description, type, is_public, share_url, created_at, cover_image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (collection_id, user_id, name, description, collection_type, is_public, share_url, created_at, cover_image))
        conn.commit()
        conn.close()
        return collection_id
    
    def add_product_to_collection(self, collection_id: str, product_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO collection_products (collection_id, product_id)
                VALUES (?, ?)
            ''', (collection_id, product_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Add product to collection error: {e}")
            return False
        finally:
            conn.close()
    
    def remove_product_from_collection(self, collection_id: str, product_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM collection_products WHERE collection_id = ? AND product_id = ?', 
                          (collection_id, product_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Remove product from collection error: {e}")
            return False
        finally:
            conn.close()
    
    def delete_collection(self, collection_id: str, user_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM collection_products WHERE collection_id = ?', (collection_id,))
            cursor.execute('DELETE FROM collections WHERE id = ? AND user_id = ?', (collection_id, user_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Collection delete error: {e}")
            return False
        finally:
            conn.close()

    def update_collection(self, collection_id: str, user_id: str, **kwargs) -> bool:
        """Update collection fields (name, description, type, is_public) for a user."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if collection is copied (cannot be edited)
            cursor.execute('SELECT description FROM collections WHERE id = ?', (collection_id,))
            result = cursor.fetchone()
            if result and result[0] and "[KOPYALANMIŞ]" in result[0]:
                print(f"[WARNING] Attempted to edit copied collection: {collection_id}")
                conn.close()
                return False
            
            allowed_fields = ['name', 'description', 'type', 'is_public']
            updates = []
            values = []

            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    # Prevent removing [KOPYALANMIŞ] marker from description
                    if field == 'description' and result and result[0] and "[KOPYALANMIŞ]" in result[0]:
                        # Keep the marker even if user tries to remove it
                        if "[KOPYALANMIŞ]" not in str(value):
                            # Extract original marker and preserve it
                            original_desc = result[0]
                            marker_part = original_desc.split("] ", 1)[0] + "] "
                            value = marker_part + str(value)
                    updates.append(f"{field} = ?")
                    values.append(value)

            if not updates:
                return False

            values.extend([collection_id, user_id])
            query = f"UPDATE collections SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Collection update error: {e}")
            return False
        finally:
            conn.close()
    
    def get_products_by_collection_id(self, collection_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.* FROM products p
            INNER JOIN collection_products cp ON p.id = cp.product_id
            WHERE cp.collection_id = ?
            ORDER BY cp.added_at DESC
        ''', (collection_id,))
        rows = cursor.fetchall()
        conn.close()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in rows] if columns else []
    
    # Favorite operations
    def add_favorite(self, user_id: str, product_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO favorites (user_id, product_id)
                VALUES (?, ?)
            ''', (user_id, product_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Add favorite error: {e}")
            return False
        finally:
            conn.close()
    
    def remove_favorite(self, user_id: str, product_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM favorites WHERE user_id = ? AND product_id = ?', 
                          (user_id, product_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Remove favorite error: {e}")
            return False
        finally:
            conn.close()
    
    def get_favorites_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.* FROM products p
            INNER JOIN favorites f ON p.id = f.product_id
            WHERE f.user_id = ?
            ORDER BY p.created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in rows] if columns else []
    
    def is_favorite(self, user_id: str, product_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM favorites WHERE user_id = ? AND product_id = ?', 
                      (user_id, product_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    # Price tracking operations
    def create_price_tracking(self, user_id: str, product_id: str, current_price: str,
                             original_price: Optional[str] = None,
                             alert_price: Optional[str] = None,
                             created_at: datetime = None) -> str:
        tracking_id = str(uuid.uuid4())
        if created_at is None:
            created_at = datetime.now()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO price_tracking (id, product_id, user_id, current_price, original_price, alert_price, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tracking_id, product_id, user_id, current_price, original_price, alert_price, created_at, True))
        conn.commit()
        conn.close()
        return tracking_id
    
    def get_price_tracking_by_id(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM price_tracking WHERE id = ?', (tracking_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row)) if columns else None
        return None
    
    def get_price_tracking_by_product_and_user(self, product_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM price_tracking 
            WHERE product_id = ? AND user_id = ? AND is_active = 1
            LIMIT 1
        ''', (product_id, user_id))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row)) if columns else None
        return None
    
    def get_price_trackings_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT pt.*, p.name, p.brand, p.image
            FROM price_tracking pt
            LEFT JOIN products p ON pt.product_id = p.id
            WHERE pt.user_id = ? AND pt.is_active = 1
            ORDER BY pt.created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in rows] if columns else []
    
    def get_all_active_price_trackings(self) -> List[Dict[str, Any]]:
        """Return all active price tracking records."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id,
                   product_id,
                   user_id,
                   current_price,
                   original_price,
                   price_change,
                   is_active,
                   alert_price,
                   created_at,
                   last_checked
            FROM price_tracking
            WHERE is_active = 1
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        results: List[Dict[str, Any]] = []
        for row in rows:
            results.append({
                'id': row[0],
                'product_id': row[1],
                'user_id': row[2],
                'current_price': row[3],
                'original_price': row[4],
                'price_change': row[5],
                'is_active': bool(row[6]),
                'alert_price': row[7],
                'created_at': row[8],
                'last_checked': row[9],
            })
        return results
    
    def update_price_tracking(self, tracking_id: str, new_price: Optional[str] = None, price_change: Optional[str] = None, is_active: Optional[bool] = None) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            updates = []
            values = []
            
            if new_price is not None:
                updates.append('current_price = ?')
                values.append(new_price)
            
            if price_change is not None:
                updates.append('price_change = ?')
                values.append(price_change)
            
            if is_active is not None:
                updates.append('is_active = ?')
                values.append(1 if is_active else 0)
            
            if not updates:
                return False
            
            values.append(tracking_id)
            query = f"UPDATE price_tracking SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Update price tracking error: {e}")
            return False
        finally:
            conn.close()
    
    def remove_price_tracking(self, tracking_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE price_tracking SET is_active = 0 WHERE id = ?', (tracking_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Remove price tracking error: {e}")
            return False
        finally:
            conn.close()
    
    # Price history operations
    def add_price_history(self, product_id: str, price: str, recorded_at: datetime) -> str:
        history_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO price_history (id, product_id, price, recorded_at)
            VALUES (?, ?, ?, ?)
        ''', (history_id, product_id, price, recorded_at))
        conn.commit()
        conn.close()
        return history_id
    
    def get_price_history_by_product_id(self, product_id: str, limit: int = 60) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, recorded_at
            FROM price_history
            WHERE product_id = ?
            ORDER BY datetime(recorded_at) ASC
            LIMIT ?
        ''', (product_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        return [{'price': row[0], 'recorded_at': row[1]} for row in rows]
    
    # Notification operations
    def create_notification(self, user_id: str, product_id: Optional[str], 
                           notification_type: str, message: str,
                           payload: Optional[str] = None,
                           created_at: datetime = None) -> str:
        notification_id = str(uuid.uuid4())
        if created_at is None:
            created_at = datetime.now()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (id, user_id, product_id, type, message, payload, created_at, read_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (notification_id, user_id, product_id, notification_type, message, payload, created_at, None))
        conn.commit()
        conn.close()
        return notification_id
    
    def get_notifications_by_user_id(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, product_id, type, message, payload, created_at, read_at
            FROM notifications
            WHERE user_id = ?
            ORDER BY datetime(created_at) DESC
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'user_id': row[1],
            'product_id': row[2],
            'type': row[3],
            'message': row[4],
            'payload': row[5],
            'created_at': row[6],
            'read_at': row[7]
        } for row in rows]
    
    def mark_notifications_read(self, user_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE notifications
                SET read_at = ?
                WHERE user_id = ? AND read_at IS NULL
            ''', (datetime.now(), user_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Mark notifications read error: {e}")
            return False
        finally:
            conn.close()
    
    def mark_notification_read_by_id(self, notification_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE notifications
                SET read_at = ?
                WHERE id = ? AND read_at IS NULL
            ''', (datetime.now(), notification_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Mark notification read by ID error: {e}")
            return False
        finally:
            conn.close()
    
    # Product import issues operations
    def create_import_issue(self, user_id: str, url: str, status: str,
                           reason: Optional[str] = None,
                           raw_data: Optional[str] = None,
                           created_at: datetime = None) -> str:
        issue_id = str(uuid.uuid4())
        if created_at is None:
            created_at = datetime.now()
        
        if isinstance(raw_data, dict):
            raw_data = json.dumps(raw_data)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO product_import_issues (id, user_id, url, status, reason, raw_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (issue_id, user_id, url, status, reason, raw_data, created_at))
        conn.commit()
        conn.close()
        return issue_id
    
    def get_import_issues_by_user_id(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, url, status, reason, raw_data, created_at
            FROM product_import_issues
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'user_id': row[1],
            'url': row[2],
            'status': row[3],
            'reason': row[4],
            'raw_data': row[5],
            'created_at': row[6]
        } for row in rows]
    
    def get_all_import_issues(self, limit: int = 200) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT pii.id, pii.user_id, u.username, pii.url, pii.status, pii.reason, pii.created_at
            FROM product_import_issues pii
            LEFT JOIN users u ON pii.user_id = u.id
            ORDER BY datetime(pii.created_at) DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'user_id': row[1],
            'username': row[2],
            'url': row[3],
            'status': row[4],
            'reason': row[5],
            'created_at': row[6]
        } for row in rows]
    
    def delete_import_issue(self, issue_id: str, user_id: str) -> bool:
        """Delete an import issue (only if it belongs to the user)"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # First check if the issue belongs to the user
            cursor.execute('SELECT user_id FROM product_import_issues WHERE id = ?', (issue_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                print(f"[ERROR] Import issue not found: {issue_id}")
                return False
            
            if row[0] != user_id:
                conn.close()
                print(f"[ERROR] User {user_id} cannot delete issue {issue_id} (belongs to {row[0]})")
                return False
            
            # Delete the issue
            cursor.execute('DELETE FROM product_import_issues WHERE id = ? AND user_id = ?', (issue_id, user_id))
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"[ERROR] Delete import issue error: {e}")
            return False
    
    # Follow operations
    def follow_user(self, follower_id: str, following_id: str) -> bool:
        """Follow a user"""
        if follower_id == following_id:
            return False  # Can't follow yourself
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if already following
            cursor.execute('SELECT id FROM follows WHERE follower_id = ? AND following_id = ?', 
                          (follower_id, following_id))
            if cursor.fetchone():
                conn.close()
                return False  # Already following
            
            follow_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO follows (id, follower_id, following_id, created_at)
                VALUES (?, ?, ?, ?)
            ''', (follow_id, follower_id, following_id, datetime.now()))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Follow user error: {e}")
            return False
        finally:
            conn.close()
    
    def unfollow_user(self, follower_id: str, following_id: str) -> bool:
        """Unfollow a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM follows WHERE follower_id = ? AND following_id = ?', 
                          (follower_id, following_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Unfollow user error: {e}")
            return False
        finally:
            conn.close()
    
    def is_following(self, follower_id: str, following_id: str) -> bool:
        """Check if user is following another user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM follows WHERE follower_id = ? AND following_id = ?', 
                      (follower_id, following_id))
        result = cursor.fetchone() is not None
        conn.close()
        return result
    
    def get_followers(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all followers of a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.id, f.follower_id, f.created_at, u.username, u.email
            FROM follows f
            JOIN users u ON f.follower_id = u.id
            WHERE f.following_id = ?
            ORDER BY f.created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in rows] if columns else []
    
    def get_following(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all users that a user is following"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.id, f.following_id, f.created_at, u.username, u.email
            FROM follows f
            JOIN users u ON f.following_id = u.id
            WHERE f.follower_id = ?
            ORDER BY f.created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in rows] if columns else []
    
    # Collection like operations
    def like_collection(self, user_id: str, collection_id: str) -> bool:
        """Like a collection"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if already liked
            cursor.execute('SELECT id FROM likes WHERE user_id = ? AND collection_id = ?', 
                          (user_id, collection_id))
            if cursor.fetchone():
                conn.close()
                return False  # Already liked
            
            like_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO likes (id, user_id, collection_id, created_at)
                VALUES (?, ?, ?, ?)
            ''', (like_id, user_id, collection_id, datetime.now()))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Like collection error: {e}")
            return False
        finally:
            conn.close()
    
    def unlike_collection(self, user_id: str, collection_id: str) -> bool:
        """Unlike a collection"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM likes WHERE user_id = ? AND collection_id = ?', 
                          (user_id, collection_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Unlike collection error: {e}")
            return False
        finally:
            conn.close()
    
    def is_collection_liked(self, user_id: str, collection_id: str) -> bool:
        """Check if collection is liked by user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM likes WHERE user_id = ? AND collection_id = ?', 
                      (user_id, collection_id))
        result = cursor.fetchone() is not None
        conn.close()
        return result
    
    def get_collection_likes_count(self, collection_id: str) -> int:
        """Get total likes count for a collection"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM likes WHERE collection_id = ?', (collection_id,))
        result = cursor.fetchone()[0]
        conn.close()
        return result

