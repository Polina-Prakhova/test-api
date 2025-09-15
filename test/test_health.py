"""
Health endpoint tests.
"""
import pytest


class TestHealthEndpoints:
    """Test health and basic endpoints."""

    def test_health_check(self, api_client, base_url):
        """Test health check endpoint."""
        response = api_client.get(f"{base_url}/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_root_endpoint(self, api_client, base_url):
        """Test root endpoint."""
        response = api_client.get(f"{base_url}/")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

    def test_health_endpoint_methods(self, api_client, base_url):
        """Test health endpoint only accepts GET method."""
        # POST should not be allowed
        response = api_client.post(f"{base_url}/health")
        assert response.status_code in [405, 404]  # Method not allowed or not found
        
        # PUT should not be allowed
        response = api_client.put(f"{base_url}/health")
        assert response.status_code in [405, 404]
        
        # DELETE should not be allowed
        response = api_client.delete(f"{base_url}/health")
        assert response.status_code in [405, 404]

    def test_root_endpoint_methods(self, api_client, base_url):
        """Test root endpoint only accepts GET method."""
        # POST should not be allowed
        response = api_client.post(f"{base_url}/")
        assert response.status_code in [405, 404]
        
        # PUT should not be allowed
        response = api_client.put(f"{base_url}/")
        assert response.status_code in [405, 404]
        
        # DELETE should not be allowed
        response = api_client.delete(f"{base_url}/")
        assert response.status_code in [405, 404]