from flask import Flask, jsonify, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# Login Page
@app.route("/")
def login():
    return render_template("login.html")

# Handle login
@app.route("/login", methods=["POST"])
def handle_login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Simple demo login (no database)
    if username == "admin" and password == "1234":
        return redirect(url_for("home"))
    else:
        return "Invalid Login"

# Main App Page
@app.route("/home")
def home():
    return render_template("index.html")

# Crowd API
@app.route("/crowd")
def crowd():
    crowd_level = random.choice(["Low", "Medium", "High"])

    if crowd_level == "High":
        suggestion = "Avoid visiting now"
    elif crowd_level == "Medium":
        suggestion = "Visit after some time"
    else:
        suggestion = "Safe to visit"

    return jsonify({
        "crowd_level": crowd_level,
        "suggestion": suggestion
    })

# Prediction API
@app.route("/predict")
def predict():
    return jsonify({
        "best_time": "6 PM - Low Crowd"
    })

if __name__ == "__main__":
    app.run()
