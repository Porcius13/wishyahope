#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple startup script with error handling"""
import sys
import os
import traceback

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print("=" * 60)
print("Starting Application...")
print("=" * 60)

try:
    print("\n[1/5] Importing modules...")
    from app import create_app, get_socketio
    from models import init_db
    print("   ✓ Imports successful")
    
    print("\n[2/5] Creating app...")
    app = create_app('development')
    print("   ✓ App created")
    
    print("\n[3/5] Initializing database...")
    init_db()
    print("   ✓ Database initialized")
    
    print("\n[4/5] Getting SocketIO...")
    socketio = get_socketio()
    if socketio:
        print("   ✓ SocketIO available")
    else:
        print("   ⚠ SocketIO not available (running without)")
    
    print("\n[5/5] Starting server...")
    port = int(os.environ.get('PORT', 5000))
    host = '127.0.0.1'  # Use localhost instead of 0.0.0.0
    debug = True
    
    print(f"\n{'=' * 60}")
    print(f"Server starting on: http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"{'=' * 60}\n")
    
    if socketio:
        socketio.run(app, host=host, port=port, debug=debug, use_reloader=False)
    else:
        app.run(host=host, port=port, debug=debug, use_reloader=False)
        
except KeyboardInterrupt:
    print("\n\nServer stopped by user")
except Exception as e:
    print(f"\n\n❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
