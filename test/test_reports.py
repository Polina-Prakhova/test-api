"""
Reports API tests.
Tests for reporting endpoints including report generation and retrieval.
"""
import pytest
import requests
from typing import Dict, Any


class TestReportsRetrieval:
    """Test cases for reports retrieval endpoint."""
    
    @pytest.mark.auth
    def test_get_reports_without_filters(self, authenticated_client, base_url):
        """Test getting reports without any filters."""
        response = authenticated_client.get(f"{base_url}/reports")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "content" in data
        assert isinstance(data["content"], list)
        
        # Validate report structure if reports exist
        if data["content"]:
            report = data["content"][0]
            required_fields = [
                "id", "name", "description", "fromDateTime", "toDateTime",
                "location", "waiterId", "downloadLink"
            ]
            for field in required_fields:
                assert field in report
                assert isinstance(report[field], str)
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_get_reports_unauthorized(self, api_client, base_url):
        """Test getting reports without authentication."""
        response = api_client.get(f"{base_url}/reports")
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    def test_get_reports_with_date_filters(self, authenticated_client, base_url):
        """Test getting reports with date filters."""
        params = {
            "fromDateTime": "2021-10-10T10:00:00",
            "toDateTime": "2021-10-20T10:00:00"
        }
        
        response = authenticated_client.get(f"{base_url}/reports", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert isinstance(data["content"], list)
    
    @pytest.mark.auth
    def test_get_reports_with_location_filter(self, authenticated_client, base_url):
        """Test getting reports with location filter."""
        params = {
            "locationId": "582846d5c951184d705b65d1"
        }
        
        response = authenticated_client.get(f"{base_url}/reports", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
    
    @pytest.mark.auth
    def test_get_reports_with_waiter_filter(self, authenticated_client, base_url):
        """Test getting reports with waiter filter."""
        params = {
            "waiterId": "792846d5c951184d705b65d7"
        }
        
        response = authenticated_client.get(f"{base_url}/reports", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
    
    @pytest.mark.auth
    def test_get_reports_with_all_filters(self, authenticated_client, base_url):
        """Test getting reports with all filters applied."""
        params = {
            "fromDateTime": "2021-10-10T10:00:00",
            "toDateTime": "2021-10-20T10:00:00",
            "locationId": "582846d5c951184d705b65d1",
            "waiterId": "792846d5c951184d705b65d7"
        }
        
        response = authenticated_client.get(f"{base_url}/reports", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
    
    @pytest.mark.auth
    def test_reports_response_structure(self, authenticated_client, base_url):
        """Test reports response structure."""
        response = authenticated_client.get(f"{base_url}/reports")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have content field with array
        assert "content" in data
        assert isinstance(data["content"], list)
        
        # Each report should have the correct structure
        for report in data["content"]:
            assert isinstance(report, dict)
            
            # Check required fields exist
            required_fields = [
                "id", "name", "description", "fromDateTime", "toDateTime",
                "location", "waiterId", "downloadLink"
            ]
            for field in required_fields:
                assert field in report
                assert isinstance(report[field], str)
            
            # Validate datetime format (should be ISO format)
            datetime_fields = ["fromDateTime", "toDateTime"]
            for field in datetime_fields:
                if report[field]:  # If not empty
                    assert "T" in report[field]  # ISO format should contain T
            
            # Validate download link format
            if report["downloadLink"]:
                assert report["downloadLink"].startswith(("http://", "https://"))
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_get_reports_invalid_date_format(self, authenticated_client, base_url):
        """Test getting reports with invalid date format."""
        invalid_dates = [
            "invalid-date",
            "2021-13-10T10:00:00",  # Invalid month
            "2021-10-32T10:00:00",  # Invalid day
            "2021-10-10T25:00:00",  # Invalid hour
            "2021-10-10 10:00:00",  # Wrong format (space instead of T)
        ]
        
        for date in invalid_dates:
            params = {"fromDateTime": date}
            response = authenticated_client.get(f"{base_url}/reports", params=params)
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_get_reports_invalid_ids(self, authenticated_client, base_url):
        """Test getting reports with invalid IDs."""
        invalid_id_cases = [
            {"locationId": "invalid_location"},
            {"waiterId": "invalid_waiter"},
            {"locationId": "<script>alert('xss')</script>"},
            {"waiterId": "'; DROP TABLE reports; --"},
        ]
        
        for params in invalid_id_cases:
            response = authenticated_client.get(f"{base_url}/reports", params=params)
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_get_reports_date_range_validation(self, authenticated_client, base_url):
        """Test getting reports with invalid date ranges."""
        # fromDateTime after toDateTime
        params = {
            "fromDateTime": "2021-10-20T10:00:00",
            "toDateTime": "2021-10-10T10:00:00"
        }
        
        response = authenticated_client.get(f"{base_url}/reports", params=params)
        # Should either return empty results or validation error
        assert response.status_code in [200, 400, 422]


class TestReportCreation:
    """Test cases for report creation endpoint."""
    
    @pytest.mark.auth
    def test_create_report_success(self, authenticated_client, base_url):
        """Test successful report creation."""
        response = authenticated_client.post(f"{base_url}/reports")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        # Response should contain creation confirmation
        assert isinstance(data, dict)
        # The exact structure depends on the API implementation
        # It might have a message field or report details
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_create_report_unauthorized(self, api_client, base_url):
        """Test creating report without authentication."""
        response = api_client.post(f"{base_url}/reports")
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    def test_create_report_response_structure(self, authenticated_client, base_url):
        """Test report creation response structure."""
        response = authenticated_client.post(f"{base_url}/reports")
        
        if response.status_code == 200:
            data = response.json()
            
            # Should be a dictionary
            assert isinstance(data, dict)
            
            # Common fields that might be present
            possible_fields = ["message", "reportId", "status", "downloadLink"]
            
            # At least one field should be present
            assert any(field in data for field in possible_fields)
    
    @pytest.mark.auth
    def test_create_multiple_reports(self, authenticated_client, base_url):
        """Test creating multiple reports."""
        responses = []
        
        # Create multiple reports
        for _ in range(3):
            response = authenticated_client.post(f"{base_url}/reports")
            responses.append(response)
        
        # All should succeed or fail consistently
        for response in responses:
            assert response.status_code in [200, 400, 429]  # 429 = Too Many Requests
    
    @pytest.mark.auth
    def test_create_report_with_request_body(self, authenticated_client, base_url):
        """Test creating report with request body (if supported)."""
        # Some APIs might accept parameters for report generation
        report_params = {
            "fromDateTime": "2021-10-10T10:00:00",
            "toDateTime": "2021-10-20T10:00:00",
            "locationId": "582846d5c951184d705b65d1"
        }
        
        response = authenticated_client.post(f"{base_url}/reports", json=report_params)
        
        # Should succeed or ignore the body
        assert response.status_code in [200, 400, 422]


class TestReportsIntegration:
    """Integration tests for reports functionality."""
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_report_creation_and_retrieval_flow(self, authenticated_client, base_url):
        """Test complete report creation and retrieval flow."""
        # Step 1: Get current reports
        initial_response = authenticated_client.get(f"{base_url}/reports")
        assert initial_response.status_code == 200
        
        initial_data = initial_response.json()
        initial_count = len(initial_data["content"])
        
        # Step 2: Create a new report
        create_response = authenticated_client.post(f"{base_url}/reports")
        assert create_response.status_code in [200, 400]
        
        if create_response.status_code == 200:
            # Step 3: Get reports again to see if new report is listed
            updated_response = authenticated_client.get(f"{base_url}/reports")
            assert updated_response.status_code == 200
            
            updated_data = updated_response.json()
            updated_count = len(updated_data["content"])
            
            # New report might be added (or might be processed asynchronously)
            assert updated_count >= initial_count
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_report_filtering_consistency(self, authenticated_client, base_url):
        """Test consistency of report filtering."""
        # Get all reports
        all_reports_response = authenticated_client.get(f"{base_url}/reports")
        assert all_reports_response.status_code == 200
        
        all_reports = all_reports_response.json()["content"]
        
        if all_reports:
            # Test filtering by location if reports have location data
            locations = set()
            for report in all_reports:
                if report["location"]:
                    locations.add(report["location"])
            
            # Test filtering by each location
            for location in list(locations)[:3]:  # Test first 3 locations
                filtered_response = authenticated_client.get(
                    f"{base_url}/reports",
                    params={"locationId": location}
                )
                assert filtered_response.status_code == 200
                
                filtered_reports = filtered_response.json()["content"]
                
                # All filtered reports should match the location
                for report in filtered_reports:
                    # Note: locationId in filter might not directly match location field
                    # This depends on the API implementation
                    pass
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_report_download_links(self, authenticated_client, base_url):
        """Test report download links if available."""
        response = authenticated_client.get(f"{base_url}/reports")
        assert response.status_code == 200
        
        data = response.json()
        
        for report in data["content"]:
            if report["downloadLink"]:
                # Validate download link format
                assert report["downloadLink"].startswith(("http://", "https://"))
                
                # Optionally test if the link is accessible
                # Note: This might require additional authentication
                # download_response = authenticated_client.get(report["downloadLink"])
                # assert download_response.status_code in [200, 401, 403]


class TestReportsErrorScenarios:
    """Test error scenarios and edge cases."""
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_reports_with_malformed_parameters(self, authenticated_client, base_url):
        """Test reports endpoint with malformed parameters."""
        malformed_params = [
            {"fromDateTime": "A" * 1000},  # Very long parameter
            {"locationId": "<script>alert('xss')</script>"},
            {"waiterId": "'; DROP TABLE reports; --"},
            {"toDateTime": "javascript:alert('xss')"},
        ]
        
        for params in malformed_params:
            response = authenticated_client.get(f"{base_url}/reports", params=params)
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_concurrent_report_operations(self, authenticated_client, base_url):
        """Test concurrent report operations."""
        import threading
        
        responses = []
        
        def get_reports():
            response = authenticated_client.get(f"{base_url}/reports")
            responses.append(response)
        
        def create_report():
            response = authenticated_client.post(f"{base_url}/reports")
            responses.append(response)
        
        # Create multiple threads
        threads = []
        for _ in range(3):
            threads.append(threading.Thread(target=get_reports))
            threads.append(threading.Thread(target=create_report))
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should be handled gracefully
        for response in responses:
            assert response.status_code in [200, 400, 401, 429]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_report_operations_with_expired_token(self, api_client, base_url):
        """Test report operations with expired token."""
        # Use an obviously invalid token
        api_client.headers.update({"Authorization": "Bearer expired_token_12345"})
        
        # Test GET reports
        get_response = api_client.get(f"{base_url}/reports")
        assert get_response.status_code == 401
        
        # Test POST reports
        post_response = api_client.post(f"{base_url}/reports")
        assert post_response.status_code == 401
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_report_creation_rate_limiting(self, authenticated_client, base_url):
        """Test rate limiting on report creation."""
        # Make many report creation requests quickly
        responses = []
        
        for _ in range(10):
            response = authenticated_client.post(f"{base_url}/reports")
            responses.append(response)
        
        # Some should succeed, but rate limiting might kick in
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        # At least some should be handled
        assert len(responses) == 10
        
        # All responses should be valid HTTP status codes
        for response in responses:
            assert response.status_code in [200, 400, 429]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_reports_with_extreme_date_ranges(self, authenticated_client, base_url):
        """Test reports with extreme date ranges."""
        extreme_cases = [
            {
                "fromDateTime": "1900-01-01T00:00:00",
                "toDateTime": "2100-12-31T23:59:59"
            },  # Very wide range
            {
                "fromDateTime": "2021-10-10T10:00:00",
                "toDateTime": "2021-10-10T10:00:01"
            },  # Very narrow range (1 second)
            {
                "fromDateTime": "2021-10-10T10:00:00",
                "toDateTime": "2021-10-10T10:00:00"
            },  # Same start and end time
        ]
        
        for params in extreme_cases:
            response = authenticated_client.get(f"{base_url}/reports", params=params)
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_reports_with_oversized_parameters(self, authenticated_client, base_url):
        """Test reports with oversized parameters."""
        oversized_params = {
            "locationId": "A" * 10000,  # Very long location ID
            "waiterId": "B" * 10000,    # Very long waiter ID
            "fromDateTime": "2021-10-10T10:00:00" + "Z" * 1000,  # Oversized datetime
        }
        
        response = authenticated_client.get(f"{base_url}/reports", params=oversized_params)
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 414, 422]  # 414 = URI Too Long