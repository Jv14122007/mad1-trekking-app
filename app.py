from flask import Flask, render_template
from werkzeug.security import generate_password_hash

from applications.database import db
from applications.models import User
from applications.routes.auth import auth
from applications.routes.dashboard import dashboard


def create_app():

    app = Flask(
        __name__,
        template_folder="applications/templates",
        static_folder="applications/static"
    )


    # CONFIG
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trek.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "wannatrek123"


    # INIT DATABASE
    db.init_app(app)


    # REGISTER BLUEPRINTS
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)


    # CREATE DATABASE + DEFAULT ADMIN
    with app.app_context():

        db.create_all()


        admin = User.query.filter_by(
            email="admin@wannatrek.com"
        ).first()


        if admin is None:

            admin = User(
                username="Admin",
                email="admin@wannatrek.com",
                password=generate_password_hash(
                    "admin123"
                ),
                role="admin",
                approved=True,
                is_active=True
            )

            db.session.add(admin)
            db.session.commit()



    @app.route("/")
    def home():

        return render_template(
            "index.html"
        )


    return app



if __name__ == "__main__":

    app = create_app()

    app.run(debug=True)