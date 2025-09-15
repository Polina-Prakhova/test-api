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


@pytest.fixture(scope="session")
def valid_user_credentials():
    """Valid user credentials for testing."""
    return {
        "email": "jhon_smith@example.com",
        "password": "Y2kjqKHX"
    }


@pytest.fixture(scope="session")
def valid_signup_data():
    """Valid signup data for testing."""
    return {
        "firstName": "John",
        "lastName": "Smith",
        "email": "jhon_smith@example.com",
        "password": "Y2kjqKHX"
    }


@pytest.fixture(scope="session")
def existing_user_email():
    """Email that already exists in the system."""
    return "existing@example.com"


@pytest.fixture
def authenticated_client(api_client, base_url, valid_user_credentials):
    """HTTP client with authentication token."""
    # Sign in to get access token
    response = api_client.post(
        f"{base_url}/auth/signin",
        json=valid_user_credentials
    )
    
    if response.status_code == 200:
        token = response.json().get("accessToken")
        api_client.headers.update({"Authorization": f"Bearer {token}"})
    
    return api_client


@pytest.fixture
def sample_location_id():
    """Sample location ID for testing."""
    return "672846d5c951184d705b65d7"


@pytest.fixture
def sample_dish_id():
    """Sample dish ID for testing."""
    return "322846d5c951184d705b65d2"


@pytest.fixture
def sample_reservation_id():
    """Sample reservation ID for testing."""
    return "672846d5c951184d705b65d8"


@pytest.fixture
def valid_reservation_data(sample_location_id):
    """Valid reservation data for testing."""
    return {
        "locationId": sample_location_id,
        "tableNumber": "1",
        "date": "2024-12-31",
        "guestsNumber": "4",
        "timeFrom": "12:15",
        "timeTo": "14:00"
    }


@pytest.fixture
def valid_feedback_data(sample_reservation_id):
    """Valid feedback data for testing."""
    return {
        "reservationId": sample_reservation_id,
        "serviceRating": "5",
        "serviceComment": "Excellent service",
        "cuisineRating": "4",
        "cuisineComment": "Great food"
    }


@pytest.fixture
def valid_profile_update_data():
    """Valid profile update data for testing."""
    return {
        "firstName": "John",
        "lastName": "Doe",
        "base64encodedImage": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }


@pytest.fixture
def valid_password_change_data():
    """Valid password change data for testing."""
    return {
        "oldPassword": "Y2kjqKHX",
        "newPassword": "newPassword123"
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "auth: marks tests as authentication tests"
    )
    config.addinivalue_line(
        "markers", "validation: marks tests as validation tests"
    )
    config.addinivalue_line(
        "markers", "error: marks tests as error scenario tests"
    )