from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Doctor, Receptionist, Appointment, DoctorAvailability, TimeSlot, Room, Equipment, Notification
from forms import (RegistrationForm, LoginForm, AppointmentBookingForm, AppointmentRequestForm,
                   AssignAppointmentForm, DoctorProfileForm, DoctorAvailabilityForm, RoomForm, 
                   EquipmentForm, ProfileUpdateForm)
from decorators import role_required
from utils import (generate_time_slots, check_slot_available, check_patient_availability,
                   assign_available_room, send_notification, can_cancel_appointment,
                   create_time_slot, free_time_slot, get_unread_notifications,
                   calculate_age, format_time_12hr)
from file_utils import save_doctor_photo, delete_doctor_photo, get_doctor_photo_url
from triage import suggest_doctors, get_specialization_summary, analyze_symptoms
from datetime import datetime, date, time, timedelta
from sqlalchemy import func, and_, or_

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Home page - redirect based on role"""
    if current_user.is_authenticated:
        if current_user.role == 'patient':
            return redirect(url_for('patient_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Patient registration only - doctors/admins are created by admin"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new patient user - role is always 'patient' for public registration
            user = User(
                name=form.name.data,
                email=form.email.data,
                role='patient',  # Force patient role - doctors/admins created by admin
                phone=form.phone.data,
                date_of_birth=form.date_of_birth.data,
                gender=form.gender.data,
                address=form.address.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Patient login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            # Only allow patients through patient login
            if user.role != 'patient':
                flash('Staff members please use the Staff Portal.', 'warning')
                return redirect(url_for('staff_login'))
            
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)


@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    """Staff login page (doctors and admins)"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            # Only allow staff through staff login
            if user.role == 'patient':
                flash('Patients please use the Patient Portal.', 'warning')
                return redirect(url_for('login'))
            
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            
            if user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'receptionist':
                return redirect(url_for('receptionist_dashboard'))
            
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/staff_login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ==================== PATIENT ROUTES ====================

@app.route('/patient/dashboard')
@login_required
@role_required('patient')
def patient_dashboard():
    """Patient dashboard - show upcoming appointments"""
    today = date.today()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == current_user.id,
        Appointment.appointment_date >= today,
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(5).all()
    
    # Get unread notifications
    unread_count = get_unread_notifications(current_user.id)
    
    return render_template('patient/dashboard.html', 
                          appointments=upcoming_appointments,
                          unread_count=unread_count)


