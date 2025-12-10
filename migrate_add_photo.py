"""
Migration script to add photo_filename column to doctors table
Run this if you want to keep your existing data
"""

from app import app
from models import db

def add_photo_column():
    """Add photo_filename column to doctors table"""
    with app.app_context():
        try:
            # Add the new column
            db.engine.execute('ALTER TABLE doctors ADD COLUMN photo_filename VARCHAR(200)')
            print("✅ Successfully added photo_filename column to doctors table!")
            
            # Verify the column was added
            result = db.engine.execute("PRAGMA table_info(doctors)")
            columns = [row[1] for row in result]
            
            if 'photo_filename' in columns:
                print("✅ Verified: photo_filename column exists")
                print("\nCurrent columns in doctors table:")
                for col in columns:
                    print(f"  - {col}")
            else:
                print("❌ Error: Column was not added properly")
                
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  Column already exists! No migration needed.")
            else:
                print(f"❌ Error: {e}")
                print("\nIf you get an error, you may need to reset the database instead.")
                print("Run: del instance\\hospital.db && python seed_data.py")

if __name__ == "__main__":
    print("="*60)
    print("ADDING PHOTO COLUMN TO DOCTORS TABLE")
    print("="*60)
    print("\n⚠️  Make sure the Flask app is NOT running!")
    print("Press Ctrl+C in the app terminal first.\n")
    
    response = input("Continue? (yes/no): ")
    
    if response.lower() == 'yes':
        add_photo_column()
    else:
        print("Migration cancelled.")

