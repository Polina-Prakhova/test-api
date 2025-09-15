"""
Locations API tests.
Tests for location-related endpoints including location listing, speciality dishes, and feedbacks.
"""
import pytest
import requests
from typing import Dict, Any


class TestLocations:
    """Test cases for locations endpoint."""
    
    def test_get_locations_success(self, api_client, base_url):
        """Test successful retrieval of locations."""
        response = api_client.get(f"{base_url}/locations")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        # Validate location structure if locations are returned
        if data:
            location = data[0]
            required_fields = [
                "id", "address", "description", "totalCapacity",
                "averageOccupancy", "imageUrl", "rating"
            ]
            for field in required_fields:
                assert field in location
                assert isinstance(location[field], str)
                assert len(location[field]) > 0
    
    def test_locations_response_structure(self, api_client, base_url):
        """Test locations response structure."""
        response = api_client.get(f"{base_url}/locations")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return an array
        assert isinstance(data, list)
        
        # Each location should have the correct structure
        for location in data:
            assert isinstance(location, dict)
            
            # Check required fields exist
            required_fields = [
                "id", "address", "description", "totalCapacity",
                "averageOccupancy", "imageUrl", "rating"
            ]
            for field in required_fields:
                assert field in location
            
            # Validate field types
            for field in required_fields:
                assert isinstance(location[field], str)
            
            # Validate URL format
            assert location["imageUrl"].startswith(("http://", "https://"))
            
            # Validate rating format (should be numeric string)
            try:
                float(location["rating"])
            except ValueError:
                pytest.fail(f"Rating should be numeric: {location['rating']}")
    
    def test_locations_data_integrity(self, api_client, base_url):
        """Test locations data integrity."""
        response = api_client.get(f"{base_url}/locations")
        
        if response.status_code == 200:
            data = response.json()
            
            for location in data:
                # ID should be non-empty
                assert len(location["id"]) > 0
                
                # Address should be meaningful
                assert len(location["address"]) > 5
                
                # Capacity should be numeric
                try:
                    int(location["totalCapacity"])
                except ValueError:
                    pytest.fail(f"Total capacity should be numeric: {location['totalCapacity']}")
                
                # Average occupancy should be numeric
                try:
                    float(location["averageOccupancy"].rstrip('%'))
                except ValueError:
                    pytest.fail(f"Average occupancy should be numeric: {location['averageOccupancy']}")


class TestLocationSelectOptions:
    """Test cases for location select options endpoint."""
    
    def test_get_location_options_success(self, api_client, base_url):
        """Test successful retrieval of location options."""
        response = api_client.get(f"{base_url}/locations/select-options")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        # Validate location brief structure
        if data:
            location = data[0]
            required_fields = ["id", "address"]
            for field in required_fields:
                assert field in location
                assert isinstance(location[field], str)
                assert len(location[field]) > 0
    
    def test_location_options_vs_full_locations(self, api_client, base_url):
        """Test consistency between location options and full locations."""
        # Get full locations
        full_response = api_client.get(f"{base_url}/locations")
        assert full_response.status_code == 200
        full_data = full_response.json()
        
        # Get location options
        options_response = api_client.get(f"{base_url}/locations/select-options")
        assert options_response.status_code == 200
        options_data = options_response.json()
        
        # Should have same number of locations (or options could be a subset)
        assert len(options_data) <= len(full_data)
        
        # IDs and addresses should match for common locations
        full_locations_map = {loc["id"]: loc["address"] for loc in full_data}
        
        for option in options_data:
            location_id = option["id"]
            if location_id in full_locations_map:
                assert option["address"] == full_locations_map[location_id]


