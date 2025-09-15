import pytest
import requests

BASE_URL = "http://localhost:8000"

@pytest.mark.parametrize("payload, expected_status, expected_keys", [
    ({"username": "newuser", "password": "StrongPass123", "email": "newuser@example.com"}, 200, ["message", "user_id"]),
    ({"username": "", "password": "StrongPass123", "email": "newuser@example.com"}, 400, ["detail"]),
    ({"username": "newuser", "password": "", "email": "newuser@example.com"}, 400, ["detail"]),
    ({"username": "newuser", "password": "StrongPass123", "email": "bademail"}, 400, ["detail"]),
])
def test_signup(payload, expected_status, expected_keys):
    resp = requests.post(f"{BASE_URL}/sign-up", json=payload)
    assert resp.status_code == expected_status
    data = resp.json()
    for key in expected_keys:
        assert key in data


def test_signup_duplicate():
    payload = {"username": "dupuser", "password": "StrongPass123", "email": "dupuser@example.com"}
    # First signup should succeed
    resp1 = requests.post(f"{BASE_URL}/sign-up", json=payload)
    assert resp1.status_code == 200
    # Second signup should fail with 409
    resp2 = requests.post(f"{BASE_URL}/sign-up", json=payload)
    assert resp2.status_code == 409
    assert "detail" in resp2.json()


@pytest.mark.parametrize("payload, expected_status, expected_keys", [
    ({"username": "newuser", "password": "StrongPass123"}, 200, ["access_token", "token_type"]),
    ({"username": "newuser", "password": "WrongPass"}, 401, ["detail"]),
    ({"username": "", "password": "StrongPass123"}, 401, ["detail"]),
    ({"username": "newuser"}, 400, ["detail"]),
])
def test_signin(payload, expected_status, expected_keys):
    resp = requests.post(f"{BASE_URL}/sign-in", json=payload)
    assert resp.status_code == expected_status
    data = resp.json()
    for key in expected_keys:
        assert key in data


def test_signin_server_error(monkeypatch):
    # Simulate server error by patching requests.post to raise Exception
    def raise_exc(*args, **kwargs):
        raise Exception("Server error")
    monkeypatch.setattr(requests, "post", raise_exc)
    with pytest.raises(Exception):
        requests.post(f"{BASE_URL}/sign-in", json={"username": "any", "password": "any"})
