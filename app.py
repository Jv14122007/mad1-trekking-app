import os
from flask import Flask, render_template
from werkzeug.security import generate_password_hash

from applications.database import db
from applications.models import User
from applications.routes.auth import auth
from applications.routes.dashboard import dashboard

# DEFAULT ADMIN SEED
def create_default_admin():
    """Creates the pre-existing admin account if it does not exist."""
    admin = User.query.filter_by(email="admin@wannatrek.com").first()
    if not admin:
        admin = User(
            username="Admin",
            email="admin@wannatrek.com",
            password=generate_password_hash("admin123"),
            role="admin",
            approved=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("[WannaTrek] Default admin created: admin@wannatrek.com / admin123")

# APPLICATION FACTORY
def create_app():
    app = Flask(
        __name__,
        template_folder="applications/templates",
        static_folder="applications/static"
    )

    # ---- Config ----
    app.config["SQLALCHEMY_DATABASE_URI"]        = "sqlite:///trek.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Use env var in production; fallback for development only
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "wannatrek-dev-secret-2026")

    # ---- Extensions ----
    db.init_app(app)

    # ---- Blueprints ----
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)

    # ---- DB init + seed ----
    with app.app_context():
        db.create_all()
        create_default_admin()

    # ---- Home route ----
    @app.route("/")
    def home():
        return render_template("index.html")

    # ---- Error handlers ----
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404
    return app

# ENTRY POINT
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)