from fastapi.testclient import TestClient
from src.app import app, activities
import copy
import urllib.parse
import pytest


ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities before each test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield


client = TestClient(app)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success():
    email = "tester@mergington.edu"
    activity = urllib.parse.quote("Chess Club", safe="")
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Verify participant was added
    r2 = client.get("/activities")
    assert email in r2.json()["Chess Club"]["participants"]


def test_signup_duplicate():
    # michael@mergington.edu is already in Chess Club initial data
    email = "michael@mergington.edu"
    activity = urllib.parse.quote("Chess Club", safe="")
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 400
    assert "already signed up" in r.json().get("detail", "")
