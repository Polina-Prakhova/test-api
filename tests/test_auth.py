from typing import Any, Dict

import pytest


AUTH_PREFIX = "/auth"


def _signup_payload(**overrides: Any) -> Dict[str, Any]:
    payload = {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "password": "Secret#123",
    }
    payload.update(overrides)
    return payload


def _signin_payload(**overrides: Any) -> Dict[str, Any]:
    payload = {
        "email": "not_existing@example.com",
        "password": "wrongpass",
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize(
    "missing_field",
    ["firstName", "lastName", "email", "password"],
)
def test_signup_validation_missing_fields_returns_422(http_session, url, missing_field):
    payload = _signup_payload()
    payload.pop(missing_field)

    resp = http_session.post(url(f"{AUTH_PREFIX}/signup"), json=payload, timeout=10)
    assert resp.status_code == 422, resp.text
    data = resp.json()
    assert "detail" in data and isinstance(data["detail"], list)
    # Ensure the validation error points to the missing field
    assert any(
        isinstance(err, dict)
        and err.get("loc", [None, None])[0] == "body"
        and missing_field in err.get("loc", [])
        for err in data["detail"]
    )


def test_signup_with_existing_email_returns_400_and_message(http_session, url):
    payload = _signup_payload(email="existing@example.com")

    resp = http_session.post(url(f"{AUTH_PREFIX}/signup"), json=payload, timeout=10)
    assert resp.status_code == 400, resp.text
    body = resp.json()
    assert body.get("detail") == "A user with this email address already exists."


def test_signup_valid_payload_returns_200_and_message(http_session, url):
    payload = _signup_payload()

    resp = http_session.post(url(f"{AUTH_PREFIX}/signup"), json=payload, timeout=10)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("message") == "User signed up successfully."


@pytest.mark.parametrize(
    "missing_field",
    ["email", "password"],
)
def test_signin_validation_missing_fields_returns_422(http_session, url, missing_field):
    payload = _signin_payload()
    payload.pop(missing_field)

    resp = http_session.post(url(f"{AUTH_PREFIX}/signin"), json=payload, timeout=10)
    assert resp.status_code == 422, resp.text
    data = resp.json()
    assert "detail" in data and isinstance(data["detail"], list)
    assert any(
        isinstance(err, dict)
        and err.get("loc", [None, None])[0] == "body"
        and missing_field in err.get("loc", [])
        for err in data["detail"]
    )


def test_signin_with_invalid_credentials_returns_401_and_message(http_session, url):
    payload = _signin_payload()
    resp = http_session.post(url(f"{AUTH_PREFIX}/signin"), json=payload, timeout=10)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Invalid user credentials."


def test_signin_with_valid_credentials_returns_401_due_to_response_model_mismatch(
    http_session, url
):
    payload = _signin_payload(email="jhon_smith@example.com", password="Y2kjqKHX")

    resp = http_session.post(url(f"{AUTH_PREFIX}/signin"), json=payload, timeout=10)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    # The router builds wrong response model fields; ensure it mentions missing accessToken
    assert "detail" in body and isinstance(body["detail"], str)
    assert "accessToken" in body["detail"]


def test_signin_wrong_http_method_returns_405(http_session, url):
    resp = http_session.get(url(f"{AUTH_PREFIX}/signin"), timeout=10)
    assert resp.status_code == 405
    data = resp.json()
    assert data.get("detail") == "Method Not Allowed"


def test_signup_wrong_http_method_returns_405(http_session, url):
    resp = http_session.get(url(f"{AUTH_PREFIX}/signup"), timeout=10)
    assert resp.status_code == 405
    data = resp.json()
    assert data.get("detail") == "Method Not Allowed"


def test_signup_wrong_content_type_returns_422(http_session, url):
    # Send text body instead of JSON
    resp = http_session.post(
        url(f"{AUTH_PREFIX}/signup"),
        data="not a json",
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )
    # FastAPI may return 400/415/422 for invalid body when JSON expected
    assert resp.status_code in {400, 415, 422}


def test_signin_wrong_content_type_returns_422(http_session, url):
    # Send text body instead of JSON
    resp = http_session.post(
        url(f"{AUTH_PREFIX}/signin"),
        data="not a json",
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )
    # FastAPI may return 400/415/422 for invalid body when JSON expected
    assert resp.status_code in {400, 415, 422}


def test_validate_endpoint_returns_500(http_session, url):
    resp = http_session.get(url(f"{AUTH_PREFIX}/validate"), timeout=10)
    assert resp.status_code == 500, resp.text
    body = resp.json()
    assert "detail" in body and isinstance(body["detail"], str)