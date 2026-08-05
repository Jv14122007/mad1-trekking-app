from flask import Blueprint, render_template, session, redirect, url_for, request, flash, abort
from applications.models import User, Trek, Booking
from applications.database import db
from datetime import datetime, date

dashboard = Blueprint("dashboard", __name__)

# HELPERS — access-control guards
def admin_required():
    if "user_id" not in session or session.get("role") != "admin":
        abort(403)

def staff_required():
    if "user_id" not in session or session.get("role") != "staff":
        abort(403)

def user_required():
    if "user_id" not in session or session.get("role") != "user":
        abort(403)

def login_required():
    if "user_id" not in session:
        flash("Please login to continue.", "warning")
        abort(redirect(url_for("auth.login")))

# ADMIN — Dashboard
@dashboard.route("/admin")
def admin_dashboard():
    admin_required()

    pending_staff = User.query.filter_by(role="staff", approved=False).all()

    data = {
        "total_users":    User.query.filter_by(role="user").count(),
        "total_staff":    User.query.filter_by(role="staff").count(),
        "total_treks":    Trek.query.count(),
        "total_bookings": Booking.query.count(),
        "pending_staff":  pending_staff,
        "open_treks":     Trek.query.filter_by(status="Open").count(),
        "pending_treks":  Trek.query.filter_by(status="Pending").count(),
    }

    return render_template("admin_dashboard.html", **data)

# ADMIN — Create Trek
@dashboard.route("/admin/create_trek", methods=["GET", "POST"])
def create_trek():
    admin_required()

    if request.method == "POST":
        try:
            name       = request.form.get("name", "").strip()
            location   = request.form.get("location", "").strip()
            difficulty = request.form.get("difficulty", "").strip()
            description = request.form.get("description", "").strip()

            start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
            end_date   = datetime.strptime(request.form["end_date"],   "%Y-%m-%d").date()
            slots      = int(request.form["slots"])

            # ---- Validations ----
            if not name or not location or not difficulty:
                flash("Name, location and difficulty are required.", "danger")
                return redirect(url_for("dashboard.create_trek"))

            if difficulty not in ["Easy", "Moderate", "Hard"]:
                flash("Invalid difficulty level.", "danger")
                return redirect(url_for("dashboard.create_trek"))

            if slots <= 0:
                flash("Slots must be greater than zero.", "danger")
                return redirect(url_for("dashboard.create_trek"))

            if end_date < start_date:
                flash("End date cannot be before start date.", "danger")
                return redirect(url_for("dashboard.create_trek"))

            # Auto-calculate duration
            duration = (end_date - start_date).days + 1

            trek = Trek(
                name=name,
                location=location,
                difficulty=difficulty,
                start_date=start_date,
                end_date=end_date,
                duration=duration,
                slots=slots,
                description=description,
                status="Pending"          # <-- starts as Pending, not Open
            )

            db.session.add(trek)
            db.session.commit()
            flash("Trek created successfully. Assign staff to open it for bookings.", "success")
            return redirect(url_for("dashboard.manage_treks"))

        except ValueError as ve:
            db.session.rollback()
            print("Create Trek ValueError:", ve)
            flash("Invalid date or slot value. Please check your input.", "danger")
        except Exception as e:
            db.session.rollback()
            print("Create Trek Error:", e)
            flash("Error creating trek. Please try again.", "danger")

    today = date.today().strftime("%Y-%m-%d")
    return render_template("create_trek.html", today=today)

# ADMIN — Manage Treks (with search)
@dashboard.route("/admin/treks")
def manage_treks():
    admin_required()

    search = request.args.get("search", "").strip()

    if search:
        if search.isdigit():
            treks = Trek.query.filter(
                (Trek.id == int(search)) | Trek.name.ilike(f"%{search}%")
            ).all()
        else:
            treks = Trek.query.filter(Trek.name.ilike(f"%{search}%")).all()
    else:
        treks = Trek.query.order_by(Trek.id.desc()).all()

    return render_template("manage_treks.html", treks=treks, search=search)

