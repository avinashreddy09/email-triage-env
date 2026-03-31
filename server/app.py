"""Main entry point for OpenEnv environment"""

from environment import EmailTriageEnv
import uvicorn

def main():
    """Run the FastAPI server"""
    from main import app
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
