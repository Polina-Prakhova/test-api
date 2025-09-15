import pytest


def test_health_endpoint(api):
    resp = api.get("/health")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, dict)
        assert data.get("status") == "ok"


def test_root_endpoint(api):
    resp = api.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert data.get("message") == "Hello World"
