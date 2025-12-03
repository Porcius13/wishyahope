"""
Product Model
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
from models import Product as BaseProduct

# Mevcut Product modelini kullan
Product = BaseProduct

# to_dict method ekle
def to_dict(self):
    """Product'ı dictionary'ye çevir"""
    return {
        'id': self.id,
        'user_id': self.user_id,
        'name': self.name,
        'price': self.price,
        'image': self.image,
        'brand': self.brand,
        'url': self.url,
        'created_at': str(self.created_at),
        'old_price': self.old_price,
        'current_price': self.current_price,
        'discount_percentage': self.discount_percentage
    }

# Method'u ekle
BaseProduct.to_dict = to_dict

# get_by_user_id method ekle - Repository pattern kullanıyor
@classmethod
def get_by_user_id(cls, user_id):
    """Kullanıcı ID'sine göre ürünleri getir (Repository pattern)"""
    from app.repositories import get_repository
    from datetime import datetime
    import json
    
    repo = get_repository()
    products_data = repo.get_products_by_user_id(user_id)
    
    products = []
    for product_data in products_data:
        # Handle images
        images_data = product_data.get('images')
        if isinstance(images_data, str):
            try:
                images_data = json.loads(images_data)
            except:
                images_data = [product_data.get('image')] if product_data.get('image') else []
        elif not images_data:
            images_data = [product_data.get('image')] if product_data.get('image') else []
        
        # Handle timestamp
        created_at = product_data.get('created_at')
        if hasattr(created_at, 'timestamp'):  # Firestore Timestamp
            created_at = created_at
        elif isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                except:
                    created_at = datetime.now()
        elif created_at is None:
            created_at = datetime.now()
        
        product = cls(
            product_data.get('id'),
            product_data.get('user_id'),
            product_data.get('name'),
            product_data.get('price'),
            product_data.get('image'),
            product_data.get('brand'),
            product_data.get('url'),
            created_at,
            product_data.get('old_price'),
            product_data.get('current_price'),
            product_data.get('discount_percentage'),
            images_data,
            product_data.get('discount_info')
        )
        products.append(product)
    
    return products

BaseProduct.get_by_user_id = get_by_user_id

Product = BaseProduct

