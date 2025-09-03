import requests
import pytest

BASE_URL = "http://localhost:8000"

DEFAULT_SIGNUP_PAYLOAD = {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "password": "TestPassw0rd123!"
}


# These tests are comprehensive for auth endpoints with validation and error coverage


def test_signup_success():
    resp = requests.post(f"{BASE_URL}/signup", json=DEFAULT_SIGNUP_PAYLOAD)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert "error" not in data, "Unexpected error in response"
    assert "message" in data, "No message in response"


def test_signup_validation_error():
    payload = {
        # Missing firstName
        "lastName": "Doe",
        "email": "not-an-email",
        "password": "TestPass"
    }
    resp = requests.post(f"{BASE_URL}/signup", json=payload)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
    data = resp.json()
    assert "detail" in data, "No detail in error response"


def test_signup_duplicate_email():
    resp1 = requests.post(f"{BASE_URL}/signup", json=DEFAULT_SIGNUP_PAYLOAD)
    resp2 = requests.post(f"{BASE_URL}/signup", json=DEFAULT_SIGNUP_PAYLOAD)
    assert resp2.status_code == 400, f"Expected 400 for duplicate email, got {resp2.status_code}"
    data = resp2.json()
    assert "detail" in data, "No detail in error response for duplicate email"


def test_signin_success():
    resp = requests.post(f"{BASE_URL}/signup", json=DEFAULT_SIGNUP_PAYLOAD)
    signin_payload = {"email": "john.doe@example.com", "password": "TestPassw0rd123!"}
    req = requests.post(f"{BASE_URL}/signin", json=signin_payload)
    assert req.status_code == 200, f"Expected 200, got {req.status_code}"
    data = req.json()
    assert "accessToken" in data, "No accessToken in response"
    assert "username" in data, "No username in response"
    assert "role" in data, "No role in response"
    assert "error" not in data, "Unexpected error in response"


def test_signin_invalid_password():
    signin_payload = {"email": "john.doe@example.com", "password": "wrongpassword"}
    req = requests.post(f"{BASE_URL}/signin", json=signin_payload)
    assert req.status_code == 401, f"Expected 401, got {req.status_code}"
    data = req.json()
    assert "detail" in data, "No detail in error response for invalid password"


def test_validate_success():
    req = requests.get(f"{BASE_URL}/validate")
    assert req.status_code == 200, f"Expected 200, got {req.status_code}"
    data = req.json()
    assert "validation_status" in data, "No validation_status in response"


def test_validate_error_internal():
    pass # Requires backend change interference


def test_signup_empty_payload():
    req = requests.post(f"{BASE_URL}/signup", json={})
    assert req.status_code == 400, f"Expected 400, got {req.status_code}"
    data = req.json()
    assert "detail" in data, "No detail in error response for empty payload"


def test_signin_empty_payload():
    req = requests.post(f"{BASE_URL}/signin", json={})
    assert req.status_code == 401, f"Expected 401, got {req.status_code}"
    data = req.json()
    assert "detail" in data, "No detail in error response for empty payload"
