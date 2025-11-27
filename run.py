#!/usr/bin/env python3
"""
Entry point for the Student Notes Sharing Platform.
Run this file to start the development server.
"""

import os
import sys
from pathlib import Path

# Add backend to path so we can import modules
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app import create_app, socketio

# Get configuration from environment or default to development
config_name = os.environ.get('FLASK_ENV', 'development')

# Create the Flask application
app = create_app(config_name)

if __name__ == '__main__':
    # Get port from environment (for deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run with SocketIO for WebSocket support
    socketio.run(
        app,
        debug=(config_name == 'development'),
        host='0.0.0.0',
        port=port,
        allow_unsafe_werkzeug=True
    )


