"""Run app and capture errors"""
import sys
import os
import traceback

# Redirect stderr to a file
error_file = os.path.join(os.path.dirname(__file__), 'startup_errors.log')
sys.stderr = open(error_file, 'w', encoding='utf-8')
sys.stdout = open(error_file, 'w', encoding='utf-8')

try:
    print("Starting application...")
    print("=" * 50)
    
    from dotenv import load_dotenv
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    
    project_root = parent_dir
    dotenv_path = os.path.join(project_root, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    
    print("Importing modules...")
    from app import create_app, get_socketio
    from models import init_db
    from app.utils.database_indexer import DatabaseIndexer
    
    print("Creating app...")
    app = create_app('development')
    
    print("Initializing database...")
    init_db()
    print("[INFO] Veritabanı başlatıldı")
    
    try:
        DatabaseIndexer.create_indexes()
        print("[INFO] Database indexler oluşturuldu")
    except Exception as e:
        print(f"[WARNING] Index oluşturma hatası: {e}")
    
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
        print("Starting with SocketIO...")
        socketio.run(app, host=host, port=port, debug=debug)
    else:
        print("Starting without SocketIO...")
        app.run(host=host, port=port, debug=debug)
        
except Exception as e:
    print(f"\nERROR: {e}")
    traceback.print_exc()
    sys.stderr.close()
    sys.stdout.close()
    # Also print to console
    with open(error_file, 'r', encoding='utf-8') as f:
        print(f.read())
    sys.exit(1)