class TestLocationSpecialityDishes:
    """Test cases for location speciality dishes endpoint."""
    
    def test_get_speciality_dishes_success(self, api_client, base_url, sample_location_id):
        """Test successful retrieval of speciality dishes for a location."""
        response = api_client.get(f"{base_url}/locations/{sample_location_id}/speciality-dishes")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        # Validate dish structure if dishes are returned
        if data:
            dish = data[0]
            required_fields = ["name", "price", "weight", "imageUrl"]
            for field in required_fields:
                assert field in dish
                assert isinstance(dish[field], str)
                assert len(dish[field]) > 0
    
    @pytest.mark.error
    def test_get_speciality_dishes_invalid_location(self, api_client, base_url):
        """Test getting speciality dishes for invalid location ID."""
        invalid_ids = [
            "invalid_id",
            "123",
            "nonexistent_location_12345",
            ""
        ]
        
        for location_id in invalid_ids:
            response = api_client.get(f"{base_url}/locations/{location_id}/speciality-dishes")
            assert response.status_code in [400, 404], f"Failed for ID: {location_id}"
    
    def test_speciality_dishes_structure(self, api_client, base_url, sample_location_id):
        """Test speciality dishes response structure."""
        response = api_client.get(f"{base_url}/locations/{sample_location_id}/speciality-dishes")
        
        if response.status_code == 200:
            data = response.json()
            
            for dish in data:
                # Validate dish structure
                required_fields = ["name", "price", "weight", "imageUrl"]
                for field in required_fields:
                    assert field in dish
                    assert isinstance(dish[field], str)
                
                # Validate URL format
                assert dish["imageUrl"].startswith(("http://", "https://"))
                
                # Validate price format
                assert dish["price"].startswith("$")


