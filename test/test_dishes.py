"""
Dishes endpoint tests.
"""
import pytest


class TestDishesEndpoints:
    """Test dishes-related endpoints."""

    def test_get_popular_dishes(self, api_client, base_url):
        """Test getting popular dishes."""
        response = api_client.get(f"{base_url}/dishes/popular")
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        
        # Verify each dish has required fields
        for dish in response_data:
            assert "name" in dish
            assert "price" in dish
            assert "weight" in dish
            assert "imageUrl" in dish

    def test_get_dishes_with_filters(self, api_client, base_url):
        """Test getting dishes with various filters."""
        # Test with dish type filter
        dish_types = ["APPETIZER", "MAIN_COURSE", "DESSERT"]
        for dish_type in dish_types:
            response = api_client.get(f"{base_url}/dishes", params={"dishType": dish_type})
            assert response.status_code == 200
            response_data = response.json()
            assert "content" in response_data
            assert isinstance(response_data["content"], list)

    def test_get_dishes_with_sorting(self, api_client, base_url):
        """Test getting dishes with sorting options."""
        sort_options = [
            "popularity,asc",
            "popularity,desc", 
            "price,asc",
            "price,desc"
        ]
        
        for sort_option in sort_options:
            response = api_client.get(f"{base_url}/dishes", params={"sort": sort_option})
            assert response.status_code == 200
            response_data = response.json()
            assert "content" in response_data
            assert isinstance(response_data["content"], list)

    def test_get_dishes_combined_filters(self, api_client, base_url):
        """Test getting dishes with combined filters."""
        params = {
            "dishType": "MAIN_COURSE",
            "sort": "price,asc"
        }
        response = api_client.get(f"{base_url}/dishes", params=params)
        
        assert response.status_code == 200
        response_data = response.json()
        assert "content" in response_data
        assert isinstance(response_data["content"], list)

    def test_get_dish_by_id(self, api_client, base_url):
        """Test getting a specific dish by ID."""
        dish_id = "322846d5c951184d705b65d2"
        response = api_client.get(f"{base_url}/dishes/{dish_id}")
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Verify extended dish response structure
        required_fields = [
            "id", "name", "price", "weight", "imageUrl", "description",
            "dishType", "calories", "proteins", "fats", "carbohydrates",
            "vitamins", "state"
        ]
        
        for field in required_fields:
            assert field in response_data
            assert response_data[field] is not None

    def test_get_dish_by_invalid_id(self, api_client, base_url):
        """Test getting dish with invalid ID."""
        invalid_ids = ["invalid-id", "000000000000000000000000", ""]
        
        for invalid_id in invalid_ids:
            response = api_client.get(f"{base_url}/dishes/{invalid_id}")
            assert response.status_code in [400, 404]

    def test_dishes_response_structure(self, api_client, base_url):
        """Test dishes list response structure."""
        response = api_client.get(f"{base_url}/dishes")
        
        assert response.status_code == 200
        response_data = response.json()
        assert "content" in response_data
        assert isinstance(response_data["content"], list)
        
        # Verify each dish preview has required fields
        for dish in response_data["content"]:
            assert "id" in dish
            assert "name" in dish
            assert "previewImageUrl" in dish
            assert "price" in dish
            assert "state" in dish
            assert "weight" in dish

    def test_dish_detail_response_structure(self, api_client, base_url):
        """Test dish detail response structure."""
        dish_id = "322846d5c951184d705b65d2"
        response = api_client.get(f"{base_url}/dishes/{dish_id}")
        
        if response.status_code == 200:
            response_data = response.json()
            # Verify extended response structure
            assert isinstance(response_data, dict)
            assert "calories" in response_data
            assert "carbohydrates" in response_data
            assert "description" in response_data
            assert "dishType" in response_data
            assert "fats" in response_data
            assert "proteins" in response_data
            assert "vitamins" in response_data

    def test_dishes_invalid_filters(self, api_client, base_url):
        """Test dishes endpoint with invalid filters."""
        invalid_params = [
            {"dishType": "INVALID_TYPE"},
            {"sort": "invalid,sort"},
            {"dishType": ""},
            {"sort": ""}
        ]
        
        for params in invalid_params:
            response = api_client.get(f"{base_url}/dishes", params=params)
            # Should either return 400 or ignore invalid params and return 200
            assert response.status_code in [200, 400]

    def test_dishes_endpoints_methods(self, api_client, base_url):
        """Test dishes endpoints only accept GET method."""
        endpoints = ["/dishes", "/dishes/popular", "/dishes/322846d5c951184d705b65d2"]
        
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

    def test_popular_dishes_response_structure(self, api_client, base_url):
        """Test popular dishes response structure."""
        response = api_client.get(f"{base_url}/dishes/popular")
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        
        # Verify each popular dish has required fields
        for dish in response_data:
            assert isinstance(dish, dict)
            assert "name" in dish
            assert "price" in dish
            assert "weight" in dish
            assert "imageUrl" in dish
            assert isinstance(dish["name"], str)
            assert isinstance(dish["price"], str)
            assert isinstance(dish["weight"], str)
            assert isinstance(dish["imageUrl"], str)