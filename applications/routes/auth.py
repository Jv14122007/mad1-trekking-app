from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from applications.database import db
from applications.models import User

auth = Blueprint("auth", __name__)

# REGISTER
@auth.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username         = request.form.get("username", "").strip()
        email            = request.form.get("email", "").strip().lower()
        contact          = request.form.get("contact", "").strip()
        password         = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role             = request.form.get("role", "").strip().lower()

        # ---- Validations ----
        if not username or not email or not password or not confirm_password or not role:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        if role not in ["user", "staff"]:
            flash("Invalid role selected.", "danger")
            return redirect(url_for("auth.register"))

        if len(username) < 3:
            flash("Username must be at least 3 characters.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        if contact:
            if not contact.isdigit() or len(contact) != 10:
                flash("Enter a valid 10-digit contact number.", "danger")
                return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))

        # Staff need admin approval; users are auto-approved
        approved = (role == "user")

        try:
            new_user = User(
                username=username,
                email=email,
                contact=contact,
                password=generate_password_hash(password),
                role=role,
                approved=approved,
                is_active=True
            )
            db.session.add(new_user)
            db.session.commit()

            if role == "staff":
                flash("Registration successful! Your account is awaiting admin approval.", "success")
            else:
                flash("Registration successful! Please login.", "success")

            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            print("Registration Error:", e)
            flash("Registration failed. Please try again.", "danger")
            return redirect(url_for("auth.register"))

    return render_template("register.html")


# LOGIN
@auth.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        if not user.is_active:
            flash("Your account has been deactivated by the admin.", "danger")
            return redirect(url_for("auth.login"))

        if user.role == "staff" and not user.approved:
            flash("Your account is awaiting admin approval.", "warning")
            return redirect(url_for("auth.login"))

        # Store session
        session["user_id"]  = user.id
        session["role"]     = user.role
        session["username"] = user.username

        flash(f"Welcome, {user.username}!", "success")

        if user.role == "admin":
            return redirect(url_for("dashboard.admin_dashboard"))
        elif user.role == "staff":
            return redirect(url_for("dashboard.staff_dashboard"))
        else:
            return redirect(url_for("dashboard.user_dashboard"))

    return render_template("login.html")

# LOGOUT
@auth.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))