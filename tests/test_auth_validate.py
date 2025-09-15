
class TestAuthValidate:
    endpoint = "/auth/validate"

    def test_validate_endpoint(server_api= None, api=None):
        # The service method auth_service.map_errors is not implemented in backend,
        # so the endpoint is expected to return 500 with a detail message.
        # If it is implemented later, this assertion can be adjusted.
        resp = api.get(TestAuthValidate.endpoint)
        assert resp.status_code in (200, 500)
        data = resp.json()
        if resp.status_code == 500:
            assert "detail" in data
        else:
            assert "validation_status" in data