class TestLocationFeedbacks:
    """Test cases for location feedbacks endpoint."""
    
    def test_get_location_feedbacks_success(self, api_client, base_url, sample_location_id):
        """Test successful retrieval of location feedbacks."""
        params = {
            "type": "CUISINE_EXPERIENCE",
            "page": 0,
            "size": 20
        }
        
        response = api_client.get(
            f"{base_url}/locations/{sample_location_id}/feedbacks",
            params=params
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        
        # Validate paginated response structure
        required_fields = [
            "totalPages", "totalElements", "size", "content",
            "number", "first", "last", "numberOfElements", "empty"
        ]
        for field in required_fields:
            assert field in data
        
        # Validate content structure
        assert isinstance(data["content"], list)
        
        if data["content"]:
            feedback = data["content"][0]
            feedback_fields = [
                "id", "rate", "comment", "userName", "userAvatarUrl",
                "date", "type", "locationId"
            ]
            for field in feedback_fields:
                assert field in feedback
    
    def test_get_location_feedbacks_different_types(self, api_client, base_url, sample_location_id):
        """Test getting location feedbacks with different types."""
        feedback_types = ["CUISINE_EXPERIENCE", "SERVICE_QUALITY"]
        
        for feedback_type in feedback_types:
            params = {"type": feedback_type}
            response = api_client.get(
                f"{base_url}/locations/{sample_location_id}/feedbacks",
                params=params
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "content" in data
    
    def test_get_location_feedbacks_pagination(self, api_client, base_url, sample_location_id):
        """Test location feedbacks pagination."""
        # Test different page sizes
        page_sizes = [5, 10, 20]
        
        for size in page_sizes:
            params = {
                "type": "CUISINE_EXPERIENCE",
                "page": 0,
                "size": size
            }
            
            response = api_client.get(
                f"{base_url}/locations/{sample_location_id}/feedbacks",
                params=params
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate pagination info
            assert data["size"] == size
            assert len(data["content"]) <= size
    
    def test_get_location_feedbacks_sorting(self, api_client, base_url, sample_location_id):
        """Test location feedbacks sorting."""
        sort_options = ["date,asc", "date,desc", "rate,asc", "rate,desc"]
        
        for sort_option in sort_options:
            params = {
                "type": "CUISINE_EXPERIENCE",
                "sort": [sort_option]
            }
            
            response = api_client.get(
                f"{base_url}/locations/{sample_location_id}/feedbacks",
                params=params
            )
            
            assert response.status_code == 200
    
    @pytest.mark.validation
    def test_get_location_feedbacks_invalid_type(self, api_client, base_url, sample_location_id):
        """Test getting location feedbacks with invalid type."""
        params = {"type": "INVALID_TYPE"}
        
        response = api_client.get(
            f"{base_url}/locations/{sample_location_id}/feedbacks",
            params=params
        )
        
        # Should return validation error or empty results
        assert response.status_code in [200, 400, 422]
    
    @pytest.mark.validation
    def test_get_location_feedbacks_invalid_pagination(self, api_client, base_url, sample_location_id):
        """Test getting location feedbacks with invalid pagination parameters."""
        invalid_params = [
            {"page": -1},
            {"size": 0},
            {"size": 1000},  # Very large size
            {"page": "invalid"},
            {"size": "invalid"}
        ]
        
        for params in invalid_params:
            params["type"] = "CUISINE_EXPERIENCE"
            response = api_client.get(
                f"{base_url}/locations/{sample_location_id}/feedbacks",
                params=params
            )
            
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.error
    def test_get_location_feedbacks_invalid_location(self, api_client, base_url):
        """Test getting feedbacks for invalid location ID."""
        invalid_ids = ["invalid_id", "123", "nonexistent_location"]
        
        for location_id in invalid_ids:
            params = {"type": "CUISINE_EXPERIENCE"}
            response = api_client.get(
                f"{base_url}/locations/{location_id}/feedbacks",
                params=params
            )
            
            assert response.status_code in [400, 404], f"Failed for ID: {location_id}"


class TestLocationsIntegration:
    """Integration tests for locations endpoints."""
    
    @pytest.mark.integration
    def test_locations_flow(self, api_client, base_url):
        """Test complete locations browsing flow."""
        # Step 1: Get all locations
        locations_response = api_client.get(f"{base_url}/locations")
        assert locations_response.status_code == 200
        
        locations_data = locations_response.json()
        
        # Step 2: Get location options
        options_response = api_client.get(f"{base_url}/locations/select-options")
        assert options_response.status_code == 200
        
        # Step 3: If locations exist, test speciality dishes and feedbacks
        if locations_data:
            location_id = locations_data[0]["id"]
            
            # Get speciality dishes
            dishes_response = api_client.get(f"{base_url}/locations/{location_id}/speciality-dishes")
            assert dishes_response.status_code == 200
            
            # Get feedbacks
            feedbacks_response = api_client.get(
                f"{base_url}/locations/{location_id}/feedbacks",
                params={"type": "CUISINE_EXPERIENCE"}
            )
            assert feedbacks_response.status_code == 200
    
    @pytest.mark.integration
    def test_location_data_consistency(self, api_client, base_url):
        """Test data consistency across location endpoints."""
        # Get full locations
        locations_response = api_client.get(f"{base_url}/locations")
        assert locations_response.status_code == 200
        
        locations_data = locations_response.json()
        
        # Get location options
        options_response = api_client.get(f"{base_url}/locations/select-options")
        assert options_response.status_code == 200
        
        options_data = options_response.json()
        
        # Verify consistency
        if locations_data and options_data:
            # Create maps for comparison
            locations_map = {loc["id"]: loc for loc in locations_data}
            options_map = {opt["id"]: opt for opt in options_data}
            
            # Check that all option IDs exist in full locations
            for option_id in options_map:
                assert option_id in locations_map
                
                # Check address consistency
                assert options_map[option_id]["address"] == locations_map[option_id]["address"]


class TestLocationsErrorScenarios:
    """Test error scenarios and edge cases."""
    
    @pytest.mark.error
    def test_locations_with_special_characters(self, api_client, base_url):
        """Test location endpoints with special characters in IDs."""
        special_ids = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE locations; --",
            "../../../etc/passwd",
            "%00"
        ]
        
        for location_id in special_ids:
            # Test speciality dishes endpoint
            response = api_client.get(f"{base_url}/locations/{location_id}/speciality-dishes")
            assert response.status_code in [400, 404]
            
            # Test feedbacks endpoint
            response = api_client.get(
                f"{base_url}/locations/{location_id}/feedbacks",
                params={"type": "CUISINE_EXPERIENCE"}
            )
            assert response.status_code in [400, 404]
    
    @pytest.mark.error
    def test_feedbacks_with_malformed_parameters(self, api_client, base_url, sample_location_id):
        """Test feedbacks endpoint with malformed parameters."""
        malformed_params = [
            {"type": "<script>alert('xss')</script>"},
            {"sort": ["'; DROP TABLE feedbacks; --"]},
            {"page": "A" * 1000},  # Very long parameter
            {"size": "javascript:alert('xss')"}
        ]
        
        for params in malformed_params:
            if "type" not in params:
                params["type"] = "CUISINE_EXPERIENCE"
                
            response = api_client.get(
                f"{base_url}/locations/{sample_location_id}/feedbacks",
                params=params
            )
            
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.error
    def test_concurrent_location_requests(self, api_client, base_url):
        """Test concurrent requests to location endpoints."""
        import threading
        
        responses = []
        
        def make_request():
            response = api_client.get(f"{base_url}/locations")
            responses.append(response)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # All responses should be consistent
        first_response_data = responses[0].json()
        for response in responses[1:]:
            assert response.json() == first_response_data