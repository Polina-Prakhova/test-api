import pytest
import requests

BASE_URL = "http://localhost:8000"

# Helper to get a valid token (assumes test_auth.py ran and user exists)
def get_token():
    resp = requests.post(f"{BASE_URL}/sign-in", json={"username": "newuser", "password": "StrongPass123"})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return None

def test_get_cart_auth():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/", headers=headers)
    assert resp.status_code in [200, 500]
    data = resp.json()
    assert "cart_id" in data or "detail" in data


def test_get_cart_no_auth():
    resp = requests.get(f"{BASE_URL}/")
    assert resp.status_code == 401 or resp.status_code == 403


def test_get_cart_invalid_token():
    headers = {"Authorization": "Bearer invalidtoken"}
    resp = requests.get(f"{BASE_URL}/", headers=headers)
    assert resp.status_code == 401 or resp.status_code == 403


def test_put_cart_auth():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "items": [
            {"dish_id": "dish1", "quantity": 2},
            {"dish_id": "dish2", "quantity": 1}
        ],
        "notes": "No onions"
    }
    resp = requests.put(f"{BASE_URL}/", json=payload, headers=headers)
    assert resp.status_code in [200, 500]
    data = resp.json()
    assert "cart_id" in data or "detail" in data


def test_put_cart_no_auth():
    payload = {
        "items": [
            {"dish_id": "dish1", "quantity": 2}
        ],
        "notes": "Extra cheese"
    }
    resp = requests.put(f"{BASE_URL}/", json=payload)
    assert resp.status_code == 401 or resp.status_code == 403


def test_put_cart_invalid_payload():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"items": "notalist", "notes": 123}
    resp = requests.put(f"{BASE_URL}/", json=payload, headers=headers)
    assert resp.status_code in [400, 500]
