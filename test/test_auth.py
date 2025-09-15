"""
Tests for authentication endpoints.
"""
import pytest


class TestAuthEndpoints:
    """Test class for authentication endpoints."""

    def test_signup_success(self, api_client, base_url, new_user_data):
        """Test successful user signup."""
        response = api_client.post(f"{base_url}/auth/signup", json=new_user_data)
        
        assert response.status_code == 201
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "User signed up successfully."

    def test_signup_existing_user_conflict(self, api_client, base_url, existing_user_email):
        """Test signup with existing user email returns conflict."""
        user_data = {
            "firstName": "Test",
            "lastName": "User",
            "email": existing_user_email,
            "password": "TestPassword123"
        }
        
        response = api_client.post(f"{base_url}/auth/signup", json=user_data)
        
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_signup_invalid_data(self, api_client, base_url):
        """Test signup with invalid data."""
        invalid_data = {
            "firstName": "",
            "lastName": "",
            "email": "invalid-email",
            "password": ""
        }
        
        response = api_client.post(f"{base_url}/auth/signup", json=invalid_data)
        
        assert response.status_code in [400, 422]

    def test_signup_missing_fields(self, api_client, base_url):
        """Test signup with missing required fields."""
        incomplete_data = {
            "firstName": "John"
            # Missing lastName, email, password
        }
        
        response = api_client.post(f"{base_url}/auth/signup", json=incomplete_data)
        
        assert response.status_code in [400, 422]

    def test_signin_success(self, api_client, base_url, test_user_credentials):
        """Test successful user signin."""
        response = api_client.post(f"{base_url}/auth/signin", json=test_user_credentials)
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "message" in data
        assert "user" in data
        assert data["message"] == "Sign in successful."
        
        user_data = data["user"]
        assert "accessToken" in user_data
        assert "username" in user_data
        assert "role" in user_data
        assert user_data["accessToken"] is not None
        assert len(user_data["accessToken"]) > 0

    def test_signin_invalid_credentials(self, api_client, base_url):
        """Test signin with invalid credentials."""
        invalid_credentials = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        
        response = api_client.post(f"{base_url}/auth/signin", json=invalid_credentials)
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_signin_missing_fields(self, api_client, base_url):
        """Test signin with missing fields."""
        incomplete_data = {
            "email": "test@example.com"
            # Missing password
        }
        
        response = api_client.post(f"{base_url}/auth/signin", json=incomplete_data)
        
        assert response.status_code in [400, 422]

    def test_signin_empty_credentials(self, api_client, base_url):
        """Test signin with empty credentials."""
        empty_credentials = {
            "email": "",
            "password": ""
        }
        
        response = api_client.post(f"{base_url}/auth/signin", json=empty_credentials)
        
        assert response.status_code == 401

    def test_validate_endpoint(self, api_client, base_url):
        """Test the validate endpoint."""
        response = api_client.get(f"{base_url}/auth/validate")
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "validation_status" in data

    def test_signin_response_structure(self, api_client, base_url, test_user_credentials):
        """Test signin response structure and data types."""
        response = api_client.post(f"{base_url}/auth/signin", json=test_user_credentials)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert isinstance(data, dict)
        assert "message" in data
        assert "user" in data
        
        user_data = data["user"]
        assert isinstance(user_data["accessToken"], str)
        assert isinstance(user_data["username"], str)
        assert isinstance(user_data["role"], str)
        
        # Validate token format (basic check)
        token = user_data["accessToken"]
        assert len(token) > 10  # Token should be reasonably long
        
        # Validate role values
        assert user_data["role"] in ["CLIENT", "ADMIN", "WAITER"]

    def test_auth_endpoints_content_type(self, api_client, base_url, test_user_credentials):
        """Test that auth endpoints return correct content type."""
        # Test signin
        response = api_client.post(f"{base_url}/auth/signin", json=test_user_credentials)
        assert "application/json" in response.headers.get("content-type", "")
        
        # Test signup
        new_user = {
            "firstName": "ContentType",
            "lastName": "Test",
            "email": "contenttype@example.com",
            "password": "TestPassword123"
        }
        response = api_client.post(f"{base_url}/auth/signup", json=new_user)
        assert "application/json" in response.headers.get("content-type", "")

    def test_auth_sql_injection_protection(self, api_client, base_url):
        """Test protection against SQL injection in auth endpoints."""
        sql_injection_payload = {
            "email": "test@example.com'; DROP TABLE users; --",
            "password": "password"
        }
        
        response = api_client.post(f"{base_url}/auth/signin", json=sql_injection_payload)
        
        # Should return 401 (unauthorized) not 500 (server error)
        assert response.status_code == 401

    def test_auth_xss_protection(self, api_client, base_url):
        """Test protection against XSS in auth endpoints."""
        xss_payload = {
            "firstName": "<script>alert('xss')</script>",
            "lastName": "<img src=x onerror=alert('xss')>",
            "email": "xss@example.com",
            "password": "password"
        }
        
        response = api_client.post(f"{base_url}/auth/signup", json=xss_payload)
        
        # Should handle gracefully, not execute script
        assert response.status_code in [201, 400, 422]