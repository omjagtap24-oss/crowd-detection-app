from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "pilgrimflow"

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
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        temple TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN PAGE ----------------
@app.route('/')
def home():
    return render_template("login.html")

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect("pilgrimflow.db")
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users(username,password) VALUES (?,?)",
                    (username,password))
        conn.commit()
    except:
        conn.close()
        return "Username already exists"

    conn.close()
    return redirect('/')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect("pilgrimflow.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                (username,password))

    user = cur.fetchone()
    conn.close()

    if user:
        session['user'] = username
        return redirect('/dashboard')
    else:
        return "Invalid Login"

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template("index.html", username=session['user'])

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- SAVE SEARCH ----------------
@app.route('/save_search/<temple>')
def save_search(temple):
    if 'user' not in session:
        return jsonify([])

    username = session['user']

    conn = sqlite3.connect("pilgrimflow.db")
    cur = conn.cursor()

    cur.execute("INSERT INTO history(username, temple) VALUES (?,?)",
                (username, temple))

    conn.commit()
    conn.close()

    return jsonify({"status":"saved"})

# ---------------- GET HISTORY ----------------
@app.route('/history')
def history():
    if 'user' not in session:
        return jsonify([])

    username = session['user']

    conn = sqlite3.connect("pilgrimflow.db")
    cur = conn.cursor()

    cur.execute("SELECT temple FROM history WHERE username=? ORDER BY id DESC LIMIT 5",
                (username,))
    data = cur.fetchall()

    conn.close()

    return jsonify([x[0] for x in data])

# ---------------- CROWD ----------------
@app.route('/crowd/<temple>')
def crowd(temple):
    level = random.choice(["Low", "Medium", "High"])

    suggestion = {
        "Low":"Good time to visit",
        "Medium":"Moderate rush",
        "High":"Avoid peak hours"
    }

    return jsonify({
        "temple": temple,
        "crowd_level": level,
        "suggestion": suggestion[level]
    })

# ---------------- BEST TIME ----------------
@app.route('/predict/<temple>')
def predict(temple):
    return jsonify({
        "temple": temple,
        "best_time": "6 AM to 9 AM"
    })

# ---------------- ADMIN PANEL ----------------
@app.route('/admin')
def admin():

    conn = sqlite3.connect("pilgrimflow.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    cur.execute("SELECT * FROM history")
    history = cur.fetchall()

    conn.close()

    return render_template("admin.html",
                           users=users,
                           history=history)

if __name__ == "__main__":
    app.run(debug=True)
