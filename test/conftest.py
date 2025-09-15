"""
Pytest configuration and fixtures for API tests.
"""
import pytest
import requests
from typing import Dict, Any


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API."""
    return "http://localhost:8080"


@pytest.fixture(scope="session")
def api_client():
    """HTTP client for API requests."""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    return session


@pytest.fixture
def valid_user_data():
    """Valid user registration data."""
    return {
        "firstName": "John",
        "lastName": "Smith",
        "email": "jhon_smith@example.com",
        "password": "Y2kjqKHX"
    }


@pytest.fixture
def valid_login_data():
    """Valid user login data."""
    return {
        "email": "jhon_smith@example.com",
        "password": "Y2kjqKHX"
    }


@pytest.fixture
def existing_user_data():
    """Existing user data for conflict tests."""
    return {
        "firstName": "Existing",
        "lastName": "User",
        "email": "existing@example.com",
        "password": "password123"
    }


@pytest.fixture
def invalid_login_data():
    """Invalid login data for negative tests."""
    return {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }


@pytest.fixture
def auth_token(api_client, base_url, valid_login_data):
    """Get authentication token for protected endpoints."""
    response = api_client.post(f"{base_url}/auth/signin", json=valid_login_data)
    if response.status_code == 200:
        return response.json().get("accessToken")
    return None


@pytest.fixture
def auth_headers(auth_token):
    """Headers with authentication token."""
    if auth_token:
        return {"Authorization": f"Bearer {auth_token}"}
    return {}


@pytest.fixture
def valid_reservation_data():
    """Valid reservation data."""
    return {
        "locationId": "672846d5c951184d705b65d7",
        "tableNumber": "1",
        "date": "2024-12-31",
        "guestsNumber": "4",
        "timeFrom": "12:15",
        "timeTo": "14:00"
    }


@pytest.fixture
def valid_feedback_data():
    """Valid feedback data."""
    return {
        "reservationId": "672846d5c951184d705b65d7",
        "serviceRating": "5",
        "serviceComment": "Excellent service",
        "cuisineRating": "4",
        "cuisineComment": "Great food"
    }


@pytest.fixture
def valid_profile_update_data():
    """Valid profile update data."""
    return {
        "firstName": "UpdatedJohn",
        "lastName": "UpdatedSmith",
        "base64encodedImage": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }


@pytest.fixture
def valid_password_change_data():
    """Valid password change data."""
    return {
        "oldPassword": "Y2kjqKHX",
        "newPassword": "newPassword123"
    }