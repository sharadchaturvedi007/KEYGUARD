from analytics import get_analytics
from flask import Flask, request, jsonify, send_from_directory
from detection import analyze_activity
from database import (
    initialize_database,
    save_event,
    get_history,
    save_assessment,
    get_assessment_history
)

import uuid

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)

initialize_database()


@app.route("/")
def home():
    return send_from_directory(
        app.static_folder,
        "index.html"
    )


@app.route("/api/status")
def status():

    return jsonify({
        "application": "KEYGUARD",
        "status": "Online",
        "backend": "Connected",
        "database": "Connected"
    })


@app.route("/api/events", methods=["POST"])
def record_event():

    data = request.get_json(silent=True) or {}

    category = data.get("category")
    session_id = data.get("session_id")

    allowed_categories = {
        "letter",
        "number",
        "space",
        "modifier",
        "navigation",
        "other"
    }

    if category not in allowed_categories or not isinstance(session_id, str) or len(session_id) > 100:
        return jsonify({"error": "Invalid event data"}), 400

    save_event(category, session_id)

    return jsonify({
        "message": "Event saved",
        "category": category
    })


@app.route("/api/history")
def history():

    rows = get_history()

    result = []

    for row in rows:
        result.append({
            "id": row[0],
            "timestamp": row[1],
            "category": row[2],
            "session_id": row[3]
        })

    return jsonify(result)




@app.route("/api/analytics")
def analytics():
    session_id = request.args.get("session_id")
    result = get_analytics(session_id)
    return jsonify(result)


@app.route("/api/analyze", methods=["POST"])
def analyze():

    data = request.get_json(silent=True) or {}

    result = analyze_activity(data)

    save_assessment(result)

    return jsonify(result)
@app.route("/api/assessment-history")
def assessment_history():

    history = get_assessment_history()

    return jsonify(history)
if __name__ == "__main__":
    app.run(debug=True, port=5000)

   