# ADMIN — Edit Trek
@dashboard.route("/admin/edit_trek/<int:trek_id>", methods=["GET", "POST"])
def edit_trek(trek_id):
    admin_required()

    trek = db.get_or_404(Trek, trek_id)

    if request.method == "POST":
        try:
            name       = request.form.get("name", "").strip()
            location   = request.form.get("location", "").strip()
            difficulty = request.form.get("difficulty", "").strip()
            description = request.form.get("description", "").strip()

            start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
            end_date   = datetime.strptime(request.form.get("end_date"),   "%Y-%m-%d").date()
            slots      = int(request.form.get("slots", trek.slots))
            status     = request.form.get("status", trek.status)

            # ---- Validations ----
            if not name or not location or not difficulty:
                flash("Name, location and difficulty are required.", "danger")
                return redirect(url_for("dashboard.edit_trek", trek_id=trek.id))

            if difficulty not in ["Easy", "Moderate", "Hard"]:
                flash("Invalid difficulty level.", "danger")
                return redirect(url_for("dashboard.edit_trek", trek_id=trek.id))

            if slots < 0:
                flash("Slots cannot be negative.", "danger")
                return redirect(url_for("dashboard.edit_trek", trek_id=trek.id))

            if end_date < start_date:
                flash("End date cannot be before start date.", "danger")
                return redirect(url_for("dashboard.edit_trek", trek_id=trek.id))

            if status not in ["Pending", "Open", "Closed", "Completed"]:
                flash("Invalid status.", "danger")
                return redirect(url_for("dashboard.edit_trek", trek_id=trek.id))

            # Apply updates
            trek.name        = name
            trek.location    = location
            trek.difficulty  = difficulty
            trek.description = description
            trek.start_date  = start_date
            trek.end_date    = end_date
            trek.duration    = (end_date - start_date).days + 1   # recalculate
            trek.slots       = slots
            trek.status      = status

            db.session.commit()
            flash("Trek updated successfully.", "success")
            return redirect(url_for("dashboard.manage_treks"))

        except ValueError as ve:
            db.session.rollback()
            print("Edit Trek ValueError:", ve)
            flash("Invalid date or slot value.", "danger")
        except Exception as e:
            db.session.rollback()
            print("Edit Trek Error:", e)
            flash("Error updating trek.", "danger")

    today = date.today().strftime("%Y-%m-%d")
    return render_template("edit_trek.html", trek=trek, today=today)

# ADMIN — Delete Trek
@dashboard.route("/admin/delete_trek/<int:trek_id>")
def delete_trek(trek_id):
    admin_required()

    trek = db.get_or_404(Trek, trek_id)
    db.session.delete(trek)   # cascade deletes bookings
    db.session.commit()

    flash("Trek deleted successfully.", "success")
    return redirect(url_for("dashboard.manage_treks"))

# ADMIN — Approve Staff
@dashboard.route("/admin/approve_staff/<int:user_id>")
def approve_staff(user_id):
    admin_required()

    staff = db.get_or_404(User, user_id)

    if staff.role != "staff":
        abort(400)

    staff.approved = True
    db.session.commit()

    flash(f"Staff member '{staff.username}' approved.", "success")
    return redirect(url_for("dashboard.manage_users"))

# ADMIN — Reject Staff
@dashboard.route("/admin/reject_staff/<int:user_id>")
def reject_staff(user_id):
    admin_required()

    staff = db.get_or_404(User, user_id)

    if staff.role != "staff":
        abort(400)

    db.session.delete(staff)
    db.session.commit()

    flash(f"Staff registration for '{staff.username}' rejected and removed.", "warning")
    return redirect(url_for("dashboard.manage_users"))

# ADMIN — Assign Staff to Trek
@dashboard.route("/admin/assign_staff/<int:trek_id>", methods=["GET", "POST"])
def assign_staff(trek_id):
    admin_required()

    trek         = db.get_or_404(Trek, trek_id)
    staff_members = User.query.filter_by(role="staff", approved=True, is_active=True).all()

    if request.method == "POST":
        staff_id = request.form.get("staff_id")

        if not staff_id:
            flash("Please select a staff member.", "danger")
            return redirect(url_for("dashboard.assign_staff", trek_id=trek_id))

        trek.assigned_staff_id = int(staff_id)

        # Auto-open the trek once staff is assigned (if it was Pending)
        if trek.status == "Pending":
            trek.status = "Open"

        db.session.commit()
        flash("Staff assigned. Trek is now Open for bookings.", "success")
        return redirect(url_for("dashboard.manage_treks"))

    return render_template("assign_staff.html", trek=trek, staff_members=staff_members)

# ADMIN — Manage Bookings (with search)
@dashboard.route("/admin/bookings")
def manage_bookings():
    admin_required()

    search = request.args.get("search", "").strip()

    if search:
        bookings = (
            Booking.query
            .join(User,  Booking.user_id  == User.id)
            .join(Trek,  Booking.trek_id  == Trek.id)
            .filter(
                User.username.ilike(f"%{search}%") |
                User.email.ilike(f"%{search}%")    |
                Trek.name.ilike(f"%{search}%")
            )
            .all()
        )
    else:
        bookings = Booking.query.order_by(Booking.id.desc()).all()

    return render_template("manage_bookings.html", bookings=bookings, search=search)

