"""
Pytest configuration and fixtures for API tests.
"""
import pytest
import requests
from typing import Dict, Any, Optional


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
def test_user_credentials():
    """Test user credentials."""
    return {
        "email": "jhon_smith@example.com",
        "password": "Y2kjqKHX"
    }


@pytest.fixture(scope="session")
def new_user_data():
    """New user registration data."""
    return {
        "firstName": "John",
        "lastName": "Smith",
        "email": "john_smith_test@example.com",
        "password": "TestPassword123"
    }


@pytest.fixture(scope="session")
def existing_user_email():
    """Email of existing user for conflict tests."""
    return "existing@example.com"


@pytest.fixture
def auth_token(api_client, base_url, test_user_credentials):
    """Get authentication token for authorized requests."""
    response = api_client.post(
        f"{base_url}/auth/signin",
        json=test_user_credentials
    )
    if response.status_code == 200:
        return response.json().get("accessToken")
    return None


@pytest.fixture
def auth_headers(auth_token):
    """Headers with authentication token."""
    if auth_token:
        return {"Authorization": f"Bearer {auth_token}"}
    return {}


@pytest.fixture(scope="session")
def sample_location_id():
    """Sample location ID for testing."""
    return "672846d5c951184d705b65d7"


@pytest.fixture(scope="session")
def sample_dish_id():
    """Sample dish ID for testing."""
    return "322846d5c951184d705b65d2"


@pytest.fixture(scope="session")
def sample_reservation_data():
    """Sample reservation data."""
    return {
        "locationId": "672846d5c951184d705b65d7",
        "tableNumber": "1",
        "date": "2024-12-31",
        "guestsNumber": "4",
        "timeFrom": "12:15",
        "timeTo": "14:00"
    }


@pytest.fixture(scope="session")
def sample_feedback_data():
    """Sample feedback data."""
    return {
        "reservationId": "672846d5c951184d705b65d7",
        "serviceRating": "5",
        "serviceComment": "Excellent service",
        "cuisineRating": "4",
        "cuisineComment": "Great food"
    }


@pytest.fixture(scope="session")
def sample_profile_update_data():
    """Sample profile update data."""
    return {
        "firstName": "UpdatedJohn",
        "lastName": "UpdatedSmith",
        "base64encodedImage": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }


@pytest.fixture(scope="session")
def sample_password_change_data():
    """Sample password change data."""
    return {
        "oldPassword": "Y2kjqKHX",
        "newPassword": "NewPassword123"
    }


def make_request(
    client: requests.Session,
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> requests.Response:
    """Helper function to make HTTP requests."""
    request_headers = headers or {}
    
    if method.upper() == "GET":
        return client.get(url, headers=request_headers, params=params)
    elif method.upper() == "POST":
        return client.post(url, headers=request_headers, json=json_data, params=params)
    elif method.upper() == "PUT":
        return client.put(url, headers=request_headers, json=json_data, params=params)
    elif method.upper() == "DELETE":
        return client.delete(url, headers=request_headers, params=params)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")


@pytest.fixture
def make_api_request(api_client):
    """Fixture that returns the make_request helper function."""
    def _make_request(method, url, headers=None, json_data=None, params=None):
        return make_request(api_client, method, url, headers, json_data, params)
    return _make_request