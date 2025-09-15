"""
Tests for cart endpoints.
"""
import pytest


class TestCartEndpoints:
    """Test class for cart endpoints."""

    def test_get_cart(self, api_client, base_url, auth_headers):
        """Test getting user's cart."""
        response = api_client.get(
            f"{base_url}/cart",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "content" in data
        assert isinstance(data["content"], list)
        
        if data["content"]:  # If there are items in cart
            cart_item = data["content"][0]
            assert "id" in cart_item
            assert "reservationId" in cart_item
            assert "address" in cart_item
            assert "date" in cart_item
            assert "timeSlot" in cart_item
            assert "state" in cart_item
            assert "dishItems" in cart_item
            assert isinstance(cart_item["dishItems"], list)

    def test_get_cart_unauthorized(self, api_client, base_url):
        """Test getting cart without authentication."""
        response = api_client.get(f"{base_url}/cart")
        
        assert response.status_code == 401

    def test_submit_preorder(self, api_client, base_url, auth_headers):
        """Test submitting a preorder."""
        preorder_data = {
            "id": "582846d5c951184d705b65d8",
            "reservationId": "672846d5c951184d705b65d7",
            "address": "123 Main St",
            "date": "2024-12-31",
            "timeSlot": "12:00 - 13:00",
            "state": "SUBMITTED",
            "dishItems": [
                {
                    "dishId": "672846d5c951184d705b65d7",
                    "dishName": "Fresh Strawberry Mint Salad",
                    "dishPrice": "$12.99",
                    "dishQuantity": 1,
                    "dishImageUrl": "https://green-and-tasty.s3.eu-central-1.amazonaws.com/img/ff7863bf-63eb-4f2e-8041-75a81507acff.jpg"
                }
            ]
        }
        
        response = api_client.put(
            f"{base_url}/cart",
            json=preorder_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "content" in data
        assert isinstance(data["content"], list)

    def test_submit_preorder_unauthorized(self, api_client, base_url):
        """Test submitting preorder without authentication."""
        preorder_data = {
            "id": "582846d5c951184d705b65d8",
            "reservationId": "672846d5c951184d705b65d7",
            "address": "123 Main St",
            "date": "2024-12-31",
            "timeSlot": "12:00 - 13:00",
            "state": "SUBMITTED",
            "dishItems": []
        }
        
        response = api_client.put(f"{base_url}/cart", json=preorder_data)
        
        assert response.status_code == 401

    def test_submit_preorder_invalid_data(self, api_client, base_url, auth_headers):
        """Test submitting preorder with invalid data."""
        invalid_data = {
            "id": "",
            "reservationId": "",
            "address": "",
            "date": "invalid-date",
            "timeSlot": "",
            "state": "INVALID_STATE",
            "dishItems": "not-a-list"
        }
        
        response = api_client.put(
            f"{base_url}/cart",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]

    def test_submit_preorder_missing_fields(self, api_client, base_url, auth_headers):
        """Test submitting preorder with missing required fields."""
        incomplete_data = {
            "id": "582846d5c951184d705b65d8"
            # Missing other required fields
        }
        
        response = api_client.put(
            f"{base_url}/cart",
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]

    def test_cart_response_structure(self, api_client, base_url, auth_headers):
        """Test cart response structure and data validation."""
        response = api_client.get(
            f"{base_url}/cart",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert "content" in data
        assert isinstance(data["content"], list)
        
        if data["content"]:
            cart_item = data["content"][0]
            required_fields = [
                "id", "reservationId", "address", "date", 
                "timeSlot", "state", "dishItems"
            ]
            
            for field in required_fields:
                assert field in cart_item, f"Missing field: {field}"
            
            # Validate data types
            assert isinstance(cart_item["dishItems"], list)
            assert isinstance(cart_item["id"], str)
            assert isinstance(cart_item["reservationId"], str)

    def test_cart_dish_items_structure(self, api_client, base_url, auth_headers):
        """Test cart dish items structure."""
        response = api_client.get(
            f"{base_url}/cart",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:
            cart_item = data["content"][0]
            dish_items = cart_item["dishItems"]
            
            if dish_items:  # If there are dish items
                dish_item = dish_items[0]
                required_fields = [
                    "dishId", "dishName", "dishPrice", 
                    "dishQuantity", "dishImageUrl"
                ]
                
                for field in required_fields:
                    assert field in dish_item, f"Missing dish item field: {field}"
                
                # Validate data types
                assert isinstance(dish_item["dishQuantity"], int)
                assert isinstance(dish_item["dishId"], str)
                assert isinstance(dish_item["dishName"], str)
                assert isinstance(dish_item["dishPrice"], str)
                assert isinstance(dish_item["dishImageUrl"], str)

    def test_cart_state_values(self, api_client, base_url, auth_headers):
        """Test that cart state values are valid."""
        response = api_client.get(
            f"{base_url}/cart",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        valid_states = ["SUBMITTED", "IN_PROGRESS", "CANCELLED"]
        
        if data["content"]:
            for cart_item in data["content"]:
                state = cart_item["state"]
                assert state in valid_states, f"Invalid cart state: {state}"

    def test_dish_price_format_in_cart(self, api_client, base_url, auth_headers):
        """Test that dish prices in cart are in correct format."""
        response = api_client.get(
            f"{base_url}/cart",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:
            for cart_item in data["content"]:
                dish_items = cart_item["dishItems"]
                for dish_item in dish_items:
                    price = dish_item["dishPrice"]
                    assert price.startswith("$"), f"Invalid price format: {price}"
                    
                    # Extract numeric part and validate
                    numeric_part = price[1:]
                    try:
                        float(numeric_part)
                    except ValueError:
                        pytest.fail(f"Price contains non-numeric value: {price}")

    def test_dish_quantity_validation(self, api_client, base_url, auth_headers):
        """Test that dish quantities in cart are valid."""
        response = api_client.get(
            f"{base_url}/cart",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:
            for cart_item in data["content"]:
                dish_items = cart_item["dishItems"]
                for dish_item in dish_items:
                    quantity = dish_item["dishQuantity"]
                    assert isinstance(quantity, int), f"Quantity is not an integer: {quantity}"
                    assert quantity > 0, f"Invalid quantity: {quantity}"

    def test_dish_image_urls_in_cart(self, api_client, base_url, auth_headers):
        """Test that dish image URLs in cart are valid."""
        response = api_client.get(
            f"{base_url}/cart",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:
            for cart_item in data["content"]:
                dish_items = cart_item["dishItems"]
                for dish_item in dish_items:
                    image_url = dish_item["dishImageUrl"]
                    assert image_url.startswith("http"), f"Invalid image URL: {image_url}"

    def test_cart_date_format(self, api_client, base_url, auth_headers):
        """Test that cart dates are in correct format."""
        response = api_client.get(
            f"{base_url}/cart",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:
            for cart_item in data["content"]:
                date = cart_item["date"]
                # Date should be in YYYY-MM-DD format
                assert len(date) == 10, f"Invalid date format: {date}"
                assert date.count("-") == 2, f"Invalid date format: {date}"

    def test_cart_time_slot_format(self, api_client, base_url, auth_headers):
        """Test that cart time slots are in correct format."""
        response = api_client.get(
            f"{base_url}/cart",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["content"]:
            for cart_item in data["content"]:
                time_slot = cart_item["timeSlot"]
                # Time slot should contain a dash or hyphen
                assert "-" in time_slot or "–" in time_slot, f"Invalid time slot format: {time_slot}"

    def test_preorder_state_transition(self, api_client, base_url, auth_headers):
        """Test preorder state transitions."""
        # Test different state values
        states = ["SUBMITTED", "IN_PROGRESS", "CANCELLED"]
        
        for state in states:
            preorder_data = {
                "id": "582846d5c951184d705b65d8",
                "reservationId": "672846d5c951184d705b65d7",
                "address": "123 Main St",
                "date": "2024-12-31",
                "timeSlot": "12:00 - 13:00",
                "state": state,
                "dishItems": []
            }
            
            response = api_client.put(
                f"{base_url}/cart",
                json=preorder_data,
                headers=auth_headers
            )
            
            assert response.status_code in [200, 400]  # May fail due to business logic