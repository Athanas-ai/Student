"""
REST API routes for the Student Notes Platform.
Handles all CRUD operations for notes, departments, semesters, subjects, and units.
"""

import os
import uuid
from functools import wraps
from flask import Blueprint, request, jsonify, current_app, send_from_directory, session
from werkzeug.utils import secure_filename
from models import db, Admin, Department, Semester, Subject, Unit, Note, LiveNote
from utils import allowed_file, generate_slug, generate_unique_filename, create_thumbnail

api = Blueprint('api', __name__, url_prefix='/api')


# ============== Admin Authentication ==============


# ============== Department Routes ==============

@api.route('/departments', methods=['GET'])
def get_departments():
    """Get all departments."""
    departments = Department.query.order_by(Department.name).all()
    return jsonify([d.to_dict() for d in departments])


@api.route('/departments/<slug>', methods=['GET'])
def get_department(slug):
    """Get a single department by slug."""
    dept = Department.query.filter_by(slug=slug).first_or_404()
    return jsonify(dept.to_dict())


@api.route('/departments', methods=['POST'])
@admin_required
def create_department():
    """Create a new department."""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    slug = generate_slug(data['name'])
    
    if Department.query.filter_by(slug=slug).first():
        return jsonify({'error': 'Department already exists'}), 400
    
    dept = Department(
        name=data['name'],
        slug=slug,
        description=data.get('description', ''),
        icon=data.get('icon', '📚')
    )
    
    db.session.add(dept)
    db.session.flush()
    
    # Auto-create 8 semesters for the department
    for sem_num in range(1, 9):
        semester = Semester(
            number=sem_num,
            name=f'Semester {sem_num}',
            department_id=dept.id
        )
        db.session.add(semester)
    
    db.session.commit()
    
    return jsonify(dept.to_dict()), 201


@api.route('/departments/<slug>', methods=['DELETE'])
@admin_required
def delete_department(slug):
    """Delete a department and all its contents."""
    dept = Department.query.filter_by(slug=slug).first_or_404()
    
    # Delete all associated files
    for semester in dept.semesters:
        for subject in semester.subjects:
            for unit in subject.units:
                for note in unit.notes:
                    try:
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], note.stored_filename)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        if note.thumbnail:
                            thumb_path = os.path.join(current_app.config['THUMBNAIL_FOLDER'], note.thumbnail)
                            if os.path.exists(thumb_path):
                                os.remove(thumb_path)
                    except Exception as e:
                        print(f"Error deleting file: {e}")
    
    db.session.delete(dept)
    db.session.commit()
    
    return jsonify({'message': 'Department deleted successfully'})


# ============== Semester Routes ==============

@api.route('/departments/<dept_slug>/semesters', methods=['GET'])
def get_semesters(dept_slug):
    """Get all semesters for a department."""
    dept = Department.query.filter_by(slug=dept_slug).first_or_404()
    semesters = Semester.query.filter_by(department_id=dept.id).order_by(Semester.number).all()
    return jsonify([s.to_dict() for s in semesters])


@api.route('/semesters/<int:semester_id>', methods=['GET'])
def get_semester(semester_id):
    """Get a single semester by ID."""
    semester = Semester.query.get_or_404(semester_id)
    return jsonify(semester.to_dict())


# ============== Subject Routes ==============

@api.route('/semesters/<int:semester_id>/subjects', methods=['GET'])
def get_subjects(semester_id):
    """Get all subjects for a semester."""
    semester = Semester.query.get_or_404(semester_id)
    subjects = Subject.query.filter_by(semester_id=semester.id).order_by(Subject.name).all()
    return jsonify([s.to_dict() for s in subjects])


