from src.app import activities


KNOWN_ACTIVITY = "Chess Club"
TEST_EMAIL = "test.student@mergington.edu"


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_static_index_is_served(client):
    # Arrange
    expected_title = "Mergington High School Activities"

    # Act
    response = client.get("/static/index.html")

    # Assert
    assert response.status_code == 200
    assert expected_title in response.text


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert KNOWN_ACTIVITY in response.json()
    assert expected_fields.issubset(response.json()[KNOWN_ACTIVITY])


def test_signup_adds_participant(client):
    # Arrange
    activity = activities[KNOWN_ACTIVITY]
    assert TEST_EMAIL not in activity["participants"]

    # Act
    response = client.post(
        f"/activities/{KNOWN_ACTIVITY}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {TEST_EMAIL} for {KNOWN_ACTIVITY}"
    }
    assert TEST_EMAIL in activity["participants"]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{unknown_activity}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activities[KNOWN_ACTIVITY]["participants"].append(TEST_EMAIL)

    # Act
    response = client.post(
        f"/activities/{KNOWN_ACTIVITY}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }


def test_unregister_removes_participant(client):
    # Arrange
    activities[KNOWN_ACTIVITY]["participants"].append(TEST_EMAIL)

    # Act
    response = client.delete(
        f"/activities/{KNOWN_ACTIVITY}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {TEST_EMAIL} from {KNOWN_ACTIVITY}"
    }
    assert TEST_EMAIL not in activities[KNOWN_ACTIVITY]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{unknown_activity}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_unregistered_participant(client):
    # Arrange
    assert TEST_EMAIL not in activities[KNOWN_ACTIVITY]["participants"]

    # Act
    response = client.delete(
        f"/activities/{KNOWN_ACTIVITY}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_signup_requires_email(client):
    # Arrange
    endpoint = f"/activities/{KNOWN_ACTIVITY}/signup"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 422


def test_unregister_requires_email(client):
    # Arrange
    endpoint = f"/activities/{KNOWN_ACTIVITY}/signup"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 422
