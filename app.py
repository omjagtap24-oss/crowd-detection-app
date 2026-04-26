from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import random

app = Flask(__name__)
app.secret_key = "secret123"

# Simple user storage
users = {}

# ---------------- LOGIN PAGE ----------------
@app.route("/")
def login():
    return render_template("login.html")

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")

    if username in users:
        return "User already exists. Go back."

    users[username] = password
    return redirect(url_for("login"))

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def handle_login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username in users and users[username] == password:
        return redirect(url_for("home"))
    else:
        return "Invalid username or password"

# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot", methods=["POST"])
def forgot():
    username = request.form.get("username")

    if username in users:
        return f"Your password is: {users[username]}"
    else:
        return "User not found"

# ---------------- HOME ----------------
@app.route("/home")
def home():
    return render_template("index.html")

# ---------------- CROWD ----------------
@app.route("/crowd/<temple>")
def crowd(temple):
    crowd_level = random.choice(["Low", "Medium", "High"])

    if crowd_level == "High":
        suggestion = "Avoid visiting now"
    elif crowd_level == "Medium":
        suggestion = "Visit after some time"
    else:
        suggestion = "Safe to visit"

    return jsonify({
        "temple": temple.title(),
        "crowd_level": crowd_level,
        "suggestion": suggestion
    })

# ---------------- PREDICT ----------------
@app.route("/predict/<temple>")
def predict(temple):
    times = [
        "6 AM - Low Crowd",
        "2 PM - Moderate Crowd",
        "8 PM - Low Crowd",
        "12 PM - High Crowd"
    ]

    return jsonify({
        "temple": temple.title(),
        "best_time": random.choice(times)
    })

if __name__ == "__main__":
    app.run()
