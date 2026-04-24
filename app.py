from flask import Flask, jsonify, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# ---------------- LOGIN PAGE ----------------
@app.route("/")
def login():
    return render_template("login.html")


# ---------------- HANDLE LOGIN ----------------
@app.route("/login", methods=["POST"])
def handle_login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username and password:
        return redirect(url_for("home"))
    else:
        return "Please enter username and password"


# ---------------- MAIN APP PAGE ----------------
@app.route("/home")
def home():
    return render_template("index.html")


# ---------------- TEMPLE DATA ----------------
temples_data = {
    "shirdi": "Shirdi Sai Baba",
    "tirupati": "Tirupati Balaji",
    "siddhivinayak": "Siddhivinayak Temple"
}


# ---------------- CROWD API (TEMPLE BASED) ----------------
@app.route("/crowd/<temple>")
def crowd(temple):

    temple_name = temples_data.get(temple.lower(), "Unknown Temple")

    crowd_level = random.choice(["Low", "Medium", "High"])

    if crowd_level == "High":
        suggestion = "Avoid visiting now"
    elif crowd_level == "Medium":
        suggestion = "Visit after some time"
    else:
        suggestion = "Safe to visit"

    return jsonify({
        "temple": temple_name,
        "crowd_level": crowd_level,
        "suggestion": suggestion
    })


# ---------------- GENERAL CROWD (fallback) ----------------
@app.route("/crowd")
def general_crowd():
    return crowd("shirdi")


# ---------------- BEST TIME API ----------------
@app.route("/predict/<temple>")
def predict(temple):

    temple_name = temples_data.get(temple.lower(), "Unknown Temple")

    times = [
        "6 AM - Low Crowd",
        "2 PM - Moderate Crowd",
        "8 PM - Low Crowd",
        "12 PM - High Crowd"
    ]

    return jsonify({
        "temple": temple_name,
        "best_time": random.choice(times)
    })


# ---------------- GENERAL PREDICT ----------------
@app.route("/predict")
def general_predict():
    return predict("shirdi")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run()
