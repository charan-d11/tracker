import math
import os
from functools import wraps
from dotenv import load_dotenv

from flask import (Flask, render_template, request, jsonify,
                   session, redirect, url_for,send_from_directory)
from werkzeug.security import generate_password_hash, check_password_hash

import database as db

load_dotenv()  # Load environment variables from .env file
app = Flask(__name__)

# Required: set SECRET_KEY as an environment variable (long random string)
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is not set")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Railway serves over https, so the cookie can be marked secure there
    SESSION_COOKIE_SECURE=bool(os.environ.get("RAILWAY_ENVIRONMENT")),
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,  # 30 days
)

with app.app_context():
    db.init_db()

MAX_MEMBERS = 20


# ---------- Helpers ----------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Not logged in"}), 401
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def parse_amount(value):
    """Return a positive finite float, or None if invalid."""
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(amount) or amount <= 0:
        return None
    return round(amount, 2)


# ---------- Auth ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", error=None)

    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")

    if len(username) < 3 or len(username) > 30:
        return render_template("register.html", error="Username must be 3-30 characters")
    if len(password) < 6:
        return render_template("register.html", error="Password must be at least 6 characters")

    user_id = db.create_user(username, generate_password_hash(password))
    if user_id is None:
        return render_template("register.html", error="That username is already taken")

    session.clear()
    session.permanent = True
    session["user_id"] = user_id
    return redirect(url_for("setup"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=None)

    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")

    user = db.get_user_by_username(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Wrong username or password")

    session.clear()
    session.permanent = True
    session["user_id"] = user["id"]
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- Setup (choose members) ----------

@app.route("/setup", methods=["GET", "POST"])
@login_required
def setup():
    user_id = session["user_id"]

    if request.method == "GET":
        return render_template("setup.html", error=None,
                               existing=db.get_members(user_id))

    names = [n.strip() for n in request.form.getlist("names")]
    names = [n for n in names if n]

    if not names:
        return render_template("setup.html", error="Add at least one person",
                               existing=db.get_members(user_id))
    if len(names) > MAX_MEMBERS:
        return render_template("setup.html", error=f"Maximum {MAX_MEMBERS} people",
                               existing=db.get_members(user_id))
    if any(len(n) > 30 for n in names):
        return render_template("setup.html", error="Names must be 30 characters or less",
                               existing=db.get_members(user_id))
    if len({n.lower() for n in names}) != len(names):
        return render_template("setup.html", error="Each name must be different",
                               existing=db.get_members(user_id))

    db.save_members(user_id, names)
    return redirect(url_for("index"))


# ---------- Pages ----------

@app.route("/")
@login_required
def index():
    if not db.get_members(session["user_id"]):
        return redirect(url_for("setup"))
    return render_template("index.html")


# ---------- API ----------

@app.route("/api/members", methods=["GET"])
@login_required
def members():
    return jsonify(db.get_members(session["user_id"]))


@app.route("/api/balance", methods=["GET"])
@login_required
def balance():
    return jsonify({"balance": db.get_balance(session["user_id"])})


@app.route("/api/add_money", methods=["POST"])
@login_required
def deposit():
    data = request.get_json(silent=True) or {}
    amount = parse_amount(data.get("amount"))
    if amount is None:
        return jsonify({"error": "Invalid amount"}), 400

    user_id = session["user_id"]
    db.add_money(user_id, amount)
    return jsonify({"message": "Money added!", "balance": db.get_balance(user_id)})


@app.route("/api/add_purchase", methods=["POST"])
@login_required
def purchase():
    data = request.get_json(silent=True) or {}
    item = str(data.get("item", "")).strip()
    bought_by = data.get("bought_by")
    amount = parse_amount(data.get("amount"))

    if not item or not bought_by or data.get("amount") is None:
        return jsonify({"error": "All fields required"}), 400
    if len(item) > 100:
        return jsonify({"error": "Item name too long"}), 400
    if amount is None:
        return jsonify({"error": "Amount must be positive"}), 400

    user_id = session["user_id"]
    if bought_by not in db.get_members(user_id):
        return jsonify({"error": "Unknown person"}), 400

    if not db.add_purchase(user_id, item, amount, bought_by):
        return jsonify({"error": "Not enough money in pot!"}), 400

    return jsonify({"message": "Purchase added!", "balance": db.get_balance(user_id)})


@app.route("/api/purchases", methods=["GET"])
@login_required
def purchases():
    return jsonify(db.get_purchases(session["user_id"]))


@app.route("/api/clear_history", methods=["DELETE"])
@login_required
def clear_history():
    db.clear_purchases(session["user_id"])
    return jsonify({"message": "Purchase history cleared!"})


@app.route("/api/reset_balance", methods=["PUT"])
@login_required
def reset_balance():
    db.reset_pot(session["user_id"])
    return jsonify({"message": "Balance reset!", "balance": 0})

@app.route("/sw.js")
def service_worker():
    resp = send_from_directory(app.static_folder, "sw.js")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["Service-Worker-Allowed"] = "/"
    return resp

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)