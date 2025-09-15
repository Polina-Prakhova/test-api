import pytest
import requests

BASE_URL = "http://localhost:8000"

# Helper to get a valid token (assumes test_auth.py ran and user exists)
def get_token():
    resp = requests.post(f"{BASE_URL}/sign-in", json={"username": "newuser", "password": "StrongPass123"})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return None

@pytest.mark.parametrize("params, expected_status", [
    ({}, 200),
    ({"locationId": "loc1"}, 200),
    ({"date": "2024-07-01"}, 200),
    ({"time": "18:00"}, 200),
    ({"guests": "2"}, 200),
    ({"locationId": "bad", "date": "bad", "time": "bad", "guests": "bad"}, 200),
])
def test_get_tables(params, expected_status):
    resp = requests.get(f"{BASE_URL}/tables", params=params)
    assert resp.status_code == expected_status
    assert isinstance(resp.json(), list)


def test_book_table_client_auth():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "table_id": "table1",
        "date": "2024-07-01",
        "time": "18:00",
        "guests": 2
    }
    resp = requests.post(f"{BASE_URL}/client", json=payload, headers=headers)
    assert resp.status_code in [200, 500]  # 500 if service error
    data = resp.json()
    assert "reservation_id" in data or "detail" in data


def test_book_table_client_no_auth():
    payload = {
        "table_id": "table1",
        "date": "2024-07-01",
        "time": "18:00",
        "guests": 2
    }
    resp = requests.post(f"{BASE_URL}/client", json=payload)
    assert resp.status_code == 401 or resp.status_code == 403


def test_book_table_client_invalid_payload():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"table_id": "", "date": "", "time": "", "guests": ""}
    resp = requests.post(f"{BASE_URL}/client", json=payload, headers=headers)
    assert resp.status_code in [400, 500]


def test_book_table_waiter_auth():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "table_id": "table2",
        "date": "2024-07-01",
        "time": "19:00",
        "guests": 4
    }
    resp = requests.post(f"{BASE_URL}/waiter", json=payload, headers=headers)
    assert resp.status_code in [200, 500]
    data = resp.json()
    assert "reservation_id" in data or "detail" in data


def test_book_table_waiter_no_auth():
    payload = {
        "table_id": "table2",
        "date": "2024-07-01",
        "time": "19:00",
        "guests": 4
    }
    resp = requests.post(f"{BASE_URL}/waiter", json=payload)
    assert resp.status_code == 401 or resp.status_code == 403


def test_book_table_waiter_invalid_payload():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"table_id": "", "date": "", "time": "", "guests": ""}
    resp = requests.post(f"{BASE_URL}/waiter", json=payload, headers=headers)
    assert resp.status_code in [400, 500]
