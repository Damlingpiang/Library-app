from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
# Secret key is required to use session storage
app.secret_key = 'library_app_secure_key_99'

# Mock database for your Library App
# Format: { email: {password, name} }
users = {
    "admin@library.com": {"password": "admin123", "name": "Head Librarian"}
}

@app.route("/")
def home():
    # If already logged in, go to dashboard, otherwise show login page
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route("/dashboard")
def dashboard():
    # Protection: check if user is logged in
    if 'user_email' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html', name=session.get('user_name'))

# API endpoint for Login
@app.route("/api/login", methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if email in users and users[email]['password'] == password:
        session['user_email'] = email
        session['user_name'] = users[email]['name']
        return jsonify({
            "success": True, 
            "message": "Welcome back!", 
            "redirect": "/dashboard"
        })
    
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

# API endpoint for Signup
@app.route("/api/signup", methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if email in users:
        return jsonify({"success": False, "message": "User already exists"}), 400

    # Save to mock database
    users[email] = {"password": password, "name": name}
    session['user_email'] = email
    session['user_name'] = name
    
    return jsonify({
        "success": True, 
        "message": "Registration successful!", 
        "redirect": "/dashboard"
    })

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    # debug=True allows the server to reload automatically when you save changes
    app.run(debug=True)
