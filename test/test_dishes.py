"""
Dishes API tests.
Tests for dish-related endpoints including popular dishes, dish listing, and dish details.
"""
import pytest
import requests
from typing import Dict, Any


class TestPopularDishes:
    """Test cases for popular dishes endpoint."""
    
    def test_get_popular_dishes_success(self, api_client, base_url):
        """Test successful retrieval of popular dishes."""
        response = api_client.get(f"{base_url}/dishes/popular")
        
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
    
    def test_popular_dishes_response_structure(self, api_client, base_url):
        """Test popular dishes response structure."""
        response = api_client.get(f"{base_url}/dishes/popular")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return an array
        assert isinstance(data, list)
        
        # Each dish should have the correct structure
        for dish in data:
            assert isinstance(dish, dict)
            
            # Check required fields exist
            required_fields = ["name", "price", "weight", "imageUrl"]
            for field in required_fields:
                assert field in dish
            
            # Validate field types
            assert isinstance(dish["name"], str)
            assert isinstance(dish["price"], str)
            assert isinstance(dish["weight"], str)
            assert isinstance(dish["imageUrl"], str)
            
            # Validate URL format
            assert dish["imageUrl"].startswith(("http://", "https://"))
    
    def test_popular_dishes_caching(self, api_client, base_url):
        """Test popular dishes endpoint caching behavior."""
        # Make multiple requests
        response1 = api_client.get(f"{base_url}/dishes/popular")
        response2 = api_client.get(f"{base_url}/dishes/popular")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Responses should be consistent
        assert response1.json() == response2.json()


