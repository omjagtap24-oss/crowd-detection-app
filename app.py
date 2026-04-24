from flask import Flask, jsonify, render_template
import random

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/crowd")
def crowd():
    return jsonify({
        "crowd_level": random.choice(["Low", "Medium", "High"]),
        "location": "Temple Area",
        "suggestion": "Check timing before visiting"
    })

@app.route("/predict")
def predict():
    return jsonify({
        "best_time": "6 PM - Low Crowd",
        "advice": "Visit during evening hours"
    })

if __name__ == "__main__":
    app.run()
