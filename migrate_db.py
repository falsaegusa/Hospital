"""
Database migration script - adds new columns for triage system.
"""
from app import app
from models import db
from sqlalchemy import text

def migrate():
    with app.app_context():
        with db.engine.connect() as conn:
            print("Adding new columns to appointments table...")
            
            # Add preferred_date column
            try:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN preferred_date DATE"))
                print("  Added preferred_date")
            except Exception as e:
                if "already exists" in str(e):
                    print("  preferred_date already exists")
                else:
                    print(f"  preferred_date: {e}")
            
            # Add assigned_by column
            try:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN assigned_by INTEGER"))
                print("  Added assigned_by")
            except Exception as e:
                if "already exists" in str(e):
                    print("  assigned_by already exists")
                else:
                    print(f"  assigned_by: {e}")
            
            # Make doctor_id nullable
            try:
                conn.execute(text("ALTER TABLE appointments ALTER COLUMN doctor_id DROP NOT NULL"))
                print("  Made doctor_id nullable")
            except Exception as e:
                print(f"  doctor_id: {e}")
            
            # Make appointment_date nullable
            try:
                conn.execute(text("ALTER TABLE appointments ALTER COLUMN appointment_date DROP NOT NULL"))
                print("  Made appointment_date nullable")
            except Exception as e:
                print(f"  appointment_date: {e}")
            
            # Make appointment_time nullable  
            try:
                conn.execute(text("ALTER TABLE appointments ALTER COLUMN appointment_time DROP NOT NULL"))
                print("  Made appointment_time nullable")
            except Exception as e:
                print(f"  appointment_time: {e}")
            
            # Update status default
            try:
                conn.execute(text("ALTER TABLE appointments ALTER COLUMN status SET DEFAULT 'pending'"))
                print("  Updated status default")
            except Exception as e:
                print(f"  status: {e}")
            
            conn.commit()
            
        # Create receptionists table if it doesn't exist
        print("\nCreating receptionists table...")
        db.create_all()
        
        print("\n✅ Migration completed!")

if __name__ == '__main__':
    migrate()
