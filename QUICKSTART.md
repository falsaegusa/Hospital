# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Seed the Database
```bash
python seed_data.py
```

### Step 3: Run the Application
```bash
python app.py
```

Visit: **http://localhost:5000**

## 🔐 Login Credentials

### Admin
- Email: `admin@hospital.com`
- Password: `admin123`

### Doctor (any of these)
- Email: `robert.anderson@hospital.com`
- Password: `doctor123`

### Patient (any of these)
- Email: `john@email.com`
- Password: `patient123`

## ✅ Test These Features

### As a Patient:
1. Login with patient credentials
2. Click "Book Appointment"
3. Select a doctor, date, and time
4. View your appointments
5. Try cancelling an appointment

### As a Doctor:
1. Login with doctor credentials
2. View today's appointments
3. Go to "Availability"
4. Set your working hours
5. Mark appointments as complete

### As an Admin:
1. Login with admin credentials
2. View system statistics
3. Check all appointments
4. Manage rooms and equipment
5. Generate reports

## 📋 Common Tasks

### Reset Database
```bash
# Delete the database file
rm hospital.db  # On Windows: del hospital.db

# Re-run seed script
python seed_data.py
```

### Change Port
Edit the last line in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### View SQL Queries
Check console output - SQL queries are printed (SQLALCHEMY_ECHO = True)

## 🐛 Troubleshooting

**Problem**: Can't login
- **Solution**: Make sure you ran `seed_data.py` first

**Problem**: Port 5000 already in use
- **Solution**: Change port in `app.py` (last line)

**Problem**: Import errors
- **Solution**: `pip install -r requirements.txt --force-reinstall`

**Problem**: Database errors
- **Solution**: Delete `hospital.db` and run `seed_data.py` again

## 📚 Next Steps

- Read `README.md` for complete documentation
- Explore all routes in `app.py`
- Check database models in `models.py`
- Review business logic in `utils.py`

---

**Need Help?** Check the console output for detailed error messages and SQL queries.

