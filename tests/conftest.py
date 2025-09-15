import os
from typing import Dict

import pytest
import requests


DEFAULT_BASE_URL = "http://localhost:8000"


class ApiClient:
    """Simple API client wrapper over requests.Session with a base URL."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def get(self, path: str, **kwargs) -> requests.Response:
        timeout = kwargs.pop("timeout", 10)
        return self.session.get(self._url(path), timeout=timeout, **kwargs)

    def post(self, path: str, json: Dict | None = None, **kwargs) -> requests.Response:
        timeout = kwargs.pop("timeout", 10)
        return self.session.post(self._url(path), json=json, timeout=timeout, **kwargs)


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for the API under test. Override via env var API_BASE_URL or BASE_URL."""
    return os.getenv("API_BASE_URL") or os.getenv("BASE_URL") or DEFAULT_BASE_URL


@pytest.fixture(scope="session")
def api(base_url: str) -> ApiClient:
    return ApiClient(base_url)


@pytest.fixture(scope="session", autouse=True)
def ensure_service_up(api: ApiClient):
    """Ensure the service is reachable; skip entire test session if not."""
    try:
        resp = api.get("/health")
        # Even if /health is missing, try root as fallback
        if resp.status_code != 200:
            alt = api.get("/")
            if alt.status_code != 200:
                pytest.skip(
                    f"API not reachable at {api.base_url} (got {resp.status_code} on /health and {alt.status_code} on /)."
                )
    except requests.RequestException as exc:
        pytest.skip(f"API not reachable at {api.base_url}: {exc}")


@pytest.fixture()
def valid_signup_payload() -> Dict:
    return {
        "firstName": "John",
        "lastName": "Doe",
        "email": "new_user@example.com",
        "password": "Secret#123",
    }


@pytest.fixture()
def existing_email_signup_payload(valid_signup_payload: Dict) -> Dict:
    payload = valid_signup_payload.copy()
    payload["email"] = "existing@example.com"
    return payload


@pytest.fixture()
def valid_signin_payload() -> Dict:
    return {
        "email": "jhon_smith@example.com",
        "password": "Y2kjqKHX",
    }


@pytest.fixture()
def invalid_signin_payload(valid_signin_payload: Dict) -> Dict:
    payload = valid_signin_payload.copy()
    payload["password"] = "wrong-password"
    return payload
