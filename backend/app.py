"""​
Main Flask Application for Student Notes Sharing Platform.
Initializes the app, registers blueprints, and sets up SocketIO for real-time features.
"""

import os
import sys
from pathlib import Path

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from models import db, init_db, LiveNote
from api import api

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")

# Track active users per room
active_users = {}


def create_app(config_name='default'):
    """Application factory for creating the Flask app."""
    
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app)
    
    # Initialize extensions
    init_db(app)
    socketio.init_app(app, async_mode='threading')
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), ''), exist_ok=True)
    
    # ============== Page Routes ==============
    
    @app.route('/')
    def home():
        """Homepage with hero, department grid, and recent uploads."""
        return render_template('home.html')
    
    @app.route('/department/<slug>')
    def department(slug):
        """Department page showing subjects list."""
        return render_template('department.html', dept_slug=slug)
    
    @app.route('/department/<dept_slug>/semester/<int:semester_id>/subject/<subject_slug>')
    def subject(dept_slug, semester_id, subject_slug):
        """Subject page showing units accordion."""
        return render_template('subject.html', dept_slug=dept_slug, semester_id=semester_id, subject_slug=subject_slug)
    
    @app.route('/department/<dept_slug>/semester/<int:semester_id>/subject/<subject_slug>/unit/<int:unit_id>')
    def unit_notes(dept_slug, semester_id, subject_slug, unit_id):
        """Notes list page for a unit."""
        return render_template('notes_list.html', dept_slug=dept_slug, semester_id=semester_id, subject_slug=subject_slug, unit_id=unit_id)
    
    @app.route('/note/<int:note_id>')
    def view_note(note_id):
        """View a single note with PDF viewer and QR code."""
        return render_template('view_note.html', note_id=note_id)
    
    @app.route('/live-notes')
    def live_notes_list():
        """List of all live collaborative notes."""
        return render_template('live_notes_list.html')
    
    @app.route('/live/<slug>')
    def live_note(slug):
        """Live collaborative note editor."""
        return render_template('live_note.html', note_slug=slug)
    
    @app.route('/search')
    def search_page():
        """Search and filter notes."""
        return render_template('search.html')
    
    @app.route('/about')
    def about():
        """About page."""
        return render_template('about.html')
    
    @app.route('/upload')
    def upload_page():
        """Upload notes page."""
        return render_template('upload.html')
    
    @app.route('/admin')
    def admin_page():
        """Admin panel for managing departments, subjects, and units."""
        return render_template('admin.html')
    
    # Serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files."""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/uploads/thumbnails/<path:filename>')
    def thumbnail_file(filename):
        """Serve thumbnail files."""
        return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    
    return app


# ============== SocketIO Events for Live Notes ==============

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('connected', {'status': 'Connected to server'})


@socketio.on('join_note')
def handle_join_note(data):
    """Handle user joining a live note room."""
    room = data.get('room')
    if room:
        join_room(room)
        
        # Track active users
        if room not in active_users:
            active_users[room] = 0
        active_users[room] += 1
        
        # Update database
        note = LiveNote.query.filter_by(slug=room).first()
        if note:
            note.active_editors = active_users[room]
            db.session.commit()
        
        emit('user_joined', {
            'active_users': active_users[room]
        }, room=room)


@socketio.on('leave_note')
def handle_leave_note(data):
    """Handle user leaving a live note room."""
    room = data.get('room')
    if room:
        leave_room(room)
        
        # Update active users
        if room in active_users:
            active_users[room] = max(0, active_users[room] - 1)
            
            # Update database
            note = LiveNote.query.filter_by(slug=room).first()
            if note:
                note.active_editors = active_users[room]
                db.session.commit()
            
            emit('user_left', {
                'active_users': active_users[room]
            }, room=room)


@socketio.on('content_change')
def handle_content_change(data):
    """Handle real-time content updates."""
    room = data.get('room')
    content = data.get('content', '')
    
    if room:
        # Save to database (auto-save)
        note = LiveNote.query.filter_by(slug=room).first()
        if note:
            note.content = content
            db.session.commit()
        
        # Broadcast to all users in the room except sender
        emit('content_updated', {
            'content': content
        }, room=room, include_self=False)


@socketio.on('cursor_position')
def handle_cursor_position(data):
    """Handle cursor position updates for collaboration awareness."""
    room = data.get('room')
    position = data.get('position')
    user_id = data.get('user_id')
    
    if room and position:
        emit('cursor_moved', {
            'user_id': user_id,
            'position': position
        }, room=room, include_self=False)


# Application entry point
if __name__ == '__main__':
    app = create_app('development')
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
