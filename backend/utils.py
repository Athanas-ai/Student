"""
Utility functions for the Student Notes Platform.
Includes file handling, slug generation, and thumbnail creation.
"""

import os
import re
import uuid
from datetime import datetime
from PIL import Image
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF for PDF handling


def allowed_file(filename, allowed_extensions):
    """Check if file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_slug(text):
    """Generate URL-friendly slug from text."""
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug


def generate_unique_filename(filename):
    """Generate a unique filename using UUID."""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return unique_name


def get_file_size_display(size_bytes):
    """Convert bytes to human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def create_thumbnail(file_path, thumbnail_path, file_type, size=(300, 400)):
    """
    Create a thumbnail for the uploaded file.
    Supports PDF and image files.
    """
    try:
        if file_type == 'pdf':
            # Create thumbnail from first page of PDF
            doc = fitz.open(file_path)
            page = doc[0]
            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            doc.close()
        else:
            # Open image file
            img = Image.open(file_path)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
        
        # Resize maintaining aspect ratio
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save thumbnail
        img.save(thumbnail_path, 'JPEG', quality=85)
        return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False


def format_datetime(dt):
    """Format datetime for display."""
    if not dt:
        return ''
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days == 0:
        if diff.seconds < 60:
            return 'Just now'
        elif diff.seconds < 3600:
            mins = diff.seconds // 60
            return f'{mins} min{"s" if mins > 1 else ""} ago'
        else:
            hours = diff.seconds // 3600
            return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif diff.days == 1:
        return 'Yesterday'
    elif diff.days < 7:
        return f'{diff.days} days ago'
    else:
        return dt.strftime('%b %d, %Y')


from datetime import datetime
