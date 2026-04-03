import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

# For the app to be importable as 'app'
# This is what openenv.yaml references with 'app: server.app:app'
