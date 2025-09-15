import pytest


def test_health_ok(http_session, url):
    resp = http_session.get(url("/health"), timeout=10)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, dict)
    assert data.get("status") == "ok"


def test_root_greeting(http_session, url):
    resp = http_session.get(url("/"), timeout=10)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data == {"message": "Hello World"}
