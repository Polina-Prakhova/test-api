"""
Locations endpoint tests.
"""
import pytest


class TestLocationsEndpoints:
    """Test locations-related endpoints."""

    def test_get_locations(self, api_client, base_url):
        """Test getting all locations."""
        response = api_client.get(f"{base_url}/locations")
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        
        # Verify each location has required fields
        for location in response_data:
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
        response_data = response.json()
        assert isinstance(response_data, list)
        
        # Verify each location brief has required fields
        for location in response_data:
            assert "id" in location
            assert "address" in location

    def test_get_speciality_dishes_by_location(self, api_client, base_url):
        """Test getting speciality dishes for a location."""
        location_id = "672846d5c951184d705b65d7"
        response = api_client.get(f"{base_url}/locations/{location_id}/speciality-dishes")
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        
        # Verify each dish has required fields
        for dish in response_data:
            assert "name" in dish
            assert "price" in dish
            assert "weight" in dish
            assert "imageUrl" in dish

    def test_get_speciality_dishes_invalid_location(self, api_client, base_url):
        """Test getting speciality dishes with invalid location ID."""
        invalid_ids = ["invalid-id", "000000000000000000000000", ""]
        
        for invalid_id in invalid_ids:
            response = api_client.get(f"{base_url}/locations/{invalid_id}/speciality-dishes")
            assert response.status_code in [400, 404]

    def test_get_location_feedbacks(self, api_client, base_url):
        """Test getting feedbacks for a location."""
        location_id = "a5d95674-e4aa-43be-8d50-7f26bcc17da0"
        params = {
            "type": "CUISINE_EXPERIENCE",
            "page": 0,
            "size": 20
        }
        response = api_client.get(f"{base_url}/locations/{location_id}/feedbacks", params=params)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Verify paginated response structure
        assert "totalPages" in response_data
        assert "totalElements" in response_data
        assert "size" in response_data
        assert "content" in response_data
        assert "number" in response_data
        assert "first" in response_data
        assert "last" in response_data
        assert isinstance(response_data["content"], list)

    def test_get_location_feedbacks_different_types(self, api_client, base_url):
        """Test getting feedbacks with different types."""
        location_id = "a5d95674-e4aa-43be-8d50-7f26bcc17da0"
        feedback_types = ["CUISINE_EXPERIENCE", "SERVICE_QUALITY"]
        
        for feedback_type in feedback_types:
            params = {"type": feedback_type}
            response = api_client.get(f"{base_url}/locations/{location_id}/feedbacks", params=params)
            assert response.status_code == 200
            response_data = response.json()
            assert "content" in response_data

    def test_get_location_feedbacks_pagination(self, api_client, base_url):
        """Test location feedbacks pagination."""
        location_id = "a5d95674-e4aa-43be-8d50-7f26bcc17da0"
        params = {
            "type": "CUISINE_EXPERIENCE",
            "page": 0,
            "size": 5
        }
        response = api_client.get(f"{base_url}/locations/{location_id}/feedbacks", params=params)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["size"] == 5
        assert len(response_data["content"]) <= 5

    def test_get_location_feedbacks_sorting(self, api_client, base_url):
        """Test location feedbacks with sorting."""
        location_id = "a5d95674-e4aa-43be-8d50-7f26bcc17da0"
        params = {
            "type": "CUISINE_EXPERIENCE",
            "sort": ["date,desc"]
        }
        response = api_client.get(f"{base_url}/locations/{location_id}/feedbacks", params=params)
        
        assert response.status_code == 200
        response_data = response.json()
        assert "content" in response_data

    def test_get_location_feedbacks_invalid_location(self, api_client, base_url):
        """Test getting feedbacks with invalid location ID."""
        invalid_id = "invalid-location-id"
        params = {"type": "CUISINE_EXPERIENCE"}
        response = api_client.get(f"{base_url}/locations/{invalid_id}/feedbacks", params=params)
        
        assert response.status_code in [400, 404]

    def test_get_location_feedbacks_missing_type(self, api_client, base_url):
        """Test getting feedbacks without required type parameter."""
        location_id = "a5d95674-e4aa-43be-8d50-7f26bcc17da0"
        response = api_client.get(f"{base_url}/locations/{location_id}/feedbacks")
        
        assert response.status_code in [400, 422]  # Bad request due to missing required parameter

    def test_locations_response_structure(self, api_client, base_url):
        """Test locations response structure."""
        response = api_client.get(f"{base_url}/locations")
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        
        # Verify each location has correct field types
        for location in response_data:
            assert isinstance(location, dict)
            assert isinstance(location["id"], str)
            assert isinstance(location["address"], str)
            assert isinstance(location["description"], str)
            assert isinstance(location["totalCapacity"], str)
            assert isinstance(location["averageOccupancy"], str)
            assert isinstance(location["imageUrl"], str)
            assert isinstance(location["rating"], str)

    def test_location_brief_response_structure(self, api_client, base_url):
        """Test location brief response structure."""
        response = api_client.get(f"{base_url}/locations/select-options")
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        
        # Verify each location brief has correct structure
        for location in response_data:
            assert isinstance(location, dict)
            assert "id" in location
            assert "address" in location
            assert isinstance(location["id"], str)
            assert isinstance(location["address"], str)

    def test_feedback_response_structure(self, api_client, base_url):
        """Test feedback response structure."""
        location_id = "a5d95674-e4aa-43be-8d50-7f26bcc17da0"
        params = {"type": "CUISINE_EXPERIENCE"}
        response = api_client.get(f"{base_url}/locations/{location_id}/feedbacks", params=params)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Verify each feedback has required fields
            for feedback in response_data["content"]:
                assert "id" in feedback
                assert "rate" in feedback
                assert "comment" in feedback
                assert "userName" in feedback
                assert "userAvatarUrl" in feedback
                assert "date" in feedback
                assert "type" in feedback
                assert "locationId" in feedback

    def test_locations_endpoints_methods(self, api_client, base_url):
        """Test locations endpoints only accept GET method."""
        endpoints = [
            "/locations",
            "/locations/select-options",
            "/locations/672846d5c951184d705b65d7/speciality-dishes",
            "/locations/a5d95674-e4aa-43be-8d50-7f26bcc17da0/feedbacks"
        ]
        
        for endpoint in endpoints:
            # POST should not be allowed
            response = api_client.post(f"{base_url}{endpoint}")
            assert response.status_code in [405, 404]
            
            # PUT should not be allowed
            response = api_client.put(f"{base_url}{endpoint}")
            assert response.status_code in [405, 404]
            
            # DELETE should not be allowed
            response = api_client.delete(f"{base_url}{endpoint}")
            assert response.status_code in [405, 404]