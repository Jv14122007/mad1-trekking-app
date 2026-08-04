from flask import Blueprint, render_template, session, redirect, url_for, request, flash, abort
from applications.models import User, Trek, Booking
from applications.database import db
from datetime import datetime, date


dashboard = Blueprint("dashboard", __name__)


# ---------------- HELPER ----------------

def admin_required():
    if "user_id" not in session or session.get("role") != "admin":
        abort(403)

def staff_required():
    if "user_id" not in session or session.get("role") != "staff":
        abort(403)

def user_required():
    if "user_id" not in session or session.get("role") != "user":
        abort(403)


# ---------------- ADMIN DASHBOARD ----------------

@dashboard.route("/admin")
def admin_dashboard():

    admin_required()

    data = {
        "total_users": User.query.filter_by(role="user").count(),
        "total_staff": User.query.filter_by(role="staff").count(),
        "total_treks": Trek.query.count(),
        "total_bookings": Booking.query.count(),
        "pending_staff": User.query.filter_by(role="staff", approved=False).all()
    }

    return render_template("admin_dashboard.html", **data)


# ---------------- CREATE TREK ----------------

@dashboard.route("/admin/create_trek", methods=["GET", "POST"])
def create_trek():

    admin_required()

    if request.method == "POST":

        try:
            name = request.form.get("name", "").strip()
            location = request.form.get("location", "").strip()
            difficulty = request.form.get("difficulty", "")
            start_date_value = request.form.get("start_date")
            end_date_value = request.form.get("end_date")

            if not start_date_value or not end_date_value:
                flash("Please select start date and end date.")
                return redirect(url_for("dashboard.create_trek"))

            start_date = datetime.strptime(
                start_date_value,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                end_date_value,
                "%Y-%m-%d"
            ).date()
            slots = int(request.form.get("slots", 0))

            if not name or not location or slots <= 0:
                flash("Invalid input.")
                return redirect(url_for("dashboard.create_trek"))

            trek = Trek(
                name=name,
                location=location,
                difficulty=difficulty,
                start_date=start_date,
                end_date=end_date,
                slots=slots,
                status="Pending"
            )

            db.session.add(trek)
            db.session.commit()

            flash("Trek created successfully.")
            return redirect(url_for("dashboard.manage_treks"))

        except Exception as e:
            db.session.rollback()
            print("Create Trek Error:", e)
            flash("Error creating trek.")

    return render_template("create_trek.html")


# ---------------- MANAGE TREKS ----------------

@dashboard.route("/admin/treks")
def manage_treks():

    admin_required()

    search = request.args.get("search", "")
    if search:
        treks = Trek.query.filter(Trek.name.contains(search)).all()
    else:
        treks = Trek.query.all()

    return render_template("manage_treks.html", treks=treks)


# ---------------- EDIT TREK ----------------

@dashboard.route("/admin/edit_trek/<int:trek_id>", methods=["GET", "POST"])
def edit_trek(trek_id):

    admin_required()

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":

        try:
            trek.name = request.form.get("name", trek.name)
            trek.location = request.form.get("location", trek.location)
            trek.difficulty = request.form.get("difficulty", trek.difficulty)
            trek.start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
            trek.end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
            trek.slots = int(request.form.get("slots", trek.slots))
            trek.status = request.form.get("status", trek.status)

            db.session.commit()

            flash("Trek updated.")
            return redirect(url_for("dashboard.manage_treks"))

        except Exception as e:
            db.session.rollback()
            print("Edit Trek Error:", e)
            flash("Error updating trek.")

    return render_template("edit_trek.html", trek=trek)


# ---------------- DELETE TREK ----------------

@dashboard.route("/admin/delete_trek/<int:trek_id>")
def delete_trek(trek_id):

    admin_required()

    trek = Trek.query.get_or_404(trek_id)

    Booking.query.filter_by(trek_id=trek.id).delete()
    db.session.delete(trek)
    db.session.commit()

    flash("Trek deleted.")
    return redirect(url_for("dashboard.manage_treks"))


# ---------------- STAFF APPROVAL ----------------

@dashboard.route("/admin/approve_staff/<int:user_id>")
def approve_staff(user_id):

    admin_required()

    staff = User.query.get_or_404(user_id)

    if staff.role != "staff":
        abort(400)

    staff.approved = True
    db.session.commit()

    flash("Staff approved.")
    return redirect(url_for("dashboard.admin_dashboard"))


# ---------------- ASSIGN STAFF ----------------

