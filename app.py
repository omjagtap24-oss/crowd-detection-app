from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import random
import requests

app = Flask(__name__)
app.secret_key = "secret123"

# Temporary storage
users = {}
search_history = []

# ---------------- SPLASH ----------------
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


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


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

    url = f"https://nominatim.openstreetmap.org/search?q={query} temple india&format=json"

    headers = {
        "User-Agent": "PilgrimFlowApp"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    results = []

    for place in data[:5]:
        results.append({
            "name": place["display_name"],
            "lat": place["lat"],
            "lon": place["lon"]
        })

    return jsonify(results)


# ---------------- SAVE SEARCH ----------------
@app.route("/save_search/<name>")
def save_search(name):
    if name not in search_history:
        search_history.insert(0, name)

    return "saved"


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
