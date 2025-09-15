import pytest


class TestAuthSignin:
    endpoint = "/auth/signin"

    def test_signin_success(self, api, valid_signin_payload):
        resp = api.post(self.endpoint, json=valid_signin_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        # Response model SignInResponse has accessToken, username, role in service
        assert data.get("message") == "Sign in successful."
        assert "accessToken" in data or "accessToken" in data.get("user", {})

    def test_signin_invalid_credentials(self, api, invalid_signin_payload):
        resp = api.post(self.endpoint, json=invalid_signin_payload)
        assert resp.status_code == 401
        data = resp.json()
        assert "detail" in data
        assert "Invalid user credentials" in str(data.get("detail"))

    @pytest.mark.parametrize("missing_field", ["email", "password"])
    def test_signin_missing_required_field(self, api, valid_signin_payload, missing_field):
        payload = valid_signin_payload.copy()
        payload.pop(missing_field)
        resp = api.post(self.endpoint, json=payload)
        assert resp.status_code == 422
        data = resp.json()
        assert "detail" in data
        assert any(err.get("loc", [None, None])[-1] == missing_field for err in data["detail"])  # type: ignore[index]

    @pytest.mark.parametrize("field,value", [("email", 123), ("password", 456)])
    def test_signin_invalid_types(self, api, valid_signin_payload, field, value):
        payload = valid_signin_payload.copy()
        payload[field] = value
        resp = api.post(self.endpoint, json=payload)
        assert resp.status_code == 422
        data = resp.json()
        assert "detail" in data
