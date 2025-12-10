"""
Database initialization script for PostgreSQL.
Run this script to create all tables and seed initial data.

Usage: python init_db.py
"""
from app import app
from models import db, User, Doctor, Receptionist, Room

def init_database():
    """Initialize the database with tables and seed data"""
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully!")
        
        # Check if admin exists
        admin = User.query.filter_by(email='admin@hospital.com').first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                name='Admin User',
                email='admin@hospital.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Check if receptionist exists
        receptionist_user = User.query.filter_by(email='sarah.jones@hospital.com').first()
        if not receptionist_user:
            print("Creating receptionist user...")
            receptionist_user = User(
                name='Sarah Jones',
                email='sarah.jones@hospital.com',
                role='receptionist',
                phone='5551234567',
                gender='female'
            )
            receptionist_user.set_password('recep123')
            db.session.add(receptionist_user)
            db.session.flush()
            
            # Create receptionist profile
            receptionist_profile = Receptionist(
                user_id=receptionist_user.id,
                employee_id='REC-001',
                department='Front Desk',
                shift='Morning',
                desk_number='D-101'
            )
            db.session.add(receptionist_profile)
            
        # Check if sample doctor exists
        doctor_user = User.query.filter_by(email='dr.smith@hospital.com').first()
        if not doctor_user:
            print("Creating sample doctor...")
            doctor_user = User(
                name='Dr. John Smith',
                email='dr.smith@hospital.com',
                role='doctor',
                phone='1234567890',
                gender='male'
            )
            doctor_user.set_password('doctor123')
            db.session.add(doctor_user)
            db.session.flush()  # Get the ID
            
            # Create doctor profile
            doctor_profile = Doctor(
                user_id=doctor_user.id,
                specialization='General Medicine',
                license_number='MD-12345',
                years_of_experience=10,
                consultation_fee=100.00,
                department='General Medicine'
            )
            db.session.add(doctor_profile)
        
        # Create cardiologist for triage testing
        cardio_user = User.query.filter_by(email='dr.heart@hospital.com').first()
        if not cardio_user:
            print("Creating cardiologist...")
            cardio_user = User(
                name='Dr. Emily Heart',
                email='dr.heart@hospital.com',
                role='doctor',
                phone='1234567891',
                gender='female'
            )
            cardio_user.set_password('doctor123')
            db.session.add(cardio_user)
            db.session.flush()
            
            cardio_profile = Doctor(
                user_id=cardio_user.id,
                specialization='Cardiology',
                license_number='MD-67890',
                years_of_experience=15,
                consultation_fee=150.00,
                department='Cardiology'
            )
            db.session.add(cardio_profile)
        
        # Check if sample patient exists
        patient = User.query.filter_by(email='patient@test.com').first()
        if not patient:
            print("Creating sample patient...")
            patient = User(
                name='Test Patient',
                email='patient@test.com',
                role='patient',
                phone='9876543210',
                gender='female'
            )
            patient.set_password('patient123')
            db.session.add(patient)
        
        # Check if sample room exists
        room = Room.query.filter_by(room_number='R-101').first()
        if not room:
            print("Creating sample rooms...")
            rooms = [
                Room(room_number='R-101', room_type='consultation', floor=1, capacity=2),
                Room(room_number='R-102', room_type='consultation', floor=1, capacity=2),
                Room(room_number='R-201', room_type='operation', floor=2, capacity=5),
            ]
            db.session.add_all(rooms)
        
        db.session.commit()
        print("\n✅ Database initialized successfully!")
        print("\n📋 Test Credentials:")
        print("   Admin:        admin@hospital.com / admin123")
        print("   Receptionist: sarah.jones@hospital.com / recep123")
        print("   Doctor:       dr.smith@hospital.com / doctor123")
        print("   Cardiologist: dr.heart@hospital.com / doctor123")
        print("   Patient:      patient@test.com / patient123")

if __name__ == '__main__':
    init_database()