@api.route('/subjects/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    """Get a single subject by ID."""
    subject = Subject.query.get_or_404(subject_id)
    return jsonify(subject.to_dict())


@api.route('/semesters/<int:semester_id>/subjects', methods=['POST'])
@admin_required
def create_subject(semester_id):
    """Create a new subject in a semester."""
    semester = Semester.query.get_or_404(semester_id)
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    slug = generate_slug(data['name'])
    
    # Check if subject already exists in this semester
    existing = Subject.query.filter_by(slug=slug, semester_id=semester.id).first()
    if existing:
        return jsonify({'error': 'Subject already exists in this semester'}), 400
    
    subject = Subject(
        name=data['name'],
        slug=slug,
        code=data.get('code', ''),
        description=data.get('description', ''),
        semester_id=semester.id
    )
    
    db.session.add(subject)
    db.session.commit()
    
    return jsonify(subject.to_dict()), 201


@api.route('/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    """Delete a subject and all its contents."""
    subject = Subject.query.get_or_404(subject_id)
    
    # Delete all associated files
    for unit in subject.units:
        for note in unit.notes:
            try:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], note.stored_filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                if note.thumbnail:
                    thumb_path = os.path.join(current_app.config['THUMBNAIL_FOLDER'], note.thumbnail)
                    if os.path.exists(thumb_path):
                        os.remove(thumb_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
    
    db.session.delete(subject)
    db.session.commit()
    
    return jsonify({'message': 'Subject deleted successfully'})


# ============== Unit Routes ==============

@api.route('/subjects/<int:subject_id>/units', methods=['GET'])
def get_units(subject_id):
    """Get all units for a subject."""
    subject = Subject.query.get_or_404(subject_id)
    units = Unit.query.filter_by(subject_id=subject.id).order_by(Unit.number).all()
    return jsonify([u.to_dict() for u in units])


@api.route('/units/<int:unit_id>', methods=['GET'])
def get_unit(unit_id):
    """Get a single unit by ID."""
    unit = Unit.query.get_or_404(unit_id)
    return jsonify(unit.to_dict())


@api.route('/subjects/<int:subject_id>/units', methods=['POST'])
@admin_required
def create_unit(subject_id):
    """Create a new unit in a subject."""
    subject = Subject.query.get_or_404(subject_id)
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    # Get the next unit number
    last_unit = Unit.query.filter_by(subject_id=subject.id).order_by(Unit.number.desc()).first()
    next_number = (last_unit.number + 1) if last_unit else 1
    
    slug = generate_slug(data['name'])
    
    unit = Unit(
        name=data['name'],
        slug=slug,
        number=data.get('number', next_number),
        description=data.get('description', ''),
        subject_id=subject.id
    )
    
    db.session.add(unit)
    db.session.commit()
    
    return jsonify(unit.to_dict()), 201


@api.route('/units/<int:unit_id>', methods=['DELETE'])
@admin_required
def delete_unit(unit_id):
    """Delete a unit and all its notes."""
    unit = Unit.query.get_or_404(unit_id)
    
    # Delete all associated files
    for note in unit.notes:
        try:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], note.stored_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            if note.thumbnail:
                thumb_path = os.path.join(current_app.config['THUMBNAIL_FOLDER'], note.thumbnail)
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    db.session.delete(unit)
    db.session.commit()
    
    return jsonify({'message': 'Unit deleted successfully'})


# ============== Note Routes ==============

@api.route('/units/<int:unit_id>/notes', methods=['GET'])
def get_notes(unit_id):
    """Get all notes for a unit."""
    unit = Unit.query.get_or_404(unit_id)
    notes = Note.query.filter_by(unit_id=unit.id).order_by(Note.uploaded_at.desc()).all()
    return jsonify([n.to_dict() for n in notes])


@api.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a single note and increment view count."""
    note = Note.query.get_or_404(note_id)
    note.view_count += 1
    db.session.commit()
    return jsonify(note.to_dict())


@api.route('/notes/recent', methods=['GET'])
def get_recent_notes():
    """Get recently uploaded notes."""
    limit = request.args.get('limit', 8, type=int)
    notes = Note.query.order_by(Note.uploaded_at.desc()).limit(limit).all()
    
    result = []
    for note in notes:
        note_data = note.to_dict()
        # Add breadcrumb info
        unit = Unit.query.get(note.unit_id)
        subject = Subject.query.get(unit.subject_id)
        semester = Semester.query.get(subject.semester_id)
        dept = Department.query.get(semester.department_id)
        note_data['unit_name'] = unit.name
        note_data['subject_name'] = subject.name
        note_data['semester_number'] = semester.number
        note_data['department_name'] = dept.name
        note_data['department_slug'] = dept.slug
        note_data['subject_slug'] = subject.slug
        result.append(note_data)
    
    return jsonify(result)


@api.route('/notes/popular', methods=['GET'])
def get_popular_notes():
    """Get most viewed notes."""
    limit = request.args.get('limit', 8, type=int)
    notes = Note.query.order_by(Note.view_count.desc()).limit(limit).all()
    
    result = []
    for note in notes:
        note_data = note.to_dict()
        # Add breadcrumb info
        unit = Unit.query.get(note.unit_id)
        subject = Subject.query.get(unit.subject_id)
        semester = Semester.query.get(subject.semester_id)
        dept = Department.query.get(semester.department_id)
        note_data['unit_name'] = unit.name
        note_data['subject_name'] = subject.name
        note_data['semester_number'] = semester.number
        note_data['department_name'] = dept.name
        note_data['department_slug'] = dept.slug
        note_data['subject_slug'] = subject.slug
        result.append(note_data)
    
    return jsonify(result)


@api.route('/units/<int:unit_id>/notes', methods=['POST'])
def upload_note(unit_id):
    """Upload a new note (PDF or image)."""
    unit = Unit.query.get_or_404(unit_id)
    
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return jsonify({'error': 'Invalid file type. Only PDF, PNG, JPG, JPEG allowed'}), 400
    
    # Get form data
    title = request.form.get('title', '')
    if not title:
        title = os.path.splitext(secure_filename(file.filename))[0]
    
    description = request.form.get('description', '')
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    stored_filename = generate_unique_filename(original_filename)
    file_type = original_filename.rsplit('.', 1)[1].lower()
    
    # Ensure upload folder exists
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(current_app.config['THUMBNAIL_FOLDER'], exist_ok=True)
    
    # Save file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_filename)
    file.save(file_path)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create thumbnail
    thumbnail_filename = f"thumb_{stored_filename.rsplit('.', 1)[0]}.jpg"
    thumbnail_path = os.path.join(current_app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
    
    if create_thumbnail(file_path, thumbnail_path, file_type):
        thumbnail = thumbnail_filename
    else:
        thumbnail = None
    
    # Create note record
    note = Note(
        title=title,
        slug=generate_slug(title),
        description=description,
        filename=original_filename,
        stored_filename=stored_filename,
        file_type=file_type,
        file_size=file_size,
        thumbnail=thumbnail,
        unit_id=unit.id
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify(note.to_dict()), 201


@api.route('/notes/<int:note_id>/download', methods=['GET'])
def download_note(note_id):
    """Download a note file and increment download count."""
    note = Note.query.get_or_404(note_id)
    note.download_count += 1
    db.session.commit()
    
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        note.stored_filename,
        as_attachment=True,
        download_name=note.filename
    )


@api.route('/notes/<int:note_id>', methods=['DELETE'])
@admin_required
def delete_note(note_id):
    """Delete a note."""
    note = Note.query.get_or_404(note_id)
    
    # Delete files
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], note.stored_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if note.thumbnail:
            thumb_path = os.path.join(current_app.config['THUMBNAIL_FOLDER'], note.thumbnail)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
    except Exception as e:
        print(f"Error deleting files: {e}")
    
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({'message': 'Note deleted successfully'})


# ============== Live Note Routes ==============

@api.route('/live-notes', methods=['GET'])
def get_live_notes():
    """Get all live notes."""
    notes = LiveNote.query.order_by(LiveNote.updated_at.desc()).all()
    return jsonify([n.to_dict() for n in notes])


@api.route('/live-notes/<slug>', methods=['GET'])
def get_live_note(slug):
    """Get a live note by slug."""
    note = LiveNote.query.filter_by(slug=slug).first_or_404()
    note.view_count += 1
    db.session.commit()
    return jsonify(note.to_dict())


@api.route('/live-notes', methods=['POST'])
def create_live_note():
    """Create a new live note."""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    # Generate unique slug
    base_slug = generate_slug(data['title'])
    slug = base_slug
    counter = 1
    
    while LiveNote.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    note = LiveNote(
        title=data['title'],
        slug=slug,
        content=data.get('content', ''),
        unit_id=data.get('unit_id')
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify(note.to_dict()), 201


@api.route('/live-notes/<slug>', methods=['PUT'])
def update_live_note(slug):
    """Update a live note content."""
    note = LiveNote.query.filter_by(slug=slug).first_or_404()
    data = request.get_json()
    
    if 'content' in data:
        note.content = data['content']
    if 'title' in data:
        note.title = data['title']
    
    db.session.commit()
    
    return jsonify(note.to_dict())


# ============== Search Route ==============

@api.route('/search', methods=['GET'])
def search():
    """Search notes, subjects, and departments."""
    query = request.args.get('q', '').strip()
    filter_dept = request.args.get('department', '')
    filter_semester = request.args.get('semester', '')
    filter_subject = request.args.get('subject', '')
    
    if not query and not filter_dept and not filter_subject:
        return jsonify({'notes': [], 'subjects': [], 'departments': []})
    
    results = {'notes': [], 'subjects': [], 'departments': []}
    
    # Search departments
    if query:
        depts = Department.query.filter(
            Department.name.ilike(f'%{query}%')
        ).all()
        results['departments'] = [d.to_dict() for d in depts]
    
    # Search subjects
    subject_query = Subject.query
    if query:
        subject_query = subject_query.filter(
            (Subject.name.ilike(f'%{query}%')) |
            (Subject.code.ilike(f'%{query}%'))
        )
    
    subjects = subject_query.all()
    results['subjects'] = [s.to_dict() for s in subjects]
    
    # Search notes
    note_query = Note.query
    if query:
        note_query = note_query.filter(
            (Note.title.ilike(f'%{query}%')) |
            (Note.description.ilike(f'%{query}%'))
        )
    
    notes = note_query.order_by(Note.view_count.desc()).limit(20).all()
    
    for note in notes:
        note_data = note.to_dict()
        unit = Unit.query.get(note.unit_id)
        subject = Subject.query.get(unit.subject_id)
        semester = Semester.query.get(subject.semester_id)
        dept = Department.query.get(semester.department_id)
        note_data['unit_name'] = unit.name
        note_data['subject_name'] = subject.name
        note_data['semester_number'] = semester.number
        note_data['department_name'] = dept.name
        results['notes'].append(note_data)
    
    return jsonify(results)


# ============== Stats Route ==============

@api.route('/stats', methods=['GET'])
def get_stats():
    """Get platform statistics."""
    return jsonify({
        'total_departments': Department.query.count(),
        'total_subjects': Subject.query.count(),
        'total_units': Unit.query.count(),
        'total_notes': Note.query.count(),
        'total_live_notes': LiveNote.query.count(),
        'total_views': db.session.query(db.func.sum(Note.view_count)).scalar() or 0,
        'total_downloads': db.session.query(db.func.sum(Note.download_count)).scalar() or 0
    })

