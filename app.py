from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import random
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = "pilgrimflow_secret"


# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # TEMPLE TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS temples(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        capacity INTEGER,
        low_threshold INTEGER,
        medium_threshold INTEGER
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- SPLASH / LOGIN ----------------

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

    try:
        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()

    except:
        conn.close()
        return "User already exists"

    conn.close()

    return redirect(url_for("splash"))


# ---------------- LOGIN ----------------

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
        return redirect(url_for("home"))

    return "Invalid Username or Password"


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin_login", methods=["POST"])
def admin_login():

    username = request.form.get("username")
    password = request.form.get("password")

    if username == "admin" and password == "admin123":

        session["admin"] = True

        return redirect(url_for("admin"))

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

    cur.execute("SELECT username,password FROM users")
    users = cur.fetchall()

    conn.close()

    temple_data = {}

    for t in temples:

        temple_data[t["name"]] = {
            "capacity": t["capacity"],
            "low": t["low_threshold"],
            "medium": t["medium_threshold"]
        }

    return render_template(
        "admin.html",
        data=temple_data,
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

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO temples
    (name,capacity,low_threshold,medium_threshold)
    VALUES(?,?,?,?)
    """, (name, capacity, low, medium))

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# ---------------- SEARCH TEMPLE ----------------

@app.route("/search_temple")
def search_temple():

    query = request.args.get("query")

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query + " temple India",
        "format": "json",
        "limit": 10
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


# ---------------- CROWD DETECTION ----------------

@app.route("/crowd/<temple>")
def crowd(temple):

    temple_name = temple.lower()

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM temples WHERE name LIKE ?",
        ('%' + temple_name + '%',)
    )

    temple_data = cur.fetchone()

    conn.close()

    # DEFAULT VALUES
    capacity = 300
    low_threshold = 100
    medium_threshold = 200

    if temple_data:

        capacity = temple_data["capacity"]
        low_threshold = temple_data["low_threshold"]
        medium_threshold = temple_data["medium_threshold"]

    # SIMULATED PEOPLE COUNT
    people = random.randint(0, capacity)

    # CROWD LEVEL
    if people < low_threshold:
        crowd_level = "Low"
        suggestion = "Safe to visit"

    elif people < medium_threshold:
        crowd_level = "Medium"
        suggestion = "Moderate crowd"

    else:
        crowd_level = "High"
        suggestion = "Avoid peak hours"

    score = int((people / capacity) * 100)

    return jsonify({
        "temple": temple,
        "people": people,
        "capacity": capacity,
        "score": score,
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


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
