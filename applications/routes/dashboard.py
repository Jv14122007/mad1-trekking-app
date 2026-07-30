from flask import Blueprint, render_template, session, redirect, url_for

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return "Access Denied"

    return render_template("admin_dashboard.html")


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