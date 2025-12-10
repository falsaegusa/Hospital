"""
File Upload Utilities for Hospital Management System
"""

import os
from werkzeug.utils import secure_filename
from config import Config


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_doctor_photo(photo, doctor_id):
    """
    Save uploaded doctor photo
    Returns filename if successful, None otherwise
    """
    if not photo or photo.filename == '':
        return None
    
    if not allowed_file(photo.filename):
        return None
    
    # Create upload directory if it doesn't exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Generate secure filename with doctor ID prefix
    file_extension = photo.filename.rsplit('.', 1)[1].lower()
    filename = f"doctor_{doctor_id}.{file_extension}"
    
    # Save the file
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    photo.save(filepath)
    
    return filename


def delete_doctor_photo(filename):
    """
    Delete doctor photo from filesystem
    Returns True if successful, False otherwise
    """
    if not filename:
        return False
    
    try:
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        print(f"Error deleting photo: {e}")
        return False


def get_doctor_photo_url(filename):
    """
    Get URL for doctor photo
    Returns URL string or default placeholder
    """
    if filename:
        return f'/static/uploads/doctors/{filename}'
    else:
        return '/static/uploads/doctors/default-doctor.png'

