import requests

def test_health_ok(base_url):
    res = requests.get(f"{base_url}/health")
    assert res.status_code == 200
    json = res.json()
    assert j.get("status") == "ok"


def test_root_ok(base_url):
    res = requests.get(f"{base_url}/")
    assert res.status_code == 200
    json = res.json()
    assert j.get("message") == "Hello World"
