# Doctor Photo Upload Feature - Implementation Guide

## ✅ Feature Overview

The doctor photo upload feature allows doctors to upload and display their profile photos throughout the hospital management system.

## 📋 What Was Implemented

### 1. **Database Changes**
- Added `photo_filename` column to the `Doctor` model in `models.py`
- Stores the filename of the uploaded photo (nullable)

### 2. **Configuration Updates** (`config.py`)
- `UPLOAD_FOLDER`: Path to store doctor photos
- `ALLOWED_EXTENSIONS`: Permitted image formats (PNG, JPG, JPEG, GIF)
- `MAX_CONTENT_LENGTH`: Maximum file size (16MB)

### 3. **New Utility File** (`file_utils.py`)
Functions for handling file uploads:
- `allowed_file()` - Validates file extension
- `save_doctor_photo()` - Saves uploaded photo with secure filename
- `delete_doctor_photo()` - Deletes old photo when updating
- `get_doctor_photo_url()` - Returns URL for displaying photo

### 4. **Form Updates** (`forms.py`)
- Added `FileField` import from `flask_wtf.file`
- Added `photo` field to `DoctorProfileForm` with validators

### 5. **Routes Added/Updated** (`app.py`)
- **Updated** `add_doctor()` - Admin can upload photo when creating doctor profile
- **New** `doctor_upload_photo()` - Doctors can upload/update their own photo
- **New** `doctor_photo` template filter - Helper for displaying photos in templates

### 6. **Templates Updated**
- `templates/admin/doctors.html` - Photo upload field in form, photos displayed in table
- `templates/doctor/profile.html` - Photo upload section for doctors
- `templates/patient/dashboard.html` - Doctor photos shown in appointment table

### 7. **Directory Structure**
```
static/
└── uploads/
    └── doctors/
        ├── doctor_1.jpg
        ├── doctor_2.png
        └── default-doctor.png
```

## 🚀 How to Use

### For Admins (Adding Doctor with Photo):

1. Go to **Admin Dashboard** → **Manage Doctors**
2. Fill out the "Add Doctor Profile" form
3. Select a photo file (PNG, JPG, JPEG, or GIF)
4. Click "Create Doctor Profile"
5. Photo will be saved with format: `doctor_{id}.{extension}`

### For Doctors (Uploading/Updating Photo):

1. Login as a doctor
2. Go to **Profile**
3. Under "Doctor Information", find the "Upload/Change Photo" section
4. Select a new photo file
5. Click "Upload Photo"
6. Old photo (if exists) will be replaced

## 📁 File Naming Convention

Photos are saved with the pattern: `doctor_{doctor_id}.{extension}`

Examples:
- `doctor_1.jpg`
- `doctor_2.png`
- `doctor_5.gif`

This ensures:
- Unique filenames per doctor
- Easy identification
- Automatic replacement when updating

## 🔒 Security Features

1. **File Type Validation**
   - Only allows PNG, JPG, JPEG, GIF
   - Validates on both client and server side

2. **Secure Filenames**
   - Uses `secure_filename()` from Werkzeug
   - Prevents directory traversal attacks

3. **File Size Limit**
   - Maximum 16MB per file
   - Configured in Flask app settings

4. **Permission Checks**
   - Doctors can only update their own photos
   - Admins can upload photos for any doctor

## 🎨 Display Locations

Doctor photos are now displayed in:

1. **Admin - Doctors Management Page**
   - 50x50 pixels in table
   - Shows all doctor photos

2. **Doctor - Profile Page**
   - 150x150 pixels
   - Shows current photo or "[No Photo Uploaded]"

3. **Patient - Dashboard**
   - 50x50 pixels
   - Shows in appointment list

4. **Patient - All Appointments Page**
   - Can be added similarly

## 🔧 Database Migration

If you already have an existing database:

### Option 1: Reset Database (Development)
```bash
# Delete existing database
del hospital.db  # Windows
rm hospital.db   # macOS/Linux

# Run seed data script (will create new DB with photo field)
python seed_data.py
```

