from datetime import datetime, date, time, timedelta
from models import db, Doctor, DoctorAvailability, TimeSlot, Appointment, Room, Notification
from config import Config
import re


def generate_time_slots(doctor_id, target_date):
    """
    Generate available 30-minute time slots for a doctor on a specific date
    Returns list of time objects representing available slots
    """
    try:
        # Get day of week for the target date
        day_name = target_date.strftime('%A')
        
        # Get doctor's availability for that day
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day_name,
            is_available=True
        ).first()
        
        if not availability:
            return []
        
        # Generate all possible slots
        slots = []
        current_time = datetime.combine(date.today(), availability.start_time)
        end_time = datetime.combine(date.today(), availability.end_time)
        
        while current_time < end_time:
            slots.append(current_time.time())
            current_time += timedelta(minutes=Config.DEFAULT_APPOINTMENT_DURATION)
        
        # Filter out already booked slots
        booked_slots = TimeSlot.query.filter_by(
            doctor_id=doctor_id,
            date=target_date,
            is_booked=True
        ).all()
        
        booked_times = [slot.start_time for slot in booked_slots]
        available_slots = [slot for slot in slots if slot not in booked_times]
        
        return available_slots
    
    except Exception as e:
        print(f"Error generating time slots: {e}")
        return []


def check_slot_available(doctor_id, appointment_date, appointment_time):
    """
    Check if a specific time slot is available for booking
    Returns (bool, message) tuple
    """
    try:
        # Check if date is in the past
        if appointment_date < date.today():
            return False, "Cannot book appointments for past dates"
        
        # Check if date is too far in future
        max_date = date.today() + timedelta(days=Config.APPOINTMENT_ADVANCE_BOOKING_DAYS)
        if appointment_date > max_date:
            return False, f"Cannot book appointments more than {Config.APPOINTMENT_ADVANCE_BOOKING_DAYS} days in advance"
        
        # Get day of week
        day_name = appointment_date.strftime('%A')
        
        # Check doctor's availability for that day
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day_name,
            is_available=True
        ).first()
        
        if not availability:
            return False, "Doctor is not available on this day"
        
        # Check if time is within working hours
        if appointment_time < availability.start_time or appointment_time >= availability.end_time:
            return False, "Selected time is outside doctor's working hours"
        
        # Check if slot is already booked
        existing_slot = TimeSlot.query.filter_by(
            doctor_id=doctor_id,
            date=appointment_date,
            start_time=appointment_time,
            is_booked=True
        ).first()
        
        if existing_slot:
            return False, "This time slot is already booked"
        
        # Check if there's an active appointment at this time
        existing_appointment = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).filter(Appointment.status != 'cancelled').first()
        
        if existing_appointment:
            return False, "Doctor already has an appointment at this time"
        
        return True, "Slot is available"
    
    except Exception as e:
        print(f"Error checking slot availability: {e}")
        return False, "Error checking availability"


def check_patient_availability(patient_id, appointment_date, appointment_time):
    """
    Check if patient already has an appointment at the given time
    Returns (bool, message) tuple
    """
    try:
        existing = Appointment.query.filter_by(
            patient_id=patient_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).filter(Appointment.status != 'cancelled').first()
        
        if existing:
            return False, "You already have an appointment at this time"
        
        return True, "Patient is available"
    
    except Exception as e:
        print(f"Error checking patient availability: {e}")
        return False, "Error checking patient availability"


def assign_available_room(room_type='consultation'):
    """
    Find and assign an available room
    Returns Room object or None
    """
    try:
        room = Room.query.filter_by(
            room_type=room_type,
            is_available=True
        ).first()
        
        return room
    
    except Exception as e:
        print(f"Error assigning room: {e}")
        return None


def send_notification(user_id, message, notification_type):
    """
    Create a notification for a user
    Returns True if successful, False otherwise
    """
    try:
        notification = Notification(
            user_id=user_id,
            message=message,
            notification_type=notification_type
        )
        db.session.add(notification)
        db.session.commit()
        return True
    
    except Exception as e:
        print(f"Error sending notification: {e}")
        db.session.rollback()
        return False


def calculate_age(date_of_birth):
    """Calculate age from date of birth"""
    if not date_of_birth:
        return None
    
    today = date.today()
    age = today.year - date_of_birth.year
    
    # Adjust if birthday hasn't occurred this year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    
    return age


def format_time_12hr(time_24hr):
    """Convert 24-hour time to 12-hour format with AM/PM"""
    if isinstance(time_24hr, str):
        time_24hr = datetime.strptime(time_24hr, '%H:%M').time()
    
    return time_24hr.strftime('%I:%M %p')


def validate_phone(phone):
    """Validate phone number format (10 digits)"""
    if not phone:
        return False
    
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's 10 digits
    return bool(re.match(r'^\d{10}$', cleaned))


def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def can_cancel_appointment(appointment):
    """
    Check if an appointment can be cancelled (at least 2 hours before)
    Returns (bool, message) tuple
    """
    if appointment.status == 'cancelled':
        return False, "Appointment is already cancelled"
    
    if appointment.status == 'completed':
        return False, "Cannot cancel a completed appointment"
    
    # Combine date and time
    appointment_datetime = datetime.combine(
        appointment.appointment_date,
        appointment.appointment_time
    )
    
    # Calculate time difference
    time_until_appointment = appointment_datetime - datetime.now()
    hours_until = time_until_appointment.total_seconds() / 3600
    
    if hours_until < Config.APPOINTMENT_CANCELLATION_HOURS:
        return False, f"Cannot cancel appointment less than {Config.APPOINTMENT_CANCELLATION_HOURS} hours before scheduled time"
    
    return True, "Appointment can be cancelled"


def create_time_slot(doctor_id, appointment_date, appointment_time, appointment_id=None):
    """
    Create a time slot for an appointment
    """
    try:
        end_time = (datetime.combine(date.today(), appointment_time) + 
                   timedelta(minutes=Config.DEFAULT_APPOINTMENT_DURATION)).time()
        
        time_slot = TimeSlot(
            doctor_id=doctor_id,
            date=appointment_date,
            start_time=appointment_time,
            end_time=end_time,
            is_booked=True,
            appointment_id=appointment_id
        )
        
        db.session.add(time_slot)
        return time_slot
    
    except Exception as e:
        print(f"Error creating time slot: {e}")
        return None


def free_time_slot(appointment):
    """
    Free up a time slot when appointment is cancelled
    """
    try:
        time_slot = TimeSlot.query.filter_by(
            doctor_id=appointment.doctor_id,
            date=appointment.appointment_date,
            start_time=appointment.appointment_time,
            appointment_id=appointment.id
        ).first()
        
        if time_slot:
            db.session.delete(time_slot)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error freeing time slot: {e}")
        return False


def get_unread_notifications(user_id):
    """Get count of unread notifications for a user"""
    try:
        count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        return count
    except Exception as e:
        print(f"Error getting unread notifications: {e}")
        return 0

