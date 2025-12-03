"""
Database Indexing Utilities
SQLite için index optimizasyonları
"""
import sqlite3

class DatabaseIndexer:
    """Database indexing utilities"""
    
    @staticmethod
    def create_indexes():
        """Performans için indexler oluştur (sadece SQLite için)"""
        from app.config import Config
        
        # Check if using Firestore
        try:
            db_backend = Config.DB_BACKEND
        except:
            import os
            db_backend = os.environ.get('DB_BACKEND', 'sqlite')
        
        if db_backend == 'firestore':
            # Firestore indexes are created manually in Firebase Console
            print("[INFO] Firestore kullanılıyor - index'ler Firebase Console'dan oluşturulmalı")
            return
        
        # SQLite indexing
        from app.utils.db_path import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        indexes = [
            # Products indexes
            "CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)",
            "CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_products_user_brand ON products(user_id, brand)",
            
            # Collections indexes
            "CREATE INDEX IF NOT EXISTS idx_collections_user_id ON collections(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_collections_share_url ON collections(share_url)",
            "CREATE INDEX IF NOT EXISTS idx_collections_is_public ON collections(is_public)",
            
            # Collection products indexes
            "CREATE INDEX IF NOT EXISTS idx_collection_products_collection_id ON collection_products(collection_id)",
            "CREATE INDEX IF NOT EXISTS idx_collection_products_product_id ON collection_products(product_id)",
            
            # Price tracking indexes
            "CREATE INDEX IF NOT EXISTS idx_price_tracking_product_id ON price_tracking(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_price_tracking_user_id ON price_tracking(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_price_tracking_is_active ON price_tracking(is_active)",
            
            # Price history indexes
            "CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_price_history_recorded_at ON price_history(recorded_at)",
            
            # Users indexes
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_profile_url ON users(profile_url)",
            
            # Notifications indexes
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_created_at ON notifications(user_id, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_read_at ON notifications(user_id, read_at)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"[INFO] Index oluşturuldu: {index_sql.split()[-1]}")
            except Exception as e:
                print(f"[WARNING] Index oluşturma hatası: {e}")
        
        conn.commit()
        conn.close()
        print("[INFO] Tüm indexler oluşturuldu")

