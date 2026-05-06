from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import requests
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2

app = Flask(__name__)
app.secret_key = "secret123"

users = {}
search_history = []
user_locations = []

# ---------------- TEMPLE CONFIG ----------------
temple_config = {
    "Dagdusheth Ganpati": {
        "lat": 18.5164,
        "lon": 73.8567,
        "capacity": 500,
        "peak_hours": [6,7,8,19,20,21],
        "weekend_boost": 1.5
    },
    "Shirdi Sai Baba": {
        "lat": 19.8762,
        "lon": 74.4760,
        "capacity": 2000,
        "peak_hours": list(range(5,12)) + list(range(17,22)),
        "weekend_boost": 2
    },
    "Siddhivinayak": {
        "lat": 19.0176,
        "lon": 72.8300,
        "capacity": 1000,
        "peak_hours": [6,7,8,18,19,20],
        "weekend_boost": 1.7
    },
    "Mahalaxmi": {
        "lat": 16.7000,
        "lon": 74.2333,
        "capacity": 800,
        "peak_hours": [7,8,9,18,19],
        "weekend_boost": 1.5
    }
}

# ---------------- HELPERS ----------------
def get_temple_config(name):
    name = name.lower()
    for key in temple_config:
        if key.lower() in name:
            return temple_config[key]

    return {
        "lat": 19.8762,
        "lon": 74.4760,
        "capacity": 300,
        "peak_hours": [8,9,10,18,19],
        "weekend_boost": 1.2
    }

def distance(lat1, lon1, lat2, lon2):
    R = 6373.0
    lat1, lon1 = radians(float(lat1)), radians(float(lon1))
    lat2, lon2 = radians(float(lat2)), radians(float(lon2))
    dlon, dlat = lon2 - lon1, lat2 - lat1

    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def predict_score(user_count, temple):
    config = get_temple_config(temple)

    hour = datetime.now().hour
    day = datetime.now().weekday()

    score = user_count

    if hour in config["peak_hours"]:
        score *= 1.5

    if day in [5,6]:
        score *= config["weekend_boost"]

    return score, config

# ---------------- ROUTES ----------------
@app.route("/")
def splash():
    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")

    if username in users:
        return "User already exists"

    users[username] = password
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username in users and users[username] == password:
        session["user"] = username
        return redirect("/home")
    return "Invalid Username or Password"

@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("index.html")

# ---------------- SEARCH ----------------
@app.route("/search_temple")
def search_temple():
    query = request.args.get("query")

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query + " temple India", "format": "json", "limit": 5}
    headers = {"User-Agent": "PilgrimFlowApp"}

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    return jsonify([{
        "name": place["display_name"],
        "lat": place["lat"],
        "lon": place["lon"]
    } for place in data])

# ---------------- LOCATION TRACK ----------------
@app.route("/update_location", methods=["POST"])
def update_location():
    data = request.json
    user_locations.append((data["lat"], data["lon"]))
    return jsonify({"status": "ok"})

# ---------------- CROWD ----------------
@app.route("/crowd/<temple>")
def crowd(temple):

    config = get_temple_config(temple)
    temple_lat, temple_lon = config["lat"], config["lon"]

    count = 0
    for user in user_locations:
        if distance(user[0], user[1], temple_lat, temple_lon) < 5:
            count += 1

    score, config = predict_score(count, temple)

    percent = (score / config["capacity"]) * 100

    if percent > 70:
        level = "High"
        suggestion = "Avoid visiting now"
    elif percent > 40:
        level = "Medium"
        suggestion = "Visit after some time"
    else:
        level = "Low"
        suggestion = "Safe to visit"

    return jsonify({
        "temple": temple,
        "people_count": count,
        "score": int(score),
        "capacity": config["capacity"],
        "crowd_level": level,
        "suggestion": suggestion
    })

# ---------------- HISTORY ----------------
@app.route("/save_search/<name>")
def save_search(name):
    if name not in search_history:
        search_history.insert(0, name)
    return "ok"

@app.route("/history")
def history():
    return jsonify(search_history[:5])

# ---------------- PREDICT ----------------
@app.route("/predict/<temple>")
def predict(temple):
    return jsonify({
        "temple": temple,
        "best_time": "Early morning or late evening"
    })

if __name__ == "__main__":
    app.run(debug=True)
