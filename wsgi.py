"""
WSGI entry point for production deployment.
Used by Gunicorn and other WSGI servers.
"""

import os
from backend.app import create_app, socketio

# Create app with production config
app = create_app('production')

# For Gunicorn with eventlet
if __name__ == '__main__':
    socketio.run(app)


