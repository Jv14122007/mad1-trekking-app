# WannaTrek — Trekking Management Application

A Flask/SQLite web application for managing trekking activities with role-based access for Admin, Trek Staff, and Trekkers (Users).

## Quick Start
# 1. Install dependencies
pip install -r requirements.txt
# 2. Run the application
python app.py
Visit: http://127.0.0.1:5000

## Default Admin Credentials

| Field    | Value                  |
|----------|------------------------|
| Email    | admin@wannatrek.com    |
| Password | admin123               |

The admin account is created automatically on first run. No manual DB setup required.

## Roles

| Role       | Access                                              |
|------------|-----------------------------------------------------|
| Admin      | Full control — treks, users, staff, bookings        |
| Trek Staff | Self-register (needs admin approval) — manage assigned treks |
| User       | Self-register — browse, book, and cancel treks      |


## Folder Structure
trekking-app/
├── app.py                        # App factory + entry point
├── requirements.txt
├── instance/
│   └── trek.db                   # SQLite DB (auto-created)
└── applications/
    ├── database.py               # SQLAlchemy instance
    ├── models.py                 # User, Trek, Booking models
    ├── routes/
    │   ├── auth.py               # Register / Login / Logout
    │   └── dashboard.py          # All role-based routes
    ├── static/
    │   ├── css/style.css
    │   └── images/Hill.jpeg
    └── templates/
        ├── base.html
        ├── index.html
        ├── login.html / register.html
        ├── admin_dashboard.html
        ├── manage_treks.html / create_trek.html / edit_trek.html
        ├── assign_staff.html
        ├── manage_users.html
        ├── manage_bookings.html
        ├── staff_dashboard.html
        ├── participants.html
        ├── user_dashboard.html
        ├── user_treks.html
        ├── my_bookings.html
        ├── edit_profile.html
        ├── 403.html / 404.html


## Tech Stack
- **Backend:** Flask 3.0, Flask-SQLAlchemy 3.1
- **Database:** SQLite (programmatically created via `db.create_all()`)
- **Frontend:** Jinja2, Bootstrap 5.3, Bootstrap Icons
- **Auth:** Session-based with Werkzeug password hashing