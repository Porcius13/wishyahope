"""
Application entry point for the modular Flask app.
This is the **only** backend entrypoint; legacy monolithic app.py is deprecated.
"""
import os
import sys

from dotenv import load_dotenv

# Ensure project root is on path (so we can import models.py etc.)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Load environment variables from .env at project root
project_root = parent_dir
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app, get_socketio
from models import init_db
from app.utils.database_indexer import DatabaseIndexer

# Create app using factory
app = create_app('development')

# Initialize database
init_db()
print("[INFO] Veritabanı başlatıldı")

# Create indexes for performance
try:
    DatabaseIndexer.create_indexes()
    print("[INFO] Database indexler oluşturuldu")
except Exception as e:
    print(f"[WARNING] Index oluşturma hatası: {e}")


if __name__ == "__main__":
    # Port ayarı - ortam değişkeninden veya varsayılan 5000
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    print("[INFO] Uygulama başlatılıyor...")
    print(f"[INFO] Host: {host}")
    print(f"[INFO] Port: {port}")
    print(f"[INFO] Debug: {debug}")
    print(f"[INFO] URL: http://localhost:{port}")

    socketio = get_socketio()
    if socketio:
        # Run with SocketIO
        socketio.run(app, host=host, port=port, debug=debug)
    else:
        # Run without SocketIO
        app.run(host=host, port=port, debug=debug)
