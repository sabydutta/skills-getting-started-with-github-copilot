import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    return TestClient(app_module.app)


@pytest.fixture
def isolated_activities(monkeypatch):
    activities = copy.deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


def test_get_activities_returns_seeded_data(client, isolated_activities):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == isolated_activities


def test_signup_adds_participant(client, isolated_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in isolated_activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client, isolated_activities):
    # Arrange
    activity_name = "Chess Club"
    email = isolated_activities[activity_name]["participants"][0]
    participant_count = len(isolated_activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up for this activity"}
    assert len(isolated_activities[activity_name]["participants"]) == participant_count


def test_signup_rejects_unknown_activity(client, isolated_activities):
    # Arrange
    activity_name = "Robotics Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_name not in isolated_activities


def test_unregister_removes_participant(client, isolated_activities):
    # Arrange
    activity_name = "Chess Club"
    email = isolated_activities[activity_name]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in isolated_activities[activity_name]["participants"]


def test_unregister_rejects_unregistered_participant(client, isolated_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "not.registered@mergington.edu"
    participants_before = isolated_activities[activity_name]["participants"].copy()

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert isolated_activities[activity_name]["participants"] == participants_before


def test_unregister_rejects_unknown_activity(client, isolated_activities):
    # Arrange
    activity_name = "Robotics Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_name not in isolated_activities