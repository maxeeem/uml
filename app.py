"""
Local development server that serves both the Flask API and static files.
Run this with: python app.py
"""
from flask import Flask, send_from_directory
from pathlib import Path
import os

# Load .env only when running locally (app.py is not used on Vercel)
if not os.environ.get("VERCEL"):
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parent
    env_path = project_root / '.env'
    load_dotenv(dotenv_path=env_path)

# Import the API blueprint
from api.generate import api_bp

# Create main app
app = Flask(__name__, static_folder='public')

# Register API blueprint
app.register_blueprint(api_bp, url_prefix='/api')

# Serve static files from public directory
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('public', path)

if __name__ == '__main__':
    # Default to port 8000 to avoid conflicts with macOS AirPlay Receiver (port 5000)
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting local development server on http://localhost:{port}")
    print("Access code check is DISABLED for localhost (set ACCESS_CODE env var to enable)")
    try:
        app.run(debug=True, host='0.0.0.0', port=port)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n⚠️  Port {port} is already in use!")
            print(f"Try setting a different port: PORT=8001 python app.py")
            print("Or disable AirPlay Receiver in System Settings > General > AirDrop & Handoff")
        else:
            raise
