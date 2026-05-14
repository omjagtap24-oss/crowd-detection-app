# app.py

from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify, session
import sqlite3
import requests
import random

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
        username TEXT,
        password TEXT

    )

    """)

    # TEMPLES TABLE

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


# ---------------- HOME ----------------

@app.route("/")
def splash():

    return render_template("login.html")


# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["POST"])
def signup():

    username = request.form["username"]

    password = request.form["password"]

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("""

    INSERT INTO users(username,password)
    VALUES(?,?)

    """, (username, password))

    conn.commit()

    conn.close()

    return redirect("/")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]

    password = request.form["password"]

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("""

    SELECT * FROM users
    WHERE username=? AND password=?

    """, (username, password))

    user = cur.fetchone()

    conn.close()

    if user:

        session["user"] = username

        return redirect("/home")

    return "Invalid Username or Password"


# ---------------- USER HOME ----------------

@app.route("/home")
def home():

    if "user" not in session:

        return redirect("/")

    return render_template("index.html")


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin_login", methods=["POST"])
def admin_login():

    username = request.form["username"]

    password = request.form["password"]

    # CHANGE THIS IF YOU WANT

    if username == "admin" and password == "admin123":

        session["admin"] = True

        return redirect("/admin")

    return "Invalid Admin Credentials"


# ---------------- ADMIN PANEL ----------------

@app.route("/admin")
def admin():

    if "admin" not in session:

        return redirect("/")

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("SELECT username FROM users")

    users = cur.fetchall()

    cur.execute("SELECT * FROM temples")

    temples = cur.fetchall()

    conn.close()

    return render_template(

        "admin.html",

        users=users,

        temples=temples

    )


# ---------------- ADD TEMPLE ----------------

@app.route("/add_temple", methods=["POST"])
def add_temple():

    if "admin" not in session:

        return redirect("/")

    name = request.form["name"]

    capacity = request.form["capacity"]

    low = request.form["low"]

    medium = request.form["medium"]

    radius = request.form["radius"]

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    # CHECK EXISTING

    cur.execute("""

    SELECT * FROM temples
    WHERE name=?

    """, (name,))

    existing = cur.fetchone()

    if existing:

        cur.execute("""

        UPDATE temples

        SET capacity=?,
            low_threshold=?,
            medium_threshold=?,
            radius=?

        WHERE name=?

        """, (

            capacity,
            low,
            medium,
            radius,
            name

        ))

    else:

        cur.execute("""

        INSERT INTO temples(

            name,
            capacity,
            low_threshold,
            medium_threshold,
            radius

        )

        VALUES(?,?,?,?,?)

        """, (

            name,
            capacity,
            low,
            medium,
            radius

        ))

    conn.commit()

    conn.close()

    return redirect("/admin")


# ---------------- SEARCH TEMPLE ----------------

@app.route("/search_temple")
def search_temple():

    query = request.args.get("query")

    if not query:

        return jsonify([])

    url = "https://nominatim.openstreetmap.org/search"

    params = {

        "q": query + " temple India",

        "format": "json",

        "limit": 10

    }

    headers = {

        "User-Agent": "PilgrimFlow"

    }

    try:

        response = requests.get(

            url,
            params=params,
            headers=headers,
            timeout=10

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

    except:

        return jsonify([])


# ---------------- CROWD DETECTION ----------------

@app.route("/crowd/<temple>")
def crowd(temple):

    temple_name = temple.lower()

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""

    SELECT * FROM temples
    WHERE LOWER(name) LIKE ?

    """, ('%' + temple_name + '%',))

    temple_data = cur.fetchone()

    conn.close()

    # DEFAULT VALUES

    capacity = 300
    low_threshold = 100
    medium_threshold = 200
    radius = 500

    # ADMIN VALUES

    if temple_data:

        capacity = temple_data["capacity"]

        low_threshold = temple_data["low_threshold"]

        medium_threshold = temple_data["medium_threshold"]

        radius = temple_data["radius"]

    # SIMULATED PEOPLE COUNT

    people = random.randint(0, capacity)

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

        "radius": radius,

        "score": score,

        "crowd_level": crowd_level,

        "suggestion": suggestion

    })


# ---------------- BEST TIME ----------------

@app.route("/predict/<temple>")
def predict(temple):

    times = [

        "6 AM - Peaceful Visit",
        "8 AM - Moderate Crowd",
        "2 PM - Less Waiting",
        "8 PM - Best Time"

    ]

    return jsonify({

        "temple": temple,

        "best_time": random.choice(times)

    })


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ---------------- RUN ----------------

if __name__ == "__main__":

    app.run(debug=True)