@app.route('/patient/request-appointment', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def request_appointment():
    """Submit an appointment request - receptionist will assign doctor"""
    form = AppointmentRequestForm()
    
    if form.validate_on_submit():
        try:
            # Create pending appointment request
            appointment = Appointment(
                patient_id=current_user.id,
                reason_for_visit=form.reason_for_visit.data,
                preferred_date=form.preferred_date.data,
                status='pending'
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            # Send notification to patient
            send_notification(
                current_user.id,
                "Your appointment request has been submitted. A receptionist will assign a doctor shortly.",
                'appointment'
            )
            
            flash('Appointment request submitted successfully! A staff member will assign a doctor and confirm your appointment.', 'success')
            return redirect(url_for('patient_appointments'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Request error: {e}")
            flash('An error occurred while submitting your request. Please try again.', 'error')
    
    return render_template('patient/request_appointment.html', form=form)


@app.route('/patient/book-appointment', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def book_appointment():
    """Legacy booking - redirects to new request flow"""
    return redirect(url_for('request_appointment'))


@app.route('/patient/appointments')
@login_required
@role_required('patient')
def patient_appointments():
    """View all patient appointments"""
    appointments = Appointment.query.filter_by(patient_id=current_user.id)\
        .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    
    return render_template('patient/appointments.html', appointments=appointments)


@app.route('/patient/cancel-appointment/<int:appointment_id>', methods=['POST'])
@login_required
@role_required('patient')
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Verify ownership
        if appointment.patient_id != current_user.id:
            flash('You do not have permission to cancel this appointment.', 'error')
            return redirect(url_for('patient_appointments'))
        
        # Check if cancellation is allowed
        can_cancel, message = can_cancel_appointment(appointment)
        if not can_cancel:
            flash(message, 'error')
            return redirect(url_for('patient_appointments'))
        
        # Update appointment status
        appointment.status = 'cancelled'
        
        # Free up time slot
        free_time_slot(appointment)
        
        # Free up room if assigned
        if appointment.room:
            appointment.room.is_available = True
        
        db.session.commit()
        
        # Send notifications
        send_notification(
            current_user.id,
            f"Your appointment on {appointment.appointment_date} at {appointment.appointment_time} has been cancelled",
            'cancellation'
        )
        send_notification(
            appointment.doctor.user_id,
            f"Appointment with {current_user.name} on {appointment.appointment_date} at {appointment.appointment_time} has been cancelled",
            'cancellation'
        )
        
        flash('Appointment cancelled successfully.', 'success')
    
    except Exception as e:
        db.session.rollback()
        print(f"Cancellation error: {e}")
        flash('An error occurred while cancelling the appointment.', 'error')
    
    return redirect(url_for('patient_appointments'))


@app.route('/patient/reschedule/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def reschedule_appointment(appointment_id):
    """Reschedule an appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify ownership
    if appointment.patient_id != current_user.id:
        flash('You do not have permission to reschedule this appointment.', 'error')
        return redirect(url_for('patient_appointments'))
    
    # Check if rescheduling is allowed
    can_cancel, message = can_cancel_appointment(appointment)
    if not can_cancel:
        flash(f"Cannot reschedule: {message}", 'error')
        return redirect(url_for('patient_appointments'))
    
    form = AppointmentBookingForm()
    doctors = Doctor.query.join(User).filter(User.role == 'doctor').all()
    form.doctor_id.choices = [(d.id, f"{d.user.name} - {d.specialization}") for d in doctors]
    
    if request.method == 'GET':
        form.doctor_id.data = appointment.doctor_id
        form.appointment_date.data = appointment.appointment_date
        form.appointment_time.data = appointment.appointment_time
        form.reason_for_visit.data = appointment.reason_for_visit
    
    if form.validate_on_submit():
        try:
            # Start transaction for atomic rescheduling
            new_doctor_id = form.doctor_id.data
            new_date = form.appointment_date.data
            new_time = form.appointment_time.data
            
            # Validate new slot
            available, avail_message = check_slot_available(new_doctor_id, new_date, new_time)
            if not available:
                flash(avail_message, 'error')
                return render_template('patient/reschedule.html', form=form, appointment=appointment)
            
            # Free old slot
            free_time_slot(appointment)
            
            # Update appointment
            appointment.doctor_id = new_doctor_id
            appointment.appointment_date = new_date
            appointment.appointment_time = new_time
            appointment.reason_for_visit = form.reason_for_visit.data
            
            # Create new time slot
            time_slot = create_time_slot(new_doctor_id, new_date, new_time, appointment.id)
            if not time_slot:
                raise Exception("Failed to create new time slot")
            
            db.session.commit()
            
            # Send notifications
            send_notification(
                current_user.id,
                f"Your appointment has been rescheduled to {new_date} at {new_time}",
                'appointment'
            )
            
            flash('Appointment rescheduled successfully!', 'success')
            return redirect(url_for('patient_appointments'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Reschedule error: {e}")
            flash('An error occurred while rescheduling the appointment.', 'error')
    
    return render_template('patient/reschedule.html', form=form, appointment=appointment)


@app.route('/patient/profile', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def patient_profile():
    """View and update patient profile"""
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        try:
            current_user.name = form.name.data
            current_user.phone = form.phone.data
            current_user.date_of_birth = form.date_of_birth.data
            current_user.gender = form.gender.data
            current_user.address = form.address.data
            current_user.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('patient_profile'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Profile update error: {e}")
            flash('An error occurred while updating profile.', 'error')
    
    if request.method == 'GET':
        form.name.data = current_user.name
        form.phone.data = current_user.phone
        form.date_of_birth.data = current_user.date_of_birth
        form.gender.data = current_user.gender
        form.address.data = current_user.address
    
    return render_template('patient/profile.html', form=form)


# ==================== DOCTOR ROUTES ====================

@app.route('/doctor/dashboard')
@login_required
@role_required('doctor')
def doctor_dashboard():
    """Doctor dashboard - show today's appointments"""
    today = date.today()
    
    # Get doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        flash('Please contact admin to complete your doctor profile.', 'warning')
        return render_template('doctor/dashboard.html', appointments=[], doctor=None)
    
    # Get today's appointments
    today_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date == today,
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_time).all()
    
    return render_template('doctor/dashboard.html', 
                          appointments=today_appointments,
                          doctor=doctor)


@app.route('/doctor/appointments')
@login_required
@role_required('doctor')
def doctor_appointments():
    """View all doctor appointments"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        flash('Please contact admin to complete your doctor profile.', 'warning')
        return render_template('doctor/appointments.html', appointments=[])
    
    appointments = Appointment.query.filter_by(doctor_id=doctor.id)\
        .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    
    return render_template('doctor/appointments.html', appointments=appointments)


@app.route('/doctor/complete-appointment/<int:appointment_id>', methods=['POST'])
@login_required
@role_required('doctor')
def complete_appointment(appointment_id):
    """Mark appointment as completed"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        
        # Verify ownership
        if appointment.doctor_id != doctor.id:
            flash('You do not have permission to modify this appointment.', 'error')
            return redirect(url_for('doctor_appointments'))
        
        appointment.status = 'completed'
        appointment.updated_at = datetime.utcnow()
        
        # Add notes if provided
        notes = request.form.get('notes')
        if notes:
            appointment.notes = notes
        
        db.session.commit()
        
        flash('Appointment marked as completed.', 'success')
    
    except Exception as e:
        db.session.rollback()
        print(f"Complete appointment error: {e}")
        flash('An error occurred while updating the appointment.', 'error')
    
    return redirect(url_for('doctor_appointments'))


@app.route('/doctor/availability', methods=['GET', 'POST'])
@login_required
@role_required('doctor')
def doctor_availability():
    """View and set doctor availability"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        flash('Please contact admin to complete your doctor profile.', 'warning')
        return redirect(url_for('doctor_dashboard'))
    
    form = DoctorAvailabilityForm()
    
    if form.validate_on_submit():
        try:
            # Check if availability already exists for this day
            existing = DoctorAvailability.query.filter_by(
                doctor_id=doctor.id,
                day_of_week=form.day_of_week.data
            ).first()
            
            if existing:
                # Update existing
                existing.start_time = form.start_time.data
                existing.end_time = form.end_time.data
                existing.is_available = True
            else:
                # Create new
                availability = DoctorAvailability(
                    doctor_id=doctor.id,
                    day_of_week=form.day_of_week.data,
                    start_time=form.start_time.data,
                    end_time=form.end_time.data,
                    is_available=True
                )
                db.session.add(availability)
            
            db.session.commit()
            flash('Availability updated successfully!', 'success')
            return redirect(url_for('doctor_availability'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Availability update error: {e}")
            flash('An error occurred while updating availability.', 'error')
    
    # Get current availability
    availability = DoctorAvailability.query.filter_by(doctor_id=doctor.id)\
        .order_by(
            db.case(
                {
                    'Monday': 1,
                    'Tuesday': 2,
                    'Wednesday': 3,
                    'Thursday': 4,
                    'Friday': 5,
                    'Saturday': 6,
                    'Sunday': 7
                },
                value=DoctorAvailability.day_of_week
            )
        ).all()
    
    return render_template('doctor/availability.html', form=form, availability=availability)


@app.route('/doctor/profile', methods=['GET', 'POST'])
@login_required
@role_required('doctor')
def doctor_profile():
    """View and update doctor profile"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    profile_form = ProfileUpdateForm()
    
    if profile_form.validate_on_submit():
        try:
            current_user.name = profile_form.name.data
            current_user.phone = profile_form.phone.data
            current_user.date_of_birth = profile_form.date_of_birth.data
            current_user.gender = profile_form.gender.data
            current_user.address = profile_form.address.data
            current_user.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('doctor_profile'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Profile update error: {e}")
            flash('An error occurred while updating profile.', 'error')
    
    if request.method == 'GET':
        profile_form.name.data = current_user.name
        profile_form.phone.data = current_user.phone
        profile_form.date_of_birth.data = current_user.date_of_birth
        profile_form.gender.data = current_user.gender
        profile_form.address.data = current_user.address
    
    return render_template('doctor/profile.html', form=profile_form, doctor=doctor)


@app.route('/doctor/upload-photo', methods=['POST'])
@login_required
@role_required('doctor')
def doctor_upload_photo():
    """Upload or update doctor photo"""
    try:
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        
        if not doctor:
            flash('Doctor profile not found.', 'error')
            return redirect(url_for('doctor_profile'))
        
        if 'photo' not in request.files:
            flash('No photo file provided.', 'error')
            return redirect(url_for('doctor_profile'))
        
        photo = request.files['photo']
        
        if photo.filename == '':
            flash('No photo selected.', 'error')
            return redirect(url_for('doctor_profile'))
        
        # Delete old photo if exists
        if doctor.photo_filename:
            delete_doctor_photo(doctor.photo_filename)
        
        # Save new photo
        filename = save_doctor_photo(photo, doctor.id)
        
        if filename:
            doctor.photo_filename = filename
            db.session.commit()
            flash('Photo uploaded successfully!', 'success')
        else:
            flash('Photo upload failed. Please ensure it is a valid image file (PNG, JPG, JPEG, GIF).', 'error')
    
    except Exception as e:
        db.session.rollback()
        print(f"Photo upload error: {e}")
        flash('An error occurred while uploading photo.', 'error')
    
    return redirect(url_for('doctor_profile'))


# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """Admin dashboard with statistics"""
    # Get statistics
    total_patients = User.query.filter_by(role='patient').count()
    total_doctors = User.query.filter_by(role='doctor').count()
    total_appointments = Appointment.query.count()
    today_appointments = Appointment.query.filter_by(appointment_date=date.today()).count()
    
    # Upcoming appointments
    upcoming = Appointment.query.filter(
        Appointment.appointment_date >= date.today(),
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(10).all()
    
    stats = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'today_appointments': today_appointments
    }
    
    return render_template('admin/dashboard.html', stats=stats, upcoming_appointments=upcoming)


@app.route('/admin/appointments')
@login_required
@role_required('admin')
def admin_appointments():
    """View all appointments with filters"""
    status_filter = request.args.get('status', 'all')
    date_filter = request.args.get('date', '')
    
    query = Appointment.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(appointment_date=filter_date)
        except ValueError:
            pass
    
    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    
    return render_template('admin/appointments.html', appointments=appointments)


@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    """Manage users"""
    role_filter = request.args.get('role', 'all')
    
    if role_filter == 'all':
        users = User.query.filter(User.role != 'admin').all()
    else:
        users = User.query.filter_by(role=role_filter).all()
    
    return render_template('admin/users.html', users=users)


@app.route('/admin/doctors', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_doctors():
    """Manage staff - doctors, receptionists, admins"""
    form = DoctorProfileForm()
    
    if form.validate_on_submit():
        # This would typically be handled in a separate route
        flash('Use the add doctor route to create new doctors.', 'info')
    
    doctors = Doctor.query.all()
    receptionists = Receptionist.query.all()
    # Get admins (users with admin role, exclude current user)
    admins = User.query.filter(User.role == 'admin', User.id != current_user.id).all()
    
    return render_template('admin/doctors.html', doctors=doctors, receptionists=receptionists, admins=admins, form=form)


@app.route('/admin/add-doctor', methods=['POST'])
@login_required
@role_required('admin')
def add_doctor():
    """Add doctor profile for existing doctor user"""
    try:
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        
        if not user or user.role != 'doctor':
            flash('Invalid user or user is not a doctor.', 'error')
            return redirect(url_for('admin_doctors'))
        
        if user.doctor_profile:
            flash('Doctor profile already exists.', 'error')
            return redirect(url_for('admin_doctors'))
        
        doctor = Doctor(
            user_id=user_id,
            specialization=request.form.get('specialization'),
            license_number=request.form.get('license_number'),
            years_of_experience=int(request.form.get('years_of_experience')),
            consultation_fee=float(request.form.get('consultation_fee')),
            department=request.form.get('department')
        )
        
        db.session.add(doctor)
        db.session.flush()  # Get doctor ID before saving photo
        
        # Handle photo upload
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename != '':
                filename = save_doctor_photo(photo, doctor.id)
                if filename:
                    doctor.photo_filename = filename
                else:
                    flash('Photo upload failed. Profile created without photo.', 'warning')
        
        db.session.commit()
        
        flash('Doctor profile created successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        print(f"Add doctor error: {e}")
        flash('An error occurred while creating doctor profile.', 'error')
    
    return redirect(url_for('admin_doctors'))


@app.route('/admin/create-staff', methods=['POST'])
@login_required
@role_required('admin')
def create_staff_account():
    """Create a new staff account (doctor or admin) - realistic hospital workflow"""
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        
        # Validate role
        if role not in ['doctor', 'admin', 'receptionist']:
            flash('Invalid role specified.', 'error')
            return redirect(url_for('admin_doctors'))
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('A user with this email already exists.', 'error')
            return redirect(url_for('admin_doctors'))
        
        # Create user account
        user = User(
            name=name,
            email=email,
            role=role,
            phone=phone if phone else None,
            gender=gender if gender else None
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # If doctor, create doctor profile
        if role == 'doctor':
            specialization = request.form.get('specialization')
            license_number = request.form.get('license_number')
            years_of_experience = request.form.get('years_of_experience')
            consultation_fee = request.form.get('consultation_fee')
            department = request.form.get('department')
            
            # Validate doctor fields
            if not all([specialization, license_number, years_of_experience, consultation_fee, department]):
                db.session.rollback()
                flash('All doctor fields are required.', 'error')
                return redirect(url_for('admin_doctors'))
            
            doctor = Doctor(
                user_id=user.id,
                specialization=specialization,
                license_number=license_number,
                years_of_experience=int(years_of_experience),
                consultation_fee=float(consultation_fee),
                department=department
            )
            
            db.session.add(doctor)
            db.session.flush()
            
            # Handle photo upload
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo and photo.filename != '':
                    filename = save_doctor_photo(photo, doctor.id)
                    if filename:
                        doctor.photo_filename = filename
        
        # If receptionist, create receptionist profile
        elif role == 'receptionist':
            employee_id = request.form.get('employee_id')
            recep_department = request.form.get('recep_department')
            shift = request.form.get('shift')
            desk_number = request.form.get('desk_number')
            
            # Validate receptionist fields
            if not all([employee_id, recep_department, shift]):
                db.session.rollback()
                flash('Employee ID, Department, and Shift are required.', 'error')
                return redirect(url_for('admin_doctors'))
            
            receptionist = Receptionist(
                user_id=user.id,
                employee_id=employee_id,
                department=recep_department,
                shift=shift,
                desk_number=desk_number if desk_number else None
            )
            
            db.session.add(receptionist)
        
        db.session.commit()
        
        flash(f'{role.capitalize()} account created successfully! Login: {email}', 'success')
    
    except Exception as e:
        db.session.rollback()
        print(f"Create staff error: {e}")
        flash('An error occurred while creating staff account.', 'error')
    
    return redirect(url_for('admin_doctors'))


@app.route('/admin/rooms', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_rooms():
    """Manage rooms"""
    form = RoomForm()
    
    if form.validate_on_submit():
        try:
            room = Room(
                room_number=form.room_number.data,
                room_type=form.room_type.data,
                floor=form.floor.data,
                capacity=form.capacity.data,
                is_available=True
            )
            
            db.session.add(room)
            db.session.commit()
            
            flash('Room added successfully!', 'success')
            return redirect(url_for('admin_rooms'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Add room error: {e}")
            flash('An error occurred while adding room.', 'error')
    
    rooms = Room.query.all()
    return render_template('admin/rooms.html', rooms=rooms, form=form)


@app.route('/admin/equipment', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_equipment():
    """Manage equipment"""
    form = EquipmentForm()
    
    # Populate room choices
    rooms = Room.query.all()
    form.room_id.choices = [(0, 'Not Assigned')] + [(r.id, f"{r.room_number} - {r.room_type}") for r in rooms]
    
    if form.validate_on_submit():
        try:
            equipment = Equipment(
                name=form.name.data,
                equipment_type=form.equipment_type.data,
                serial_number=form.serial_number.data,
                room_id=form.room_id.data if form.room_id.data != 0 else None,
                status=form.status.data
            )
            
            db.session.add(equipment)
            db.session.commit()
            
            flash('Equipment added successfully!', 'success')
            return redirect(url_for('admin_equipment'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Add equipment error: {e}")
            flash('An error occurred while adding equipment.', 'error')
    
    equipment = Equipment.query.all()
    return render_template('admin/equipment.html', equipment=equipment, form=form)


@app.route('/admin/reports')
@login_required
@role_required('admin')
def admin_reports():
    """Generate reports"""
    report_type = request.args.get('type', 'daily')
    today = date.today()
    
    if report_type == 'daily':
        appointments = Appointment.query.filter_by(appointment_date=today).all()
        title = f"Daily Report - {today}"
    elif report_type == 'weekly':
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        appointments = Appointment.query.filter(
            Appointment.appointment_date >= week_start,
            Appointment.appointment_date <= week_end
        ).all()
        title = f"Weekly Report - {week_start} to {week_end}"
    elif report_type == 'monthly':
        month_start = date(today.year, today.month, 1)
        if today.month == 12:
            month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        appointments = Appointment.query.filter(
            Appointment.appointment_date >= month_start,
            Appointment.appointment_date <= month_end
        ).all()
        title = f"Monthly Report - {today.strftime('%B %Y')}"
    else:
        appointments = []
        title = "Reports"
    
    # Calculate statistics
    total = len(appointments)
    completed = len([a for a in appointments if a.status == 'completed'])
    cancelled = len([a for a in appointments if a.status == 'cancelled'])
    scheduled = len([a for a in appointments if a.status == 'scheduled'])
    
    report_stats = {
        'total': total,
        'completed': completed,
        'cancelled': cancelled,
        'scheduled': scheduled
    }
    
    return render_template('admin/reports.html', 
                          appointments=appointments,
                          report_stats=report_stats,
                          title=title,
                          report_type=report_type)


# ==================== API ROUTES ====================

@app.route('/api/available-slots')
@login_required
def api_available_slots():
    """Get available time slots for a doctor on a specific date"""
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date')
    
    if not doctor_id or not date_str:
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        slots = generate_time_slots(doctor_id, target_date)
        
        # Convert time objects to strings
        slot_strings = [slot.strftime('%H:%M') for slot in slots]
        
        return jsonify({'slots': slot_strings})
    
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({'error': 'Error fetching slots'}), 500


@app.route('/api/doctors')
@login_required
def api_doctors():
    """Get doctors, optionally filtered by department"""
    department = request.args.get('department')
    
    query = Doctor.query.join(User)
    
    if department:
        query = query.filter(Doctor.department == department)
    
    doctors = query.all()
    
    doctor_list = [{
        'id': d.id,
        'name': d.user.name,
        'specialization': d.specialization,
        'department': d.department,
        'fee': d.consultation_fee
    } for d in doctors]
    
    return jsonify({'doctors': doctor_list})


@app.route('/api/mark-notification-read/<int:notification_id>', methods=['POST'])
@login_required
def api_mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        
        # Verify ownership
        if notification.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        print(f"Mark notification error: {e}")
        return jsonify({'error': 'Error updating notification'}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ==================== RECEPTIONIST ROUTES ====================

@app.route('/receptionist/dashboard')
@login_required
@role_required('receptionist')
def receptionist_dashboard():
    """Receptionist dashboard - show pending requests and stats"""
    today = date.today()
    
    # Get pending requests count
    pending_count = Appointment.query.filter_by(status='pending').count()
    
    # Get today's scheduled appointments
    today_count = Appointment.query.filter(
        Appointment.appointment_date == today,
        Appointment.status == 'scheduled'
    ).count()
    
    # Get recent pending requests
    pending_requests = Appointment.query.filter_by(status='pending')\
        .order_by(Appointment.created_at.desc()).limit(5).all()
    
    stats = {
        'pending_count': pending_count,
        'today_count': today_count,
        'total_doctors': Doctor.query.count()
    }
    
    return render_template('receptionist/dashboard.html', 
                          stats=stats, 
                          pending_requests=pending_requests)


@app.route('/receptionist/pending')
@login_required
@role_required('receptionist')
def receptionist_pending():
    """View all pending appointment requests"""
    pending_requests = Appointment.query.filter_by(status='pending')\
        .order_by(Appointment.created_at.desc()).all()
    
    # Add suggested doctors for each request
    requests_with_suggestions = []
    for req in pending_requests:
        suggestions = suggest_doctors(req.reason_for_visit, limit=3)
        specialty_summary = get_specialization_summary(req.reason_for_visit)
        requests_with_suggestions.append({
            'appointment': req,
            'suggestions': suggestions,
            'specialty_summary': specialty_summary
        })
    
    return render_template('receptionist/pending.html', 
                          requests=requests_with_suggestions)


@app.route('/receptionist/assign/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
@role_required('receptionist')
def receptionist_assign(appointment_id):
    """Assign a doctor and time to a pending appointment request"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.status != 'pending':
        flash('This appointment has already been processed.', 'warning')
        return redirect(url_for('receptionist_pending'))
    
    form = AssignAppointmentForm()
    
    # Populate doctor choices
    doctors = Doctor.query.join(User).filter(User.role == 'doctor').all()
    form.doctor_id.choices = [(d.id, f"Dr. {d.user.name} - {d.specialization}") for d in doctors]
    
    # Get suggested doctors
    suggestions = suggest_doctors(appointment.reason_for_visit, limit=5)
    specialty_summary = get_specialization_summary(appointment.reason_for_visit)
    
    if form.validate_on_submit():
        try:
            doctor_id = form.doctor_id.data
            appointment_date = form.appointment_date.data
            appointment_time = form.appointment_time.data
            
            # Validate slot availability
            available, message = check_slot_available(doctor_id, appointment_date, appointment_time)
            if not available:
                flash(message, 'error')
                return render_template('receptionist/assign.html', 
                                     form=form, 
                                     appointment=appointment,
                                     suggestions=suggestions,
                                     specialty_summary=specialty_summary)
            
            # Assign room
            room = assign_available_room('consultation')
            
            # Update appointment
            appointment.doctor_id = doctor_id
            appointment.appointment_date = appointment_date
            appointment.appointment_time = appointment_time
            appointment.status = 'scheduled'
            appointment.assigned_by = current_user.id
            appointment.room_id = room.id if room else None
            appointment.updated_at = datetime.utcnow()
            
            # Create time slot
            time_slot = create_time_slot(doctor_id, appointment_date, appointment_time, appointment.id)
            if not time_slot:
                raise Exception("Failed to create time slot")
            
            db.session.commit()
            
            # Send notifications
            doctor = Doctor.query.get(doctor_id)
            send_notification(
                appointment.patient_id,
                f"Your appointment has been confirmed with Dr. {doctor.user.name} on {appointment_date} at {appointment_time}",
                'appointment'
            )
            send_notification(
                doctor.user_id,
                f"New appointment assigned: {appointment.patient.name} on {appointment_date} at {appointment_time}",
                'appointment'
            )
            
            flash(f'Appointment assigned to Dr. {doctor.user.name} successfully!', 'success')
            return redirect(url_for('receptionist_pending'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Assignment error: {e}")
            flash('An error occurred while assigning the appointment.', 'error')
    
    # Pre-fill preferred date if available
    if request.method == 'GET' and appointment.preferred_date:
        form.appointment_date.data = appointment.preferred_date
    
    return render_template('receptionist/assign.html', 
                          form=form, 
                          appointment=appointment,
                          suggestions=suggestions,
                          specialty_summary=specialty_summary)


@app.route('/receptionist/appointments')
@login_required
@role_required('receptionist')
def receptionist_appointments():
    """View scheduled appointments for today - receptionist can only see, not manage"""
    today = date.today()
    
    # Get today's scheduled appointments
    today_appointments = Appointment.query.filter(
        Appointment.appointment_date == today,
        Appointment.status.in_(['scheduled', 'completed'])
    ).order_by(Appointment.appointment_time).all()
    
    # Get upcoming appointments (next 7 days)
    upcoming = Appointment.query.filter(
        Appointment.appointment_date > today,
        Appointment.appointment_date <= today + timedelta(days=7),
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    
    return render_template('receptionist/appointments.html',
                          today_appointments=today_appointments,
                          upcoming_appointments=upcoming,
                          today=today)


# ==================== TEMPLATE FILTERS ====================

@app.template_filter('format_date')
def format_date(value):
    """Format date for display"""
    if not value:
        return ''
    return value.strftime('%B %d, %Y')


@app.template_filter('format_time')
def format_time(value):
    """Format time for display"""
    if not value:
        return ''
    return value.strftime('%I:%M %p')


@app.template_filter('format_datetime')
def format_datetime(value):
    """Format datetime for display"""
    if not value:
        return ''
    return value.strftime('%B %d, %Y at %I:%M %p')


@app.template_filter('doctor_photo')
def doctor_photo(filename):
    """Get doctor photo URL"""
    return get_doctor_photo_url(filename)


# ==================== APPLICATION STARTUP ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