# ADMIN — Manage Users & Staff (with search)
@dashboard.route("/admin/users")
def manage_users():
    admin_required()

    search = request.args.get("search", "").strip()

    query = User.query
    if search:
        if search.isdigit():
            query = query.filter(
                (User.id == int(search)) | User.username.ilike(f"%{search}%")
            )
        else:
            query = query.filter(User.username.ilike(f"%{search}%"))

    users = query.order_by(User.role, User.username).all()
    return render_template("manage_users.html", users=users, search=search)


# ADMIN — Toggle User/Staff active status (blacklist/activate)
@dashboard.route("/admin/toggle_user/<int:user_id>")
def toggle_user(user_id):
    admin_required()

    user = db.get_or_404(User, user_id)

    if user.role == "admin":
        flash("Cannot deactivate the admin account.", "danger")
        return redirect(url_for("dashboard.manage_users"))

    user.is_active = not user.is_active
    db.session.commit()

    status_label = "activated" if user.is_active else "blacklisted"
    flash(f"User '{user.username}' has been {status_label}.", "success")
    return redirect(url_for("dashboard.manage_users"))

# ADMIN — Toggle Trek status (Open - Closed)
@dashboard.route("/admin/toggle_trek/<int:trek_id>")
def toggle_trek(trek_id):
    admin_required()

    trek = db.get_or_404(Trek, trek_id)

    # Do not re-open a completed trek via toggle
    if trek.status == "Completed":
        flash("Completed treks cannot be toggled.", "warning")
        return redirect(url_for("dashboard.manage_treks"))

    trek.status = "Closed" if trek.status == "Open" else "Open"
    db.session.commit()

    flash(f"Trek '{trek.name}' is now {trek.status}.", "success")
    return redirect(url_for("dashboard.manage_treks"))


# USER — Dashboard
@dashboard.route("/user")
def user_dashboard():
    user_required()

    treks    = Trek.query.filter_by(status="Open").order_by(Trek.start_date).all()
    bookings = (
        Booking.query
        .filter_by(user_id=session["user_id"])
        .order_by(Booking.booking_date.desc())
        .all()
    )

    return render_template("user_dashboard.html", treks=treks, bookings=bookings)

# USER — Edit Profile
@dashboard.route("/user/profile", methods=["GET", "POST"])
def edit_profile():
    user_required()

    user = db.get_or_404(User, session["user_id"])

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email",    "").strip().lower()
        contact  = request.form.get("contact",  "").strip()

        if not username or not email:
            flash("Username and Email are required.", "danger")
            return redirect(url_for("dashboard.edit_profile"))

        if len(username) < 3:
            flash("Username must be at least 3 characters.", "danger")
            return redirect(url_for("dashboard.edit_profile"))

        if contact:
            if not contact.isdigit() or len(contact) != 10:
                flash("Enter a valid 10-digit contact number.", "danger")
                return redirect(url_for("dashboard.edit_profile"))

        # Check uniqueness excluding current user
        if User.query.filter(User.username == username, User.id != user.id).first():
            flash("Username already taken.", "danger")
            return redirect(url_for("dashboard.edit_profile"))

        if User.query.filter(User.email == email, User.id != user.id).first():
            flash("Email already registered to another account.", "danger")
            return redirect(url_for("dashboard.edit_profile"))

        user.username = username
        user.email    = email
        user.contact  = contact
        db.session.commit()

        session["username"] = username
        flash("Profile updated successfully.", "success")
        return redirect(url_for("dashboard.user_dashboard"))

    return render_template("edit_profile.html", user=user)


# USER — Browse & Filter Treks
@dashboard.route("/user/treks")
def user_treks():
    user_required()

    difficulty = request.args.get("difficulty", "").strip()
    location   = request.args.get("location",   "").strip()

    query = Trek.query.filter_by(status="Open")

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    treks = query.order_by(Trek.start_date).all()

    # Pass user's existing bookings so the template can mark booked treks
    user_bookings = Booking.query.filter_by(user_id=session["user_id"]).all()
    booked_trek_ids = {b.trek_id for b in user_bookings}

    return render_template(
        "user_treks.html",
        treks=treks,
        booked_trek_ids=booked_trek_ids
    )

