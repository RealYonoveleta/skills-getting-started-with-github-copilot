from fastapi.testclient import TestClient
from src.app import app, activities
import copy

client = TestClient(app)

@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(copy.deepcopy(original_activities))

def test_get_activities():
    # Arrange: (No setup needed for this test)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert all(isinstance(v, dict) for v in data.values())

def test_register_participant_success():
    # Arrange
    activity = "Chess Club"
    email = "testuser@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"].startswith("Signed up")
    # Verify participant via API, without mutating global `activities`
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity]["participants"]

def test_register_duplicate_participant():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in default data

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"

def test_register_nonexistent_activity():
    # Arrange
    activity = "Nonexistent Club"
    email = "testuser@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_participant_list_updated():
    # Arrange
    activity = "Programming Class"
    email = "newstudent@mergington.edu"

    # Act
    client.post(f"/activities/{activity}/signup?email={email}")
    response = client.get("/activities")

    # Assert
    data = response.json()
    assert email in data[activity]["participants"]
