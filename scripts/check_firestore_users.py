"""
Firestore'da kullanıcıları kontrol et
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
    print("Firestore Users Kontrol")
    print("="*60)
    print(f"Project ID: {Config.FIREBASE_PROJECT_ID}")
    print(f"Credentials Path: {Config.FIREBASE_CREDENTIALS_PATH or 'Application Default Credentials'}")
    print("="*60)
    
    try:
        # Initialize Firestore repository
        print("\nFirestore'a bağlanılıyor...")
        repo = FirestoreRepository()
        print("✓ Bağlantı başarılı!")
        
        # Get all users (we'll need to query directly)
        print("\nKullanıcılar getiriliyor...")
        db = repo.db
        users_ref = db.collection('users')
        users = users_ref.stream()
        
        user_count = 0
        print("\n" + "-"*60)
        print("KULLANICILAR:")
        print("-"*60)
        
        for user_doc in users:
            user_count += 1
            user_data = user_doc.to_dict()
            print(f"\n[{user_count}] User ID: {user_doc.id}")
            print(f"    Username: {user_data.get('username', 'N/A')}")
            print(f"    Email: {user_data.get('email', 'N/A')}")
            print(f"    Profile URL: {user_data.get('profile_url', 'N/A')}")
            created_at = user_data.get('created_at')
            if created_at:
                print(f"    Created At: {created_at}")
        
        print("\n" + "-"*60)
        if user_count == 0:
            print("⚠️  Henüz hiç kullanıcı yok!")
        else:
            print(f"✓ Toplam {user_count} kullanıcı bulundu")
        print("-"*60)
        
    except ImportError as e:
        print(f"\n✗ Firebase Admin SDK yüklü değil: {e}")
        print("   Çözüm: pip install firebase-admin")
    except Exception as e:
        print(f"\n✗ Hata: {e}")
        import traceback
        traceback.print_exc()
        print("\nOlası sorunlar:")
        print("1. FIREBASE_CREDENTIALS_PATH yanlış veya dosya bulunamıyor")
        print("2. Service Account Key geçersiz")
        print("3. Firebase projesi bulunamıyor")
        print("4. Firestore Database aktif değil")

if __name__ == '__main__':
    main()

