from flask import Flask, jsonify
import random

app = Flask(__name__)

# Home route
@app.route("/")
def home():
    return "Crowd Detection App is Running!"

# Crowd data (random for demo)
@app.route("/crowd")
def crowd():
    return jsonify({
        "crowd_level": random.choice(["Low", "Medium", "High"]),
        "location": "Temple Area",
        "suggestion": "Check timing before visiting"
    })

# Prediction feature
@app.route("/predict")
def predict():
    return jsonify({
        "best_time": "6 PM - Low Crowd",
        "advice": "Visit during evening hours"
    })

if __name__ == "__main__":
    app.run()