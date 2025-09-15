"""
Authentication API Tests.

This module contains comprehensive tests for authentication endpoints
including signup, signin, validation, and security scenarios.
"""

import pytest
import requests
from typing import Dict, Any

from tests.utils.api_client import APIClient
from tests.utils.validators import validator
from tests.utils.test_data import test_data
from tests.config import api_config, test_config


class TestAuthenticationEndpoints:
    """Test suite for authentication endpoints."""
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_signup_success(
        self,
        api_client: APIClient,
        test_user_data: Dict[str, str],
        cleanup_test_user
    ):
        """Test successful user registration."""
        # Register user for cleanup
        cleanup_test_user(test_user_data["email"])
        
        # Make signup request
        response = api_client.post(
            api_config.auth_endpoints["signup"],
            data=test_user_data
        )
        
        # Assertions
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        
        response_data = response.json()
        assert "message" in response_data
        assert response_data["message"] == "User registered successfully"
        
        # Validate response schema
        validator.validate_response(response_data, "signup_success")
    
    @pytest.mark.positive
    def test_signup_existing_user(self, api_client: APIClient):
        """Test signup with existing user email."""
        existing_user_data = test_data.generate_user_data(
            email=test_config.EXISTING_USER_EMAIL
        )
        
        response = api_client.post(
            api_config.auth_endpoints["signup"],
            data=existing_user_data
        )
        
        # Should return conflict status
        assert response.status_code == 409, f"Expected 409, got {response.status_code}"
        
        response_data = response.json()
        assert "message" in response_data
        assert "already exists" in response_data["message"].lower()
        
        # Validate response schema
        validator.validate_response(response_data, "signup_fail")
    
    @pytest.mark.negative
    @pytest.mark.parametrize("invalid_data_type", [
        "empty_strings",
        "null_values",
        "invalid_email",
        "short_password"
    ])
    def test_signup_invalid_data(
        self,
        api_client: APIClient,
        invalid_data_variants: Dict[str, Dict[str, Any]],
        invalid_data_type: str
    ):
        """Test signup with various invalid data."""
        invalid_data = invalid_data_variants[invalid_data_type]
        
        response = api_client.post(
            api_config.auth_endpoints["signup"],
            data=invalid_data
        )
        
        # Should return validation error
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
        
        response_data = response.json()
        assert "detail" in response_data or "message" in response_data
    
    @pytest.mark.negative
    def test_signup_missing_fields(self, api_client: APIClient):
        """Test signup with missing required fields."""
        incomplete_data = {"firstName": "John"}
        
        response = api_client.post(
            api_config.auth_endpoints["signup"],
            data=incomplete_data
        )
        
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_signin_success(
        self,
        api_client: APIClient,
        valid_signin_data: Dict[str, str]
    ):
        """Test successful user sign-in."""
        response = api_client.post(
            api_config.auth_endpoints["signin"],
            data=valid_signin_data
        )
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert "accessToken" in response_data
        assert "username" in response_data
        assert "role" in response_data
        
        # Validate JWT token format
        assert validator.validate_jwt_token(response_data["accessToken"])
        
        # Validate response schema
        validator.validate_response(response_data, "signin_response")
        
        # Validate business rules
        business_rules = {
            "username_not_empty": {
                "field": "username",
                "condition": "not_empty"
            },
            "valid_role": {
                "field": "role",
                "value": "CLIENT",
                "condition": "equals"
            }
        }
        errors = validator.validate_business_rules(response_data, business_rules)
        assert not errors, f"Business rule violations: {errors}"
    
    @pytest.mark.negative
    def test_signin_invalid_credentials(
        self,
        api_client: APIClient,
        invalid_signin_data: Dict[str, str]
    ):
        """Test sign-in with invalid credentials."""
        response = api_client.post(
            api_config.auth_endpoints["signin"],
            data=invalid_signin_data
        )
        
        # Should return unauthorized status
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        response_data = response.json()
        assert "detail" in response_data
        assert "invalid" in response_data["detail"].lower()
    
    @pytest.mark.negative
    def test_signin_missing_credentials(self, api_client: APIClient):
        """Test sign-in with missing credentials."""
        response = api_client.post(
            api_config.auth_endpoints["signin"],
            data={}
        )
        
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    @pytest.mark.negative
    @pytest.mark.parametrize("field,value", [
        ("email", ""),
        ("email", None),
        ("password", ""),
        ("password", None),
        ("email", "invalid-email"),
    ])
    def test_signin_invalid_field_values(
        self,
        api_client: APIClient,
        field: str,
        value: Any
    ):
        """Test sign-in with invalid field values."""
        signin_data = {
            "email": test_config.TEST_USER_EMAIL,
            "password": test_config.TEST_USER_PASSWORD
        }
        signin_data[field] = value
        
        response = api_client.post(
            api_config.auth_endpoints["signin"],
            data=signin_data
        )
        
        assert response.status_code in [400, 401, 422], f"Expected 400, 401, or 422, got {response.status_code}"
    
    @pytest.mark.positive
    def test_validate_endpoint(self, api_client: APIClient):
        """Test validation endpoint."""
        response = api_client.get(api_config.auth_endpoints["validate"])
        
        # This endpoint should return validation status
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert "validation_status" in response_data
    
    @pytest.mark.security
    def test_sql_injection_protection(self, api_client: APIClient):
        """Test protection against SQL injection attacks."""
        malicious_data = {
            "email": "admin@example.com'; DROP TABLE users; --",
            "password": "password"
        }
        
        response = api_client.post(
            api_config.auth_endpoints["signin"],
            data=malicious_data
        )
        
        # Should not cause server error, should return proper error response
        assert response.status_code in [400, 401, 422], f"Expected error status, got {response.status_code}"
    
    @pytest.mark.security
    def test_xss_protection(self, api_client: APIClient):
        """Test protection against XSS attacks."""
        xss_data = test_data.generate_user_data(
            first_name="<script>alert('xss')</script>",
            last_name="<img src=x onerror=alert('xss')>",
            email="test@example.com"
        )
        
        response = api_client.post(
            api_config.auth_endpoints["signup"],
            data=xss_data
        )
        
        # Should handle XSS attempts gracefully
        assert response.status_code in [201, 400, 422], f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 201:
            # If successful, ensure no script tags in response
            response_text = response.text.lower()
            assert "<script>" not in response_text
            assert "onerror=" not in response_text
    
    @pytest.mark.security
    def test_password_complexity_enforcement(self, api_client: APIClient):
        """Test password complexity requirements."""
        weak_passwords = [
            "123",
            "password",
            "abc",
            "111111",
            ""
        ]
        
        for weak_password in weak_passwords:
            user_data = test_data.generate_user_data(password=weak_password)
            
            response = api_client.post(
                api_config.auth_endpoints["signup"],
                data=user_data
            )
            
            # Should reject weak passwords
            assert response.status_code in [400, 422], f"Weak password '{weak_password}' was accepted"
    
    @pytest.mark.security
    def test_rate_limiting_protection(self, api_client: APIClient):
        """Test rate limiting on authentication endpoints."""
        invalid_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        # Make multiple rapid requests
        responses = []
        for _ in range(10):
            response = api_client.post(
                api_config.auth_endpoints["signin"],
                data=invalid_data
            )
            responses.append(response.status_code)
        
        # Should eventually return rate limit error (429) or continue returning 401
        # The exact behavior depends on rate limiting implementation
        assert all(status in [401, 429] for status in responses), f"Unexpected status codes: {responses}"
    
    @pytest.mark.integration
    def test_signup_signin_flow(self, api_client: APIClient, cleanup_test_user):
        """Test complete signup and signin flow."""
        # Generate unique user data
        user_data = test_data.generate_user_data()
        cleanup_test_user(user_data["email"])
        
        # Step 1: Sign up
        signup_response = api_client.post(
            api_config.auth_endpoints["signup"],
            data=user_data
        )
        assert signup_response.status_code == 201
        
        # Step 2: Sign in with the same credentials
        signin_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        signin_response = api_client.post(
            api_config.auth_endpoints["signin"],
            data=signin_data
        )
        assert signin_response.status_code == 200
        
        # Validate signin response
        signin_data = signin_response.json()
        assert "accessToken" in signin_data
        assert validator.validate_jwt_token(signin_data["accessToken"])
    
    @pytest.mark.performance
    def test_auth_endpoint_response_time(
        self,
        api_client: APIClient,
        valid_signin_data: Dict[str, str]
    ):
        """Test authentication endpoint response time."""
        import time
        
        start_time = time.time()
        response = api_client.post(
            api_config.auth_endpoints["signin"],
            data=valid_signin_data
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Response should be within reasonable time (adjust threshold as needed)
        assert response_time < 5.0, f"Response time too slow: {response_time}s"
        assert response.status_code == 200
    
    @pytest.mark.negative
    def test_malformed_json_request(self, api_client: APIClient):
        """Test handling of malformed JSON requests."""
        # Send malformed JSON
        response = api_client.session.post(
            api_config.auth_endpoints["signin"],
            data="{'invalid': json}",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    @pytest.mark.negative
    def test_unsupported_content_type(self, api_client: APIClient):
        """Test handling of unsupported content types."""
        response = api_client.session.post(
            api_config.auth_endpoints["signin"],
            data="email=test@example.com&password=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should handle gracefully or return appropriate error
        assert response.status_code in [400, 415, 422], f"Unexpected status code: {response.status_code}"