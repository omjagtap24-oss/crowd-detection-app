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

    # Accept ANY username/password (for demo)
    if username and password:
        return redirect(url_for("home"))
    else:
        return "Please enter username and password"


# ---------------- MAIN APP PAGE ----------------
@app.route("/home")
def home():
    return render_template("index.html")


# ---------------- CROWD API ----------------
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


# ---------------- PREDICTION API ----------------
@app.route("/predict")
def predict():
    return jsonify({
        "best_time": "6 PM - Low Crowd"
    })


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run()
