from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import psycopg2

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "library_app_secure_key_99")
CORS(app, supports_credentials=True)

# 🔥 Connect PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not found!")

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

# 🔥 Create table if not exists
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
# ROUTES
# =========================

# Home
@app.route("/")
def home():
    return render_template("index.html")


# Dashboard (Protected)
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", name=session["user"])


# Admin Panel (Protected)
@app.route("/admin")
def admin():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")
    return render_template("admin.html")


# =========================
# AUTH SYSTEM
# =========================

# Signup
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()

    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    # 🔐 Hash password
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

        return jsonify({"success": True})

    except psycopg2.Error:
        return jsonify({
            "success": False,
            "message": "User already exists"
        }), 400


# Login
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

    # 🔐 Check hashed password
    if user and check_password_hash(user[1], password):
        session["user"] = user[0]
        session["role"] = user[2]

        if user[2] == "admin":
            return jsonify({"success": True, "redirect": "/admin"})
        else:
            return jsonify({"success": True, "redirect": "/dashboard"})

    return jsonify({
        "success": False,
        "message": "Invalid credentials"
    }), 401


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
