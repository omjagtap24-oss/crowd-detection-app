from flask import Flask, render_template, request, redirect, url_for, jsonify
import random

app = Flask(__name__)

# Temporary user storage
users = {}

# ---------------- SPLASH SCREEN ----------------
@app.route("/")
def splash():
    return render_template("login.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")

    if username in users:
        return "User already exists"

    users[username] = password
    return redirect(url_for("splash"))


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username in users and users[username] == password:
        return redirect(url_for("home"))
    else:
        return "Invalid Username or Password"


# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot", methods=["POST"])
def forgot():
    username = request.form.get("username")

    if username in users:
        return "Your password is: " + users[username]
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
        "temple": temple,
        "crowd_level": crowd_level,
        "suggestion": suggestion
    })


# ---------------- BEST TIME ----------------
@app.route("/predict/<temple>")
def predict(temple):

    best = random.choice([
        "6 AM - Low Crowd",
        "8 AM - Best Time",
        "2 PM - Moderate Crowd",
        "8 PM - Peaceful Visit"
    ])

    return jsonify({
        "temple": temple,
        "best_time": best
    })


if __name__ == "__main__":
    app.run()   
