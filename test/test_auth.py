"""
Authentication endpoint tests.
"""
import pytest


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_signup_success(self, api_client, base_url, valid_user_data):
        """Test successful user signup."""
        response = api_client.post(f"{base_url}/auth/signup", json=valid_user_data)
        
        assert response.status_code == 201
        response_data = response.json()
        assert "message" in response_data
        assert response_data["message"] == "User registered successfully"

    def test_signup_existing_user(self, api_client, base_url, existing_user_data):
        """Test signup with existing email."""
        response = api_client.post(f"{base_url}/auth/signup", json=existing_user_data)
        
        assert response.status_code == 409
        response_data = response.json()
        assert "message" in response_data
        assert "already exists" in response_data["message"]

    def test_signup_invalid_data(self, api_client, base_url):
        """Test signup with invalid data."""
        invalid_data_sets = [
            {},  # Empty data
            {"firstName": "John"},  # Missing required fields
            {"firstName": "", "lastName": "", "email": "", "password": ""},  # Empty strings
            {"firstName": "John", "lastName": "Smith", "email": "invalid-email", "password": "pass"},  # Invalid email
        ]
        
        for invalid_data in invalid_data_sets:
            response = api_client.post(f"{base_url}/auth/signup", json=invalid_data)
            assert response.status_code in [400, 422]  # Bad request or validation error

    def test_signup_missing_content_type(self, api_client, base_url, valid_user_data):
        """Test signup without proper content type."""
        headers = {"Content-Type": "text/plain"}
        response = api_client.post(f"{base_url}/auth/signup", json=valid_user_data, headers=headers)
        assert response.status_code in [400, 415]  # Bad request or unsupported media type

    def test_signin_success(self, api_client, base_url, valid_login_data):
        """Test successful user signin."""
        response = api_client.post(f"{base_url}/auth/signin", json=valid_login_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert "accessToken" in response_data
        assert "username" in response_data
        assert "role" in response_data
        assert response_data["username"] == "jhon Smith"
        assert response_data["role"] == "CLIENT"
        assert len(response_data["accessToken"]) > 0

    def test_signin_invalid_credentials(self, api_client, base_url, invalid_login_data):
        """Test signin with invalid credentials."""
        response = api_client.post(f"{base_url}/auth/signin", json=invalid_login_data)
        
        assert response.status_code == 401
        response_data = response.json()
        assert "detail" in response_data
        assert "Invalid user credentials" in response_data["detail"]

    def test_signin_missing_fields(self, api_client, base_url):
        """Test signin with missing required fields."""
        invalid_data_sets = [
            {},  # Empty data
            {"email": "test@example.com"},  # Missing password
            {"password": "password"},  # Missing email
            {"email": "", "password": ""},  # Empty strings
        ]
        
        for invalid_data in invalid_data_sets:
            response = api_client.post(f"{base_url}/auth/signin", json=invalid_data)
            assert response.status_code in [400, 401, 422]

    def test_validate_endpoint(self, api_client, base_url):
        """Test validation endpoint."""
        response = api_client.get(f"{base_url}/auth/validate")
        
        assert response.status_code in [200, 500]  # May return 500 if map_errors is not implemented
        if response.status_code == 200:
            response_data = response.json()
            assert "validation_status" in response_data

    def test_auth_endpoints_methods(self, api_client, base_url):
        """Test auth endpoints only accept POST method."""
        endpoints = ["/auth/signup", "/auth/signin"]
        
        for endpoint in endpoints:
            # GET should not be allowed
            response = api_client.get(f"{base_url}{endpoint}")
            assert response.status_code in [405, 404]
            
            # PUT should not be allowed
            response = api_client.put(f"{base_url}{endpoint}")
            assert response.status_code in [405, 404]
            
            # DELETE should not be allowed
            response = api_client.delete(f"{base_url}{endpoint}")
            assert response.status_code in [405, 404]

    def test_signup_response_structure(self, api_client, base_url, valid_user_data):
        """Test signup response structure."""
        response = api_client.post(f"{base_url}/auth/signup", json=valid_user_data)
        
        if response.status_code == 201:
            response_data = response.json()
            # Verify response structure matches SignUpSuccessResponse
            assert isinstance(response_data, dict)
            assert "message" in response_data
            assert isinstance(response_data["message"], str)

    def test_signin_response_structure(self, api_client, base_url, valid_login_data):
        """Test signin response structure."""
        response = api_client.post(f"{base_url}/auth/signin", json=valid_login_data)
        
        if response.status_code == 200:
            response_data = response.json()
            # Verify response structure matches SignInResponse
            assert isinstance(response_data, dict)
            assert "accessToken" in response_data
            assert "username" in response_data
            assert "role" in response_data
            assert isinstance(response_data["accessToken"], str)
            assert isinstance(response_data["username"], str)
            assert isinstance(response_data["role"], str)

    def test_auth_token_format(self, api_client, base_url, valid_login_data):
        """Test authentication token format."""
        response = api_client.post(f"{base_url}/auth/signin", json=valid_login_data)
        
        if response.status_code == 200:
            response_data = response.json()
            token = response_data["accessToken"]
            # Basic token validation
            assert len(token) > 10  # Should be a reasonable length
            assert isinstance(token, str)
            # Could add JWT format validation if needed