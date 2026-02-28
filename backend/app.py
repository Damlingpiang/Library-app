from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import psycopg2
import time
print("Server started at", time.time())
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "library_app_secure_key_99")

# Allow frontend connection
CORS(app, supports_credentials=True)

# =========================
# DATABASE CONNECTION
# =========================

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not found!")

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'user'
);
""")
conn.commit()


# =========================
# PAGE ROUTES
# =========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", name=session["user"])


@app.route("/admin")
def admin():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")
    return render_template("admin.html")


# =========================
# AUTH ROUTES
# =========================

# SIGNUP
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()

    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    if not email or not name or not password:
        return jsonify({"message": "All fields required"}), 400

    hashed_password = generate_password_hash(password)

    # Only this email becomes admin
    role = "admin" if email == "admin@library.com" else "user"

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, role)
        )
        conn.commit()

        session["user"] = name
        session["role"] = role

        return jsonify({
            "message": "Signup successful",
            "role": role
        }), 200

    except psycopg2.Error:
        conn.rollback()
        return jsonify({
            "message": "User already exists"
        }), 400


# LOGIN
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    cursor.execute(
        "SELECT name, password, role FROM users WHERE email=%s",
        (email,)
    )
    user = cursor.fetchone()

    if user and check_password_hash(user[1], password):
        session["user"] = user[0]
        session["role"] = user[2]

        return jsonify({
            "message": "Login successful",
            "role": user[2]
        }), 200

    return jsonify({
        "message": "Invalid email or password"
    }), 401


# LOGOUT
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
