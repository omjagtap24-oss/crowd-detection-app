from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import random
import requests

app = Flask(__name__)
app.secret_key = "secret123"

users = {}
search_history = []

# ---------------- HOME (LOGIN PAGE) ----------------
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
        session["user"] = username
        return redirect(url_for("home"))
    else:
        return "Invalid Username or Password"


# ---------------- HOME ----------------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("index.html")


# ---------------- SEARCH TEMPLE ----------------
@app.route("/search_temple")
def search_temple():
    query = request.args.get("query")

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query + " temple India",
        "format": "json",
        "limit": 5
    }

    headers = {
        "User-Agent": "PilgrimFlowApp"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    results = []

    for place in data:
        results.append({
            "name": place.get("display_name"),
            "lat": place.get("lat"),
            "lon": place.get("lon")
        })

    return jsonify(results)


# ---------------- SAVE SEARCH ----------------
@app.route("/save_search/<name>")
def save_search(name):
    if name not in search_history:
        search_history.insert(0, name)
    return "ok"


# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    return jsonify(search_history[:5])


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
    app.run(debug=True)
