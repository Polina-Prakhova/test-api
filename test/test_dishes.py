"""
Tests for dishes endpoints.
"""
import pytest


class TestDishesEndpoints:
    """Test class for dishes endpoints."""

    def test_get_popular_dishes(self, api_client, base_url):
        """Test getting popular dishes."""
        response = api_client.get(f"{base_url}/dishes/popular")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # If there are dishes
            dish = data[0]
            assert "name" in dish
            assert "price" in dish
            assert "weight" in dish
            assert "imageUrl" in dish

    def test_get_all_dishes(self, api_client, base_url):
        """Test getting all dishes."""
        response = api_client.get(f"{base_url}/dishes")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "content" in data
        assert isinstance(data["content"], list)
        
        if data["content"]:  # If there are dishes
            dish = data["content"][0]
            assert "id" in dish
            assert "name" in dish
            assert "previewImageUrl" in dish
            assert "price" in dish
            assert "state" in dish
            assert "weight" in dish

    def test_get_dishes_with_dish_type_filter(self, api_client, base_url):
        """Test getting dishes with dish type filter."""
        dish_types = ["APPETIZER", "MAIN_COURSE", "DESSERT"]
        
        for dish_type in dish_types:
            response = api_client.get(
                f"{base_url}/dishes",
                params={"dishType": dish_type}
            )
            
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
            response = api_client.get(
                f"{base_url}/dishes",
                params={"sort": sort_option}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "content" in data

    def test_get_dishes_with_combined_filters(self, api_client, base_url):
        """Test getting dishes with combined filters."""
        response = api_client.get(
            f"{base_url}/dishes",
            params={
                "dishType": "MAIN_COURSE",
                "sort": "price,asc"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    def test_get_dish_by_id(self, api_client, base_url, sample_dish_id):
        """Test getting a specific dish by ID."""
        response = api_client.get(f"{base_url}/dishes/{sample_dish_id}")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "description" in data
        assert "price" in data
        assert "weight" in data
        assert "imageUrl" in data
        assert "dishType" in data
        assert "state" in data
        assert "calories" in data
        assert "proteins" in data
        assert "fats" in data
        assert "carbohydrates" in data
        assert "vitamins" in data
        
        # Validate data types
        assert isinstance(data["id"], str)
        assert isinstance(data["name"], str)
        assert isinstance(data["description"], str)
        assert isinstance(data["price"], str)
        assert isinstance(data["weight"], str)

    def test_get_dish_by_invalid_id(self, api_client, base_url):
        """Test getting a dish with invalid ID."""
        invalid_id = "invalid-dish-id-123"
        response = api_client.get(f"{base_url}/dishes/{invalid_id}")
        
        assert response.status_code in [404, 400]

    def test_get_dish_by_nonexistent_id(self, api_client, base_url):
        """Test getting a dish with nonexistent but valid format ID."""
        nonexistent_id = "999999999999999999999999"
        response = api_client.get(f"{base_url}/dishes/{nonexistent_id}")
        
        assert response.status_code == 404

    def test_dishes_response_structure(self, api_client, base_url):
        """Test dishes response structure and data validation."""
        response = api_client.get(f"{base_url}/dishes")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate main structure
        assert isinstance(data, dict)
        assert "content" in data
        assert isinstance(data["content"], list)
        
        # If there are dishes, validate structure
        if data["content"]:
            dish = data["content"][0]
            required_fields = ["id", "name", "previewImageUrl", "price", "state", "weight"]
            
            for field in required_fields:
                assert field in dish, f"Missing field: {field}"
                assert dish[field] is not None, f"Field {field} is None"

    def test_dishes_price_format(self, api_client, base_url):
        """Test that dish prices are in correct format."""
        response = api_client.get(f"{base_url}/dishes")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:
            for dish in data["content"]:
                price = dish["price"]
                # Price should start with $ and contain numbers
                assert price.startswith("$"), f"Price format invalid: {price}"
                # Extract numeric part and validate
                numeric_part = price[1:]  # Remove $
                try:
                    float(numeric_part)
                except ValueError:
                    pytest.fail(f"Price contains non-numeric value: {price}")

    def test_dishes_image_urls(self, api_client, base_url):
        """Test that dish image URLs are valid."""
        response = api_client.get(f"{base_url}/dishes")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:
            for dish in data["content"]:
                image_url = dish["previewImageUrl"]
                assert image_url.startswith("http"), f"Invalid image URL: {image_url}"

    def test_dishes_state_values(self, api_client, base_url):
        """Test that dish state values are valid."""
        response = api_client.get(f"{base_url}/dishes")
        
        assert response.status_code == 200
        data = response.json()
        
        valid_states = ["Available", "On Stop", "Out of Stock"]
        
        if data["content"]:
            for dish in data["content"]:
                state = dish["state"]
                assert state in valid_states, f"Invalid dish state: {state}"

    def test_dishes_weight_format(self, api_client, base_url):
        """Test that dish weights are in correct format."""
        response = api_client.get(f"{base_url}/dishes")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:
            for dish in data["content"]:
                weight = dish["weight"]
                # Weight should end with 'g' and contain numbers
                assert weight.endswith(" g"), f"Weight format invalid: {weight}"

    def test_invalid_dish_type_filter(self, api_client, base_url):
        """Test dishes endpoint with invalid dish type filter."""
        response = api_client.get(
            f"{base_url}/dishes",
            params={"dishType": "INVALID_TYPE"}
        )
        
        # Should either return empty results or handle gracefully
        assert response.status_code in [200, 400]

    def test_invalid_sort_parameter(self, api_client, base_url):
        """Test dishes endpoint with invalid sort parameter."""
        response = api_client.get(
            f"{base_url}/dishes",
            params={"sort": "invalid_sort"}
        )
        
        # Should either use default sort or handle gracefully
        assert response.status_code in [200, 400]