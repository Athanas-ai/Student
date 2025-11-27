"""
Database models for the Student Notes Platform.
Defines all SQLAlchemy models for departments, semesters, subjects, units, notes, and live notes.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Admin(db.Model):
    """Admin user model for authentication."""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_logged_in = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    session_token = db.Column(db.String(100), unique=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'


class Department(db.Model):
    """Department model - top level of the hierarchy."""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='📚')  # Emoji icon
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    semesters = db.relationship('Semester', backref='department', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Department {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'semester_count': self.semesters.count()
        }


class Semester(db.Model):
    """Semester model - belongs to a department."""
    __tablename__ = 'semesters'
    
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4, 5, 6, 7, 8
    name = db.Column(db.String(50))  # Optional name like "First Semester"
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subjects = db.relationship('Subject', backref='semester', lazy='dynamic', cascade='all, delete-orphan')
    
    # Unique constraint for semester number within department
    __table_args__ = (db.UniqueConstraint('number', 'department_id', name='unique_semester_dept'),)
    
    def __repr__(self):
        return f'<Semester {self.number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'name': self.name or f'Semester {self.number}',
            'department_id': self.department_id,
            'subject_count': self.subjects.count()
        }


class Subject(db.Model):
    """Subject model - belongs to a semester."""
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))  # Subject code like CS101
    description = db.Column(db.Text)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    units = db.relationship('Unit', backref='subject', lazy='dynamic', cascade='all, delete-orphan')
    
    # Unique constraint for slug within semester
    __table_args__ = (db.UniqueConstraint('slug', 'semester_id', name='unique_subject_slug'),)
    
    def __repr__(self):
        return f'<Subject {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'code': self.code,
            'description': self.description,
            'semester_id': self.semester_id,
            'unit_count': self.units.count()
        }


class Unit(db.Model):
    """Unit model - belongs to a subject."""
    __tablename__ = 'units'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    number = db.Column(db.Integer, default=1)  # Unit number
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    notes = db.relationship('Note', backref='unit', lazy='dynamic', cascade='all, delete-orphan')
    
    # Unique constraint for slug within subject
    __table_args__ = (db.UniqueConstraint('slug', 'subject_id', name='unique_unit_slug'),)
    
    def __repr__(self):
        return f'<Unit {self.number}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'number': self.number,
            'description': self.description,
            'subject_id': self.subject_id,
            'note_count': self.notes.count()
        }


class Note(db.Model):
    """Note model - uploaded files (PDF/images)."""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)  # Original filename
    stored_filename = db.Column(db.String(255), nullable=False)  # UUID filename
    file_type = db.Column(db.String(10), nullable=False)  # pdf, png, jpg, jpeg
    file_size = db.Column(db.Integer)  # Size in bytes
    thumbnail = db.Column(db.String(255))  # Thumbnail filename
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=False)
    view_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Note {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'filename': self.filename,
            'stored_filename': self.stored_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'thumbnail': self.thumbnail,
            'unit_id': self.unit_id,
            'view_count': self.view_count,
            'download_count': self.download_count,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class LiveNote(db.Model):
    """Live collaborative notes - real-time editing."""
    __tablename__ = 'live_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    content = db.Column(db.Text, default='')  # Rich text content (HTML)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=True)  # Optional unit association
    view_count = db.Column(db.Integer, default=0)
    active_editors = db.Column(db.Integer, default=0)  # Current active editors
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LiveNote {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'unit_id': self.unit_id,
            'view_count': self.view_count,
            'active_editors': self.active_editors,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if Admin.query.count() == 0:
            admin = Admin(username='admin')
            admin.set_password('admin123')  # Default password - change in production!
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: username='admin', password='admin123'")
        
        # Seed initial data if database is empty
        if Department.query.count() == 0:
            seed_data()


def seed_data():
    """Seed the database with initial departments and semesters."""
    departments = [
        {
            'name': 'Computer Science',
            'slug': 'computer-science',
            'description': 'Programming, algorithms, data structures, and software development',
            'icon': '💻',
        },
        {
            'name': 'Electronics',
            'slug': 'electronics',
            'description': 'Circuit design, digital systems, and embedded programming',
            'icon': '🔌',
        },
        {
            'name': 'Mechanical',
            'slug': 'mechanical',
            'description': 'Mechanics, thermodynamics, and manufacturing',
            'icon': '⚙️',
        },
        {
            'name': 'Civil',
            'slug': 'civil',
            'description': 'Structures, construction, and infrastructure',
            'icon': '🏗️',
        },
        {
            'name': 'Electrical',
            'slug': 'electrical',
            'description': 'Power systems, machines, and control systems',
            'icon': '⚡',
        },
    ]
    
    for dept_data in departments:
        dept = Department(**dept_data)
        db.session.add(dept)
        db.session.flush()  # Get the department ID
        
        # Add 8 semesters for each department
        for sem_num in range(1, 9):
            semester = Semester(
                number=sem_num,
                name=f'Semester {sem_num}',
                department_id=dept.id
            )
            db.session.add(semester)
    
    db.session.commit()
