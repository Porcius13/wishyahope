"""
Firestore'da ürünleri kontrol et
"""
import sys
import os

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
    print("Firestore Products Kontrol")
    print("="*60)
    print(f"Project ID: {Config.FIREBASE_PROJECT_ID}")
    print(f"Credentials Path: {Config.FIREBASE_CREDENTIALS_PATH or 'Application Default Credentials'}")
    print("="*60)
    
    try:
        # Initialize Firestore repository
        print("\nFirestore'a bağlanılıyor...")
        repo = FirestoreRepository()
        print("✓ Bağlantı başarılı!")
        
        # Get all products
        print("\nÜrünler getiriliyor...")
        db = repo.db
        products_ref = db.collection('products')
        products = products_ref.stream()
        
        product_count = 0
        print("\n" + "-"*60)
        print("ÜRÜNLER:")
        print("-"*60)
        
        for product_doc in products:
            product_count += 1
            product_data = product_doc.to_dict()
            print(f"\n[{product_count}] Product ID: {product_doc.id}")
            print(f"    Name: {product_data.get('name', 'N/A')}")
            print(f"    Brand: {product_data.get('brand', 'N/A')}")
            print(f"    Price: {product_data.get('price', 'N/A')}")
            print(f"    User ID: {product_data.get('user_id', 'N/A')}")
            created_at = product_data.get('created_at')
            if created_at:
                print(f"    Created At: {created_at}")
        
        print("\n" + "-"*60)
        if product_count == 0:
            print("⚠️  Henüz hiç ürün yok!")
        else:
            print(f"✓ Toplam {product_count} ürün bulundu")
        print("-"*60)
        
    except ImportError as e:
        print(f"\n✗ Firebase Admin SDK yüklü değil: {e}")
        print("   Çözüm: pip install firebase-admin")
    except Exception as e:
        print(f"\n✗ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

