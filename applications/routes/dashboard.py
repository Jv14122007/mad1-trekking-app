from flask import Blueprint, render_template, session, redirect, url_for, request
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

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings
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

@dashboard.route("/staff")
def staff_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "staff":
        return "Access Denied"

    return render_template("staff_dashboard.html")


@dashboard.route("/user")
def user_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "user":
        return "Access Denied"

    return render_template("user_dashboard.html")