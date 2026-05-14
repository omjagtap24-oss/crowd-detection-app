# app.py

from flask import Flask, render_template, request, redirect, jsonify, session
import sqlite3
import requests
import math
import random

app = Flask(__name__)

app.secret_key = "pilgrim_secret"


# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS temples(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        capacity INTEGER,
        low_threshold INTEGER,
        medium_threshold INTEGER,
        radius INTEGER
    )
    """)

    conn.commit()

    conn.close()


init_db()


# ---------------- LIVE GPS STORAGE ----------------

live_users = []


# ---------------- HAVERSINE DISTANCE ----------------

def haversine(lat1, lon1, lat2, lon2):

    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        +
        math.cos(phi1)
        *
        math.cos(phi2)
        *
        math.sin(dlambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ---------------- LOGIN PAGE ----------------

@app.route("/")
def splash():

    return render_template("login.html")


# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["POST"])
def signup():

    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (username, password)
    )

    conn.commit()

    conn.close()

    return redirect("/")


# ---------------- USER LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cur.fetchone()

    conn.close()

    if user:

        session["user"] = username

        return redirect("/home")

    return "Invalid Login"


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin_login", methods=["POST"])
def admin_login():

    username = request.form.get("username")
    password = request.form.get("password")

    if username == "admin" and password == "admin123":

        session["admin"] = True

        return redirect("/admin")

    return "Invalid Admin Credentials"


# ---------------- HOME ----------------

@app.route("/home")
def home():

    if "user" not in session:

        return redirect("/")

    return render_template("index.html")


# ---------------- ADMIN PANEL ----------------

@app.route("/admin")
def admin():

    if "admin" not in session:

        return redirect("/")

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("SELECT * FROM temples")

    temples = cur.fetchall()

    cur.execute("SELECT * FROM users")

    users = cur.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        temples=temples,
        users=users
    )


# ---------------- ADD TEMPLE ----------------

@app.route("/add_temple", methods=["POST"])
def add_temple():

    if "admin" not in session:

        return redirect("/")

    name = request.form.get("name").lower()

    capacity = int(request.form.get("capacity"))

    low = int(request.form.get("low"))

    medium = int(request.form.get("medium"))

    radius = int(request.form.get("radius"))

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("""
    INSERT INTO temples
    (name,capacity,low_threshold,medium_threshold,radius)

    VALUES(?,?,?,?,?)
    """, (name, capacity, low, medium, radius))

    conn.commit()

    conn.close()

    return redirect("/admin")


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
        "User-Agent": "PilgrimFlowAI"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers
    )

    data = response.json()

    results = []

    for place in data:

        results.append({
            "name": place.get("display_name"),
            "lat": place.get("lat"),
            "lon": place.get("lon")
        })

    return jsonify(results)


# ---------------- UPDATE LIVE LOCATION ----------------

@app.route("/update_location", methods=["POST"])
def update_location():

    data = request.json

    lat = data.get("lat")
    lon = data.get("lon")

    if lat and lon:

        live_users.append({
            "lat": lat,
            "lon": lon
        })

    return jsonify({
        "status": "success"
    })


# ---------------- CROWD DETECTION ----------------

@app.route("/crowd/<temple>")
def crowd(temple):

    temple_name = temple.lower()

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM temples
    WHERE name LIKE ?
    """, ('%' + temple_name + '%',))

    temple_data = cur.fetchone()

    conn.close()

    # DEFAULT VALUES

    capacity = 300
    low_threshold = 100
    medium_threshold = 200
    radius = 500

    if temple_data:

        capacity = temple_data["capacity"]
        low_threshold = temple_data["low_threshold"]
        medium_threshold = temple_data["medium_threshold"]
        radius = temple_data["radius"]

    # SEARCH TEMPLE GPS

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": temple + " temple India",
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "PilgrimFlowAI"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers
    )

    data = response.json()

    if len(data) == 0:

        return jsonify({
            "error": "Temple not found"
        })

    temple_lat = float(data[0]["lat"])
    temple_lon = float(data[0]["lon"])

    # COUNT PEOPLE INSIDE RADIUS

    people = 0

    for user in live_users:

        distance = haversine(
            temple_lat,
            temple_lon,
            float(user["lat"]),
            float(user["lon"])
        )

        if distance <= radius:

            people += 1

    # CROWD LOGIC

    if people < low_threshold:

        crowd_level = "Low"

        suggestion = "Safe to visit"

    elif people < medium_threshold:

        crowd_level = "Medium"

        suggestion = "Moderate crowd nearby"

    else:

        crowd_level = "High"

        suggestion = "Heavy crowd and traffic nearby"

    score = int((people / capacity) * 100)

    return jsonify({

        "temple": temple,

        "people": people,

        "capacity": capacity,

        "score": score,

        "radius": radius,

        "crowd_level": crowd_level,

        "suggestion": suggestion
    })


# ---------------- BEST TIME ----------------

@app.route("/predict/<temple>")
def predict(temple):

    best = random.choice([

        "5 AM - Peaceful",

        "6 AM - Low Crowd",

        "8 AM - Best Time",

        "2 PM - Moderate Crowd",

        "8 PM - Peaceful Visit"
    ])

    return jsonify({

        "temple": temple,

        "best_time": best
    })


# ---------------- RUN ----------------

if __name__ == "__main__":

    app.run(debug=True)
