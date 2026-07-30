"""
Integration tests for the Flask API (backend/app.py).

Unlike tests/test_data_loader.py (unit tests of isolated functions),
these tests exercise the full request/response cycle through Flask's
test client -- routing, query-param handling, data loading, and JSON
serialization together -- to catch integration-level regressions that
unit tests alone would miss.

Run with:
    pytest tests/ -v
from the project root.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import app  # noqa: E402


def client():
    app.testing = True
    return app.test_client()


def test_health_check_returns_ok():
    resp = client().get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_get_prices_returns_full_series():
    resp = client().get("/api/prices")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "data" in body and "count" in body
    assert body["count"] == len(body["data"])
    assert body["count"] > 8000
    first = body["data"][0]
    assert set(first.keys()) == {"date", "price"}


def test_get_prices_respects_date_filter():
    resp = client().get("/api/prices?start_date=2020-01-01&end_date=2020-01-10")
    assert resp.status_code == 200
    body = resp.get_json()
    for row in body["data"]:
        assert "2020-01-01" <= row["date"] <= "2020-01-10"


def test_get_events_returns_all_events():
    resp = client().get("/api/events")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["count"] >= 10


def test_get_events_filters_by_category():
    all_resp = client().get("/api/events").get_json()
    categories = {e["category"] for e in all_resp["data"]}
    sample_category = next(iter(categories))

    filtered = client().get(f"/api/events?category={sample_category}").get_json()
    assert filtered["count"] >= 1
    assert all(e["category"] == sample_category for e in filtered["data"])


def test_get_changepoint_handles_missing_or_present_file():
    resp = client().get("/api/changepoint")
    # Either the cached results exist (200) or the endpoint correctly
    # reports their absence (404) -- both are valid, well-handled states.
    assert resp.status_code in (200, 404)
    body = resp.get_json()
    assert isinstance(body, dict)
