import os
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Fix for Render Postgres URL
db_url = os.environ.get("DATABASE_URL", "sqlite:///local.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Submission(db.Model):
    __tablename__ = "submission"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sapid = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sapid": self.sapid,
            "age": self.age,
            "gender": self.gender
        }


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return send_from_directory(".", "app.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = (request.form.get("name") or "").strip()
    sapid = (request.form.get("sapid") or "").strip()
    age = (request.form.get("age") or "").strip()
    gender = (request.form.get("gender") or "").strip()

    if not name or not sapid or not age or not gender:
        return {"message": "All fields are required"}, 400

    try:
        age_value = int(age)
        if age_value < 1 or age_value > 120:
            return {"message": "Age must be between 1 and 120"}, 400
    except ValueError:
        return {"message": "Age must be a valid number"}, 400

    row = Submission(
        name=name,
        sapid=sapid,
        age=age_value,
        gender=gender
    )

    db.session.add(row)
    db.session.commit()

    return redirect(url_for("home"))


@app.route("/search", methods=["GET"])
def search():
    name = (request.args.get("name") or "").strip()

    if not name:
        return jsonify({
            "success": False,
            "message": "Please enter a name to search",
            "results": []
        }), 400

    matches = Submission.query.filter(
        Submission.name.ilike(f"%{name}%")
    ).order_by(Submission.name.asc()).all()

    return jsonify({
        "success": True,
        "count": len(matches),
        "results": [row.to_dict() for row in matches]
    })


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
