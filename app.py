from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = "secret123"

users = {}
search_history = []
user_locations = []

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("temples.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS temples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        capacity INTEGER,
        low INTEGER,
        medium INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
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
    return redirect("/")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username in users and users[username] == password:
        session["user"] = username
        return redirect("/home")

    return "Invalid Username or Password"

# ---------------- HOME PAGE ----------------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("index.html")

# ---------------- ADMIN PANEL ----------------
@app.route("/admin")
def admin():
    conn = sqlite3.connect("temples.db")
    cur = conn.cursor()

    cur.execute("SELECT name, capacity, low, medium FROM temples")
    rows = cur.fetchall()
    conn.close()

    data = {}
    for r in rows:
        data[r[0]] = {
            "capacity": r[1],
            "low": r[2],
            "medium": r[3]
        }

    return render_template("admin.html", data=data)

# ---------------- ADD/UPDATE TEMPLE ----------------
@app.route("/add_temple", methods=["POST"])
def add_temple():
    name = request.form.get("name").lower()
    capacity = int(request.form.get("capacity"))
    low = int(request.form.get("low"))
    medium = int(request.form.get("medium"))

    conn = sqlite3.connect("temples.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO temples (name, capacity, low, medium)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(name) DO UPDATE SET
        capacity=excluded.capacity,
        low=excluded.low,
        medium=excluded.medium
    """, (name, capacity, low, medium))

    conn.commit()
    conn.close()

    return redirect("/admin")

# ---------------- GET THRESHOLD ----------------
def get_threshold(temple_name):
    temple_name = temple_name.lower()

    conn = sqlite3.connect("temples.db")
    cur = conn.cursor()

    cur.execute("SELECT name, capacity, low, medium FROM temples")
    rows = cur.fetchall()
    conn.close()

    for r in rows:
        if r[0] in temple_name:
            return {
                "capacity": r[1],
                "low": r[2],
                "medium": r[3]
            }

    return {
        "capacity": 300,
        "low": 100,
        "medium": 200
    }

# ---------------- SEARCH ----------------
@app.route("/search_temple")
def search_temple():
    query = request.args.get("query")

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query + " temple India", "format": "json", "limit": 5}
    headers = {"User-Agent": "PilgrimFlowApp"}

    res = requests.get(url, params=params, headers=headers)
    data = res.json()

    return jsonify([{
        "name": d["display_name"],
        "lat": d["lat"],
        "lon": d["lon"]
    } for d in data])

# ---------------- SAVE LOCATION ----------------
@app.route("/update_location", methods=["POST"])
def update_location():
    data = request.json
    user_locations.append((data["lat"], data["lon"]))
    return jsonify({"status": "ok"})

# ---------------- CROWD ----------------
@app.route("/crowd/<temple>")
def crowd(temple):

    config = get_threshold(temple)

    # simulate users
    people = len(user_locations) * 5

    if people <= config["low"]:
        level = "Low"
        suggestion = "Safe to visit"
    elif people <= config["medium"]:
        level = "Medium"
        suggestion = "Visit after some time"
    else:
        level = "High"
        suggestion = "Avoid visiting now"

    return jsonify({
        "temple": temple,
        "people": people,
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

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
