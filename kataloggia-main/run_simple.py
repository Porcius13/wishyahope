"""
Simple startup without SocketIO for troubleshooting
"""
import os
import sys

from dotenv import load_dotenv

# Ensure project root is on path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Load environment variables
project_root = parent_dir
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

print("=" * 60)
print("Starting Favit Application (Simple Mode)")
print("=" * 60)

try:
    print("\n[1/5] Importing modules...")
    from app import create_app
    from models import init_db
    from app.utils.database_indexer import DatabaseIndexer
    print("✓ Modules imported")
    
    print("\n[2/5] Creating Flask app...")
    app = create_app('development')
    print("✓ App created")
    
    print("\n[3/5] Initializing database...")
    init_db()
    print("✓ Database initialized")
    
    print("\n[4/5] Creating indexes...")
    try:
        DatabaseIndexer.create_indexes()
        print("✓ Indexes created")
    except Exception as e:
        print(f"⚠ Index creation warning: {e}")
    
    print("\n[5/5] Starting server...")
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')  # Use 127.0.0.1 instead of 0.0.0.0
    
    print(f"\n{'=' * 60}")
    print(f"Server starting on http://{host}:{port}")
    print(f"{'=' * 60}\n")
    
    # Run without SocketIO
    app.run(host=host, port=port, debug=True, use_reloader=False)
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nPlease install missing dependencies:")
    print("  pip install -r requirements.txt")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
