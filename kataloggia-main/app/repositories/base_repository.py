"""
Abstract base repository interface
All repository implementations must inherit from this
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime


class BaseRepository(ABC):
    """Abstract base class for all repositories"""
    
    @abstractmethod
    def init_db(self):
        """Initialize database schema/tables"""
        pass
    
    # User operations
    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        pass
    
    @abstractmethod
    def get_user_by_profile_url(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """Get user by profile URL"""
        pass
    
    @abstractmethod
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users (for public user listing)"""
        pass
    
    @abstractmethod
    def create_user(self, username: str, email: str, password_hash: str, 
                   profile_url: str, created_at: datetime, 
                   last_read_notifications_at: Optional[datetime] = None,
                   avatar_url: Optional[str] = None) -> str:
        """Create a new user, returns user_id"""
        pass
    
    @abstractmethod
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user fields"""
        pass
    
    # Product operations
    @abstractmethod
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        pass
    
    @abstractmethod
    def get_product_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Get product by URL (returns the most recent one if multiple exist)"""
        pass
    
    @abstractmethod
    def get_products_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all products for a user"""
        pass
    
    @abstractmethod
    def create_product(self, user_id: str, name: str, price: str, image: Optional[str],
                      brand: str, url: str, created_at: datetime,
                      old_price: Optional[str] = None,
                      current_price: Optional[str] = None,
                      discount_percentage: Optional[str] = None,
                      images: Optional[List[str]] = None,
                      discount_info: Optional[str] = None) -> str:
        """Create a new product, returns product_id"""
        pass
    
    @abstractmethod
    def update_product(self, product_id: str, user_id: str, **kwargs) -> bool:
        """Update product fields"""
        pass
    
    @abstractmethod
    def delete_product(self, product_id: str, user_id: str) -> bool:
        """Delete a product"""
        pass
    
    # Collection operations
    @abstractmethod
    def get_collection_by_id(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """Get collection by ID"""
        pass
    
    @abstractmethod
    def get_collection_by_share_url(self, share_url: str) -> Optional[Dict[str, Any]]:
        """Get collection by share URL"""
        pass
    
    @abstractmethod
    def get_collections_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all collections for a user"""
        pass
    
    @abstractmethod
    def get_products_by_collection_id(self, collection_id: str) -> List[Dict[str, Any]]:
        """Get all products in a collection"""
        pass
    
    @abstractmethod
    def create_collection(self, user_id: str, name: str, description: Optional[str],
                         collection_type: str, is_public: bool, share_url: str,
                         created_at: datetime, cover_image: Optional[str] = None) -> str:
        """Create a new collection, returns collection_id"""
        pass
    
    @abstractmethod
    def add_product_to_collection(self, collection_id: str, product_id: str) -> bool:
        """Add product to collection"""
        pass
    
    @abstractmethod
    def remove_product_from_collection(self, collection_id: str, product_id: str) -> bool:
        """Remove product from collection"""
        pass
    
    @abstractmethod
    def delete_collection(self, collection_id: str, user_id: str) -> bool:
        """Delete a collection"""
        pass
    
    # Favorite operations
    @abstractmethod
    def add_favorite(self, user_id: str, product_id: str) -> bool:
        """Add product to favorites"""
        pass
    
    @abstractmethod
    def remove_favorite(self, user_id: str, product_id: str) -> bool:
        """Remove product from favorites"""
        pass
    
    @abstractmethod
    def get_favorites_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all favorite products for a user"""
        pass
    
    @abstractmethod
    def is_favorite(self, user_id: str, product_id: str) -> bool:
        """Check if product is favorite"""
        pass
    
    # Price tracking operations
    @abstractmethod
    def create_price_tracking(self, user_id: str, product_id: str, current_price: str,
                             original_price: Optional[str] = None,
                             alert_price: Optional[str] = None,
                             created_at: datetime = None) -> str:
        """Create price tracking, returns tracking_id"""
        pass
    
    @abstractmethod
    def get_price_tracking_by_id(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        """Get price tracking by ID"""
        pass
    
    @abstractmethod
    def get_price_tracking_by_product_and_user(self, product_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get price tracking for a product and user"""
        pass
    
    @abstractmethod
    def get_price_trackings_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all price trackings for a user"""
        pass
    
    @abstractmethod
    def update_price_tracking(self, tracking_id: str, new_price: Optional[str] = None, price_change: Optional[str] = None, is_active: Optional[bool] = None) -> bool:
        """Update price tracking"""
        pass
    
    @abstractmethod
    def remove_price_tracking(self, tracking_id: str) -> bool:
        """Remove/deactivate price tracking"""
        pass
    
    # Price history operations
    @abstractmethod
    def add_price_history(self, product_id: str, price: str, recorded_at: datetime) -> str:
        """Add price history entry, returns history_id"""
        pass
    
    @abstractmethod
    def get_price_history_by_product_id(self, product_id: str, limit: int = 60) -> List[Dict[str, Any]]:
        """Get price history for a product"""
        pass
    
    # Notification operations
    @abstractmethod
    def create_notification(self, user_id: str, product_id: Optional[str], 
                           notification_type: str, message: str,
                           payload: Optional[str] = None,
                           created_at: datetime = None) -> str:
        """Create notification, returns notification_id"""
        pass
    
    @abstractmethod
    def get_notifications_by_user_id(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        pass
    
    @abstractmethod
    def mark_notifications_read(self, user_id: str) -> bool:
        """Mark all notifications as read for a user"""
        pass
    
    # Product import issues operations
    @abstractmethod
    def create_import_issue(self, user_id: str, url: str, status: str,
                           reason: Optional[str] = None,
                           raw_data: Optional[str] = None,
                           created_at: datetime = None,
                           error_code: Optional[str] = None,
                           error_category: Optional[str] = None,
                           domain: Optional[str] = None,
                           retry_count: int = 0,
                           resolved: bool = False) -> str:
        """Create import issue with enhanced tracking, returns issue_id"""
        pass
    
    @abstractmethod
    def get_import_issues_by_user_id(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get import issues for a user"""
        pass
    
    @abstractmethod
    def get_all_import_issues(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Get all import issues (admin)"""
        pass
    
    @abstractmethod
    def delete_import_issue(self, issue_id: str, user_id: str) -> bool:
        """Delete an import issue (only if it belongs to the user)"""
        pass
    
    # Follow operations
    @abstractmethod
    def follow_user(self, follower_id: str, following_id: str) -> bool:
        """Follow a user"""
        pass
    
    @abstractmethod
    def unfollow_user(self, follower_id: str, following_id: str) -> bool:
        """Unfollow a user"""
        pass
    
    @abstractmethod
    def is_following(self, follower_id: str, following_id: str) -> bool:
        """Check if user is following another user"""
        pass
    
    @abstractmethod
    def get_followers(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all followers of a user"""
        pass
    
    @abstractmethod
    def get_following(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all users that a user is following"""
        pass
    
    # Collection like operations
    @abstractmethod
    def like_collection(self, user_id: str, collection_id: str) -> bool:
        """Like a collection"""
        pass
    
    @abstractmethod
    def unlike_collection(self, user_id: str, collection_id: str) -> bool:
        """Unlike a collection"""
        pass
    
    @abstractmethod
    def is_collection_liked(self, user_id: str, collection_id: str) -> bool:
        """Check if collection is liked by user"""
        pass
    
    @abstractmethod
    def get_collection_likes_count(self, collection_id: str) -> int:
        """Get total likes count for a collection"""
        pass

