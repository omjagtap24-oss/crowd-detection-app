from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Crowd Detection App is Running!"

@app.route("/crowd")
def crowd():
    return jsonify({
        "location": "Temple Area",
        "crowd_level": "High",
        "suggestion": "Avoid visiting now"
    })

if __name__ == "__main__":
    app.run()