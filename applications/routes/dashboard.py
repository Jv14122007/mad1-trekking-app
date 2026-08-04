from flask import Blueprint, render_template, session, redirect, url_for, request,flash
from applications.models import User, Trek, Booking
from datetime import datetime
from applications.database import db
dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return "Access Denied"

    total_users = User.query.filter_by(role="user").count()
    total_staff = User.query.filter_by(role="staff").count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()
    pending_staff = User.query.filter_by(role="staff", approved=False).all()


    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings,
        pending_staff=pending_staff
    )

@dashboard.route("/admin/create_trek", methods=["GET", "POST"])
def create_trek():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return "Access Denied"

    if request.method == "POST":

        trek = Trek(
            name=request.form["name"],
            location=request.form["location"],
            difficulty=request.form["difficulty"],
            date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
            slots=int(request.form["slots"])
        )

        db.session.add(trek)
        db.session.commit()

        return redirect(url_for("dashboard.admin_dashboard"))

    return render_template("create_trek.html")

@dashboard.route("/admin/treks")
def manage_treks():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return "Access Denied"

    treks = Trek.query.all()

    return render_template(
        "manage_treks.html",
        treks=treks
    )

@dashboard.route("/admin/delete_trek/<int:trek_id>")
def delete_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)
    db.session.commit()

    return redirect(url_for("dashboard.manage_treks"))

@dashboard.route("/admin/edit_trek/<int:trek_id>", methods=["GET", "POST"])
def edit_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":

        trek.name = request.form["name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.date = datetime.strptime(
            request.form["date"],
            "%Y-%m-%d"
        ).date()
        trek.slots = int(request.form["slots"])

        db.session.commit()

        return redirect(url_for("dashboard.manage_treks"))

    return render_template(
        "edit_trek.html",
        trek=trek
    )

@dashboard.route("/admin/assign_staff/<int:trek_id>", methods=["GET", "POST"])
def assign_staff(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)

    staff_members = User.query.filter_by(
        role="staff",
        approved=True
    ).all()

    if request.method == "POST":

        trek.assigned_staff_id = int(request.form["staff_id"])

        db.session.commit()

        return redirect(url_for("dashboard.manage_treks"))

    return render_template(
        "assign_staff.html",
        trek=trek,
        staff_members=staff_members
    )

@dashboard.route("/admin/approve_staff/<int:user_id>")
def approve_staff(user_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return "Access Denied"

    staff = User.query.get_or_404(user_id)

    staff.approved = True

    db.session.commit()

    return redirect(url_for("dashboard.admin_dashboard"))

@dashboard.route("/admin/bookings")
def manage_bookings():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return "Access Denied"

    bookings = Booking.query.all()

    return render_template(
        "manage_bookings.html",
        bookings=bookings
    )

@dashboard.route("/user")
def user_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "user":
        return "Access Denied"

    return render_template("user_dashboard.html")

@dashboard.route("/user/treks")
def user_treks():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "user":
        return "Access Denied"

    treks = Trek.query.filter_by(status="Open").all()

    return render_template(
        "user_treks.html",
        treks=treks
    )

@dashboard.route("/user/book/<int:trek_id>")
def book_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "user":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)
    existing_booking = Booking.query.filter_by(
        user_id=session["user_id"],
        trek_id=trek.id
    ).first()

    if existing_booking:
        flash("You have already booked this trek.")
        return redirect(url_for("dashboard.user_treks"))

    if trek.status != "Open":
        flash("Bookings are closed for this trek.")
        return redirect(url_for("dashboard.user_treks"))

    if trek.slots <= 0:
        flash("No slots available.")
    return redirect(url_for("dashboard.user_treks"))

    booking = Booking(
        user_id=session["user_id"],
        trek_id=trek.id,
        booking_date=datetime.today().date()
    )

    trek.slots -= 1

    db.session.add(booking)
    db.session.commit()

    return redirect(url_for("dashboard.user_treks"))
@dashboard.route("/user/bookings")
def my_bookings():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "user":
        return "Access Denied"

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )
@dashboard.route("/user/cancel_booking/<int:booking_id>")
def cancel_booking(booking_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "user":
        return "Access Denied"

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session["user_id"]:
        return "Access Denied"

    booking.trek.slots += 1

    db.session.delete(booking)
    db.session.commit()

    flash("Booking cancelled successfully.")

    return redirect(url_for("dashboard.my_bookings"))

@dashboard.route("/staff")
def staff_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "staff":
        return "Access Denied"

    treks = Trek.query.filter_by(
        assigned_staff_id=session["user_id"]
    ).all()

    return render_template(
        "staff_dashboard.html",
        treks=treks
    )

@dashboard.route("/staff/participants/<int:trek_id>")
def view_participants(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "staff":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != session["user_id"]:
        return "Access Denied"

    bookings = Booking.query.filter_by(trek_id=trek.id).all()

    return render_template(
        "participants.html",
        trek=trek,
        bookings=bookings
    )
@dashboard.route("/admin/toggle_trek/<int:trek_id>")
def toggle_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)

    if trek.status == "Open":
        trek.status = "Closed"
    else:
        trek.status = "Open"

    db.session.commit()

    return redirect(url_for("dashboard.manage_treks"))