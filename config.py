import os
from datetime import timedelta

class Config:
    """Configuration class for the Flask application"""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration - PostgreSQL
    # Format: postgresql+psycopg://username:password@host:port/database_name
    # We use psycopg (v3) driver, so scheme is postgresql+psycopg://
    _database_url = os.environ.get('DATABASE_URL') or 'postgresql+psycopg://postgres:2005@localhost:5432/hospital_db'
    # Render uses postgres:// but we need postgresql+psycopg:// for psycopg3
    if _database_url.startswith('postgres://'):
        _database_url = _database_url.replace('postgres://', 'postgresql+psycopg://', 1)
    elif _database_url.startswith('postgresql://'):
        _database_url = _database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    SQLALCHEMY_DATABASE_URI = _database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for debugging SQL queries
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # WTF Forms configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Application specific settings
    APPOINTMENT_ADVANCE_BOOKING_DAYS = 90  # 3 months
    APPOINTMENT_CANCELLATION_HOURS = 2     # Minimum hours before appointment to cancel
    DEFAULT_APPOINTMENT_DURATION = 30      # Minutes
    BUSINESS_HOURS_START = 9               # 9 AM
    BUSINESS_HOURS_END = 17                # 5 PM
    
    # Pagination
    APPOINTMENTS_PER_PAGE = 20
    USERS_PER_PAGE = 25
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'doctors')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image formats
