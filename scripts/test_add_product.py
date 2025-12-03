"""
Test script: Firestore'a ürün ekleme testi
"""
import sys
import os
from datetime import datetime

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
kataloggia_main = os.path.join(project_root, 'kataloggia-main')
sys.path.insert(0, kataloggia_main)
sys.path.insert(0, project_root)

from app.repositories.firestore_repository import FirestoreRepository
from app.config import Config

def main():
    print("="*60)
    print("Firestore Ürün Ekleme Testi")
    print("="*60)
    
    try:
        repo = FirestoreRepository()
        print("✓ Firestore repository initialized")
        
        # Test user ID (mevcut kullanıcılardan biri)
        test_user_id = "1f2c15c4-7a0c-46b7-ae44-23201118711b"  # Mevcut kullanıcılardan biri
        
        print(f"\nTest ürünü ekleniyor (user_id: {test_user_id})...")
        product_id = repo.create_product(
            user_id=test_user_id,
            name="TEST ÜRÜN",
            price="999,00 TL",
            image="https://example.com/test.jpg",
            brand="TEST BRAND",
            url="https://example.com/test-product",
            created_at=datetime.now(),
            old_price=None,
            current_price="999,00 TL",
            discount_percentage=None,
            images=None,
            discount_info=None
        )
        
        print(f"✓ Ürün oluşturuldu: {product_id}")
        
        # Kontrol et
        product = repo.get_product_by_id(product_id)
        if product:
            print(f"\n✓ Ürün Firestore'da bulundu:")
            print(f"  ID: {product.get('id')}")
            print(f"  Name: {product.get('name')}")
            print(f"  User ID: {product.get('user_id')}")
        else:
            print("\n✗ Ürün Firestore'da bulunamadı!")
        
        # Tüm ürünleri listele
        print("\n" + "-"*60)
        print("TÜM ÜRÜNLER:")
        print("-"*60)
        all_products = repo.get_products_by_user_id(test_user_id)
        for i, p in enumerate(all_products, 1):
            print(f"[{i}] {p.get('name')} - {p.get('id')}")
        
    except Exception as e:
        print(f"\n✗ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