### Option 2: Manual Migration (Production)
```python
# Run this in Python shell
from app import app
from models import db

with app.app_context():
    # Add column to existing database
    db.engine.execute('ALTER TABLE doctors ADD COLUMN photo_filename VARCHAR(200)')
    print("Photo column added successfully!")
```

## 📝 Code Examples

### Uploading Photo (Backend)
```python
# In app.py - add_doctor route
if 'photo' in request.files:
    photo = request.files['photo']
    if photo and photo.filename != '':
        filename = save_doctor_photo(photo, doctor.id)
        if filename:
            doctor.photo_filename = filename
```

### Displaying Photo (Template)
```html
{% if doctor.photo_filename %}
    <img src="{{ doctor.photo_filename|doctor_photo }}" alt="{{ doctor.user.name }}" width="150">
{% else %}
    <span>[No Photo]</span>
{% endif %}
```

### Template Filter Usage
```python
# In app.py
@app.template_filter('doctor_photo')
def doctor_photo(filename):
    """Get doctor photo URL"""
    return get_doctor_photo_url(filename)
```

## ⚠️ Troubleshooting

### Issue: "No such file or directory" error
**Solution**: Ensure the uploads directory exists
```bash
mkdir -p static/uploads/doctors  # macOS/Linux
New-Item -ItemType Directory -Force -Path "static\uploads\doctors"  # Windows
```

### Issue: Photo not displaying
**Solutions**:
1. Check that `photo_filename` is saved in database
2. Verify file exists in `static/uploads/doctors/`
3. Check file permissions
4. Clear browser cache

### Issue: "File too large" error
**Solution**: Adjust `MAX_CONTENT_LENGTH` in `config.py`:
```python
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB instead of 16MB
```

### Issue: Photo uploads but doesn't save to DB
**Solution**: Ensure you're calling `db.session.flush()` before saving photo:
```python
db.session.add(doctor)
db.session.flush()  # Get doctor ID
filename = save_doctor_photo(photo, doctor.id)
doctor.photo_filename = filename
db.session.commit()
```

## 🎯 Testing Checklist

- [ ] Admin can upload photo when creating doctor profile
- [ ] Doctor can upload their own photo
- [ ] Doctor can update existing photo (old one is deleted)
- [ ] Photos display correctly in admin doctors table
- [ ] Photos display correctly in doctor profile page
- [ ] Photos display correctly in patient dashboard
- [ ] Invalid file types are rejected
- [ ] Files larger than 16MB are rejected
- [ ] Photos persist after server restart

## 📊 Accepted File Formats

| Format | Extension | Recommended |
|--------|-----------|-------------|
| PNG | `.png` | ✅ Yes (best quality) |
| JPEG | `.jpg`, `.jpeg` | ✅ Yes (smaller file size) |
| GIF | `.gif` | ⚠️ Use for animations only |

**Recommended**: Use JPEG for photographs, PNG for graphics

## 🔮 Future Enhancements

Potential improvements (not yet implemented):
- [ ] Image resizing/cropping on upload
- [ ] Thumbnail generation
- [ ] Default placeholder image
- [ ] Photo gallery for multiple images
- [ ] Face detection/validation
- [ ] Cloud storage integration (AWS S3, Azure Blob)

## 📚 Related Files

**Backend:**
- `models.py` - Database model changes
- `config.py` - Upload configuration
- `file_utils.py` - File handling utilities
- `app.py` - Routes and logic
- `forms.py` - Form with file upload

**Frontend:**
- `templates/admin/doctors.html`
- `templates/doctor/profile.html`
- `templates/patient/dashboard.html`

**Storage:**
- `static/uploads/doctors/` - Photo storage directory

## ✨ Summary

The doctor photo upload feature is now **fully functional** and integrated into:
- ✅ Admin management interface
- ✅ Doctor profile management
- ✅ Patient appointment views
- ✅ All relevant templates

Doctors and admins can now upload, update, and display professional profile photos throughout the system!

