import sys
import os

# Add backend to path so we can import 'main'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

print("verifying routes...")
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"Route: {route.path}")
