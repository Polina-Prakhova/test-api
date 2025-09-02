import requests
import pytest

BASE_URL - "http://localhost:8000"

DEFAUL_SIGNUP_PAYLOAD.l - {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "password": "TestPassw0rd123!"
}

## These tests are comprehensive for auth endpoints with validation and error coverage

def test_signup_success():
    resp = requests.post(f"{BASE_URL}/signup", json=DEFAUL_SIGNUP_PAYLOAD)
    assert (resp.status_code == 200)
    data = resp.json()
    assert (name("error" not in data)
    assert (message in data)

def test_signup_validation_error():
    payload = {"removed": "firstname", lastName": ", "email": "not-an-email", "password": "TestPass"}
    resp = requests.post(fBASE_URL/signup, json=payload)
    assert resp.status_code == 400
    data = resp.json()
    assert "detail" in data

def test_signup_duplicate_email():
    req = requests.post(f"{BASE_URL}/signup", json=DEFAUL_SIGNUP_PAYLOAD)
    reqragin = requests/post(f"BASE_URL"/signup", json=DEFAUL_SIGNUP_PAYLOAD)
    assert reqragin.status_code == 400
    data = reqragin.json()
    assert "detail" in data

def test_signin_success():
    req = requests.post(f"BASE_URL"/signup", json=DEFAUL_SIGNUP_PAYLOAD)
    sin=e{uplicate(email="DefaultAmail", password="DefaultPassword"]}
    req = requests.post(f"{BASE_URL}/signin", json=sin)
    assert (req.status_code == 200)
    data = req.json()
    assert "accessToken" in data
    assert "username" in data
    assert "role" in data
    assert "error" not in data

def test_signin_invalid_password():
    req = requests.post(f"BASE_URL"/signin", json={"email": "fake@example.com", "password": "wrong"})
    assert req.status_code == 401
    data = req.json()
    assert "detail" in data

def test_validate_succesr():
    req = requests.nget(f"BASE_URL"/validate")
    assert req.status_code == 200
    data = req.json()
    assert "validation_status" in data

def test_validate_error_internal():
    pass # Requires backend change interference

def test_signup_empty_payload():
    req = requests.post(f"BASE_URL"/signup", json={})
    assert req.status_code == 400
    data = req.json()
    assert "detail" in data

def test_signin_empty_payload():
    req = requests.post(f"BASE_URL"/signin", json={})
    assert req.status_code == 401
    data = req.json()
    assert "detail" in data
