import pytest


class TestAuthSignup:
    endpoint = "/auth/signup"

    def test_signup_success(self, api, valid_signup_payload):
        resp = api.post(self.endpoint, json=valid_signup_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        # Response model SignUpSuccessResponse has only message
        assert data.get("message") == "User signed up successfully."
        # Ensure no sensitive data leaked
        assert "password" not in data

    def test_signup_existing_email_conflict(self, api, existing_email_signup_payload):
        resp = api.post(self.endpoint, json=existing_email_signup_payload)
        assert resp.status_code == 400
        data = resp.json()
        assert "detail" in data
        assert "already exists" in str(data.get("detail"))

    @pytest.mark.parametrize(
        "missing_field",
        ["firstName", "lastName", "email", "password"],
    )
    def test_signup_missing_required_field(self, api, valid_signup_payload, missing_field):
        payload = valid_signup_payload.copy()
        payload.pop(missing_field)
        resp = api.post(self.endpoint, json=payload)
        assert resp.status_code == 422
        data = resp.json()
        # FastAPI validation error structure
        assert "detail" in data
        assert any(err.get("loc", [None, None])[-1] == missing_field for err in data["detail"])  # type: ignore[index]

    @pytest.mark.parametrize(
        "field,value",
        [
            ("firstName", 123),
            ("lastName", 456),
            ("email", 789),
            ("password", 111),
        ],
    )
    def test_signup_invalid_types(self, api, valid_signup_payload, field, value):
        payload = valid_signup_payload.copy()
        payload[field] = value
        resp = api.post(self.endpoint, json=payload)
        assert resp.status_code == 422
        data = resp.json()
        assert "detail" in data

    def test_signup_ignores_extra_fields(self, api, valid_signup_payload):
        payload = valid_signup_payload.copy()
        payload["role"] = "ADMIN"  # extra field not in model, should be ignored
        resp = api.post(self.endpoint, json=payload)
        # Pydantic default extra is ignore -> still success
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("message") == "User signed up successfully."
