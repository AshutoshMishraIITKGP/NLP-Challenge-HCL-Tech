"""Flask server to serve the web interface."""
from flask import Flask, send_from_directory, render_template
import os

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("=" * 80)
    print("AGENTIC RAG WEB INTERFACE")
    print("=" * 80)
    print("\nStarting web server...")
    print("Frontend: http://127.0.0.1:5000")
    print("Backend API: http://127.0.0.1:8000")
    print("\nMake sure to start the backend API first:")
    print("  python backend_api.py")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
