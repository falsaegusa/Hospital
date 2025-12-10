"""
Seed Data Script for Hospital Management System
Populates the database with test data for development and testing
"""

from app import app
from models import db, User, Doctor, Appointment, DoctorAvailability, Room, Equipment, Notification
from datetime import date, time, datetime, timedelta
import random

def clear_database():
    """Clear all existing data"""
    print("Clearing existing data...")
    with app.app_context():
        # Order matters due to foreign key constraints
        Notification.query.delete()
        Appointment.query.delete()
        DoctorAvailability.query.delete()
        Doctor.query.delete()
        Equipment.query.delete()
        Room.query.delete()
        User.query.delete()
        db.session.commit()
    print("Database cleared!")


def create_admin():
    """Create admin user"""
    print("\nCreating admin user...")
    admin = User(
        name="Admin User",
        email="admin@hospital.com",
        role="admin",
        phone="1234567890",
        date_of_birth=date(1980, 1, 1),
        gender="other",
        address="Hospital Administration Building"
    )
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()
    print(f"✓ Admin created: {admin.email} / admin123")
    return admin


def create_patients():
    """Create patient users"""
    print("\nCreating patients...")
    patients = []
    
    patient_data = [
        ("John Smith", "john@email.com", "1990-05-15", "male", "123 Main St"),
        ("Sarah Johnson", "sarah@email.com", "1985-08-22", "female", "456 Oak Ave"),
        ("Michael Brown", "michael@email.com", "1992-03-10", "male", "789 Pine Rd"),
        ("Emily Davis", "emily@email.com", "1988-11-30", "female", "321 Elm St"),
        ("David Wilson", "david@email.com", "1995-07-18", "male", "654 Maple Dr"),
        ("Jessica Martinez", "jessica@email.com", "1987-09-25", "female", "987 Cedar Ln"),
        ("Christopher Lee", "chris@email.com", "1991-12-05", "male", "147 Birch Way"),
        ("Amanda Taylor", "amanda@email.com", "1989-04-14", "female", "258 Spruce St"),
        ("Daniel Anderson", "daniel@email.com", "1993-06-20", "male", "369 Willow Ct"),
        ("Lisa Thomas", "lisa@email.com", "1986-02-28", "female", "741 Ash Blvd")
    ]
    
    for name, email, dob, gender, address in patient_data:
        patient = User(
            name=name,
            email=email,
            role="patient",
            phone=f"{random.randint(1000000000, 9999999999)}",
            date_of_birth=datetime.strptime(dob, "%Y-%m-%d").date(),
            gender=gender,
            address=address
        )
        patient.set_password("patient123")
        db.session.add(patient)
        patients.append(patient)
    
    db.session.commit()
    print(f"✓ Created {len(patients)} patients (password: patient123)")
    return patients


def create_doctors():
    """Create doctor users and profiles"""
    print("\nCreating doctors...")
    doctors = []
    
    doctor_data = [
        ("Dr. Robert Anderson", "robert.anderson@hospital.com", "Cardiology", "LIC001", 15, 150.00, "Cardiology"),
        ("Dr. Jennifer White", "jennifer.white@hospital.com", "Pediatrics", "LIC002", 12, 120.00, "Pediatrics"),
        ("Dr. William Harris", "william.harris@hospital.com", "Orthopedics", "LIC003", 20, 200.00, "Orthopedics"),
        ("Dr. Maria Garcia", "maria.garcia@hospital.com", "Dermatology", "LIC004", 10, 130.00, "Dermatology"),
        ("Dr. James Miller", "james.miller@hospital.com", "Neurology", "LIC005", 18, 180.00, "Neurology")
    ]
    
    for name, email, specialization, license_num, experience, fee, department in doctor_data:
        # Create user
        user = User(
            name=name,
            email=email,
            role="doctor",
            phone=f"{random.randint(1000000000, 9999999999)}",
            date_of_birth=date(1970 + random.randint(0, 15), random.randint(1, 12), random.randint(1, 28)),
            gender="male" if name.startswith("Dr. William") or name.startswith("Dr. Robert") or name.startswith("Dr. James") else "female",
            address=f"Hospital Staff Quarters - {name.split()[-1]}"
        )
        user.set_password("doctor123")
        db.session.add(user)
        db.session.flush()
        
        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            specialization=specialization,
            license_number=license_num,
            years_of_experience=experience,
            consultation_fee=fee,
            department=department
        )
        db.session.add(doctor)
        doctors.append((user, doctor))
    
    db.session.commit()
    print(f"✓ Created {len(doctors)} doctors (password: doctor123)")
    return doctors


