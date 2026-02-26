from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'library_app_secure_key_99'

CORS(app, supports_credentials=True)

# Mock database
users = {
    "admin@library.com": {"password": "admin123", "name": "Head Librarian"}
}

# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Dashboard page (PROTECTED)
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html", name=session["user"])


# Login API
@app.route("/api/login", methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if email in users and users[email]['password'] == password:
        session["user"] = users[email]["name"]   # ✅ SAVE SESSION

        return jsonify({
            "success": True,
            "message": "Welcome back!",
            "user": users[email]['name']
        })

    return jsonify({"success": False, "message": "Invalid credentials"}), 401


# Signup API
@app.route("/api/signup", methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if email in users:
        return jsonify({"success": False, "message": "User already exists"}), 400

    users[email] = {"password": password, "name": name}
    return jsonify({"success": True, "message": "Registration successful!"})


# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
