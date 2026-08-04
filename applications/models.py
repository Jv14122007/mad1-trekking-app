from applications.database import db


# ---------------- USER MODEL ----------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Roles: admin / staff / user
    role = db.Column(db.String(20), nullable=False)

    contact = db.Column(db.String(15))

    # Admin blacklist control
    is_active = db.Column(db.Boolean, default=True)

    # Staff approval control
    approved = db.Column(db.Boolean, default=False)

    # Relationship: User → Bookings
    bookings = db.relationship(
        "Booking",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # Relationship: Staff → Assigned Treks
    assigned_treks = db.relationship(
        "Trek",
        backref="assigned_staff",
        lazy=True,
        foreign_keys="Trek.assigned_staff_id"
    )

    def __repr__(self):
        return f"<User {self.username}>"


# ---------------- TREK MODEL ----------------

class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    # Easy / Moderate / Hard
    difficulty = db.Column(db.String(20), nullable=False)

    duration = db.Column(db.Integer, default=1)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    # Available slots
    slots = db.Column(db.Integer, nullable=False)

    # Pending / Approved / Open / Closed / Completed
    status = db.Column(db.String(20), default="Pending")

    # Assigned staff
    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    # Relationship: Trek → Bookings
    bookings = db.relationship(
        "Booking",
        backref="trek",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Trek {self.name}>"


# ---------------- BOOKING MODEL ----------------

class Booking(db.Model):
    __tablename__ = "bookings"

    # Prevent duplicate booking by same user for same trek
    __table_args__ = (
        db.UniqueConstraint("user_id", "trek_id", name="unique_booking"),
    )

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id"),
        nullable=False
    )

    booking_date = db.Column(
        db.Date,
        nullable=False
    )

    # Booked / Cancelled / Completed
    status = db.Column(
        db.String(20),
        default="Booked"
    )

    def __repr__(self):
        return f"<Booking {self.id}>"