"""Test startup to see errors"""
import sys
import os
import traceback

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print(f"Python version: {sys.version}")
print(f"Current directory: {current_dir}")
print(f"Parent directory: {parent_dir}")
print("-" * 50)

try:
    print("1. Testing app import...")
    from app import create_app, get_socketio
    print("   ✓ App import OK")
except Exception as e:
    print(f"   ✗ App import FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("2. Testing models import...")
    from models import init_db
    print("   ✓ Models import OK")
except Exception as e:
    print(f"   ✗ Models import FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("3. Testing app creation...")
    app = create_app('development')
    print("   ✓ App creation OK")
except Exception as e:
    print(f"   ✗ App creation FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("4. Testing database init...")
    init_db()
    print("   ✓ Database init OK")
except Exception as e:
    print(f"   ✗ Database init FAILED: {e}")
    traceback.print_exc()

try:
    print("5. Testing SocketIO...")
    socketio = get_socketio()
    if socketio:
        print("   ✓ SocketIO available")
    else:
        print("   ⚠ SocketIO not available (will run without)")
except Exception as e:
    print(f"   ⚠ SocketIO check FAILED: {e}")

print("-" * 50)
print("All checks passed! Starting server...")
print("-" * 50)

port = int(os.environ.get('PORT', 5000))
host = os.environ.get('HOST', '127.0.0.1')
debug = os.environ.get('DEBUG', 'True').lower() == 'true'

print(f"Starting on http://{host}:{port}")

socketio = get_socketio()
if socketio:
    socketio.run(app, host=host, port=port, debug=debug)
else:
    app.run(host=host, port=port, debug=debug)
