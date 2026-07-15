"""
Flask backend for the Brent Oil Price Change Point Analysis dashboard.

Serves three endpoints consumed by the React frontend:
  GET /api/prices           - historical daily price series (optionally date-filtered)
  GET /api/changepoint       - cached Bayesian change point model results
  GET /api/events            - researched events dataset (optionally category-filtered)
"""

import os
import sys
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from data_loader import load_brent_prices, load_events, DataLoadError

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PRICES_PATH = os.path.join(DATA_DIR, "BrentOilPrices.csv")
EVENTS_PATH = os.path.join(DATA_DIR, "events.csv")
CHANGEPOINT_PATH = os.path.join(DATA_DIR, "change_point_results.json")


@app.route("/api/prices", methods=["GET"])
def get_prices():
    """
    Return historical Brent oil prices.
    Optional query params: start_date, end_date (YYYY-MM-DD).
    """
    try:
        df = load_brent_prices(PRICES_PATH)
    except DataLoadError as exc:
        return jsonify({"error": str(exc)}), 500

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        if start_date:
            df = df[df["Date"] >= start_date]
        if end_date:
            df = df[df["Date"] <= end_date]
    except Exception as exc:
        return jsonify({"error": f"Invalid date filter: {exc}"}), 400

    result = [
        {"date": row["Date"].strftime("%Y-%m-%d"), "price": round(row["Price"], 2)}
        for _, row in df.iterrows()
    ]
    return jsonify({"count": len(result), "data": result})


@app.route("/api/changepoint", methods=["GET"])
def get_changepoint():
    """Return the cached Bayesian change point model results."""
    if not os.path.exists(CHANGEPOINT_PATH):
        return jsonify({"error": "Change point results not found. Run the Task 2 notebook first."}), 404

    try:
        with open(CHANGEPOINT_PATH, "r") as f:
            results = json.load(f)
    except Exception as exc:
        return jsonify({"error": f"Failed to load change point results: {exc}"}), 500

    return jsonify(results)


@app.route("/api/events", methods=["GET"])
def get_events():
    """
    Return the researched events dataset.
    Optional query param: category (exact match).
    """
    try:
        df = load_events(EVENTS_PATH)
    except DataLoadError as exc:
        return jsonify({"error": str(exc)}), 500

    category = request.args.get("category")
    if category:
        df = df[df["Category"] == category]

    result = [
        {
            "date": row["Date"].strftime("%Y-%m-%d"),
            "event_name": row["Event_Name"],
            "category": row["Category"],
            "description": row["Description"],
            "expected_impact": row["Expected_Impact"],
        }
        for _, row in df.iterrows()
    ]
    return jsonify({"count": len(result), "data": result})


@app.route("/api/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)