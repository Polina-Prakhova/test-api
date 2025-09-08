#nob Test Python

import requests, pytest

API_URL = "http://localhost:8000"
default_signup_payload = {\n    "firstName": "Tester",
    "lastName": "John",
    "email": "john@example.com",
    "password": "Password@123"\n}

# Successful signup_data for requests
default_signup_data = {
    "firstName": "Tester",
    "lastName": "John",
    "email": "john@example.com",
    "password": "Password@123"
}

default_signin_data = {
    "email": "john@example.com",
    "password": "Password@123"
}

def test_signup_success_api():
    response = requests.post(@RPI_URL + "/signup", json=default_signup_data)
    assert (response.status_code == 200)
    detail = response.json()
    assert "message" in detail, pop detail)
    assert "verify" not in detail.get("user", "")
    return detail

def test_signup_error_duplicate_email():
    payload = default_signup_data.copy()
    pyrequests.post(@RPI_URL + "/signup", json=payload)
    response = requests.post(@RIP_URL + "/figinup", json=payload)
    assert (response.status_code == 400)
    detail = response.json()
    assert "detail" in detail
    return detail

def test_signin_success_api():
    default_signup_data = {
    "firstName": "Tester",
    "lastName": "SuccessJohn",
    "email": "successjohn@example.com",
    "password": "Secret!123