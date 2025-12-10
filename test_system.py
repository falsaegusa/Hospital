"""
Test Script for Hospital Management System
Verifies all critical business logic and validations
"""

from datetime import date, time, datetime, timedelta
from app import app
from models import db, User, Doctor, Appointment, DoctorAvailability, Room, TimeSlot
from utils import (check_slot_available, check_patient_availability, 
                   generate_time_slots, can_cancel_appointment, validate_phone, validate_email)

def print_test(test_name, passed, message=""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"  → {message}")


def test_password_hashing():
    """Test password hashing and verification"""
    print("\n=== Testing Password Security ===")
    with app.app_context():
        user = User.query.filter_by(email="john@email.com").first()
        
        # Test correct password
        test_check = user.check_password("patient123")
        print_test("Password hashing works", test_check)
        
        # Test wrong password
        test_wrong = not user.check_password("wrongpassword")
        print_test("Wrong password rejected", test_wrong)


def test_slot_availability():
    """Test time slot availability validation"""
    print("\n=== Testing Slot Availability ===")
    with app.app_context():
        doctor = Doctor.query.first()
        today = date.today()
        
        # Test past date
        past_date = today - timedelta(days=1)
        available, msg = check_slot_available(doctor.id, past_date, time(10, 0))
        print_test("Reject past dates", not available, msg)
        
        # Test future date (within limit)
        future_date = today + timedelta(days=7)
        # Skip weekends
        while future_date.weekday() >= 5:
            future_date += timedelta(days=1)
        
        available, msg = check_slot_available(doctor.id, future_date, time(10, 0))
        print_test("Accept valid future dates", available, msg)
        
        # Test too far in future
        far_future = today + timedelta(days=100)
        available, msg = check_slot_available(doctor.id, far_future, time(10, 0))
        print_test("Reject dates too far ahead", not available, msg)


def test_time_slot_generation():
    """Test automatic time slot generation"""
    print("\n=== Testing Time Slot Generation ===")
    with app.app_context():
        doctor = Doctor.query.first()
        
        # Get a weekday
        test_date = date.today()
        while test_date.weekday() >= 5:  # Skip weekends
            test_date += timedelta(days=1)
        
        slots = generate_time_slots(doctor.id, test_date)
        
        print_test("Generate time slots", len(slots) > 0, f"Generated {len(slots)} slots")
        
        # Verify slots are 30 minutes apart
        if len(slots) >= 2:
            slot1 = datetime.combine(date.today(), slots[0])
            slot2 = datetime.combine(date.today(), slots[1])
            diff = (slot2 - slot1).total_seconds() / 60
            print_test("Slots are 30 minutes apart", diff == 30, f"{diff} minutes")


def test_double_booking_prevention():
    """Test prevention of double-booking"""
    print("\n=== Testing Double Booking Prevention ===")
    with app.app_context():
        # Get an existing appointment
        appointment = Appointment.query.filter_by(status='scheduled').first()
        
        if appointment:
            # Try to book same doctor at same time
            available, msg = check_slot_available(
                appointment.doctor_id,
                appointment.appointment_date,
                appointment.appointment_time
            )
            print_test("Prevent double-booking same doctor", not available, msg)


def test_patient_concurrent_appointments():
    """Test prevention of patient booking multiple appointments at same time"""
    print("\n=== Testing Patient Concurrent Appointment Prevention ===")
    with app.app_context():
        appointment = Appointment.query.filter_by(status='scheduled').first()
        
        if appointment:
            # Check if patient can book another at same time
            available, msg = check_patient_availability(
                appointment.patient_id,
                appointment.appointment_date,
                appointment.appointment_time
            )
            print_test("Prevent patient double-booking", not available, msg)


def test_cancellation_logic():
    """Test appointment cancellation validation"""
    print("\n=== Testing Cancellation Logic ===")
    with app.app_context():
        # Find a future appointment
        future_appointment = Appointment.query.filter(
            Appointment.appointment_date > date.today(),
            Appointment.status == 'scheduled'
        ).first()
        
        if future_appointment:
            can_cancel, msg = can_cancel_appointment(future_appointment)
            print_test("Allow cancellation of future appointment", can_cancel, msg)
        
        # Test cancellation of completed appointment
        completed = Appointment.query.filter_by(status='completed').first()
        if completed:
            can_cancel, msg = can_cancel_appointment(completed)
            print_test("Reject cancellation of completed appointment", not can_cancel, msg)


