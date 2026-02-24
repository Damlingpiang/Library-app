from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS # Import CORS

app = Flask(__name__)
app.secret_key = 'library_app_secure_key_99'

# Enable CORS so your frontend can talk to this Render URL
CORS(app, supports_credentials=True)

# Mock database
users = {
    "admin@library.com": {"password": "admin123", "name": "Head Librarian"}
}

@app.route("/")
def home():
    return jsonify({"status": "Library App Backend Running Successfully!"})

@app.route("/api/login", methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if email in users and users[email]['password'] == password:
        return jsonify({
            "success": True, 
            "message": "Welcome back!", 
            "user": users[email]['name']
        })
    
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

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

if __name__ == "__main__":
    app.run()