@dashboard.route("/admin/assign_staff/<int:trek_id>", methods=["GET", "POST"])
def assign_staff(trek_id):

    admin_required()

    trek = Trek.query.get_or_404(trek_id)
    staff_members = User.query.filter_by(role="staff", approved=True).all()

    if request.method == "POST":

        trek.assigned_staff_id = int(request.form.get("staff_id"))
        trek.status = "Open"

        db.session.commit()

        flash("Staff assigned.")
        return redirect(url_for("dashboard.manage_treks"))

    return render_template("assign_staff.html", trek=trek, staff_members=staff_members)


# ---------------- BOOKINGS ADMIN ----------------

@dashboard.route("/admin/bookings")
def manage_bookings():

    admin_required()

    bookings = Booking.query.all()
    return render_template("manage_bookings.html", bookings=bookings)


# ---------------- BLACKLIST USER/STAFF ----------------

@dashboard.route("/admin/toggle_user/<int:user_id>")
def toggle_user(user_id):

    admin_required()

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active

    db.session.commit()

    flash("User status updated.")
    return redirect(url_for("dashboard.admin_dashboard"))


# ---------------- USER DASHBOARD ----------------

@dashboard.route("/user")
def user_dashboard():

    user_required()

    treks = Trek.query.filter_by(status="Open").all()
    bookings = Booking.query.filter_by(user_id=session["user_id"]).all()

    return render_template("user_dashboard.html", treks=treks, bookings=bookings)


# ---------------- USER TREKS ----------------

@dashboard.route("/user/treks")
def user_treks():

    user_required()

    difficulty = request.args.get("difficulty")
    location = request.args.get("location")

    query = Trek.query.filter_by(status="Open")

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    if location:
        query = query.filter(Trek.location.contains(location))

    treks = query.all()

    return render_template("user_treks.html", treks=treks)


# ---------------- BOOK TREK ----------------

@dashboard.route("/user/book/<int:trek_id>", methods=["POST"])
def book_trek(trek_id):

    user_required()

    trek = Trek.query.get_or_404(trek_id)

    if trek.status != "Open" or trek.slots <= 0:
        flash("No slots available.")
        return redirect(url_for("dashboard.user_treks"))

    existing = Booking.query.filter_by(
        user_id=session["user_id"],
        trek_id=trek.id
    ).first()

    if existing:
        flash("Already booked.")
        return redirect(url_for("dashboard.user_treks"))

    booking = Booking(
        user_id=session["user_id"],
        trek_id=trek.id,
        booking_date=date.today(),
        status="Booked"
    )

    trek.slots -= 1

    db.session.add(booking)
    db.session.commit()

    flash("Trek booked successfully.")
    return redirect(url_for("dashboard.user_treks"))


# ---------------- USER BOOKINGS ----------------

@dashboard.route("/user/bookings")
def my_bookings():

    user_required()

    bookings = Booking.query.filter_by(user_id=session["user_id"]).all()
    return render_template("my_bookings.html", bookings=bookings)


# ---------------- CANCEL BOOKING ----------------

@dashboard.route("/user/cancel_booking/<int:booking_id>")
def cancel_booking(booking_id):

    user_required()

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session["user_id"]:
        abort(403)

    booking.trek.slots += 1
    booking.status = "Cancelled"

    db.session.commit()

    flash("Booking cancelled.")
    return redirect(url_for("dashboard.my_bookings"))


# ---------------- STAFF DASHBOARD ----------------

@dashboard.route("/staff")
def staff_dashboard():

    staff_required()

    treks = Trek.query.filter_by(assigned_staff_id=session["user_id"]).all()

    return render_template("staff_dashboard.html", treks=treks)


# ---------------- UPDATE TREK BY STAFF ----------------

@dashboard.route("/staff/update_trek/<int:trek_id>", methods=["POST"])
def update_trek(trek_id):

    staff_required()

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != session["user_id"]:
        abort(403)

    trek.slots = int(request.form.get("slots", trek.slots))
    trek.status = request.form.get("status", trek.status)

    db.session.commit()

    flash("Trek updated.")
    return redirect(url_for("dashboard.staff_dashboard"))


# ---------------- VIEW PARTICIPANTS ----------------

@dashboard.route("/staff/participants/<int:trek_id>")
def view_participants(trek_id):

    staff_required()

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != session["user_id"]:
        abort(403)

    bookings = Booking.query.filter_by(trek_id=trek.id).all()

    return render_template("participants.html", trek=trek, bookings=bookings)


# ---------------- TREK STATUS TOGGLE ----------------

@dashboard.route("/admin/toggle_trek/<int:trek_id>")
def toggle_trek(trek_id):

    admin_required()

    trek = Trek.query.get_or_404(trek_id)

    trek.status = "Open" if trek.status != "Open" else "Closed"

    db.session.commit()

    flash("Trek status updated.")
    return redirect(url_for("dashboard.manage_treks"))