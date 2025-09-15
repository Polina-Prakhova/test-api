"""
Tests for locations endpoints.
"""
import pytest


class TestLocationsEndpoints:
    """Test class for locations endpoints."""

    def test_get_all_locations(self, api_client, base_url):
        """Test getting all locations."""
        response = api_client.get(f"{base_url}/locations")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # If there are locations
            location = data[0]
            assert "id" in location
            assert "address" in location
            assert "description" in location
            assert "totalCapacity" in location
            assert "averageOccupancy" in location
            assert "imageUrl" in location
            assert "rating" in location

    def test_get_location_select_options(self, api_client, base_url):
        """Test getting location select options."""
        response = api_client.get(f"{base_url}/locations/select-options")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # If there are locations
            location = data[0]
            assert "id" in location
            assert "address" in location

    def test_get_speciality_dishes_by_location(self, api_client, base_url, sample_location_id):
        """Test getting speciality dishes for a location."""
        response = api_client.get(f"{base_url}/locations/{sample_location_id}/speciality-dishes")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # If there are speciality dishes
            dish = data[0]
            assert "name" in dish
            assert "price" in dish
            assert "weight" in dish
            assert "imageUrl" in dish

    def test_get_speciality_dishes_invalid_location(self, api_client, base_url):
        """Test getting speciality dishes for invalid location."""
        invalid_location_id = "invalid-location-id"
        response = api_client.get(f"{base_url}/locations/{invalid_location_id}/speciality-dishes")
        
        assert response.status_code in [404, 400]

    def test_get_location_feedbacks(self, api_client, base_url, sample_location_id):
        """Test getting feedbacks for a location."""
        response = api_client.get(
            f"{base_url}/locations/{sample_location_id}/feedbacks",
            params={"type": "CUISINE_EXPERIENCE"}
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "content" in data
        assert "totalPages" in data
        assert "totalElements" in data
        assert "size" in data
        assert "number" in data
        assert "first" in data
        assert "last" in data
        assert "numberOfElements" in data
        assert "empty" in data
        
        # Validate pagination structure
        assert isinstance(data["content"], list)
        assert isinstance(data["totalPages"], int)
        assert isinstance(data["totalElements"], int)
        assert isinstance(data["size"], int)
        assert isinstance(data["number"], int)
        assert isinstance(data["first"], bool)
        assert isinstance(data["last"], bool)

    def test_get_location_feedbacks_service_quality(self, api_client, base_url, sample_location_id):
        """Test getting service quality feedbacks for a location."""
        response = api_client.get(
            f"{base_url}/locations/{sample_location_id}/feedbacks",
            params={"type": "SERVICE_QUALITY"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    def test_get_location_feedbacks_with_pagination(self, api_client, base_url, sample_location_id):
        """Test getting location feedbacks with pagination parameters."""
        response = api_client.get(
            f"{base_url}/locations/{sample_location_id}/feedbacks",
            params={
                "type": "CUISINE_EXPERIENCE",
                "page": 0,
                "size": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["size"] <= 5
        assert data["number"] == 0

    def test_get_location_feedbacks_with_sorting(self, api_client, base_url, sample_location_id):
        """Test getting location feedbacks with sorting."""
        response = api_client.get(
            f"{base_url}/locations/{sample_location_id}/feedbacks",
            params={
                "type": "CUISINE_EXPERIENCE",
                "sort": ["date,desc"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    def test_get_location_feedbacks_missing_type(self, api_client, base_url, sample_location_id):
        """Test getting location feedbacks without required type parameter."""
        response = api_client.get(f"{base_url}/locations/{sample_location_id}/feedbacks")
        
        assert response.status_code in [400, 422]

    def test_get_location_feedbacks_invalid_type(self, api_client, base_url, sample_location_id):
        """Test getting location feedbacks with invalid type."""
        response = api_client.get(
            f"{base_url}/locations/{sample_location_id}/feedbacks",
            params={"type": "INVALID_TYPE"}
        )
        
        assert response.status_code in [400, 422]

    def test_locations_response_structure(self, api_client, base_url):
        """Test locations response structure and data validation."""
        response = api_client.get(f"{base_url}/locations")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        if data:
            location = data[0]
            required_fields = [
                "id", "address", "description", "totalCapacity", 
                "averageOccupancy", "imageUrl", "rating"
            ]
            
            for field in required_fields:
                assert field in location, f"Missing field: {field}"

    def test_location_image_urls(self, api_client, base_url):
        """Test that location image URLs are valid."""
        response = api_client.get(f"{base_url}/locations")
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for location in data:
                image_url = location["imageUrl"]
                assert image_url.startswith("http"), f"Invalid image URL: {image_url}"

    def test_location_rating_format(self, api_client, base_url):
        """Test that location ratings are in valid format."""
        response = api_client.get(f"{base_url}/locations")
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for location in data:
                rating = location["rating"]
                try:
                    rating_value = float(rating)
                    assert 0 <= rating_value <= 5, f"Rating out of range: {rating}"
                except ValueError:
                    pytest.fail(f"Rating is not a valid number: {rating}")

    def test_location_capacity_format(self, api_client, base_url):
        """Test that location capacity values are valid."""
        response = api_client.get(f"{base_url}/locations")
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for location in data:
                total_capacity = location["totalCapacity"]
                average_occupancy = location["averageOccupancy"]
                
                try:
                    capacity_value = int(total_capacity)
                    occupancy_value = float(average_occupancy.rstrip('%'))
                    
                    assert capacity_value > 0, f"Invalid capacity: {total_capacity}"
                    assert 0 <= occupancy_value <= 100, f"Invalid occupancy: {average_occupancy}"
                except ValueError:
                    pytest.fail(f"Invalid capacity or occupancy format")

    def test_location_select_options_structure(self, api_client, base_url):
        """Test location select options response structure."""
        response = api_client.get(f"{base_url}/locations/select-options")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        if data:
            location = data[0]
            assert "id" in location
            assert "address" in location
            assert isinstance(location["id"], str)
            assert isinstance(location["address"], str)

    def test_feedback_content_structure(self, api_client, base_url, sample_location_id):
        """Test feedback content structure when available."""
        response = api_client.get(
            f"{base_url}/locations/{sample_location_id}/feedbacks",
            params={"type": "CUISINE_EXPERIENCE"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:  # If there are feedbacks
            feedback = data["content"][0]
            expected_fields = [
                "id", "rate", "comment", "userName", 
                "userAvatarUrl", "date", "type", "locationId"
            ]
            
            for field in expected_fields:
                assert field in feedback, f"Missing feedback field: {field}"