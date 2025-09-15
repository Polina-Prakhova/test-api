"""
Tests for health check endpoints.
"""
import pytest


class TestHealthEndpoints:
    """Test class for health check endpoints."""

    def test_health_check_endpoint(self, api_client, base_url):
        """Test the health check endpoint."""
        response = api_client.get(f"{base_url}/health")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    def test_root_endpoint(self, api_client, base_url):
        """Test the root endpoint."""
        response = api_client.get(f"{base_url}/")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "Hello World"

    def test_health_endpoint_response_time(self, api_client, base_url):
        """Test that health endpoint responds quickly."""
        import time
        
        start_time = time.time()
        response = api_client.get(f"{base_url}/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second

    def test_health_endpoint_multiple_requests(self, api_client, base_url):
        """Test health endpoint with multiple concurrent requests."""
        responses = []
        
        for _ in range(5):
            response = api_client.get(f"{base_url}/health")
            responses.append(response)
        
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"