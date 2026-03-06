import os
from flask import Flask, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Fix for Render Postgres URL
db_url = os.environ.get("DATABASE_URL", "sqlite:///local.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -----------------------------
# Database Model
# -----------------------------
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sapid = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

# -----------------------------
# Serve HTML
# -----------------------------
@app.route("/")
def home():
    return send_from_directory(".", "app.html")

# -----------------------------
# Form Submission
# -----------------------------
@app.route("/submit", methods=["POST"])
def submit():

    name = request.form.get("name")
    sapid = request.form.get("sapid")
    age = request.form.get("age")
    gender = request.form.get("gender")

    if not name or not sapid or not age or not gender:
        flash("All fields are required")
        return redirect(url_for("home"))

    row = Submission(
        name=name,
        sapid=sapid,
        age=int(age),
        gender=gender
    )

    db.session.add(row)
    db.session.commit()

    return redirect(url_for("home"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)