def set_doctor_availability(doctors):
    """Set weekly availability for all doctors"""
    print("\nSetting doctor availability...")
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    for user, doctor in doctors:
        for day in days:
            availability = DoctorAvailability(
                doctor_id=doctor.id,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_available=True
            )
            db.session.add(availability)
    
    db.session.commit()
    print(f"✓ Set availability for {len(doctors)} doctors (Mon-Fri, 9AM-5PM)")


def create_rooms():
    """Create hospital rooms"""
    print("\nCreating rooms...")
    rooms = []
    
    room_data = [
        ("101", "consultation", 1, 2),
        ("102", "consultation", 1, 2),
        ("103", "consultation", 1, 2),
        ("201", "operation", 2, 5),
        ("202", "emergency", 2, 3),
    ]
    
    for room_num, room_type, floor, capacity in room_data:
        room = Room(
            room_number=room_num,
            room_type=room_type,
            floor=floor,
            capacity=capacity,
            is_available=True
        )
        db.session.add(room)
        rooms.append(room)
    
    db.session.commit()
    print(f"✓ Created {len(rooms)} rooms")
    return rooms


def create_equipment(rooms):
    """Create medical equipment"""
    print("\nCreating equipment...")
    equipment_list = []
    
    equipment_data = [
        ("ECG Machine", "Diagnostic", "ECG-001"),
        ("X-Ray Machine", "Imaging", "XRAY-001"),
        ("Ultrasound Machine", "Imaging", "US-001"),
        ("Blood Pressure Monitor", "Diagnostic", "BP-001"),
        ("Defibrillator", "Emergency", "DEF-001"),
        ("Ventilator", "Life Support", "VENT-001"),
        ("Surgical Table", "Surgery", "TABLE-001"),
        ("Anesthesia Machine", "Surgery", "ANES-001"),
        ("Patient Monitor", "Monitoring", "MON-001"),
        ("Infusion Pump", "Treatment", "INF-001")
    ]
    
    for i, (name, eq_type, serial) in enumerate(equipment_data):
        # Assign some equipment to rooms
        room_id = rooms[i % len(rooms)].id if i < 7 else None
        
        equipment = Equipment(
            name=name,
            equipment_type=eq_type,
            serial_number=serial,
            room_id=room_id,
            status="available"
        )
        db.session.add(equipment)
        equipment_list.append(equipment)
    
    db.session.commit()
    print(f"✓ Created {len(equipment_list)} equipment items")
    return equipment_list


def create_appointments(patients, doctors, rooms):
    """Create sample appointments"""
    print("\nCreating appointments...")
    appointments = []
    
    today = date.today()
    
    # Create past appointments (completed)
    for i in range(10):
        days_ago = random.randint(7, 30)
        appointment_date = today - timedelta(days=days_ago)
        
        # Skip weekends
        while appointment_date.weekday() >= 5:
            appointment_date -= timedelta(days=1)
        
        patient = random.choice(patients)
        user, doctor = random.choice(doctors)
        room = random.choice(rooms)
        
        # Random time between 9 AM and 4 PM
        hour = random.randint(9, 16)
        minute = random.choice([0, 30])
        
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            appointment_time=time(hour, minute),
            status="completed",
            reason_for_visit=random.choice([
                "Regular checkup",
                "Follow-up consultation",
                "Annual physical",
                "Vaccination",
                "Lab results review"
            ]),
            notes="Consultation completed successfully.",
            room_id=room.id
        )
        db.session.add(appointment)
        appointments.append(appointment)
    
    # Create upcoming appointments (scheduled)
    for i in range(10):
        days_ahead = random.randint(1, 14)
        appointment_date = today + timedelta(days=days_ahead)
        
        # Skip weekends
        while appointment_date.weekday() >= 5:
            appointment_date += timedelta(days=1)
        
        patient = random.choice(patients)
        user, doctor = random.choice(doctors)
        room = random.choice(rooms)
        
        # Random time between 9 AM and 4 PM
        hour = random.randint(9, 16)
        minute = random.choice([0, 30])
        
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            appointment_time=time(hour, minute),
            status="scheduled",
            reason_for_visit=random.choice([
                "Consultation",
                "New patient visit",
                "Follow-up",
                "Treatment",
                "Examination"
            ]),
            room_id=room.id
        )
        db.session.add(appointment)
        appointments.append(appointment)
    
    db.session.commit()
    print(f"✓ Created {len(appointments)} appointments (10 past, 10 upcoming)")
    return appointments


