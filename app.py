from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "pilgrimflow_secret_key"


# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("pilgrimflow.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS searches(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        temple_name TEXT,
        searched_at TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ---------------- LOGIN PAGE ----------------
@app.route("/")
def home():
    return render_template("login.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("pilgrimflow.db")
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
    return redirect("/")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("pilgrimflow.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cur.fetchone()
    conn.close()

    if user:
        session["user"] = username
        return redirect("/dashboard")
    else:
        return "Invalid Username or Password"


# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot", methods=["POST"])
def forgot():
    username = request.form["username"]

    conn = sqlite3.connect("pilgrimflow.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT password FROM users WHERE username=?",
        (username,)
    )

    user = cur.fetchone()
    conn.close()

    if user:
        return "Your password is: " + user[0]
    else:
        return "User not found"


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template(
        "index.html",
        username=session["user"]
    )


# ---------------- SAVE SEARCH ----------------
@app.route("/search", methods=["POST"])
def search():
    if "user" not in session:
        return redirect("/")

    temple = request.form["temple"]

    conn = sqlite3.connect("pilgrimflow.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO searches(username, temple_name, searched_at)
    VALUES(?,?,?)
    """, (
        session["user"],
        temple,
        datetime.now().strftime("%d-%m-%Y %H:%M")
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------------- RECENTS ----------------
@app.route("/recents")
def recents():
    if "user" not in session:
        return jsonify([])

    conn = sqlite3.connect("pilgrimflow.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT temple_name, searched_at
    FROM searches
    WHERE username=?
    ORDER BY id DESC
    LIMIT 5
    """, (session["user"],))

    rows = cur.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            "temple": row[0],
            "time": row[1]
        })

    return jsonify(data)


# ---------------- CROWD ----------------
@app.route("/crowd/<temple>")
def crowd(temple):
    level = random.choice(["Low", "Medium", "High"])

    if level == "High":
        suggestion = "Avoid visiting now"
    elif level == "Medium":
        suggestion = "Visit after some time"
    else:
        suggestion = "Safe to visit"

    return jsonify({
        "temple": temple,
        "crowd_level": level,
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


if __name__ == "__main__":
    app.run()
