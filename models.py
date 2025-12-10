from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for patients, doctors, and admins"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # patient, doctor, admin, receptionist
    phone = db.Column(db.String(15), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, lazy=True, cascade='all, delete-orphan')
    receptionist_profile = db.relationship('Receptionist', backref='user', uselist=False, lazy=True, cascade='all, delete-orphan')
    patient_appointments = db.relationship('Appointment', foreign_keys='Appointment.patient_id', backref='patient', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Doctor(db.Model):
    """Doctor-specific profile data"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    specialization = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    years_of_experience = db.Column(db.Integer, nullable=False)
    consultation_fee = db.Column(db.Float, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    photo_filename = db.Column(db.String(200), nullable=True)  # Store uploaded photo filename
    
    # Relationships
    availability_slots = db.relationship('DoctorAvailability', backref='doctor', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', foreign_keys='Appointment.doctor_id', backref='doctor', lazy=True)
    time_slots = db.relationship('TimeSlot', backref='doctor', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Doctor {self.user.name} - {self.specialization}>'


class Receptionist(db.Model):
    """Receptionist-specific profile data - similar to Doctor model"""
    __tablename__ = 'receptionists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "REC-001"
    department = db.Column(db.String(100), nullable=False)  # e.g., "Front Desk", "ER Reception", "Outpatient"
    shift = db.Column(db.String(50), nullable=False)  # e.g., "Morning", "Afternoon", "Night"
    desk_number = db.Column(db.String(20), nullable=True)  # e.g., "D-101"
    
    def __repr__(self):
        return f'<Receptionist {self.user.name} - {self.department}>'


class Appointment(db.Model):
    """Appointment booking model - supports both requests and confirmed appointments"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True, index=True)  # Nullable for pending requests
    appointment_date = db.Column(db.Date, nullable=True, index=True)  # Nullable for pending requests
    appointment_time = db.Column(db.Time, nullable=True)  # Nullable for pending requests
    preferred_date = db.Column(db.Date, nullable=True)  # Patient's preferred date
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, assigned, scheduled, completed, cancelled, no-show
    reason_for_visit = db.Column(db.Text, nullable=False)  # Required - used for triage
    notes = db.Column(db.Text, nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Receptionist who assigned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    room = db.relationship('Room', backref='appointments', lazy=True)
    time_slot = db.relationship('TimeSlot', backref='appointment', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<Appointment {self.id} - Patient: {self.patient_id} - Doctor: {self.doctor_id} - {self.appointment_date} {self.appointment_time}>'


class DoctorAvailability(db.Model):
    """Doctor's weekly recurring availability"""
    __tablename__ = 'doctor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, index=True)
    day_of_week = db.Column(db.String(10), nullable=False)  # Monday, Tuesday, etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<DoctorAvailability Doctor: {self.doctor_id} - {self.day_of_week} {self.start_time}-{self.end_time}>'


class TimeSlot(db.Model):
    """Individual time slots for appointments"""
    __tablename__ = 'time_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    
    def __repr__(self):
        return f'<TimeSlot Doctor: {self.doctor_id} - {self.date} {self.start_time}-{self.end_time} (Booked: {self.is_booked})>'


class Room(db.Model):
    """Hospital room model"""
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # consultation, operation, emergency
    floor = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    # Relationships
    equipment = db.relationship('Equipment', backref='room', lazy=True)
    
    def __repr__(self):
        return f'<Room {self.room_number} - {self.room_type} (Floor {self.floor})>'


class Equipment(db.Model):
    """Medical equipment model"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='available')  # available, in-use, maintenance
    
    def __repr__(self):
        return f'<Equipment {self.name} - {self.serial_number} ({self.status})>'


class Notification(db.Model):
    """Notification model for users"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(30), nullable=False)  # appointment, reminder, cancellation
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id} - User: {self.user_id} - Type: {self.notification_type}>'

