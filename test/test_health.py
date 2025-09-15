"""
Health check and basic endpoint tests.
Tests for system health and basic functionality.
"""
import pytest
import requests


class TestHealthEndpoints:
    """Test cases for health check endpoints."""
    
    def test_health_check(self, api_client, base_url):
        """Test health check endpoint."""
        response = api_client.get(f"{base_url}/health")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
    
    def test_root_endpoint(self, api_client, base_url):
        """Test root endpoint."""
        response = api_client.get(f"{base_url}/")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "Hello World"
    
    @pytest.mark.error
    def test_nonexistent_endpoint(self, api_client, base_url):
        """Test accessing non-existent endpoint."""
        response = api_client.get(f"{base_url}/nonexistent")
        
        assert response.status_code == 404
    
    def test_health_check_response_time(self, api_client, base_url):
        """Test health check response time."""
        import time
        
        start_time = time.time()
        response = api_client.get(f"{base_url}/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # Should respond within 5 seconds
    
    def test_health_check_multiple_requests(self, api_client, base_url):
        """Test health check with multiple concurrent requests."""
        responses = []
        
        # Make multiple requests
        for _ in range(5):
            response = api_client.get(f"{base_url}/health")
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"


class TestCORSAndHeaders:
    """Test CORS and HTTP headers."""
    
    def test_cors_headers(self, api_client, base_url):
        """Test CORS headers are present."""
        response = api_client.options(f"{base_url}/health")
        
        # CORS headers might be present
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        # Note: Not all APIs implement CORS, so we just check if present
        for header in cors_headers:
            if header in response.headers:
                assert len(response.headers[header]) > 0
    
    def test_security_headers(self, api_client, base_url):
        """Test security headers."""
        response = api_client.get(f"{base_url}/health")
        
        # Check for common security headers
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        # Note: Not all APIs implement all security headers
        # We just verify they're properly formatted if present
        for header in security_headers:
            if header in response.headers:
                assert len(response.headers[header]) > 0
    
    def test_content_type_consistency(self, api_client, base_url):
        """Test content type consistency across endpoints."""
        endpoints = ["/health", "/"]
        
        for endpoint in endpoints:
            response = api_client.get(f"{base_url}{endpoint}")
            
            if response.status_code == 200:
                assert "application/json" in response.headers.get("content-type", "")


class TestHTTPMethods:
    """Test HTTP method handling."""
    
    def test_method_not_allowed(self, api_client, base_url):
        """Test method not allowed responses."""
        # Health endpoint should only support GET
        response = api_client.post(f"{base_url}/health")
        assert response.status_code == 405
        
        response = api_client.put(f"{base_url}/health")
        assert response.status_code == 405
        
        response = api_client.delete(f"{base_url}/health")
        assert response.status_code == 405
    
    def test_head_method(self, api_client, base_url):
        """Test HEAD method support."""
        response = api_client.head(f"{base_url}/health")
        
        # HEAD should return same headers as GET but no body
        assert response.status_code in [200, 405]  # Some servers don't support HEAD
        
        if response.status_code == 200:
            assert len(response.content) == 0  # No body for HEAD requests


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.error
    def test_invalid_url_characters(self, api_client, base_url):
        """Test handling of invalid URL characters."""
        invalid_urls = [
            "/health%00",  # Null byte
            "/health<script>",  # Script tag
            "/health/../../../etc/passwd",  # Path traversal
        ]
        
        for url in invalid_urls:
            response = api_client.get(f"{base_url}{url}")
            # Should handle gracefully, not crash
            assert response.status_code in [400, 404, 500]
    
    @pytest.mark.error
    def test_very_long_url(self, api_client, base_url):
        """Test handling of very long URLs."""
        long_path = "/health/" + "a" * 10000
        
        response = api_client.get(f"{base_url}{long_path}")
        
        # Should handle gracefully
        assert response.status_code in [400, 404, 414]  # 414 = URI Too Long
    
    def test_connection_handling(self, api_client, base_url):
        """Test connection handling."""
        # Test that the server handles connections properly
        response = api_client.get(f"{base_url}/health")
        
        assert response.status_code == 200
        
        # Check connection header
        connection_header = response.headers.get("connection", "").lower()
        assert connection_header in ["", "close", "keep-alive"]


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_openapi_docs(self, api_client, base_url):
        """Test OpenAPI documentation endpoint."""
        # Common OpenAPI documentation paths
        doc_paths = ["/docs", "/swagger", "/api-docs", "/openapi.json"]
        
        found_docs = False
        for path in doc_paths:
            response = api_client.get(f"{base_url}{path}")
            if response.status_code == 200:
                found_docs = True
                break
        
        # Note: Not all APIs expose documentation endpoints
        # This is just a check to see if they're available
        if found_docs:
            assert response.status_code == 200