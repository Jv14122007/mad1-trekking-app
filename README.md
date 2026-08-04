# 🥾 WannaTrek – Trekking Management Application

WannaTrek is a Flask-based Trekking Management Application developed as part of the **Modern Application Development I (MAD-1)** course.

The application provides a role-based system for managing trekking activities with three different user roles:
- Admin– Creates and manages treks, approves trek staff, assigns staff, and monitors bookings.
- Trek Staff– Views assigned treks, manages participants, and updates trek information.
- Users (Trekkers) – Browse available treks, book treks, and manage their bookings.

## Features
- User and Trek Staff Registration
- Secure Login Authentication
- Admin Approval for Trek Staff
- Trek Creation, Editing, and Deletion
- Trek Staff Assignment
- Trek Booking System
- Booking Management
- Role-Based Dashboards
- SQLite Database using SQLAlchemy ORM
- Responsive Bootstrap User Interface

## Technologies Used
- Python
- Flask
- SQLite
- SQLAlchemy
- HTML
- CSS
- Bootstrap 5
- Jinja2

## Project Structure
mad1-trekking-app/
│
├── app.py
├── requirements.txt
├── applications/
│   ├── database.py
│   ├── models.py
│   ├── routes/
│   ├── templates/
│   └── static/
└── README.md

## Default Admin Credentials
Email:
admin@wannatrek.com
Password:
admin123

## Developed For
Modern Application Development I (MAD-1)
IIT Madras BS Degree Programme