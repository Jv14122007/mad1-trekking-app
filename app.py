from flask import Flask, render_template

from applications.database import db
from applications.models import User, Trek, Booking
from applications.routes.auth import auth

app = Flask(
    __name__,
    template_folder="applications/templates",
    static_folder="applications/static"
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trek.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "wannatrek123"

db.init_app(app)
app.register_blueprint(auth)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)