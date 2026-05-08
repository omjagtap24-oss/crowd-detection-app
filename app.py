from flask import Flask, render_template, request, redirect, url_for, jsonify, session
            "name": place.get("display_name"),
            "lat": place.get("lat"),
            "lon": place.get("lon")
        })

    return jsonify(results)

# ---------------- UPDATE LOCATION ----------------
@app.route("/update_location", methods=["POST"])
def update_location():

    data = request.json

    user_locations.append((data["lat"], data["lon"]))

    return jsonify({"status": "ok"})

# ---------------- CROWD ----------------
@app.route("/crowd/<temple>")
def crowd(temple):

    config = get_threshold(temple)

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

# ---------------- SAVE SEARCH ----------------
@app.route("/save_search/<name>")
def save_search(name):

    if name not in search_history:
        search_history.insert(0, name)

    return "ok"

# ---------------- HISTORY ----------------
@app.route("/history")
def history():

    return jsonify(search_history[:5])

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
