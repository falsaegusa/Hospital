# Hospital Appointment and Resource Scheduling System

A comprehensive backend system for managing hospital appointments, doctor schedules, and resource allocation using Python Flask and SQLite.

## 🎯 Features

### Core Functionality
- **User Authentication**: Role-based access control (Patient, Doctor, Admin)
- **Appointment Management**: Book, view, cancel, and reschedule appointments
- **Doctor Availability**: Set weekly schedules and block specific dates
- **Resource Management**: Track rooms and medical equipment
- **Notification System**: In-app notifications for appointment events
- **Admin Dashboard**: Comprehensive management and reporting tools

### Business Logic Implemented
- ✅ Prevent double-booking (same doctor, same time)
- ✅ Prevent patient from booking multiple appointments at same time
- ✅ Validate appointment dates (no past dates, max 90 days ahead)
- ✅ Validate appointment times (only during doctor's working hours)
- ✅ Auto-generate 30-minute time slots based on availability
- ✅ Automatic room assignment when available
- ✅ Minimum 2-hour cancellation notice requirement
- ✅ Atomic transactions for rescheduling operations
- ✅ Automatic notification creation for all appointment events

## 📋 Requirements

- Python 3.8+
- Flask 2.3.3
- SQLite 3

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd hospital-system

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database

The database will be automatically created when you first run the application:

```bash
python app.py
```

This will create `hospital.db` in the project root.

### 3. Seed Test Data

Populate the database with test users and sample data:

```bash
python seed_data.py
```

This creates:
- 1 Admin user
- 10 Patient users
- 5 Doctor users with profiles
- 5 Hospital rooms
- 10 Equipment items
- 20 Sample appointments (10 past, 10 upcoming)
- Sample notifications

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## 🔐 Test Credentials

### Admin Account
- **Email**: `admin@hospital.com`
- **Password**: `admin123`

### Doctor Accounts (Password: `doctor123`)
- `robert.anderson@hospital.com` - Cardiology
- `jennifer.white@hospital.com` - Pediatrics
- `william.harris@hospital.com` - Orthopedics
- `maria.garcia@hospital.com` - Dermatology
- `james.miller@hospital.com` - Neurology

### Patient Accounts (Password: `patient123`)
- `john@email.com` - John Smith
- `sarah@email.com` - Sarah Johnson
- `michael@email.com` - Michael Brown
- `emily@email.com` - Emily Davis
- `david@email.com` - David Wilson
- ... and 5 more patients

## 📁 Project Structure

```
hospital-system/
├── app.py                      # Main Flask application with all routes
├── models.py                   # Database models (8 models)
├── forms.py                    # WTForms form definitions
├── config.py                   # Application configuration
├── utils.py                    # Helper functions and business logic
├── decorators.py               # Custom decorators (role_required)
├── seed_data.py                # Database seeding script
├── requirements.txt            # Python dependencies
├── hospital.db                 # SQLite database (auto-generated)
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── index.html             # Home page
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── patient/
│   │   ├── dashboard.html
│   │   ├── book_appointment.html
│   │   ├── appointments.html
│   │   ├── reschedule.html
│   │   └── profile.html
│   ├── doctor/
│   │   ├── dashboard.html
│   │   ├── appointments.html
│   │   ├── availability.html
│   │   └── profile.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── appointments.html
│   │   ├── users.html
│   │   ├── doctors.html
│   │   ├── rooms.html
│   │   ├── equipment.html
│   │   └── reports.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
└── static/
    └── css/
        └── style.css          # Empty (no styling per requirements)
```

## 🛣️ API Routes

### Authentication Routes
- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Patient Routes
- `GET /patient/dashboard` - View upcoming appointments
- `GET /patient/book-appointment` - Show booking form
- `POST /patient/book-appointment` - Process booking
- `GET /patient/appointments` - View all appointments
- `POST /patient/cancel-appointment/<id>` - Cancel appointment
- `GET /patient/reschedule/<id>` - Show reschedule form
- `POST /patient/reschedule/<id>` - Process reschedule
- `GET/POST /patient/profile` - View/edit profile

### Doctor Routes
- `GET /doctor/dashboard` - View today's appointments
- `GET /doctor/appointments` - View all appointments
- `GET/POST /doctor/availability` - Manage availability
- `POST /doctor/complete-appointment/<id>` - Mark appointment complete
- `GET/POST /doctor/profile` - View/edit profile

### Admin Routes
- `GET /admin/dashboard` - Overview statistics
- `GET /admin/appointments` - View all appointments (with filters)
- `GET /admin/users` - Manage users
- `GET /admin/doctors` - Manage doctor profiles
- `POST /admin/add-doctor` - Create doctor profile
- `GET/POST /admin/rooms` - Manage rooms
- `GET/POST /admin/equipment` - Manage equipment
- `GET /admin/reports` - Generate reports (daily/weekly/monthly)

### API Routes
- `GET /api/available-slots?doctor_id=X&date=Y` - Get available time slots
- `GET /api/doctors?department=X` - Get doctors by department
- `POST /api/mark-notification-read/<id>` - Mark notification as read

## 🗄️ Database Models

### 1. User Model
Base model for all users (patients, doctors, admins)
- Authentication fields (email, password_hash)
- Personal information (name, phone, DOB, gender, address)
- Role-based access control
- Timestamps (created_at, updated_at)

### 2. Doctor Model
Extended profile for doctor users
- Specialization, license number, experience
- Consultation fee, department
- Relationships to availability and appointments

### 3. Appointment Model
Core appointment data
- Patient and doctor references
- Date, time, and status
- Reason for visit and notes
- Optional room assignment

### 4. DoctorAvailability Model
Weekly recurring availability schedule
- Day of week (Monday-Sunday)
- Start and end times
- Availability flag

### 5. TimeSlot Model
Individual time slots for appointments
- Doctor and date references
- Start and end times
- Booking status

### 6. Room Model
Hospital room management
- Room number, type (consultation/operation/emergency)
- Floor, capacity
- Availability status

### 7. Equipment Model
Medical equipment tracking
- Name, type, serial number
- Room assignment (nullable)
- Status (available/in-use/maintenance)

### 8. Notification Model
In-app notifications
- User reference
- Message and type
- Read status
- Timestamp

## 🔒 Security Features

- **Password Hashing**: Using Werkzeug's secure password hashing
- **CSRF Protection**: Enabled on all forms via Flask-WTF
- **Session Management**: Flask-Login for secure session handling
- **Role-Based Access Control**: Custom decorators enforce permissions
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries

## ✅ Testing the System

### Test Workflow 1: Patient Booking Flow
1. Register as a new patient or login with test credentials
2. Navigate to "Book Appointment"
3. Select a doctor, date, and time
4. Submit the form
5. Verify appointment appears in dashboard
6. Test cancellation (must be >2 hours away)
7. Test rescheduling

### Test Workflow 2: Doctor Availability
1. Login as a doctor
2. Navigate to "Availability"
3. Set working hours for different days
4. Verify time slots are generated correctly
5. Check that patients can only book during these hours

### Test Workflow 3: Admin Management
1. Login as admin
2. View system statistics on dashboard
3. Filter appointments by status/date
4. Manage rooms and equipment
5. Generate daily/weekly/monthly reports

### Validation Tests
- ✅ Try booking past date (should fail)
- ✅ Try booking same slot twice (should fail)
- ✅ Try booking outside doctor's hours (should fail)
- ✅ Try cancelling appointment <2 hours before (should fail)
- ✅ Verify notifications are created on booking/cancellation
- ✅ Verify rooms are auto-assigned when available

## 🐛 Known Limitations

1. **No Email Notifications**: Currently only in-app notifications
2. **No Payment Processing**: Consultation fees are tracked but not processed
3. **No File Uploads**: No support for medical records or documents
4. **Basic Time Zone Handling**: All times stored in UTC
5. **No Appointment Reminders**: No automated reminder system
6. **Simple Search**: No advanced search or filtering on frontend
7. **No Calendar View**: Appointments displayed in table format only
8. **No Real-time Updates**: Requires page refresh to see changes

## 🔧 Configuration

Edit `config.py` to modify:

- `SECRET_KEY`: Change for production
- `APPOINTMENT_ADVANCE_BOOKING_DAYS`: Max days ahead for booking (default: 90)
- `APPOINTMENT_CANCELLATION_HOURS`: Minimum hours before appointment to cancel (default: 2)
- `DEFAULT_APPOINTMENT_DURATION`: Duration in minutes (default: 30)
- `BUSINESS_HOURS_START`: Start of business day (default: 9)
- `BUSINESS_HOURS_END`: End of business day (default: 17)

## 📝 Development Notes

### Adding New Features

**To add a new user role:**
1. Update `User.role` field in `models.py`
2. Create role-specific routes in `app.py`
3. Add `@role_required('new_role')` decorator
4. Create templates in `templates/new_role/`

**To add new appointment statuses:**
1. Update status field validation in models
2. Update forms and templates to handle new status
3. Add business logic in utils.py if needed

### Database Migrations

For schema changes:
1. Delete `hospital.db`
2. Run `python app.py` to recreate database
3. Run `python seed_data.py` to repopulate data

## 🔍 Troubleshooting

### Database Issues
```bash
# Reset database
rm hospital.db
python app.py
python seed_data.py
```

### Port Already in Use
```bash
# Change port in app.py (last line):
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### CSRF Token Errors
- Ensure `{{ form.hidden_tag() }}` is in all forms
- Check `WTF_CSRF_ENABLED = True` in config.py

## 📚 Technology Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite 3
- **ORM**: SQLAlchemy 3.0.5
- **Authentication**: Flask-Login 0.6.3
- **Forms**: Flask-WTF 1.1.1, WTForms 3.0.1
- **Validation**: Email-validator 2.0.0
- **Password Hashing**: Werkzeug 2.3.7

## 📄 License

This project is for educational purposes.

## 👨‍💻 Development

- **Debug Mode**: Enabled by default
- **SQL Echo**: Enabled for query debugging
- **Error Handling**: Comprehensive try-catch blocks with rollback
- **Validation**: Server-side validation on all forms
- **Code Style**: Follows PEP 8 guidelines

## 🎓 Learning Outcomes

This project demonstrates:
- RESTful API design principles
- Database relationship management
- Business logic implementation
- Form validation and security
- Role-based access control
- Transaction management
- Error handling best practices
- Template inheritance in Jinja2

## 📞 Support

For issues or questions:
1. Check the console output for SQL queries and errors
2. Verify test credentials are correct
3. Ensure database is properly seeded
4. Check browser console for any client-side errors

---

**Happy Coding! 🏥**

