"""Check startup errors"""
import sys
import traceback

try:
    print("=" * 50)
    print("Checking imports...")
    print("=" * 50)
    
    from dotenv import load_dotenv
    print("✓ dotenv imported")
    
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    
    from app import create_app, get_socketio
    print("✓ app imported")
    
    from models import init_db
    print("✓ models imported")
    
    from app.utils.database_indexer import DatabaseIndexer
    print("✓ DatabaseIndexer imported")
    
    print("\n" + "=" * 50)
    print("Creating app...")
    print("=" * 50)
    app = create_app('development')
    print("✓ App created")
    
    print("\n" + "=" * 50)
    print("Initializing database...")
    print("=" * 50)
    init_db()
    print("✓ Database initialized")
    
    print("\n" + "=" * 50)
    print("SUCCESS! App can start.")
    print("=" * 50)
    print("\nTo start the server, run: python run.py")
    
except Exception as e:
    print("\n" + "=" * 50)
    print("ERROR FOUND!")
    print("=" * 50)
    print(f"Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
