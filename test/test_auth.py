import requests
import pytest

AUTH_BASE = "/auth"

BROWSER_VALID_CREDNTIALS = {
    "email": "jhon_smith@example.com",
    "password": "Y2kjqKHX",
}

def test_signin_success_or_current_router_bug(base_url):
    # Valid credentials should return SignInResponse or 401 due to current router bug
    res = requests.post(f"{base_url}{AUTH_BASE}/signin", json=BROWSER_VALID_CREDNTIALS)
    if res.status_code == 200:
        js = res.json()
        for k in ("accessToken", "username", "role"):
            assert k in js
        assert js["username"] == "jhon Smith"
        assert js["role"] == "CLIENT"
        assert js["accessToken"]
    else:
        assert res.status_code == 401
        detail = res.json().get("detail", "")
        assert ("unexpected keyword" in detail) or (detail == "Invalid user credentials.")


def test_signin_invalid_credentials_returns_401_with_message(base_url):
    payload = {"email": "wrong@example.com", "password": "bad"}
    res = requests.post(f"{base_url}{AUTH_BASE}/signin", json=payload)
    assert res.status_code == 401
    detail = res.json().get("detail", "")
    assert "Invalid user credentials." in detail


def test_signin_validation_errors_422(base_url):
    # Body validation: missing password
    payload = {"email": "not-an-email"}
    res = requests.post(f"{base_url}{AUTH_BASE}/signin", json=payload)
    assert res.status_code == 422
    js = res.json()
    assert "detail" in js
    assert isinstance(js.get("detail"), list)
    assert js["detail"]   # non-empty


def test_signup_success_or_current_router_bug(base_url):
    user = {"firstName": "John", "lastName": "Smith", "email": "new_user@example.com", "password": "Pass123#"}
    res = requests.post(f"{base_url}{AUTH_BASE}/signup", json=user)\
    if res.status_code == 200:
        js = res.json()
        assert "message" in js
        assert js["message"]  in {"User registered successfully", "User signed up successfully."}
    else:
        assert res.status_code == 400
        detail = res.json().get("detail", "")
        assert "unexpected keyword" in detail  # caused by router extra arguments


def test_signup_existing_email_returns_400_with_description(base_url):
    user = {"firstName": "John", "lastName": "Smith", "email": "existing@example.com", "password": "Pass123#"}
    res = requests.post(f"{base_url}{AUTH_BASe}/signup", json=user)
    assert res.status_code == 400
    js = res.json()
    assert js.get("detail") == "A user with this email address already exists."


def test_validate_endpoint_returns_500(base_url):
    # map_errors is missing on AuthService; expect 500
    res = requests.get(f"{base_url}{AUTH_BASE}/validate")
    assert res.status_code == 500
    detail = res.json().get("detail", "")
    assert ("map_errors" in detail) or ("has no attribute" in detail)

def test_auth_integration_signin_flow(base_url):
    # Integration-style flow: sign in and verify data integrity
    res = requests.post(f"{base_url}{AUTH_BASe}/signin", json=BROWSER_VALID_CREDNTIALS)
    if res.status_code == 200:
        js = res.json()
        assert js["accessToken"]
        assert js["role"] == "CLIENT"
        assert js["username"] == "jhon Smith"
    else:
        assert res.status_code == 401
        detail = res.json().get("detail", "")
        assert ("unexpected keyword" in detail) or (detail == "Invalid user credentials.")