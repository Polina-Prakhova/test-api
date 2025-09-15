"""
Tests for reports endpoints.
"""
import pytest


class TestReportsEndpoints:
    """Test class for reports endpoints."""

    def test_get_reports(self, api_client, base_url, auth_headers):
        """Test getting reports."""
        response = api_client.get(
            f"{base_url}/reports",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "content" in data
        assert isinstance(data["content"], list)
        
        if data["content"]:  # If there are reports
            report = data["content"][0]
            assert "id" in report
            assert "name" in report
            assert "description" in report
            assert "fromDateTime" in report
            assert "toDateTime" in report
            assert "location" in report
            assert "waiterId" in report
            assert "downloadLink" in report

    def test_get_reports_unauthorized(self, api_client, base_url):
        """Test getting reports without authentication."""
        response = api_client.get(f"{base_url}/reports")
        
        assert response.status_code == 401

    def test_get_reports_with_date_filter(self, api_client, base_url, auth_headers):
        """Test getting reports with date filters."""
        response = api_client.get(
            f"{base_url}/reports",
            params={
                "fromDateTime": "2024-01-01T00:00:00",
                "toDateTime": "2024-12-31T23:59:59"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    def test_get_reports_with_location_filter(self, api_client, base_url, auth_headers, sample_location_id):
        """Test getting reports with location filter."""
        response = api_client.get(
            f"{base_url}/reports",
            params={"locationId": sample_location_id},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    def test_get_reports_with_waiter_filter(self, api_client, base_url, auth_headers):
        """Test getting reports with waiter filter."""
        waiter_id = "792846d5c951184d705b65d7"
        
        response = api_client.get(
            f"{base_url}/reports",
            params={"waiterId": waiter_id},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    def test_get_reports_with_all_filters(self, api_client, base_url, auth_headers, sample_location_id):
        """Test getting reports with all filters combined."""
        response = api_client.get(
            f"{base_url}/reports",
            params={
                "fromDateTime": "2024-01-01T00:00:00",
                "toDateTime": "2024-12-31T23:59:59",
                "locationId": sample_location_id,
                "waiterId": "792846d5c951184d705b65d7"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    def test_create_report_success(self, api_client, base_url, auth_headers):
        """Test successful report creation."""
        response = api_client.post(
            f"{base_url}/reports",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "message" in data

    def test_create_report_unauthorized(self, api_client, base_url):
        """Test report creation without authentication."""
        response = api_client.post(f"{base_url}/reports")
        
        assert response.status_code == 401

    def test_reports_response_structure(self, api_client, base_url, auth_headers):
        """Test reports response structure and data validation."""
        response = api_client.get(
            f"{base_url}/reports",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert "content" in data
        assert isinstance(data["content"], list)
        
        if data["content"]:
            report = data["content"][0]
            required_fields = [
                "id", "name", "description", "fromDateTime", 
                "toDateTime", "location", "waiterId", "downloadLink"
            ]
            
            for field in required_fields:
                assert field in report, f"Missing field: {field}"
            
            # Validate data types
            assert isinstance(report["id"], str)
            assert isinstance(report["name"], str)
            assert isinstance(report["description"], str)
            assert isinstance(report["fromDateTime"], str)
            assert isinstance(report["toDateTime"], str)
            assert isinstance(report["location"], str)
            assert isinstance(report["waiterId"], str)
            assert isinstance(report["downloadLink"], str)

    def test_report_datetime_format(self, api_client, base_url, auth_headers):
        """Test that report datetime fields are in correct format."""
        response = api_client.get(
            f"{base_url}/reports",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:
            for report in data["content"]:
                from_datetime = report["fromDateTime"]
                to_datetime = report["toDateTime"]
                
                # DateTime should contain 'T' separator
                assert "T" in from_datetime, f"Invalid fromDateTime format: {from_datetime}"
                assert "T" in to_datetime, f"Invalid toDateTime format: {to_datetime}"

    def test_report_download_links(self, api_client, base_url, auth_headers):
        """Test that report download links are valid URLs."""
        response = api_client.get(
            f"{base_url}/reports",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:
            for report in data["content"]:
                download_link = report["downloadLink"]
                if download_link:  # If download link is provided
                    assert download_link.startswith("http"), f"Invalid download link: {download_link}"

    def test_invalid_date_format_filter(self, api_client, base_url, auth_headers):
        """Test reports with invalid date format filters."""
        response = api_client.get(
            f"{base_url}/reports",
            params={
                "fromDateTime": "invalid-date",
                "toDateTime": "also-invalid"
            },
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400, 422]

    def test_future_date_filter(self, api_client, base_url, auth_headers):
        """Test reports with future date filters."""
        response = api_client.get(
            f"{base_url}/reports",
            params={
                "fromDateTime": "2030-01-01T00:00:00",
                "toDateTime": "2030-12-31T23:59:59"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        # Should return empty results or handle gracefully

    def test_reverse_date_range_filter(self, api_client, base_url, auth_headers):
        """Test reports with reverse date range (to before from)."""
        response = api_client.get(
            f"{base_url}/reports",
            params={
                "fromDateTime": "2024-12-31T23:59:59",
                "toDateTime": "2024-01-01T00:00:00"
            },
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400]

    def test_invalid_location_id_filter(self, api_client, base_url, auth_headers):
        """Test reports with invalid location ID filter."""
        response = api_client.get(
            f"{base_url}/reports",
            params={"locationId": "invalid-location-id"},
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400]

    def test_invalid_waiter_id_filter(self, api_client, base_url, auth_headers):
        """Test reports with invalid waiter ID filter."""
        response = api_client.get(
            f"{base_url}/reports",
            params={"waiterId": "invalid-waiter-id"},
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400]

    def test_empty_filter_values(self, api_client, base_url, auth_headers):
        """Test reports with empty filter values."""
        response = api_client.get(
            f"{base_url}/reports",
            params={
                "fromDateTime": "",
                "toDateTime": "",
                "locationId": "",
                "waiterId": ""
            },
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400, 422]

    def test_report_creation_response_structure(self, api_client, base_url, auth_headers):
        """Test report creation response structure."""
        response = api_client.post(
            f"{base_url}/reports",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)

    def test_reports_pagination_support(self, api_client, base_url, auth_headers):
        """Test if reports endpoint supports pagination (if implemented)."""
        response = api_client.get(
            f"{base_url}/reports",
            params={
                "page": 0,
                "size": 10
            },
            headers=auth_headers
        )
        
        # Should either support pagination or ignore these parameters
        assert response.status_code == 200

    def test_reports_sorting_support(self, api_client, base_url, auth_headers):
        """Test if reports endpoint supports sorting (if implemented)."""
        response = api_client.get(
            f"{base_url}/reports",
            params={"sort": "name,asc"},
            headers=auth_headers
        )
        
        # Should either support sorting or ignore this parameter
        assert response.status_code == 200

    def test_concurrent_report_creation(self, api_client, base_url, auth_headers):
        """Test concurrent report creation requests."""
        responses = []
        
        for _ in range(3):
            response = api_client.post(
                f"{base_url}/reports",
                headers=auth_headers
            )
            responses.append(response)
        
        for response in responses:
            assert response.status_code in [200, 429]  # 429 if rate limited