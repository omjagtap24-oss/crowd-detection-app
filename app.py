from flask import Flask, jsonify, render_template
import random

app = Flask(__name__)

# Home page (UI)
@app.route("/")
def home():
    return render_template("index.html")

# Crowd API with smart suggestion
@app.route("/crowd")
def crowd():
    crowd_level = random.choice(["Low", "Medium", "High"])

    if crowd_level == "High":
        suggestion = "Avoid visiting now"
    elif crowd_level == "Medium":
        suggestion = "Visit after some time"
    else:
        suggestion = "Safe to visit"

    return jsonify({
        "crowd_level": crowd_level,
        "location": "Temple Area",
        "suggestion": suggestion
    })

# Prediction API
@app.route("/predict")
def predict():
    return jsonify({
        "best_time": "6 PM - Low Crowd",
        "advice": "Visit during evening hours"
    })

if __name__ == "__main__":
    app.run()
