
import sys
from pathlib import Path

# Add the backend folder so Python can find app.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app import app


def test_home_endpoint():
    """Test that the home endpoint works."""
    app.config["TESTING"] = True

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert response.is_json


def test_total_revenue():
    """Test the total revenue question."""
    response = app.test_client().post(
        "/ask",
        json={"question": "What is the total revenue?"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["intent"] == "total_revenue"
    assert data["answer"]["total_revenue"] == 1439200.0


def test_highest_revenue_product():
    """Test the highest revenue product."""
    response = app.test_client().post(
        "/ask",
        json={
            "question": "Which product generated the highest revenue?"
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["answer"]["product"] == "Monitor"
    assert data["answer"]["revenue"] == 473000.0


def test_monthly_revenue_trend():
    """Test monthly revenue results."""
    response = app.test_client().post(
        "/ask",
        json={"question": "What is the monthly revenue trend?"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["intent"] == "monthly_revenue"
    assert len(data["answer"]) == 6


def test_highest_revenue_region():
    """Test the region with the highest revenue."""
    response = app.test_client().post(
        "/ask",
        json={"question": "Which region generated the highest sales?"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["answer"]["region"] == "South"
    assert data["answer"]["revenue"] == 411200.0


def test_compare_two_months():
    """Test January versus February revenue."""
    response = app.test_client().post(
        "/ask",
        json={
            "question": "Compare revenue between 2026-01 and 2026-02"
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["answer"]["change"] == 24350.0
    assert data["answer"]["percentage_change"] == 11.58


def test_empty_question():
    """Test that an empty question is rejected."""
    response = app.test_client().post(
        "/ask",
        json={"question": ""},
    )

    assert response.status_code == 400


def test_unsupported_question():
    """Test that an unsupported question is rejected."""
    response = app.test_client().post(
        "/ask",
        json={"question": "What is the weather today?"},
    )

    assert response.status_code == 400


def test_missing_question():
    """Test that a missing question is rejected."""
    response = app.test_client().post("/ask", json={})

    assert response.status_code == 400
