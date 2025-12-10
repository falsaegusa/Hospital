from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, TimeField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional
from models import User
import re


class RegistrationForm(FlaskForm):
    """User registration form"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Register As', choices=[('patient', 'Patient'), ('doctor', 'Doctor')], validators=[Optional()])
    phone = StringField('Phone Number', validators=[Optional(), Length(min=10, max=15)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_phone(self, phone):
        """Validate phone number format"""
        if phone.data:
            cleaned = re.sub(r'[\s\-\(\)]', '', phone.data)
            if not re.match(r'^\d{10}$', cleaned):
                raise ValidationError('Phone number must be 10 digits.')


class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class AppointmentRequestForm(FlaskForm):
    """Patient appointment request form - no doctor selection, receptionist will assign"""
    reason_for_visit = TextAreaField('Describe Your Symptoms or Reason for Visit', 
                                      validators=[DataRequired(), Length(min=10, max=1000,
                                      message="Please provide at least 10 characters describing your symptoms")])
    preferred_date = DateField('Preferred Date (Optional)', validators=[Optional()])


class AppointmentBookingForm(FlaskForm):
    """Legacy appointment booking form - kept for compatibility"""
    doctor_id = SelectField('Select Doctor', coerce=int, validators=[DataRequired()])
    appointment_date = DateField('Appointment Date', validators=[DataRequired()])
    appointment_time = TimeField('Appointment Time', validators=[DataRequired()])
    reason_for_visit = TextAreaField('Reason for Visit', validators=[Optional()])


class AssignAppointmentForm(FlaskForm):
    """Receptionist form for assigning doctor and time to pending requests"""
    doctor_id = SelectField('Assign Doctor', coerce=int, validators=[DataRequired()])
    appointment_date = DateField('Appointment Date', validators=[DataRequired()])
    appointment_time = TimeField('Appointment Time', validators=[DataRequired()])


class DoctorProfileForm(FlaskForm):
    """Doctor profile creation/update form"""
    specialization = StringField('Specialization', validators=[DataRequired(), Length(max=100)])
    license_number = StringField('License Number', validators=[DataRequired(), Length(max=50)])
    years_of_experience = IntegerField('Years of Experience', validators=[DataRequired()])
    consultation_fee = FloatField('Consultation Fee', validators=[DataRequired()])
    department = StringField('Department', validators=[DataRequired(), Length(max=100)])
    photo = FileField('Doctor Photo', validators=[Optional(), FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Images only!')])


class DoctorAvailabilityForm(FlaskForm):
    """Form for setting doctor's weekly availability"""
    day_of_week = SelectField('Day of Week', 
                               choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), 
                                       ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'),
                                       ('Friday', 'Friday'), ('Saturday', 'Saturday'),
                                       ('Sunday', 'Sunday')],
                               validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])


class RoomForm(FlaskForm):
    """Form for adding/updating rooms"""
    room_number = StringField('Room Number', validators=[DataRequired(), Length(max=20)])
    room_type = SelectField('Room Type', 
                           choices=[('consultation', 'Consultation'), 
                                   ('operation', 'Operation'),
                                   ('emergency', 'Emergency')],
                           validators=[DataRequired()])
    floor = IntegerField('Floor', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired()])


class EquipmentForm(FlaskForm):
    """Form for adding/updating equipment"""
    name = StringField('Equipment Name', validators=[DataRequired(), Length(max=100)])
    equipment_type = StringField('Equipment Type', validators=[DataRequired(), Length(max=50)])
    serial_number = StringField('Serial Number', validators=[DataRequired(), Length(max=100)])
    room_id = SelectField('Assigned Room', coerce=int, validators=[Optional()])
    status = SelectField('Status',
                        choices=[('available', 'Available'),
                                ('in-use', 'In Use'),
                                ('maintenance', 'Maintenance')],
                        validators=[DataRequired()])


class ProfileUpdateForm(FlaskForm):
    """Form for updating user profile"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(min=10, max=15)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])

