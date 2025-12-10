"""
Clear database script - removes all data except admin user
"""
from app import app
from models import db, User, Doctor, Receptionist, Appointment, DoctorAvailability, TimeSlot, Room, Equipment, Notification

def clear_database_keep_admin():
    """Clear all data except admin user"""
    print("\n" + "="*60)
    print("CLEARING DATABASE (KEEPING ADMIN)")
    print("="*60)
    
    with app.app_context():
        # Delete in proper order due to foreign key constraints
        print("\nDeleting notifications...")
        Notification.query.delete()
        
        print("Deleting time slots...")
        TimeSlot.query.delete()
        
        print("Deleting appointments...")
        Appointment.query.delete()
        
        print("Deleting doctor availability...")
        DoctorAvailability.query.delete()
        
        print("Deleting equipment...")
        Equipment.query.delete()
        
        print("Deleting rooms...")
        Room.query.delete()
        
        print("Deleting receptionists...")
        Receptionist.query.delete()
        
        print("Deleting doctors...")
        Doctor.query.delete()
        
        print("Deleting non-admin users...")
        User.query.filter(User.role != 'admin').delete()
        
        db.session.commit()
        
        # Verify admin still exists
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"\n✓ Admin user preserved: {admin.email}")
        else:
            print("\n⚠ No admin user found. Creating one...")
            from datetime import date
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
            print(f"✓ Admin created: admin@hospital.com / admin123")
        
        print("\n" + "="*60)
        print("DATABASE CLEARED SUCCESSFULLY!")
        print("="*60)
        print("\nRemaining data:")
        print(f"  - Admin users: {User.query.filter_by(role='admin').count()}")
        print(f"  - Other users: {User.query.filter(User.role != 'admin').count()}")
        print(f"  - Doctors: {Doctor.query.count()}")
        print(f"  - Appointments: {Appointment.query.count()}")
        print(f"  - Rooms: {Room.query.count()}")
        print(f"  - Equipment: {Equipment.query.count()}")

if __name__ == "__main__":
    clear_database_keep_admin()
