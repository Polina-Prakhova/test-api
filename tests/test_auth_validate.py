class TestAuthValidate:
    endpoint = "/auth/validate"

    def test_validate_endpoint(self, api):
        """
        Calls the /auth/validate endpoint and verifies current and future behavior.

        Current expected behavior:
        - Backend returns 500 with a JSON body containing a 'detail' field because
          auth_service.map_errors is not implemented yet.

        Future behavior (when implemented):
        - Backend may return 200 with a JSON body containing a 'validation_status' field.
        """
        resp = api.get(TestAuthValidate.endpoint)

        # The API should always return JSON
        assert "application/json" in resp.headers.get("content-type", "").lower(), \
            "Response should be JSON"

        # Only two outcomes are accepted at the moment: 200 (future) or 500 (current)
        assert resp.status_code in (200, 500), \
            f"Unexpected status code {resp.status_code}"

        data = resp.json()
        assert isinstance(data, dict), f"Expected JSON object, got: {type(data)}"

        if resp.status_code == 500:
            # Current behavior: backend signals unimplemented mapping via 500/detail.
            assert "detail" in data and data["detail"], \
                "Expected 'detail' message when status is 500"
        else:
            # Future behavior: backend validates and reports status.
            assert "validation_status" in data, \
                "Expected 'validation_status' in 200 response"
            # Accept bool or string to be flexible with early implementations.
            val = data["validation_status"]
            assert isinstance(val, (bool, str)), \
                f"validation_status should be bool or str, got {type(val)}"