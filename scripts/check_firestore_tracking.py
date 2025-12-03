"""
Check price tracking in Firestore
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
    print("Firestore Price Tracking Kontrol")
    print("="*60)
    print(f"Project ID: {Config.FIREBASE_PROJECT_ID}")
    print(f"Credentials Path: {Config.FIREBASE_CREDENTIALS_PATH}")
    print("="*60)
    print()
    
    try:
        repo = FirestoreRepository()
        print("✓ Firestore repository initialized")
        print()
        
        # Get all price trackings
        print("Fiyat takipleri getiriliyor...")
        print()
        
        # Get all active trackings
        trackings = repo.get_price_trackings_by_user_id("1f2c15c4-7a0c-46b7-ae44-23201118711b")
        
        if trackings:
            print("-"*60)
            print("FİYAT TAKİPLERİ:")
            print("-"*60)
            for i, tracking in enumerate(trackings, 1):
                print(f"[{i}] Tracking ID: {tracking.get('id')}")
                print(f"    Product ID: {tracking.get('product_id')}")
                print(f"    User ID: {tracking.get('user_id')}")
                print(f"    Current Price: {tracking.get('current_price')}")
                print(f"    Original Price: {tracking.get('original_price')}")
                print(f"    Is Active: {tracking.get('is_active')}")
                print(f"    Created At: {tracking.get('created_at')}")
                print()
            
            print("-"*60)
            print(f"✓ Toplam {len(trackings)} fiyat takibi bulundu")
            print("-"*60)
        else:
            print("⚠ Hiç fiyat takibi bulunamadı")
        
    except Exception as e:
        print(f"\n✗ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

