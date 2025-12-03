"""
Check which database backend is being used
"""
import sys
import os

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
kataloggia_main = os.path.join(project_root, 'kataloggia-main')
sys.path.insert(0, kataloggia_main)
sys.path.insert(0, project_root)

from app.config import Config
from app.repositories import get_repository

def main():
    print("="*60)
    print("Database Backend Kontrolü")
    print("="*60)
    
    print(f"\nDB_BACKEND (Config): {Config.DB_BACKEND}")
    print(f"DB_BACKEND (Environment): {os.environ.get('DB_BACKEND', 'NOT SET')}")
    
    try:
        repo = get_repository()
        repo_type = type(repo).__name__
        print(f"\nRepository Type: {repo_type}")
        
        if 'Firestore' in repo_type:
            print("✓ Firestore repository kullanılıyor")
        elif 'SQLite' in repo_type:
            print("⚠ SQLite repository kullanılıyor (Firestore bekleniyorsa sorun var!)")
        else:
            print(f"? Bilinmeyen repository tipi: {repo_type}")
            
    except Exception as e:
        print(f"\n✗ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

