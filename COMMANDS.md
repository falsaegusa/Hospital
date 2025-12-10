# Hospital Management System - Command Reference

## 🚀 Essential Commands

### First Time Setup
```bash
# 1. Install all required packages
pip install -r requirements.txt

# 2. Populate the database with test data
python seed_data.py

# 3. (Optional) Run automated tests
python test_system.py

# 4. Start the application
python app.py
```

### Daily Use
```bash
# Start the server
python app.py

# Access in browser
# Open: http://localhost:5000
```

## 🔧 Maintenance Commands

### Reset Database
```bash
# Windows
del hospital.db
python seed_data.py

# macOS/Linux
rm hospital.db
python seed_data.py
```

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Reinstall Dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

## 🧪 Testing Commands

### Run Full Test Suite
```bash
python test_system.py
```

### Test Specific Feature (Manual)
```bash
# Start the app
python app.py

# Then test in browser:
# 1. Go to http://localhost:5000
# 2. Login with test credentials
# 3. Perform actions
```

## 🐍 Python Environment

### Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Check Installed Packages
```bash
pip list
```

### Generate New Requirements File
```bash
pip freeze > requirements.txt
```

## 🗄️ Database Operations

### Create Database (First Time)
```bash
python app.py
# Database automatically created on first run
```

### View Database (Optional)
```bash
# Install SQLite browser or use command line
sqlite3 hospital.db

# SQLite commands:
.tables              # List all tables
.schema users        # Show table structure
SELECT * FROM users; # Query data
.quit                # Exit
```

### Backup Database
```bash
# Windows
copy hospital.db hospital_backup.db

# macOS/Linux
cp hospital.db hospital_backup.db
```

### Restore Database
```bash
# Windows
copy hospital_backup.db hospital.db

# macOS/Linux
cp hospital_backup.db hospital.db
```

## 🔍 Debugging Commands

### Run with Verbose Output
```bash
# Debug mode is already enabled in app.py
# SQL queries are printed to console
python app.py
```

### Check Python Version
```bash
python --version
# Requires Python 3.8+
```

### Check Flask Version
```bash
python -c "import flask; print(flask.__version__)"
```

### Check All Dependencies
```bash
pip check
```

## 📝 Development Commands

### Create New Migration (Future Use)
```bash
# If you add Flask-Migrate later:
flask db init
flask db migrate -m "Description"
flask db upgrade
```

### Run Flask Shell
```bash
# Interactive Python shell with app context
python
>>> from app import app, db
>>> from models import User, Doctor, Appointment
>>> with app.app_context():
...     users = User.query.all()
...     print(len(users))
```

## 🌐 Server Configuration

### Change Port
```bash
# Edit last line in app.py:
# app.run(debug=True, host='0.0.0.0', port=5001)
python app.py
```

### Run on Specific IP
```bash
# Edit last line in app.py:
# app.run(debug=True, host='192.168.1.100', port=5000)
python app.py
```

### Production Mode (Not Recommended for Development)
```bash
# Edit last line in app.py:
# app.run(debug=False)
python app.py
```

## 📊 Data Commands

### Query Database Directly
```bash
python
>>> from app import app
>>> from models import db, User, Doctor, Appointment
>>> with app.app_context():
...     # Count users
...     print(f"Total users: {User.query.count()}")
...     
...     # Count appointments
...     print(f"Total appointments: {Appointment.query.count()}")
...     
...     # Get specific user
...     user = User.query.filter_by(email='john@email.com').first()
...     print(f"User: {user.name}")
```

### Add Custom Data
```bash
python
>>> from app import app
>>> from models import db, User
>>> with app.app_context():
...     user = User(name="Test User", email="test@test.com", role="patient")
...     user.set_password("test123")
...     db.session.add(user)
...     db.session.commit()
...     print("User added!")
```

## 🧹 Cleanup Commands

### Remove Cache Files
```bash
# Windows
del /s *.pyc
rmdir /s /q __pycache__

# macOS/Linux
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete
```

### Remove Database
```bash
# Windows
del hospital.db

# macOS/Linux
rm hospital.db
```

### Clean Project (Keep Source)
```bash
# Remove database and cache
# Windows
del hospital.db
del /s *.pyc
rmdir /s /q __pycache__

# macOS/Linux
rm hospital.db
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete
```

## 📦 Package Management

### Install Specific Package Version
```bash
pip install Flask==2.3.3
```

### Uninstall Package
```bash
pip uninstall flask-sqlalchemy
```

### Show Package Info
```bash
pip show Flask
```

## 🔐 Security Commands

### Change Secret Key (Production)
```bash
# Generate new secret key
python
>>> import secrets
>>> print(secrets.token_hex(32))
# Copy output to config.py SECRET_KEY
```

### Check Security Issues
```bash
pip install safety
safety check
```

## 📋 Git Commands (If Using Version Control)

### Initialize Repository
```bash
git init
git add .
git commit -m "Initial commit: Hospital Management System"
```

### Ignore Sensitive Files
```bash
# .gitignore is already created
# Includes: *.db, venv/, __pycache__, etc.
```

### Create Backup Branch
```bash
git branch backup
git checkout backup
git checkout main
```

## 🎯 Quick Troubleshooting

### "Port already in use" Error
```bash
# Option 1: Kill process on port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>

# Option 2: Change port in app.py
```

### "Module not found" Error
```bash
pip install -r requirements.txt --force-reinstall
```

### "Database locked" Error
```bash
# Close all connections to database
# Delete hospital.db and reseed
python seed_data.py
```

### "CSRF token missing" Error
```bash
# Ensure {{ form.hidden_tag() }} is in all forms
# Check config.py: WTF_CSRF_ENABLED = True
```

## 📞 Help Commands

### Flask Help
```bash
flask --help
```

### Python Help
```bash
python --help
```

### Pip Help
```bash
pip --help
```

## 🎓 Learning Commands

### Explore Models
```bash
python
>>> from models import *
>>> help(User)
>>> help(Appointment)
```

### Check Route List
```bash
python
>>> from app import app
>>> with app.app_context():
...     for rule in app.url_map.iter_rules():
...         print(f"{rule.endpoint}: {rule.rule}")
```

### View Configuration
```bash
python
>>> from config import Config
>>> print(Config.APPOINTMENT_ADVANCE_BOOKING_DAYS)
>>> print(Config.BUSINESS_HOURS_START)
```

## 💡 Pro Tips

### Run in Background (Advanced)
```bash
# Windows (PowerShell)
Start-Process python -ArgumentList "app.py" -WindowStyle Hidden

# macOS/Linux
nohup python app.py > output.log 2>&1 &
```

### Monitor Logs
```bash
# If running in background
tail -f output.log
```

### Quick Health Check
```bash
curl http://localhost:5000
# Should return HTML of home page
```

---

## 📚 Most Common Workflow

```bash
# Morning routine
cd hospital-system
venv\Scripts\activate    # Windows
# source venv/bin/activate  # macOS/Linux
python app.py

# End of day
# Ctrl+C to stop server
deactivate

# Weekly maintenance
del hospital.db          # Windows
# rm hospital.db         # macOS/Linux
python seed_data.py
python test_system.py
```

---

**Keep this file handy for quick reference!**