# USER — Book Trek
@dashboard.route("/user/book/<int:trek_id>", methods=["POST"])
def book_trek(trek_id):
    user_required()

    trek = db.get_or_404(Trek, trek_id)

    # Guard: must be Open AND have slots
    if trek.status != "Open":
        flash("This trek is not open for bookings.", "warning")
        return redirect(url_for("dashboard.user_treks"))

    if trek.slots <= 0:
        flash("No slots available for this trek.", "warning")
        return redirect(url_for("dashboard.user_treks"))

    # Guard: no duplicate bookings
    existing = Booking.query.filter_by(
        user_id=session["user_id"],
        trek_id=trek.id
    ).first()

    if existing:
        if existing.status == "Cancelled":
            # Allow re-booking a cancelled booking
            existing.status       = "Booked"
            existing.booking_date = date.today()
            trek.slots           -= 1
            db.session.commit()
            flash("Trek re-booked successfully!", "success")
        else:
            flash("You have already booked this trek.", "warning")
        return redirect(url_for("dashboard.user_treks"))

    booking = Booking(
        user_id=session["user_id"],
        trek_id=trek.id,
        booking_date=date.today(),
        status="Booked"
    )
    trek.slots -= 1

    # Auto-close if no slots left
    if trek.slots == 0:
        trek.status = "Closed"

    db.session.add(booking)
    db.session.commit()

    flash("Trek booked successfully!", "success")
    return redirect(url_for("dashboard.my_bookings"))

# USER — My Bookings / History
@dashboard.route("/user/bookings")
def my_bookings():
    user_required()

    bookings = (
        Booking.query
        .filter_by(user_id=session["user_id"])
        .order_by(Booking.booking_date.desc())
        .all()
    )
    return render_template("my_bookings.html", bookings=bookings)


# USER — Cancel Booking
@dashboard.route("/user/cancel_booking/<int:booking_id>")
def cancel_booking(booking_id):
    user_required()

    booking = db.get_or_404(Booking, booking_id)

    # Ownership check
    if booking.user_id != session["user_id"]:
        abort(403)

    if booking.status != "Booked":
        flash("Only active bookings can be cancelled.", "warning")
        return redirect(url_for("dashboard.my_bookings"))

    booking.status      = "Cancelled"
    booking.trek.slots += 1

    # Re-open the trek if it was auto-closed on full booking
    if booking.trek.status == "Closed" and booking.trek.slots > 0:
        booking.trek.status = "Open"

    db.session.commit()
    flash("Booking cancelled. Slot has been released.", "success")
    return redirect(url_for("dashboard.my_bookings"))


# STAFF — Dashboard
@dashboard.route("/staff")
def staff_dashboard():
    staff_required()

    treks = (
        Trek.query
        .filter_by(assigned_staff_id=session["user_id"])
        .order_by(Trek.start_date)
        .all()
    )
    return render_template("staff_dashboard.html", treks=treks)


# STAFF — Update Trek (slots + status)
@dashboard.route("/staff/update_trek/<int:trek_id>", methods=["POST"])
def update_trek(trek_id):
    staff_required()

    trek = db.get_or_404(Trek, trek_id)

    # Only the assigned staff can update
    if trek.assigned_staff_id != session["user_id"]:
        abort(403)

    slots  = request.form.get("slots",  trek.slots)
    status = request.form.get("status", trek.status)

    try:
        slots = int(slots)
    except (ValueError, TypeError):
        flash("Invalid slot value.", "danger")
        return redirect(url_for("dashboard.staff_dashboard"))

    if slots < 0:
        flash("Slots cannot be negative.", "danger")
        return redirect(url_for("dashboard.staff_dashboard"))

    if status not in ["Open", "Closed", "Completed"]:
        flash("Invalid status.", "danger")
        return redirect(url_for("dashboard.staff_dashboard"))

    trek.slots  = slots
    trek.status = status
    db.session.commit()

    flash("Trek updated successfully.", "success")
    return redirect(url_for("dashboard.staff_dashboard"))

# STAFF — View Participants for a Trek
@dashboard.route("/staff/participants/<int:trek_id>")
def view_participants(trek_id):
    staff_required()
    trek = db.get_or_404(Trek, trek_id)
    # Only the assigned staff can view
    if trek.assigned_staff_id != session["user_id"]:
        abort(403)
    bookings = (
        Booking.query
        .filter_by(trek_id=trek.id)
        .order_by(Booking.booking_date)
        .all()
    )
    return render_template("participants.html", trek=trek, bookings=bookings)
