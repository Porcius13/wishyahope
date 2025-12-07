"""
Firebase Firestore repository implementation
"""
import uuid
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

from app.repositories.base_repository import BaseRepository
from app.config import Config


class FirestoreRepository(BaseRepository):
    """Firestore implementation of the repository interface"""
    
    def __init__(self):
        if not FIREBASE_AVAILABLE:
            raise ImportError("firebase-admin package is not installed. Install it with: pip install firebase-admin")
        
        # Initialize Firebase Admin SDK if not already initialized
        if not firebase_admin._apps:
            import os
            
            # Check for JSON credentials in environment variable (for Render/cloud platforms)
            firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
            if firebase_creds_json:
                try:
                    # Parse JSON string from environment variable
                    cred_dict = json.loads(firebase_creds_json)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred, {
                        'projectId': Config.FIREBASE_PROJECT_ID
                    })
                    print("[INFO] Firebase initialized with credentials from FIREBASE_CREDENTIALS_JSON")
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")
                    raise
            elif Config.FIREBASE_CREDENTIALS_PATH:
                cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred, {
                    'projectId': Config.FIREBASE_PROJECT_ID
                })
                print(f"[INFO] Firebase initialized with credentials from file: {Config.FIREBASE_CREDENTIALS_PATH}")
            else:
                # Use Application Default Credentials
                try:
                    firebase_admin.initialize_app(options={
                        'projectId': Config.FIREBASE_PROJECT_ID
                    })
                    print("[INFO] Firebase initialized with Application Default Credentials")
                except Exception as e:
                    error_msg = str(e)
                    if "DefaultCredentialsError" in error_msg or "credentials were not found" in error_msg.lower():
                        raise RuntimeError(
                            "Firebase credentials not found. For local development, you have two options:\n"
                            "1. Use SQLite instead: Set environment variable DB_BACKEND=sqlite\n"
                            "2. Set up Firebase credentials:\n"
                            "   - Set FIREBASE_CREDENTIALS_PATH to your service account JSON file path, OR\n"
                            "   - Set FIREBASE_CREDENTIALS_JSON with the JSON content as a string, OR\n"
                            "   - Set up Application Default Credentials (gcloud auth application-default login)"
                        ) from e
                    raise
        
        try:
            self.db = firestore.client()
        except Exception as e:
            error_msg = str(e)
            if "DefaultCredentialsError" in error_msg or "credentials were not found" in error_msg.lower():
                raise RuntimeError(
                    "Firebase credentials not found. For local development, you have two options:\n"
                    "1. Use SQLite instead: Set environment variable DB_BACKEND=sqlite\n"
                    "2. Set up Firebase credentials:\n"
                    "   - Set FIREBASE_CREDENTIALS_PATH to your service account JSON file path, OR\n"
                    "   - Set FIREBASE_CREDENTIALS_JSON with the JSON content as a string, OR\n"
                    "   - Set up Application Default Credentials (gcloud auth application-default login)"
                ) from e
            raise
    
    def init_db(self):
        """Firestore doesn't require schema initialization"""
        pass
    
    def _timestamp_to_datetime(self, timestamp) -> Optional[datetime]:
        """Convert Firestore timestamp to datetime"""
        if timestamp is None:
            return None
        if hasattr(timestamp, 'timestamp'):
            return timestamp
        return datetime.fromtimestamp(timestamp)
    
    def _datetime_to_timestamp(self, dt: datetime):
        """Convert datetime to Firestore timestamp"""
        from google.cloud.firestore import SERVER_TIMESTAMP
        if dt is None:
            return SERVER_TIMESTAMP
        return dt
    
    # User operations
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.collection('users').document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        docs = self.db.collection('users').where('username', '==', username).limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        docs = self.db.collection('users').where('email', '==', email).limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_user_by_profile_url(self, profile_url: str) -> Optional[Dict[str, Any]]:
        docs = self.db.collection('users').where('profile_url', '==', profile_url).limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        users = []
        # Firestore doesn't support offset with order_by, so we'll get all and slice
        # For better performance with large datasets, consider using cursor-based pagination
        query = self.db.collection('users').order_by('created_at', direction='DESCENDING').limit(limit + offset)
        docs = query.stream()
        
        all_docs = list(docs)
        # Apply offset manually
        for doc in all_docs[offset:]:
            data = doc.to_dict()
            data['id'] = doc.id
            users.append(data)
        return users
    
    def create_user(self, username: str, email: str, password_hash: str, 
                   profile_url: str, created_at: datetime, 
                   last_read_notifications_at: Optional[datetime] = None,
                   avatar_url: Optional[str] = None) -> str:
        user_id = str(uuid.uuid4())
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'profile_url': profile_url,
            'created_at': self._datetime_to_timestamp(created_at),
            'last_read_notifications_at': self._datetime_to_timestamp(last_read_notifications_at),
            'avatar_url': avatar_url
        }
        self.db.collection('users').document(user_id).set(user_data)
        return user_id
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        try:
            updates = {}
            for key, value in kwargs.items():
                if value is not None:
                    if isinstance(value, datetime):
                        updates[key] = self._datetime_to_timestamp(value)
                    else:
                        updates[key] = value
            
            if updates:
                self.db.collection('users').document(user_id).update(updates)
            return True
        except Exception as e:
            print(f"[ERROR] User update error: {e}")
            return False
    
    # Product operations
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.collection('products').document(product_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_product_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Get product by URL (returns the most recent one if multiple exist)"""
        try:
            # Normalize URL - remove trailing slashes and query params for better matching
            normalized_url = url.strip().rstrip('/')
            # Try exact match first
            docs = self.db.collection('products').where('url', '==', normalized_url).order_by('created_at', direction=firestore.Query.DESCENDING).limit(1).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            
            # If no exact match, try with original URL
            if normalized_url != url:
                docs = self.db.collection('products').where('url', '==', url).order_by('created_at', direction=firestore.Query.DESCENDING).limit(1).stream()
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    return data
            
            return None
        except Exception as e:
            # Fallback to memory sort if index not ready yet
            print(f"[WARNING] Index not ready for URL search, using memory sort: {e}")
            docs = self.db.collection('products').where('url', '==', url).stream()
            products = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                products.append(data)
            if products:
                products.sort(key=lambda x: x.get('created_at') or datetime.min, reverse=True)
                return products[0]
            return None
    
    def get_products_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        # Use order_by now that index is created (faster than memory sort)
        try:
            docs = self.db.collection('products').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
            products = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                products.append(data)
            return products
        except Exception as e:
            # Fallback to memory sort if index not ready yet
            print(f"[WARNING] Index not ready, using memory sort: {e}")
            docs = self.db.collection('products').where('user_id', '==', user_id).stream()
            products = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                products.append(data)
            products.sort(key=lambda x: x.get('created_at') or datetime.min, reverse=True)
            return products
    
    def create_product(self, user_id: str, name: str, price: str, image: Optional[str],
                      brand: str, url: str, created_at: datetime,
                      old_price: Optional[str] = None,
                      current_price: Optional[str] = None,
                      discount_percentage: Optional[str] = None,
                      images: Optional[List[str]] = None,
                      discount_info: Optional[str] = None) -> str:
        try:
            product_id = str(uuid.uuid4())
            product_data = {
                'user_id': user_id,
                'name': name,
                'price': price,
                'image': image,
                'brand': brand,
                'url': url,
                'old_price': old_price,
                'current_price': current_price,
                'discount_percentage': discount_percentage,
                'images': images or ([image] if image else []),
                'discount_info': discount_info,
                'created_at': self._datetime_to_timestamp(created_at)
            }
            print(f"[DEBUG] Creating product in Firestore: {product_id}, user_id: {user_id}, name: {name}")
            self.db.collection('products').document(product_id).set(product_data)
            print(f"[DEBUG] Product created successfully in Firestore: {product_id}")
            return product_id
        except Exception as e:
            print(f"[ERROR] Firestore create_product error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def update_product(self, product_id: str, user_id: str, **kwargs) -> bool:
        try:
            # Verify ownership
            product = self.get_product_by_id(product_id)
            if not product or product.get('user_id') != user_id:
                return False
            
            updates = {}
            for key, value in kwargs.items():
                if value is not None:
                    if key == 'images' and isinstance(value, list):
                        updates[key] = value
                    else:
                        updates[key] = value
            
            if updates:
                self.db.collection('products').document(product_id).update(updates)
            return True
        except Exception as e:
            print(f"[ERROR] Product update error: {e}")
            return False
    
    def delete_product(self, product_id: str, user_id: str) -> bool:
        try:
            # Verify ownership
            product = self.get_product_by_id(product_id)
            if not product:
                print(f"[ERROR] Product not found: {product_id}")
                return False
            
            if product.get('user_id') != user_id:
                print(f"[ERROR] Product ownership mismatch: product.user_id={product.get('user_id')}, requested_user_id={user_id}")
                return False
            
            # Delete related data using batch operations for better performance
            batch = self.db.batch()
            delete_count = 0
            
            # Collections - Get all and delete in batch
            try:
                collection_refs = self.db.collection('collection_products').where('product_id', '==', product_id).stream()
                for ref in collection_refs:
                    batch.delete(ref.reference)
                    delete_count += 1
            except Exception as e:
                print(f"[WARNING] Error deleting collection_products: {e}")
            
            # Price tracking
            try:
                tracking_refs = self.db.collection('price_tracking').where('product_id', '==', product_id).stream()
                for ref in tracking_refs:
                    batch.delete(ref.reference)
                    delete_count += 1
            except Exception as e:
                print(f"[WARNING] Error deleting price_tracking: {e}")
            
            # Price history
            try:
                history_refs = self.db.collection('price_history').where('product_id', '==', product_id).stream()
                for ref in history_refs:
                    batch.delete(ref.reference)
                    delete_count += 1
            except Exception as e:
                print(f"[WARNING] Error deleting price_history: {e}")
            
            # Favorites
            try:
                favorite_refs = self.db.collection('favorites').where('product_id', '==', product_id).stream()
                for ref in favorite_refs:
                    batch.delete(ref.reference)
                    delete_count += 1
            except Exception as e:
                print(f"[WARNING] Error deleting favorites: {e}")
            
            # Delete product
            product_ref = self.db.collection('products').document(product_id)
            batch.delete(product_ref)
            delete_count += 1
            
            # Commit batch (Firestore batch limit is 500, we're safe)
            if delete_count > 0:
                batch.commit()
            
            print(f"[INFO] Product deleted: {product_id} (deleted {delete_count} related documents)")
            return True
        except Exception as e:
            print(f"[ERROR] Product delete error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Collection operations
    def get_collection_by_id(self, collection_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.collection('collections').document(collection_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_collection_by_share_url(self, share_url: str) -> Optional[Dict[str, Any]]:
        docs = self.db.collection('collections').where('share_url', '==', share_url).limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_collections_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all collections for a user without requiring Firestore composite indexes."""
        try:
            # Simple query without order_by to avoid composite index requirement
            docs = self.db.collection('collections').where('user_id', '==', user_id).stream()

            collections: List[Dict[str, Any]] = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                collections.append(data)

            # Sort in memory by created_at (newest first) if available
            def _created_at_key(item: Dict[str, Any]):
                ts = item.get('created_at')
                try:
                    if hasattr(ts, 'timestamp'):
                        return ts
                    if isinstance(ts, datetime):
                        return ts
                    return datetime.min
                except Exception:
                    return datetime.min

            collections.sort(key=_created_at_key, reverse=True)
            return collections
        except Exception as e:
            print(f"[ERROR] Get collections by user id error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_products_by_collection_id(self, collection_id: str) -> List[Dict[str, Any]]:
        try:
            # Get product IDs from collection_products
            cp_refs = self.db.collection('collection_products').where('collection_id', '==', collection_id).stream()
            product_ids = [ref.to_dict()['product_id'] for ref in cp_refs]
            
            if not product_ids:
                return []
            
            # Get products (Firestore 'in' query limit is 10, so we need to batch)
            products = []
            for i in range(0, len(product_ids), 10):
                batch_ids = product_ids[i:i+10]
                docs = self.db.collection('products').where('__name__', 'in', batch_ids).stream()
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    products.append(data)
            
            return products
        except Exception as e:
            print(f"[ERROR] Get products by collection id error: {e}")
            return []
    
    def create_collection(self, user_id: str, name: str, description: Optional[str],
                         collection_type: str, is_public: bool, share_url: str,
                         created_at: datetime, cover_image: Optional[str] = None) -> str:
        collection_id = str(uuid.uuid4())
        collection_data = {
            'user_id': user_id,
            'name': name,
            'description': description,
            'type': collection_type,
            'is_public': is_public,
            'share_url': share_url,
            'created_at': self._datetime_to_timestamp(created_at),
            'cover_image': cover_image
        }
        self.db.collection('collections').document(collection_id).set(collection_data)
        return collection_id
    
    def add_product_to_collection(self, collection_id: str, product_id: str) -> bool:
        try:
            # Check if already exists
            existing = self.db.collection('collection_products').where('collection_id', '==', collection_id).where('product_id', '==', product_id).limit(1).stream()
            if list(existing):
                return True  # Already exists
            
            ref_id = str(uuid.uuid4())
            self.db.collection('collection_products').document(ref_id).set({
                'collection_id': collection_id,
                'product_id': product_id
            })
            return True
        except Exception as e:
            print(f"[ERROR] Add product to collection error: {e}")
            return False
    
    def remove_product_from_collection(self, collection_id: str, product_id: str) -> bool:
        try:
            refs = self.db.collection('collection_products').where('collection_id', '==', collection_id).where('product_id', '==', product_id).stream()
            for ref in refs:
                ref.reference.delete()
            return True
        except Exception as e:
            print(f"[ERROR] Remove product from collection error: {e}")
            return False
    
    def delete_collection(self, collection_id: str, user_id: str) -> bool:
        try:
            collection = self.get_collection_by_id(collection_id)
            if not collection or collection.get('user_id') != user_id:
                return False
            
            # Delete collection products
            refs = self.db.collection('collection_products').where('collection_id', '==', collection_id).stream()
            for ref in refs:
                ref.reference.delete()
            
            # Delete collection
            self.db.collection('collections').document(collection_id).delete()
            return True
        except Exception as e:
            print(f"[ERROR] Collection delete error: {e}")
            return False

    def update_collection(self, collection_id: str, user_id: str, **kwargs) -> bool:
        """Update collection fields (name, description, type, is_public) for a user."""
        try:
            collection = self.get_collection_by_id(collection_id)
            if not collection or collection.get('user_id') != user_id:
                return False

            # Check if collection is copied (cannot be edited)
            description = collection.get('description', '')
            if description and "[KOPYALANMIŞ]" in description:
                print(f"[WARNING] Attempted to edit copied collection: {collection_id}")
                return False

            allowed_fields = ['name', 'description', 'type', 'is_public']
            updates: Dict[str, Any] = {}
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    # Prevent removing [KOPYALANMIŞ] marker from description
                    if field == 'description' and description and "[KOPYALANMIŞ]" in description:
                        # Keep the marker even if user tries to remove it
                        if "[KOPYALANMIŞ]" not in str(value):
                            # Extract original marker and preserve it
                            marker_part = description.split("] ", 1)[0] + "] "
                            value = marker_part + str(value)
                    updates[field] = value

            if not updates:
                return False

            self.db.collection('collections').document(collection_id).update(updates)
            return True
        except Exception as e:
            print(f"[ERROR] Collection update error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Favorite operations
    def add_favorite(self, user_id: str, product_id: str) -> bool:
        try:
            # Check if already exists
            existing = self.db.collection('favorites').where('user_id', '==', user_id).where('product_id', '==', product_id).limit(1).stream()
            existing_list = list(existing)
            if existing_list:
                print(f"[DEBUG] Favorite already exists: user_id={user_id}, product_id={product_id}")
                return False  # Already exists, return False to match SQLite behavior
            
            ref_id = str(uuid.uuid4())
            favorite_data = {
                'user_id': user_id,
                'product_id': product_id,
                'created_at': self._datetime_to_timestamp(datetime.now())
            }
            print(f"[DEBUG] Adding favorite to Firestore: {ref_id}, user_id={user_id}, product_id={product_id}")
            self.db.collection('favorites').document(ref_id).set(favorite_data)
            print(f"[DEBUG] Favorite added successfully: {ref_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Add favorite error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def remove_favorite(self, user_id: str, product_id: str) -> bool:
        try:
            print(f"[DEBUG] Removing favorite from Firestore: user_id={user_id}, product_id={product_id}")
            refs = self.db.collection('favorites').where('user_id', '==', user_id).where('product_id', '==', product_id).stream()
            deleted_count = 0
            for ref in refs:
                ref.reference.delete()
                deleted_count += 1
            print(f"[DEBUG] Removed {deleted_count} favorite(s)")
            return deleted_count > 0
        except Exception as e:
            print(f"[ERROR] Remove favorite error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_favorites_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        # Get favorite product IDs
        favorite_refs = self.db.collection('favorites').where('user_id', '==', user_id).stream()
        product_ids = [ref.to_dict()['product_id'] for ref in favorite_refs]
        
        if not product_ids:
            return []
        
        # Get products (Firestore 'in' query limit is 10, so we need to batch)
        products = []
        for i in range(0, len(product_ids), 10):
            batch_ids = product_ids[i:i+10]
            docs = self.db.collection('products').where('__name__', 'in', batch_ids).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                products.append(data)
        
        return products
    
    def is_favorite(self, user_id: str, product_id: str) -> bool:
        refs = self.db.collection('favorites').where('user_id', '==', user_id).where('product_id', '==', product_id).limit(1).stream()
        return len(list(refs)) > 0
    
    # Price tracking operations
    def create_price_tracking(self, user_id: str, product_id: str, current_price: str,
                             original_price: Optional[str] = None,
                             alert_price: Optional[str] = None,
                             created_at: datetime = None) -> str:
        try:
            tracking_id = str(uuid.uuid4())
            if created_at is None:
                created_at = datetime.now()
            
            tracking_data = {
                'product_id': product_id,
                'user_id': user_id,
                'current_price': current_price,
                'original_price': original_price or current_price,
                'alert_price': alert_price,
                'is_active': True,
                'price_change': '0',
                'created_at': self._datetime_to_timestamp(created_at),
                'last_checked': self._datetime_to_timestamp(created_at)
            }
            print(f"[DEBUG] Creating price tracking in Firestore: {tracking_id}, user_id={user_id}, product_id={product_id}")
            self.db.collection('price_tracking').document(tracking_id).set(tracking_data)
            print(f"[DEBUG] Price tracking created successfully: {tracking_id}")
            return tracking_id
        except Exception as e:
            print(f"[ERROR] Create price tracking error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_price_tracking_by_id(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.collection('price_tracking').document(tracking_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_price_tracking_by_product_and_user(self, product_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            print(f"[DEBUG] Checking for existing tracking: product_id={product_id}, user_id={user_id}")
            docs = self.db.collection('price_tracking').where('product_id', '==', product_id).where('user_id', '==', user_id).where('is_active', '==', True).limit(1).stream()
            doc_list = list(docs)
            print(f"[DEBUG] Found {len(doc_list)} existing tracking(s)")
            for doc in doc_list:
                data = doc.to_dict()
                data['id'] = doc.id
                print(f"[DEBUG] Existing tracking found: {doc.id}, is_active={data.get('is_active')}")
                return data
            print(f"[DEBUG] No existing tracking found")
            return None
        except Exception as e:
            print(f"[ERROR] Get price tracking by product and user error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_price_trackings_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            print(f"[DEBUG] Getting price trackings for user: {user_id}")
            # Simple query without order_by to avoid composite index requirement
            docs = (
                self.db.collection('price_tracking')
                .where('user_id', '==', user_id)
                .where('is_active', '==', True)
                .stream()
            )

            trackings: List[Dict[str, Any]] = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Fetch product info
                product_id = data.get('product_id')
                if product_id:
                    product = self.get_product_by_id(product_id)
                    if product:
                        data['product_name'] = product.get('name')
                        data['product_brand'] = product.get('brand')
                        data['product_image'] = product.get('image')
                trackings.append(data)

            # Sort in memory by created_at (newest first) if available
            def _created_at_key(item: Dict[str, Any]):
                ts = item.get('created_at')
                try:
                    if hasattr(ts, 'timestamp'):
                        return ts
                    if isinstance(ts, datetime):
                        return ts
                    return datetime.min
                except Exception:
                    return datetime.min

            trackings.sort(key=_created_at_key, reverse=True)

            print(f"[DEBUG] Found {len(trackings)} price trackings")
            return trackings
        except Exception as e:
            print(f"[ERROR] Get price trackings by user id error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_all_active_price_trackings(self) -> List[Dict[str, Any]]:
        """Return all active price tracking records."""
        try:
            docs = self.db.collection('price_tracking').where('is_active', '==', True).stream()
            trackings: List[Dict[str, Any]] = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                trackings.append(data)
            return trackings
        except Exception as e:
            print(f"[ERROR] Get all active price trackings error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def update_price_tracking(self, tracking_id: str, new_price: Optional[str] = None, price_change: Optional[str] = None, is_active: Optional[bool] = None) -> bool:
        try:
            updates = {}
            if new_price is not None:
                updates['current_price'] = new_price
            if price_change is not None:
                updates['price_change'] = price_change
            if is_active is not None:
                updates['is_active'] = is_active
            if not updates:
                return False
            self.db.collection('price_tracking').document(tracking_id).update(updates)
            return True
        except Exception as e:
            print(f"[ERROR] Update price tracking error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def remove_price_tracking(self, tracking_id: str) -> bool:
        try:
            self.db.collection('price_tracking').document(tracking_id).update({'is_active': False})
            return True
        except Exception as e:
            print(f"[ERROR] Remove price tracking error: {e}")
            return False
    
    # Price history operations
    def add_price_history(self, product_id: str, price: str, recorded_at: datetime) -> str:
        history_id = str(uuid.uuid4())
        history_data = {
            'product_id': product_id,
            'price': price,
            'recorded_at': self._datetime_to_timestamp(recorded_at)
        }
        self.db.collection('price_history').document(history_id).set(history_data)
        return history_id
    
    def get_price_history_by_product_id(self, product_id: str, limit: int = 60) -> List[Dict[str, Any]]:
        docs = self.db.collection('price_history').where('product_id', '==', product_id).order_by('recorded_at', direction=firestore.Query.ASCENDING).limit(limit).stream()
        return [{'price': doc.to_dict()['price'], 'recorded_at': doc.to_dict()['recorded_at']} for doc in docs]
    
    # Notification operations
    def create_notification(self, user_id: str, product_id: Optional[str], 
                           notification_type: str, message: str,
                           payload: Optional[str] = None,
                           created_at: datetime = None) -> str:
        notification_id = str(uuid.uuid4())
        if created_at is None:
            created_at = datetime.now()
        
        notification_data = {
            'user_id': user_id,
            'product_id': product_id,
            'type': notification_type,
            'message': message,
            'payload': payload,
            'read_at': None,
            'created_at': self._datetime_to_timestamp(created_at)
        }
        self.db.collection('notifications').document(notification_id).set(notification_data)
        return notification_id
    
    def get_notifications_by_user_id(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        docs = self.db.collection('notifications').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
        notifications = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            notifications.append(data)
        return notifications
    
    def mark_notifications_read(self, user_id: str) -> bool:
        try:
            refs = self.db.collection('notifications').where('user_id', '==', user_id).where('read_at', '==', None).stream()
            batch = self.db.batch()
            count = 0
            for ref in refs:
                batch.update(ref.reference, {'read_at': self._datetime_to_timestamp(datetime.now())})
                count += 1
                if count >= 500:  # Firestore batch limit
                    batch.commit()
                    batch = self.db.batch()
                    count = 0
            if count > 0:
                batch.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Mark notifications read error: {e}")
            return False
    
    # Product import issues operations
    def create_import_issue(self, user_id: str, url: str, status: str,
                           reason: Optional[str] = None,
                           raw_data: Optional[str] = None,
                           created_at: datetime = None,
                           error_code: Optional[str] = None,
                           error_category: Optional[str] = None,
                           domain: Optional[str] = None,
                           retry_count: int = 0,
                           resolved: bool = False) -> str:
        issue_id = str(uuid.uuid4())
        if created_at is None:
            created_at = datetime.now()
        
        if isinstance(raw_data, dict):
            raw_data = json.dumps(raw_data)
        
        # Extract domain from URL if not provided
        if not domain and url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = (parsed.netloc or "").lower().replace("www.", "")
            except Exception:
                domain = None
        
        issue_data = {
            'user_id': user_id,
            'url': url,
            'status': status,
            'reason': reason,
            'raw_data': raw_data,
            'created_at': self._datetime_to_timestamp(created_at),
            'error_code': error_code,
            'error_category': error_category,
            'domain': domain,
            'retry_count': retry_count,
            'resolved': resolved,
            'last_retry_at': None
        }
        self.db.collection('product_import_issues').document(issue_id).set(issue_data)
        return issue_id
    
    def update_import_issue_retry(self, issue_id: str, retry_count: int) -> bool:
        """Update retry count for an import issue"""
        try:
            self.db.collection('product_import_issues').document(issue_id).update({
                'retry_count': retry_count,
                'last_retry_at': self._datetime_to_timestamp(datetime.now())
            })
            return True
        except Exception as e:
            print(f"[ERROR] Update import issue retry error: {e}")
            return False
    
    def mark_import_issue_resolved(self, issue_id: str) -> bool:
        """Mark an import issue as resolved"""
        try:
            self.db.collection('product_import_issues').document(issue_id).update({
                'resolved': True
            })
            return True
        except Exception as e:
            print(f"[ERROR] Mark import issue resolved error: {e}")
            return False
    
    def delete_import_issue(self, issue_id: str, user_id: str) -> bool:
        """Delete an import issue (only if it belongs to the user)"""
        try:
            doc_ref = self.db.collection('product_import_issues').document(issue_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                print(f"[ERROR] Import issue not found: {issue_id}")
                return False
            
            issue_data = doc.to_dict()
            if issue_data.get('user_id') != user_id:
                print(f"[ERROR] User {user_id} cannot delete issue {issue_id} (belongs to {issue_data.get('user_id')})")
                return False
            
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"[ERROR] Delete import issue error: {e}")
            return False
    
    def get_import_issues_by_domain(self, domain: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get import issues for a specific domain"""
        try:
            docs = self.db.collection('product_import_issues').where('domain', '==', domain).order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
            issues = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                issues.append(data)
            return issues
        except Exception as e:
            print(f"[ERROR] Get import issues by domain error: {e}")
            return []
    
    def get_import_issue_statistics(self) -> Dict[str, Any]:
        """Get statistics about import issues"""
        try:
            all_issues = self.db.collection('product_import_issues').stream()
            
            stats = {
                'total': 0,
                'failed': 0,
                'partial': 0,
                'resolved': 0,
                'by_domain': {},
                'by_error_category': {},
                'by_status': {}
            }
            
            for doc in all_issues:
                data = doc.to_dict()
                stats['total'] += 1
                
                status = data.get('status', 'unknown')
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                if status == 'failed':
                    stats['failed'] += 1
                elif status == 'partial':
                    stats['partial'] += 1
                
                if data.get('resolved'):
                    stats['resolved'] += 1
                
                domain = data.get('domain')
                if domain:
                    stats['by_domain'][domain] = stats['by_domain'].get(domain, 0) + 1
                
                error_category = data.get('error_category')
                if error_category:
                    stats['by_error_category'][error_category] = stats['by_error_category'].get(error_category, 0) + 1
            
            return stats
        except Exception as e:
            print(f"[ERROR] Get import issue statistics error: {e}")
            return {}
    
    def get_import_issues_by_user_id(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        docs = self.db.collection('product_import_issues').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
        issues = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            issues.append(data)
        return issues
    
    def get_all_import_issues(self, limit: int = 200) -> List[Dict[str, Any]]:
        docs = self.db.collection('product_import_issues').order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
        issues = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            # Fetch username
            user_id = data.get('user_id')
            if user_id:
                user = self.get_user_by_id(user_id)
                if user:
                    data['username'] = user.get('username')
            issues.append(data)
        return issues
    
    # Follow operations
    def follow_user(self, follower_id: str, following_id: str) -> bool:
        """Follow a user"""
        if follower_id == following_id:
            return False  # Can't follow yourself
        
        try:
            # Check if already following
            existing = self.db.collection('follows').where('follower_id', '==', follower_id).where('following_id', '==', following_id).limit(1).stream()
            if list(existing):
                return False  # Already following
            
            follow_id = str(uuid.uuid4())
            follow_data = {
                'follower_id': follower_id,
                'following_id': following_id,
                'created_at': self._datetime_to_timestamp(datetime.now())
            }
            self.db.collection('follows').document(follow_id).set(follow_data)
            return True
        except Exception as e:
            print(f"[ERROR] Follow user error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def unfollow_user(self, follower_id: str, following_id: str) -> bool:
        """Unfollow a user"""
        try:
            follows = self.db.collection('follows').where('follower_id', '==', follower_id).where('following_id', '==', following_id).stream()
            deleted = False
            for follow in follows:
                follow.reference.delete()
                deleted = True
            return deleted
        except Exception as e:
            print(f"[ERROR] Unfollow user error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def is_following(self, follower_id: str, following_id: str) -> bool:
        """Check if user is following another user"""
        try:
            follows = self.db.collection('follows').where('follower_id', '==', follower_id).where('following_id', '==', following_id).limit(1).stream()
            return len(list(follows)) > 0
        except Exception as e:
            print(f"[ERROR] Is following check error: {e}")
            return False
    
    def get_followers(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all followers of a user"""
        try:
            follows = self.db.collection('follows').where('following_id', '==', user_id).stream()
            followers = []
            for follow in follows:
                data = follow.to_dict()
                data['id'] = follow.id
                # Fetch user info
                follower_id = data.get('follower_id')
                if follower_id:
                    user = self.get_user_by_id(follower_id)
                    if user:
                        data['username'] = user.get('username')
                        data['email'] = user.get('email')
                followers.append(data)
            return followers
        except Exception as e:
            print(f"[ERROR] Get followers error: {e}")
            return []
    
    def get_following(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all users that a user is following"""
        try:
            follows = self.db.collection('follows').where('follower_id', '==', user_id).stream()
            following = []
            for follow in follows:
                data = follow.to_dict()
                data['id'] = follow.id
                # Fetch user info
                following_id = data.get('following_id')
                if following_id:
                    user = self.get_user_by_id(following_id)
                    if user:
                        data['username'] = user.get('username')
                        data['email'] = user.get('email')
                following.append(data)
            return following
        except Exception as e:
            print(f"[ERROR] Get following error: {e}")
            return []
    
    # Collection like operations
    def like_collection(self, user_id: str, collection_id: str) -> bool:
        """Like a collection"""
        try:
            # Check if already liked
            existing = self.db.collection('likes').where('user_id', '==', user_id).where('collection_id', '==', collection_id).limit(1).stream()
            if list(existing):
                return False  # Already liked
            
            like_id = str(uuid.uuid4())
            like_data = {
                'user_id': user_id,
                'collection_id': collection_id,
                'created_at': self._datetime_to_timestamp(datetime.now())
            }
            self.db.collection('likes').document(like_id).set(like_data)
            return True
        except Exception as e:
            print(f"[ERROR] Like collection error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def unlike_collection(self, user_id: str, collection_id: str) -> bool:
        """Unlike a collection"""
        try:
            likes = self.db.collection('likes').where('user_id', '==', user_id).where('collection_id', '==', collection_id).stream()
            deleted = False
            for like in likes:
                like.reference.delete()
                deleted = True
            return deleted
        except Exception as e:
            print(f"[ERROR] Unlike collection error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def is_collection_liked(self, user_id: str, collection_id: str) -> bool:
        """Check if collection is liked by user"""
        try:
            likes = self.db.collection('likes').where('user_id', '==', user_id).where('collection_id', '==', collection_id).limit(1).stream()
            return len(list(likes)) > 0
        except Exception as e:
            print(f"[ERROR] Is collection liked check error: {e}")
            return False
    
    def get_collection_likes_count(self, collection_id: str) -> int:
        """Get total likes count for a collection"""
        try:
            likes = self.db.collection('likes').where('collection_id', '==', collection_id).stream()
            return len(list(likes))
        except Exception as e:
            print(f"[ERROR] Get collection likes count error: {e}")
            return 0

