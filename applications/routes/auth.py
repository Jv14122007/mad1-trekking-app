from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from applications.database import db
from applications.models import User


auth = Blueprint("auth", __name__)


# ---------------- REGISTER ----------------

@auth.route("/register", methods=["GET", "POST"])
def register():

    # Already logged in → redirect
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        contact = request.form.get("contact", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "")

        # -------- VALIDATIONS --------

        # Empty field check
        if not username or not email or not password or not confirm_password or not role:
            flash("All fields are required.")
            return redirect(url_for("auth.register"))

        # Password match check
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("auth.register"))

        # Role validation (NO admin registration)
        if role not in ["user", "staff"]:
            flash("Invalid role selected.")
            return redirect(url_for("auth.register"))

        # Username length
        if len(username) < 3:
            flash("Username must be at least 3 characters.")
            return redirect(url_for("auth.register"))

        # Password validation
        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return redirect(url_for("auth.register"))

        # Duplicate username
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("auth.register"))

        # Duplicate email
        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("auth.register"))

        # Staff needs approval
        approved = False if role == "staff" else True

        # -------- CREATE USER --------
        try:
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                role=role,
                approved=approved
            )

            db.session.add(new_user)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print("Registration Error:", e)
            flash("Registration failed. Try again.")
            return redirect(url_for("auth.register"))

        flash("Registration successful. Please login.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------

@auth.route("/login", methods=["GET", "POST"])
def login():

    # Already logged in → redirect
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Empty validation
        if not email or not password:
            flash("All fields are required.")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            # -------- BLACKLIST CHECK (IMPORTANT FOR MARKS) --------
            if hasattr(user, "is_active") and not user.is_active:
                flash("Your account has been deactivated by admin.")
                return redirect(url_for("auth.login"))

            # -------- STAFF APPROVAL CHECK --------
            if user.role == "staff" and not user.approved:
                flash("Your account is waiting for admin approval.")
                return redirect(url_for("auth.login"))

            # -------- SESSION --------
            session["user_id"] = user.id
            session["role"] = user.role
            session["username"] = user.username

            flash("Login successful.")

            # -------- ROLE-BASED REDIRECTION --------
            if user.role == "admin":
                return redirect(url_for("dashboard.admin_dashboard"))

            elif user.role == "staff":
                return redirect(url_for("dashboard.staff_dashboard"))

            else:
                return redirect(url_for("dashboard.user_dashboard"))

        flash("Invalid email or password.")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@auth.route("/logout")
def logout():

    session.clear()
    flash("Logged out successfully.")

    return redirect(url_for("home"))