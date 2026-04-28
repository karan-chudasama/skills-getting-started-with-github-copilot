"""
Unit tests for the Mergington High School API

Tests cover all endpoints using the AAA (Arrange-Act-Assert) pattern with
clear section comments for readability and maintainability.
"""

import pytest
from fastapi import HTTPException


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_index(self, client):
        """
        Test that the root endpoint redirects to the static index.html page.

        AAA Pattern:
        - Arrange: Client is ready (via fixture)
        - Act: Make GET request to root
        - Assert: Verify 307 redirect status and correct location
        """
        # Arrange
        # (client fixture is already arranged)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""

    def test_get_all_activities_returns_dict(self, client, reset_activities):
        """
        Test that GET /activities returns all activities as a dictionary.

        AAA Pattern:
        - Arrange: Initialize clean activity state
        - Act: Make GET request to /activities
        - Assert: Verify response is dict and contains expected activities
        """
        # Arrange
        expected_activity_names = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Soccer Club", "Art Club",
            "Drama Club", "Debate Club", "Science Club"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert len(activities_data) == 9
        for activity_name in expected_activity_names:
            assert activity_name in activities_data

    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """
        Test that each activity has required fields.

        AAA Pattern:
        - Arrange: Define required fields
        - Act: Fetch activities and check structure
        - Assert: Verify all required fields exist for each activity
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        for activity_name, activity_data in activities_data.items():
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupForActivityEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client, reset_activities):
        """
        Test successful signup for an activity.

        AAA Pattern:
        - Arrange: Prepare activity name and email of new student
        - Act: Send signup request
        - Assert: Verify 200 response and success message
        """
        # Arrange
        activity_name = "Chess Club"
        new_student_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert new_student_email in response.json()["message"]

    def test_signup_adds_student_to_participants(self, client, reset_activities, isolated_activity):
        """
        Test that signup actually adds the student to the activity's participants list.

        AAA Pattern:
        - Arrange: Verify student not in activity initially
        - Act: Send signup request
        - Assert: Verify student now appears in participants list
        """
        # Arrange
        activity_name = "Chess Club"
        new_student_email = "newstudent@mergington.edu"
        assert new_student_email not in isolated_activity[activity_name]["participants"]

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email}
        )

        # Assert
        assert new_student_email in isolated_activity[activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Test that signing up for a nonexistent activity returns 404.

        AAA Pattern:
        - Arrange: Use a fake activity name
        - Act: Send signup request for nonexistent activity
        - Assert: Verify 404 status and appropriate error message
        """
        # Arrange
        fake_activity = "Nonexistent Club"
        student_email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_registered_returns_400(self, client, reset_activities):
        """
        Test that signing up twice for the same activity returns 400 error.

        AAA Pattern:
        - Arrange: Use an already-registered student
        - Act: Attempt to sign up for the same activity
        - Assert: Verify 400 status and conflict message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_student = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_student}
        )

        # Assert
        assert response.status_code == 400
        assert "Student already signed up" in response.json()["detail"]


class TestUnregisterFromActivityEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_unregister_from_activity_success(self, client, reset_activities):
        """
        Test successful unregistration from an activity.

        AAA Pattern:
        - Arrange: Use existing participant
        - Act: Send delete request
        - Assert: Verify 200 response and success message
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{student_email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_from_participants(self, client, reset_activities, isolated_activity):
        """
        Test that unregister actually removes the student from participants.

        AAA Pattern:
        - Arrange: Verify student is in activity initially
        - Act: Send delete request
        - Assert: Verify student no longer in participants list
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"
        assert student_email in isolated_activity[activity_name]["participants"]

        # Act
        client.delete(
            f"/activities/{activity_name}/participants/{student_email}"
        )

        # Assert
        assert student_email not in isolated_activity[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Test that unregistering from a nonexistent activity returns 404.

        AAA Pattern:
        - Arrange: Use fake activity name
        - Act: Send delete request
        - Assert: Verify 404 status and error message
        """
        # Arrange
        fake_activity = "Nonexistent Club"
        student_email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{fake_activity}/participants/{student_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered_returns_400(self, client, reset_activities):
        """
        Test that unregistering a student not in activity returns 400.

        AAA Pattern:
        - Arrange: Use non-participant student
        - Act: Attempt to unregister
        - Assert: Verify 400 status and error message
        """
        # Arrange
        activity_name = "Chess Club"
        nonexistent_student = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_student}"
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestIntegrationScenarios:
    """Integration tests for realistic user scenarios"""

    def test_signup_and_unregister_workflow(self, client, reset_activities, isolated_activity):
        """
        Test complete workflow: signup and then unregister.

        AAA Pattern:
        - Arrange: Prepare student and activity
        - Act: Sign up, then unregister
        - Assert: Verify state changes at each step
        """
        # Arrange
        activity_name = "Art Club"
        student_email = "workflow_test@mergington.edu"
        initial_count = len(isolated_activity[activity_name]["participants"])

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Assert signup worked
        assert signup_response.status_code == 200
        assert len(isolated_activity[activity_name]["participants"]) == initial_count + 1

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/participants/{student_email}"
        )

        # Assert unregister worked
        assert unregister_response.status_code == 200
        assert len(isolated_activity[activity_name]["participants"]) == initial_count
        assert student_email not in isolated_activity[activity_name]["participants"]

    def test_multiple_students_signup_for_same_activity(self, client, reset_activities, isolated_activity):
        """
        Test that multiple students can sign up for the same activity.

        AAA Pattern:
        - Arrange: Prepare multiple students
        - Act: Sign all of them up for same activity
        - Assert: Verify all are registered
        """
        # Arrange
        activity_name = "Science Club"
        new_students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        initial_count = len(isolated_activity[activity_name]["participants"])

        # Act
        for student_email in new_students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student_email}
            )
            assert response.status_code == 200

        # Assert
        assert len(isolated_activity[activity_name]["participants"]) == initial_count + 3
        for student_email in new_students:
            assert student_email in isolated_activity[activity_name]["participants"]