def create_notifications(patients, doctors, appointments):
    """Create sample notifications"""
    print("\nCreating notifications...")
    notifications = []
    
    for appointment in appointments[:5]:  # Create notifications for first 5 appointments
        # Notification for patient
        patient_notif = Notification(
            user_id=appointment.patient_id,
            message=f"Your appointment with Dr. {appointment.doctor.user.name} is scheduled for {appointment.appointment_date} at {appointment.appointment_time}",
            notification_type="appointment",
            is_read=random.choice([True, False])
        )
        db.session.add(patient_notif)
        notifications.append(patient_notif)
        
        # Notification for doctor
        doctor_notif = Notification(
            user_id=appointment.doctor.user_id,
            message=f"New appointment with {appointment.patient.name} scheduled for {appointment.appointment_date} at {appointment.appointment_time}",
            notification_type="appointment",
            is_read=random.choice([True, False])
        )
        db.session.add(doctor_notif)
        notifications.append(doctor_notif)
    
    db.session.commit()
    print(f"✓ Created {len(notifications)} notifications")
    return notifications


def print_credentials():
    """Print test credentials"""
    print("\n" + "="*60)
    print("TEST CREDENTIALS")
    print("="*60)
    print("\nADMIN:")
    print("  Email: admin@hospital.com")
    print("  Password: admin123")
    print("\nDOCTORS (all have password: doctor123):")
    print("  - robert.anderson@hospital.com (Cardiology)")
    print("  - jennifer.white@hospital.com (Pediatrics)")
    print("  - william.harris@hospital.com (Orthopedics)")
    print("  - maria.garcia@hospital.com (Dermatology)")
    print("  - james.miller@hospital.com (Neurology)")
    print("\nPATIENTS (all have password: patient123):")
    print("  - john@email.com (John Smith)")
    print("  - sarah@email.com (Sarah Johnson)")
    print("  - michael@email.com (Michael Brown)")
    print("  - emily@email.com (Emily Davis)")
    print("  - david@email.com (David Wilson)")
    print("  - ... and 5 more patients")
    print("\n" + "="*60)


def seed_all():
    """Main function to seed all data"""
    print("\n" + "="*60)
    print("HOSPITAL MANAGEMENT SYSTEM - SEED DATA")
    print("="*60)
    
    with app.app_context():
        # Clear existing data
        clear_database()
        
        # Create all data
        admin = create_admin()
        patients = create_patients()
        doctors = create_doctors()
        set_doctor_availability(doctors)
        rooms = create_rooms()
        equipment = create_equipment(rooms)
        appointments = create_appointments(patients, doctors, rooms)
        notifications = create_notifications(patients, doctors, appointments)
        
        print("\n" + "="*60)
        print("SEEDING COMPLETE!")
        print("="*60)
        print(f"\nDatabase Statistics:")
        print(f"  - Admins: 1")
        print(f"  - Patients: {len(patients)}")
        print(f"  - Doctors: {len(doctors)}")
        print(f"  - Rooms: {len(rooms)}")
        print(f"  - Equipment: {len(equipment)}")
        print(f"  - Appointments: {len(appointments)}")
        print(f"  - Notifications: {len(notifications)}")
        
        print_credentials()


if __name__ == "__main__":
    seed_all()

