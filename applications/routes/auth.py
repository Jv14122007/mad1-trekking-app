from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from applications.database import db
from applications.models import User

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        hashed_password = generate_password_hash(password)

        if role == "staff":
            approved = False
        else:
            approved = True

        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            role=role,
            approved=approved
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("home"))
    return render_template("register.html")
@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            if user.role == "staff" and not user.approved:
                flash("Your account is waiting for admin approval.")
                return redirect(url_for("auth.login"))

            session["user_id"] = user.id
            session["role"] = user.role

            if user.role == "admin":
                return redirect(url_for("dashboard.admin_dashboard"))

            elif user.role == "staff":
                return redirect(url_for("dashboard.staff_dashboard"))

            else:
                return redirect(url_for("dashboard.user_dashboard"))

        flash("Invalid email or password")

    return render_template("login.html")