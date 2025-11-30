import sys
import os

# Add the nested project directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
nested_dir = os.path.join(current_dir, 'kataloggia-main')
sys.path.insert(0, nested_dir)
sys.path.insert(0, current_dir)

from app import create_app
from models import init_db

app = create_app('production')

# Initialize DB on startup (for SQLite)
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run()
