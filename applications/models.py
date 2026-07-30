from applications.database import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    active = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.username}>"

class Trek(db.Model):
    __tablename__ = "treks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Open")
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    assigned_staff = db.relationship("User", backref="assigned_treks")

class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="Booked")
    user = db.relationship("User", backref="bookings")
    trek = db.relationship("Trek", backref="bookings")