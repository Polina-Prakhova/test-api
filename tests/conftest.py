import os
from typing import Callable

import pytest
import requests


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Base URL for the API under test.

    Can be overridden via environment variable API_BASE_URL.
    Defaults to http://localhost:8000
    """
    return os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def http_session() -> requests.Session:
    """Configured HTTP session to reuse TCP connections across tests."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture()
def url(api_base_url: str) -> Callable[[str], str]:
    """Helper to build absolute URLs from path fragments."""
    def _builder(path: str) -> str:
        return f"{api_base_url.rstrip('/')}/{path.lstrip('/')}"

    return _builder