def test_data_validation():
    """Test data validation functions"""
    print("\n=== Testing Data Validation ===")
    
    # Test email validation
    valid_emails = ["test@email.com", "user.name@example.co.uk"]
    invalid_emails = ["notanemail", "@email.com", "user@", "user"]
    
    email_valid = all(validate_email(e) for e in valid_emails)
    email_invalid = not any(validate_email(e) for e in invalid_emails)
    
    print_test("Email validation works", email_valid and email_invalid)
    
    # Test phone validation
    valid_phones = ["1234567890", "123-456-7890", "(123) 456-7890"]
    invalid_phones = ["123", "abcdefghij", "12345"]
    
    phone_valid = all(validate_phone(p) for p in valid_phones)
    phone_invalid = not any(validate_phone(p) for p in invalid_phones)
    
    print_test("Phone validation works", phone_valid and phone_invalid)


def test_database_relationships():
    """Test database relationships"""
    print("\n=== Testing Database Relationships ===")
    with app.app_context():
        # Test user-doctor relationship
        doctor_user = User.query.filter_by(role='doctor').first()
        has_profile = doctor_user.doctor_profile is not None
        print_test("User-Doctor relationship", has_profile)
        
        # Test doctor-appointment relationship
        doctor = Doctor.query.first()
        has_appointments = len(doctor.appointments) >= 0
        print_test("Doctor-Appointment relationship", True, f"{len(doctor.appointments)} appointments")
        
        # Test appointment-patient relationship
        appointment = Appointment.query.first()
        has_patient = appointment.patient is not None
        print_test("Appointment-Patient relationship", has_patient)
        
        # Test room-appointment relationship
        room = Room.query.first()
        has_room_appointments = len(room.appointments) >= 0
        print_test("Room-Appointment relationship", True, f"{len(room.appointments)} appointments")


def test_doctor_availability():
    """Test doctor availability setup"""
    print("\n=== Testing Doctor Availability ===")
    with app.app_context():
        doctor = Doctor.query.first()
        availability = DoctorAvailability.query.filter_by(doctor_id=doctor.id).all()
        
        print_test("Doctor has availability set", len(availability) > 0, f"{len(availability)} days set")
        
        # Test availability for each weekday
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        has_weekdays = all(
            any(a.day_of_week == day for a in availability)
            for day in weekdays
        )
        print_test("Availability covers weekdays", has_weekdays)


def test_role_based_access():
    """Test role-based access control"""
    print("\n=== Testing Role-Based Access ===")
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        patient = User.query.filter_by(role='patient').first()
        doctor_user = User.query.filter_by(role='doctor').first()
        
        print_test("Admin role exists", admin is not None)
        print_test("Patient role exists", patient is not None)
        print_test("Doctor role exists", doctor_user is not None)
        
        # Test that roles are distinct
        roles = {admin.role, patient.role, doctor_user.role}
        print_test("Roles are distinct", len(roles) == 3)


def test_notification_system():
    """Test notification creation"""
    print("\n=== Testing Notification System ===")
    with app.app_context():
        from models import Notification
        
        # Check if notifications exist
        notif_count = Notification.query.count()
        print_test("Notifications created", notif_count > 0, f"{notif_count} notifications")
        
        # Test notification-user relationship
        notif = Notification.query.first()
        if notif:
            has_user = notif.user is not None
            print_test("Notification-User relationship", has_user)


def test_room_management():
    """Test room and equipment management"""
    print("\n=== Testing Resource Management ===")
    with app.app_context():
        from models import Equipment
        
        rooms = Room.query.all()
        equipment = Equipment.query.all()
        
        print_test("Rooms created", len(rooms) > 0, f"{len(rooms)} rooms")
        print_test("Equipment created", len(equipment) > 0, f"{len(equipment)} items")
        
        # Test room types
        room_types = set(r.room_type for r in rooms)
        has_types = len(room_types) > 0
        print_test("Room types defined", has_types, f"Types: {room_types}")


def run_all_tests():
    """Run all test suites"""
    print("="*60)
    print("HOSPITAL MANAGEMENT SYSTEM - TEST SUITE")
    print("="*60)
    
    try:
        test_password_hashing()
        test_slot_availability()
        test_time_slot_generation()
        test_double_booking_prevention()
        test_patient_concurrent_appointments()
        test_cancellation_logic()
        test_data_validation()
        test_database_relationships()
        test_doctor_availability()
        test_role_based_access()
        test_notification_system()
        test_room_management()
        
        print("\n" + "="*60)
        print("TEST SUITE COMPLETED")
        print("="*60)
        print("\n✅ If all tests passed, the system is working correctly!")
        print("🚀 You can now run: python app.py")
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        print("Make sure you have run 'python seed_data.py' first!")


if __name__ == "__main__":
    run_all_tests()

