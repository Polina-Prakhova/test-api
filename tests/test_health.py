"""
Health Check API Tests.

This module contains tests for health check and basic API endpoints
to ensure the API is running and accessible.
"""

import pytest
import requests
from typing import Dict, Any

from tests.utils.api_client import APIClient
from tests.utils.validators import validator
from tests.config import api_config


class TestHealthEndpoints:
    """Test suite for health check endpoints."""
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_health_check_endpoint(self, api_client: APIClient):
        """Test health check endpoint returns OK status."""
        response = api_client.get(api_config.health_endpoints["health"])
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert "status" in response_data
        assert response_data["status"] == "ok"
        
        # Validate response schema
        validator.validate_response(response_data, "health_response")
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_root_endpoint(self, api_client: APIClient):
        """Test root endpoint returns welcome message."""
        response = api_client.get(api_config.health_endpoints["root"])
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert "message" in response_data
        assert response_data["message"] == "Hello World"
        
        # Validate response schema
        validator.validate_response(response_data, "root_response")
    
    @pytest.mark.positive
    def test_health_endpoint_response_headers(self, api_client: APIClient):
        """Test health endpoint returns proper response headers."""
        response = api_client.get(api_config.health_endpoints["health"])
        
        assert response.status_code == 200
        
        # Check for common headers
        headers = response.headers
        assert "content-type" in headers
        assert "application/json" in headers["content-type"].lower()
    
    @pytest.mark.performance
    def test_health_endpoint_response_time(self, api_client: APIClient):
        """Test health endpoint response time."""
        import time
        
        start_time = time.time()
        response = api_client.get(api_config.health_endpoints["health"])
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Health check should be very fast
        assert response_time < 2.0, f"Health check too slow: {response_time}s"
        assert response.status_code == 200
    
    @pytest.mark.positive
    def test_multiple_health_checks(self, api_client: APIClient):
        """Test multiple consecutive health checks."""
        for i in range(5):
            response = api_client.get(api_config.health_endpoints["health"])
            assert response.status_code == 200, f"Health check {i+1} failed"
            
            response_data = response.json()
            assert response_data["status"] == "ok"
    
    @pytest.mark.negative
    def test_invalid_health_endpoint_method(self, api_client: APIClient):
        """Test health endpoint with invalid HTTP methods."""
        # Health endpoint should only accept GET
        response = api_client.post(api_config.health_endpoints["health"])
        assert response.status_code == 405, f"Expected 405, got {response.status_code}"
        
        response = api_client.put(api_config.health_endpoints["health"])
        assert response.status_code == 405, f"Expected 405, got {response.status_code}"
        
        response = api_client.delete(api_config.health_endpoints["health"])
        assert response.status_code == 405, f"Expected 405, got {response.status_code}"
    
    @pytest.mark.negative
    def test_nonexistent_endpoint(self, api_client: APIClient):
        """Test request to non-existent endpoint."""
        response = api_client.get(f"{api_config.BASE_URL}/nonexistent")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    @pytest.mark.integration
    def test_api_availability(self, api_client: APIClient):
        """Test overall API availability by checking multiple endpoints."""
        endpoints_to_check = [
            api_config.health_endpoints["health"],
            api_config.health_endpoints["root"]
        ]
        
        for endpoint in endpoints_to_check:
            response = api_client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} is not available"
    
    @pytest.mark.security
    def test_health_endpoint_no_sensitive_info(self, api_client: APIClient):
        """Test that health endpoint doesn't expose sensitive information."""
        response = api_client.get(api_config.health_endpoints["health"])
        
        assert response.status_code == 200
        
        response_text = response.text.lower()
        
        # Check that no sensitive information is exposed
        sensitive_keywords = [
            "password", "secret", "key", "token", "database", 
            "connection", "config", "env", "credential"
        ]
        
        for keyword in sensitive_keywords:
            assert keyword not in response_text, f"Sensitive keyword '{keyword}' found in health response"
    
    @pytest.mark.positive
    def test_cors_headers(self, api_client: APIClient):
        """Test CORS headers in health endpoint response."""
        response = api_client.get(api_config.health_endpoints["health"])
        
        assert response.status_code == 200
        
        # Check for CORS headers (if implemented)
        headers = response.headers
        
        # These are optional but good to have
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers"
        ]
        
        # Log which CORS headers are present (not asserting as they might not be implemented)
        present_cors_headers = [h for h in cors_headers if h in headers]
        if present_cors_headers:
            print(f"CORS headers present: {present_cors_headers}")
    
    @pytest.mark.regression
    def test_health_endpoint_consistency(self, api_client: APIClient):
        """Test that health endpoint returns consistent responses."""
        responses = []
        
        # Make multiple requests
        for _ in range(3):
            response = api_client.get(api_config.health_endpoints["health"])
            assert response.status_code == 200
            responses.append(response.json())
        
        # All responses should be identical
        first_response = responses[0]
        for response in responses[1:]:
            assert response == first_response, "Health endpoint responses are inconsistent"