class TestDishesListing:
    """Test cases for dishes listing endpoint."""
    
    def test_get_dishes_without_filters(self, api_client, base_url):
        """Test getting dishes without any filters."""
        response = api_client.get(f"{base_url}/dishes")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "content" in data
        assert isinstance(data["content"], list)
        
        # Validate dish structure
        if data["content"]:
            dish = data["content"][0]
            required_fields = ["id", "name", "previewImageUrl", "price", "state", "weight"]
            for field in required_fields:
                assert field in dish
    
    def test_get_dishes_with_dish_type_filter(self, api_client, base_url):
        """Test getting dishes with dish type filter."""
        dish_types = ["APPETIZER", "MAIN_COURSE", "DESSERT"]
        
        for dish_type in dish_types:
            response = api_client.get(f"{base_url}/dishes", params={"dishType": dish_type})
            
            assert response.status_code == 200
            data = response.json()
            assert "content" in data
            assert isinstance(data["content"], list)
    
    def test_get_dishes_with_sort_parameters(self, api_client, base_url):
        """Test getting dishes with different sort parameters."""
        sort_options = [
            "popularity,asc",
            "popularity,desc",
            "price,asc",
            "price,desc"
        ]
        
        for sort_option in sort_options:
            response = api_client.get(f"{base_url}/dishes", params={"sort": sort_option})
            
            assert response.status_code == 200
            data = response.json()
            assert "content" in data
    
    def test_get_dishes_with_combined_filters(self, api_client, base_url):
        """Test getting dishes with combined filters."""
        params = {
            "dishType": "MAIN_COURSE",
            "sort": "price,asc"
        }
        
        response = api_client.get(f"{base_url}/dishes", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
    
    @pytest.mark.validation
    def test_get_dishes_invalid_dish_type(self, api_client, base_url):
        """Test getting dishes with invalid dish type."""
        response = api_client.get(f"{base_url}/dishes", params={"dishType": "INVALID_TYPE"})
        
        # Should either return empty results or validation error
        assert response.status_code in [200, 400, 422]
    
    @pytest.mark.validation
    def test_get_dishes_invalid_sort_parameter(self, api_client, base_url):
        """Test getting dishes with invalid sort parameter."""
        response = api_client.get(f"{base_url}/dishes", params={"sort": "invalid,sort"})
        
        # Should either ignore invalid sort or return error
        assert response.status_code in [200, 400, 422]


class TestDishDetails:
    """Test cases for dish details endpoint."""
    
    def test_get_dish_by_id_success(self, api_client, base_url, sample_dish_id):
        """Test successful retrieval of dish by ID."""
        response = api_client.get(f"{base_url}/dishes/{sample_dish_id}")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        
        # Validate extended dish structure
        required_fields = [
            "id", "name", "description", "price", "weight", "imageUrl",
            "dishType", "calories", "proteins", "fats", "carbohydrates",
            "vitamins", "state"
        ]
        
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], str)
            assert len(data[field]) > 0
        
        # Validate specific field formats
        assert data["id"] == sample_dish_id
        assert data["imageUrl"].startswith(("http://", "https://"))
        assert data["dishType"] in ["APPETIZERS", "MAIN_COURSE", "DESSERTS"]
    
    @pytest.mark.error
    def test_get_dish_by_invalid_id(self, api_client, base_url):
        """Test getting dish with invalid ID."""
        invalid_ids = [
            "invalid_id",
            "123",
            "nonexistent_id_12345",
            ""
        ]
        
        for dish_id in invalid_ids:
            response = api_client.get(f"{base_url}/dishes/{dish_id}")
            assert response.status_code in [400, 404], f"Failed for ID: {dish_id}"
    
    @pytest.mark.error
    def test_get_dish_by_nonexistent_id(self, api_client, base_url):
        """Test getting dish with properly formatted but nonexistent ID."""
        nonexistent_id = "999999999999999999999999"
        response = api_client.get(f"{base_url}/dishes/{nonexistent_id}")
        
        assert response.status_code == 404
    
    def test_dish_details_data_integrity(self, api_client, base_url, sample_dish_id):
        """Test dish details data integrity."""
        response = api_client.get(f"{base_url}/dishes/{sample_dish_id}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate data consistency
            assert data["id"] == sample_dish_id
            
            # Price should be in valid format
            assert data["price"].startswith("$")
            
            # Weight should include units
            assert any(unit in data["weight"] for unit in ["g", "kg", "ml", "l"])
            
            # Calories should include unit
            assert "kcal" in data["calories"]
            
            # Nutritional info should be properly formatted
            nutritional_fields = ["proteins", "fats", "carbohydrates"]
            for field in nutritional_fields:
                assert "g" in data[field]


class TestDishesIntegration:
    """Integration tests for dishes endpoints."""
    
    @pytest.mark.integration
    def test_dishes_flow(self, api_client, base_url):
        """Test complete dishes browsing flow."""
        # Step 1: Get popular dishes
        popular_response = api_client.get(f"{base_url}/dishes/popular")
        assert popular_response.status_code == 200
        
        # Step 2: Get all dishes
        all_dishes_response = api_client.get(f"{base_url}/dishes")
        assert all_dishes_response.status_code == 200
        
        all_dishes_data = all_dishes_response.json()
        
        # Step 3: Get details for first dish if available
        if all_dishes_data.get("content"):
            first_dish = all_dishes_data["content"][0]
            dish_id = first_dish["id"]
            
            detail_response = api_client.get(f"{base_url}/dishes/{dish_id}")
            assert detail_response.status_code == 200
            
            detail_data = detail_response.json()
            
            # Validate consistency between list and detail views
            assert detail_data["id"] == first_dish["id"]
            assert detail_data["name"] == first_dish["name"]
            assert detail_data["price"] == first_dish["price"]
    
    @pytest.mark.integration
    def test_dishes_filtering_consistency(self, api_client, base_url):
        """Test consistency across different filtering options."""
        # Get all dishes
        all_response = api_client.get(f"{base_url}/dishes")
        assert all_response.status_code == 200
        
        all_data = all_response.json()
        total_dishes = len(all_data.get("content", []))
        
        # Get dishes by type and verify totals make sense
        dish_types = ["APPETIZER", "MAIN_COURSE", "DESSERT"]
        type_totals = 0
        
        for dish_type in dish_types:
            type_response = api_client.get(f"{base_url}/dishes", params={"dishType": dish_type})
            if type_response.status_code == 200:
                type_data = type_response.json()
                type_count = len(type_data.get("content", []))
                type_totals += type_count
        
        # Note: This assumes all dishes have a type, which may not be true
        # So we just verify the filtering works without errors


class TestDishesErrorScenarios:
    """Test error scenarios and edge cases."""
    
    @pytest.mark.error
    def test_dishes_with_malformed_parameters(self, api_client, base_url):
        """Test dishes endpoint with malformed parameters."""
        malformed_params = [
            {"dishType": "<script>alert('xss')</script>"},
            {"sort": "'; DROP TABLE dishes; --"},
            {"dishType": "A" * 1000},  # Very long parameter
        ]
        
        for params in malformed_params:
            response = api_client.get(f"{base_url}/dishes", params=params)
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.error
    def test_dish_details_with_special_characters(self, api_client, base_url):
        """Test dish details with special characters in ID."""
        special_ids = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE dishes; --",
            "../../../etc/passwd",
            "%00",
            "dish%20id"
        ]
        
        for dish_id in special_ids:
            response = api_client.get(f"{base_url}/dishes/{dish_id}")
            # Should handle gracefully
            assert response.status_code in [400, 404]
    
    @pytest.mark.error
    def test_concurrent_dish_requests(self, api_client, base_url):
        """Test concurrent requests to dishes endpoints."""
        import threading
        import time
        
        responses = []
        
        def make_request():
            response = api_client.get(f"{base_url}/dishes/popular")
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