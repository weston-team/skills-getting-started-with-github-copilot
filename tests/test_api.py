from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


# Snapshot initial activities so tests can reset state
_INITIAL_ACTIVITIES = deepcopy(app_module.activities)


def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(_INITIAL_ACTIVITIES))


@pytest.fixture(autouse=True)
def run_around_tests():
    reset_activities()
    yield
    reset_activities()


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate():
    name = "Chess Club"
    email = "newstudent@example.com"

    # sign up
    resp = client.post(f"/activities/{quote(name)}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app_module.activities[name]["participants"]

    # duplicate signup should fail
    resp2 = client.post(f"/activities/{quote(name)}/signup", params={"email": email})
    assert resp2.status_code == 400


def test_remove_participant_success_and_not_found():
    name = "Chess Club"
    # michael@mergington.edu is in initial participants
    email = "michael@mergington.edu"

    resp = client.delete(f"/activities/{quote(name)}/participants", params={"email": email})
    assert resp.status_code == 200
    assert email not in app_module.activities[name]["participants"]

    # trying to remove again should return 404
    resp2 = client.delete(f"/activities/{quote(name)}/participants", params={"email": email})
    assert resp2.status_code == 404
