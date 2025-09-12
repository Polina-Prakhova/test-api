import os
import pytest

BASE_URL_ENV_KEY = "API_BASE_URL"

@pytest.fixture(scope="session")
def base_url():
    _base_url = os.getenv(BASE_URL_ENV_KEY, "http://localhost:8000")
    return _base_url

def assert_res_json_keys(data, keys_present):
    for k in keys_present:
        assert k in data, f"Missing key: {k}".format(k)