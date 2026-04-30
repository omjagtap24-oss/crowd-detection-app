from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import random
import requests

app = Flask(__name__)
app.secret_key = "pilgrimflow_secret"


# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect("pilgrimflow.db")
    cur = conn.cursor()

    # Users Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Search History Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        temple TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- HOME / LOGIN PAGE ----------------
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


# ---------------- SEARCH TEMPLE ----------------
@app.route("/search_temple", methods=["GET"])
def search_temple():
    query = request.args.get("query")
    
    if not query:
        return jsonify([])

    # Debugging - print the search term
    print(f"Searching for temple: {query}")
    
    response = []

    # Fetch temple details from OpenStreetMap API
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={query} temple India&limit=5"
    
    # Try to get data from OpenStreetMap
    try:
        data = requests.get(url).json()

        # Debugging - print API response
        print(f"API Response: {data}")

        for place in data:
            response.append({
                "name": place["display_name"],
                "lat": place["lat"],
                "lon": place["lon"]
            })
    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify([])

    return jsonify(response)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
