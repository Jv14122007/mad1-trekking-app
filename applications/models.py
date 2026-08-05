from applications.database import db
# USER MODEL
class User(db.Model):
    __tablename__ = "users"
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(100), unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password     = db.Column(db.String(255), nullable=False)
    # admin / staff / user
    role         = db.Column(db.String(20), nullable=False)
    contact      = db.Column(db.String(15), nullable=True)
    # Account status — False = blacklisted
    is_active    = db.Column(db.Boolean, default=True,  nullable=False)
    # Staff must be approved by admin before they can log in
    approved     = db.Column(db.Boolean, default=False, nullable=False)
    # Relationships
    bookings = db.relationship(
        "Booking",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
    assigned_treks = db.relationship(
        "Trek",
        backref="assigned_staff",
        lazy=True,
        foreign_keys="Trek.assigned_staff_id"
    )

    def __repr__(self):
        return f"<User {self.id}: {self.username} ({self.role})>"

# TREK MODEL
class Trek(db.Model):
    __tablename__ = "treks"
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    location    = db.Column(db.String(100), nullable=False)
    # Easy / Moderate / Hard
    difficulty  = db.Column(db.String(20), nullable=False)
    # Dates
    start_date  = db.Column(db.Date, nullable=False)
    end_date    = db.Column(db.Date, nullable=False)
    # Auto-calculated from dates on save
    duration    = db.Column(db.Integer, default=1, nullable=False)
    # Available slots (decremented on booking, incremented on cancel)
    slots       = db.Column(db.Integer, nullable=False)
    # Description (optional extra info)
    description = db.Column(db.Text, nullable=True)
    # Pending / Open / Closed / Completed
    # New treks start as Pending; become Open once staff is assigned
    status      = db.Column(db.String(20), default="Pending", nullable=False)
    # FK to the staff member managing this trek
    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )
    bookings = db.relationship(
        "Booking",
        backref="trek",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Trek {self.id}: {self.name}>"

# BOOKING MODEL
class Booking(db.Model):
    __tablename__ = "bookings"
    # Prevent the same user booking the same trek twice
    __table_args__ = (
        db.UniqueConstraint("user_id", "trek_id", name="unique_booking"),
    )
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"),  nullable=False)
    trek_id      = db.Column(db.Integer, db.ForeignKey("treks.id"),  nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    # Booked / Cancelled / Completed
    status       = db.Column(db.String(20), default="Booked", nullable=False)

    def __repr__(self):
        return f"<Booking {self.id}: User={self.user_id}, Trek={self.trek_id}>"