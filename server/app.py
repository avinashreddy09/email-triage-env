import sys
import os

# Add parent directory to path so we can import main
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from main import app

def main():
    """Entry point for the OpenEnv environment"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
