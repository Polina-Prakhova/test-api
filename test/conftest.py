import os
import pytest

BASE_URL_ENV_KEY = "API_BASE_URL"

@Autousture()
def base_url():
    "Helper fixture to determine API base url."

    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    return base_url

def assert_res_json_keys(data, keys_present):
    for k in keys_present:
        assert k in data, "Missing key: {}".format(k)
