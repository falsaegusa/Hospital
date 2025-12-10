"""
QUICK FIX: Add photo_filename column
Run this while Flask is stopped
"""
import sqlite3

# Connect directly to database
conn = sqlite3.connect('instance/hospital.db')
cursor = conn.cursor()

try:
    # Add the column
    cursor.execute('ALTER TABLE doctors ADD COLUMN photo_filename VARCHAR(200)')
    conn.commit()
    print("✅ SUCCESS! Photo column added.")
    print("\nYou can now restart Flask with: python app.py")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✅ Column already exists! You're good to go.")
    else:
        print(f"❌ Error: {e}")
finally:
    conn.close()


