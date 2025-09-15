"""
Cart API tests.
Tests for cart management endpoints including viewing and submitting cart.
"""
import pytest
import requests
from typing import Dict, Any


class TestCartRetrieval:
    """Test cases for cart retrieval endpoint."""
    
    @pytest.mark.auth
    def test_get_cart_success(self, authenticated_client, base_url):
        """Test successful retrieval of user cart."""
        response = authenticated_client.get(f"{base_url}/cart")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "content" in data
        assert isinstance(data["content"], list)
        
        # Validate cart item structure if items exist
        if data["content"]:
            cart_item = data["content"][0]
            required_fields = [
                "id", "reservationId", "address", "date", "timeSlot",
                "state", "dishItems"
            ]
            for field in required_fields:
                assert field in cart_item
            
            # Validate dish items structure
            assert isinstance(cart_item["dishItems"], list)
            
            if cart_item["dishItems"]:
                dish_item = cart_item["dishItems"][0]
                dish_fields = [
                    "dishId", "dishName", "dishPrice", "dishQuantity",
                    "dishImageUrl"
                ]
                for field in dish_fields:
                    assert field in dish_item
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_get_cart_unauthorized(self, api_client, base_url):
        """Test getting cart without authentication."""
        response = api_client.get(f"{base_url}/cart")
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    def test_cart_response_structure(self, authenticated_client, base_url):
        """Test cart response structure."""
        response = authenticated_client.get(f"{base_url}/cart")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have content field with array
        assert "content" in data
        assert isinstance(data["content"], list)
        
        # Each cart item should have the correct structure
        for cart_item in data["content"]:
            assert isinstance(cart_item, dict)
            
            # Check required fields exist
            required_fields = [
                "id", "reservationId", "address", "date", "timeSlot",
                "state", "dishItems"
            ]
            for field in required_fields:
                assert field in cart_item
            
            # Validate field types
            assert isinstance(cart_item["id"], str)
            assert isinstance(cart_item["reservationId"], str)
            assert isinstance(cart_item["address"], str)
            assert isinstance(cart_item["date"], str)
            assert isinstance(cart_item["timeSlot"], str)
            assert isinstance(cart_item["state"], str)
            assert isinstance(cart_item["dishItems"], list)
            
            # Validate state values
            valid_states = ["SUBMITTED", "IN_PROGRESS", "CANCELLED", "COMPLETED"]
            assert cart_item["state"] in valid_states
            
            # Validate dish items
            for dish_item in cart_item["dishItems"]:
                dish_fields = [
                    "dishId", "dishName", "dishPrice", "dishQuantity",
                    "dishImageUrl"
                ]
                for field in dish_fields:
                    assert field in dish_item
                
                # Validate dish item types
                assert isinstance(dish_item["dishId"], str)
                assert isinstance(dish_item["dishName"], str)
                assert isinstance(dish_item["dishPrice"], str)
                assert isinstance(dish_item["dishQuantity"], int)
                assert isinstance(dish_item["dishImageUrl"], str)
                
                # Validate quantity is positive
                assert dish_item["dishQuantity"] > 0
                
                # Validate price format
                assert dish_item["dishPrice"].startswith("$")
                
                # Validate URL format
                assert dish_item["dishImageUrl"].startswith(("http://", "https://"))
    
    @pytest.mark.auth
    def test_cart_data_integrity(self, authenticated_client, base_url):
        """Test cart data integrity."""
        response = authenticated_client.get(f"{base_url}/cart")
        
        if response.status_code == 200:
            data = response.json()
            
            for cart_item in data["content"]:
                # IDs should be non-empty
                assert len(cart_item["id"]) > 0
                assert len(cart_item["reservationId"]) > 0
                
                # Address should be meaningful
                assert len(cart_item["address"]) > 5
                
                # Date should be in valid format
                date_parts = cart_item["date"].split("-")
                assert len(date_parts) == 3
                
                # Time slot should contain time information
                assert ":" in cart_item["timeSlot"] or "-" in cart_item["timeSlot"]
                
                # Dish items should have valid data
                for dish_item in cart_item["dishItems"]:
                    assert len(dish_item["dishId"]) > 0
                    assert len(dish_item["dishName"]) > 0
                    
                    # Price should be valid
                    price_str = dish_item["dishPrice"].replace("$", "")
                    try:
                        float(price_str)
                    except ValueError:
                        pytest.fail(f"Invalid price format: {dish_item['dishPrice']}")


class TestCartSubmission:
    """Test cases for cart submission endpoint."""
    
    @pytest.mark.auth
    def test_submit_cart_success(self, authenticated_client, base_url):
        """Test successful cart submission."""
        # First, get the current cart to see if there's anything to submit
        cart_response = authenticated_client.get(f"{base_url}/cart")
        assert cart_response.status_code == 200
        
        cart_data = cart_response.json()
        
        # If cart has items, try to submit
        if cart_data["content"]:
            cart_item = cart_data["content"][0]
            
            # Submit the cart item
            response = authenticated_client.put(f"{base_url}/cart", json=cart_item)
            
            # Should succeed or fail gracefully
            assert response.status_code in [200, 400, 409]
            
            if response.status_code == 200:
                assert response.headers["content-type"] == "application/json"
                
                data = response.json()
                # Response should contain cart information
                assert "content" in data or "message" in data
    
    @pytest.mark.auth
    def test_submit_cart_with_valid_preorder(self, authenticated_client, base_url):
        """Test submitting cart with valid preorder data."""
        valid_preorder = {
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
        
        response = authenticated_client.put(f"{base_url}/cart", json=valid_preorder)
        
        # Should succeed or fail based on business logic
        assert response.status_code in [200, 400, 404, 409]
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_submit_cart_unauthorized(self, api_client, base_url):
        """Test submitting cart without authentication."""
        preorder_data = {
            "id": "test_id",
            "reservationId": "test_reservation",
            "address": "Test Address",
            "date": "2024-12-31",
            "timeSlot": "12:00 - 13:00",
            "state": "SUBMITTED",
            "dishItems": []
        }
        
        response = api_client.put(f"{base_url}/cart", json=preorder_data)
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_submit_cart_missing_fields(self, authenticated_client, base_url):
        """Test submitting cart with missing required fields."""
        incomplete_data_sets = [
            {},  # Empty payload
            {"id": "test_id"},  # Missing other fields
            {
                "id": "test_id",
                "reservationId": "test_reservation"
                # Missing address, date, etc.
            },
            {
                "id": "test_id",
                "reservationId": "test_reservation",
                "address": "Test Address",
                "date": "2024-12-31",
                "timeSlot": "12:00 - 13:00",
                "state": "SUBMITTED"
                # Missing dishItems
            }
        ]
        
        for incomplete_data in incomplete_data_sets:
            response = authenticated_client.put(f"{base_url}/cart", json=incomplete_data)
            assert response.status_code in [400, 422], f"Failed for data: {incomplete_data}"
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_submit_cart_invalid_state(self, authenticated_client, base_url):
        """Test submitting cart with invalid state."""
        invalid_preorder = {
            "id": "test_id",
            "reservationId": "test_reservation",
            "address": "Test Address",
            "date": "2024-12-31",
            "timeSlot": "12:00 - 13:00",
            "state": "INVALID_STATE",
            "dishItems": []
        }
        
        response = authenticated_client.put(f"{base_url}/cart", json=invalid_preorder)
        
        assert response.status_code in [400, 422]
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_submit_cart_invalid_dish_items(self, authenticated_client, base_url):
        """Test submitting cart with invalid dish items."""
        invalid_dish_items = [
            # Missing required fields
            [{"dishId": "test_dish"}],
            # Invalid quantity
            [{
                "dishId": "test_dish",
                "dishName": "Test Dish",
                "dishPrice": "$10.00",
                "dishQuantity": 0,  # Invalid quantity
                "dishImageUrl": "https://example.com/image.jpg"
            }],
            # Invalid price format
            [{
                "dishId": "test_dish",
                "dishName": "Test Dish",
                "dishPrice": "invalid_price",
                "dishQuantity": 1,
                "dishImageUrl": "https://example.com/image.jpg"
            }],
            # Invalid URL format
            [{
                "dishId": "test_dish",
                "dishName": "Test Dish",
                "dishPrice": "$10.00",
                "dishQuantity": 1,
                "dishImageUrl": "invalid_url"
            }]
        ]
        
        for dish_items in invalid_dish_items:
            preorder_data = {
                "id": "test_id",
                "reservationId": "test_reservation",
                "address": "Test Address",
                "date": "2024-12-31",
                "timeSlot": "12:00 - 13:00",
                "state": "SUBMITTED",
                "dishItems": dish_items
            }
            
            response = authenticated_client.put(f"{base_url}/cart", json=preorder_data)
            assert response.status_code in [400, 422], f"Failed for dish items: {dish_items}"
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_submit_cart_invalid_date_format(self, authenticated_client, base_url):
        """Test submitting cart with invalid date format."""
        invalid_dates = [
            "invalid-date",
            "2024-13-01",  # Invalid month
            "2024-02-30",  # Invalid day
            "01-12-2024",  # Wrong format
            ""
        ]
        
        for date in invalid_dates:
            preorder_data = {
                "id": "test_id",
                "reservationId": "test_reservation",
                "address": "Test Address",
                "date": date,
                "timeSlot": "12:00 - 13:00",
                "state": "SUBMITTED",
                "dishItems": []
            }
            
            response = authenticated_client.put(f"{base_url}/cart", json=preorder_data)
            assert response.status_code in [400, 422], f"Failed for date: {date}"


class TestCartIntegration:
    """Integration tests for cart functionality."""
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_cart_management_flow(self, authenticated_client, base_url):
        """Test complete cart management flow."""
        # Step 1: Get current cart
        cart_response = authenticated_client.get(f"{base_url}/cart")
        assert cart_response.status_code == 200
        
        cart_data = cart_response.json()
        
        # Step 2: If cart has items, try to submit
        if cart_data["content"]:
            original_cart_item = cart_data["content"][0]
            
            # Modify the cart item (e.g., change state to SUBMITTED)
            modified_cart_item = original_cart_item.copy()
            modified_cart_item["state"] = "SUBMITTED"
            
            # Submit the modified cart
            submit_response = authenticated_client.put(f"{base_url}/cart", json=modified_cart_item)
            
            # Should succeed or fail gracefully
            assert submit_response.status_code in [200, 400, 409]
            
            # Step 3: Get cart again to see changes
            updated_cart_response = authenticated_client.get(f"{base_url}/cart")
            assert updated_cart_response.status_code == 200
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_cart_and_reservations_consistency(self, authenticated_client, base_url):
        """Test consistency between cart and reservations."""
        # Get cart
        cart_response = authenticated_client.get(f"{base_url}/cart")
        assert cart_response.status_code == 200
        
        cart_data = cart_response.json()
        
        # Get reservations
        reservations_response = authenticated_client.get(f"{base_url}/reservations")
        assert reservations_response.status_code == 200
        
        reservations_data = reservations_response.json()
        
        # Check consistency between cart and reservations
        if cart_data["content"] and reservations_data:
            cart_reservation_ids = {item["reservationId"] for item in cart_data["content"]}
            reservation_ids = {reservation["id"] for reservation in reservations_data}
            
            # Cart items should reference existing reservations
            for cart_reservation_id in cart_reservation_ids:
                assert cart_reservation_id in reservation_ids, f"Cart references non-existent reservation: {cart_reservation_id}"


class TestCartErrorScenarios:
    """Test error scenarios and edge cases."""
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_cart_with_malformed_json(self, authenticated_client, base_url):
        """Test cart submission with malformed JSON."""
        malformed_json = '{"id": "test_id", "reservationId": "test"'  # Missing closing brace
        
        response = authenticated_client.put(
            f"{base_url}/cart",
            data=malformed_json,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_cart_with_special_characters(self, authenticated_client, base_url):
        """Test cart submission with special characters."""
        special_char_data = {
            "id": "<script>alert('xss')</script>",
            "reservationId": "'; DROP TABLE cart; --",
            "address": "Test Address",
            "date": "2024-12-31",
            "timeSlot": "12:00 - 13:00",
            "state": "SUBMITTED",
            "dishItems": []
        }
        
        response = authenticated_client.put(f"{base_url}/cart", json=special_char_data)
        
        # Should handle gracefully
        assert response.status_code in [400, 422]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_cart_with_oversized_payload(self, authenticated_client, base_url):
        """Test cart submission with oversized payload."""
        # Create a very large dish items array
        large_dish_items = []
        for i in range(1000):
            large_dish_items.append({
                "dishId": f"dish_{i}",
                "dishName": f"Dish {i}" * 100,  # Very long name
                "dishPrice": "$10.00",
                "dishQuantity": 1,
                "dishImageUrl": "https://example.com/image.jpg"
            })
        
        oversized_data = {
            "id": "test_id",
            "reservationId": "test_reservation",
            "address": "Test Address",
            "date": "2024-12-31",
            "timeSlot": "12:00 - 13:00",
            "state": "SUBMITTED",
            "dishItems": large_dish_items
        }
        
        response = authenticated_client.put(f"{base_url}/cart", json=oversized_data)
        
        # Should handle gracefully
        assert response.status_code in [400, 413, 422]  # 413 = Payload Too Large
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_concurrent_cart_operations(self, authenticated_client, base_url):
        """Test concurrent cart operations."""
        import threading
        
        responses = []
        
        def get_cart():
            response = authenticated_client.get(f"{base_url}/cart")
            responses.append(response)
        
        def submit_cart():
            preorder_data = {
                "id": "concurrent_test",
                "reservationId": "test_reservation",
                "address": "Test Address",
                "date": "2024-12-31",
                "timeSlot": "12:00 - 13:00",
                "state": "SUBMITTED",
                "dishItems": []
            }
            response = authenticated_client.put(f"{base_url}/cart", json=preorder_data)
            responses.append(response)
        
        # Create multiple threads
        threads = []
        for _ in range(3):
            threads.append(threading.Thread(target=get_cart))
            threads.append(threading.Thread(target=submit_cart))
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should be handled gracefully
        for response in responses:
            assert response.status_code in [200, 400, 401, 409, 422]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_cart_operations_with_expired_token(self, api_client, base_url):
        """Test cart operations with expired token."""
        # Use an obviously invalid token
        api_client.headers.update({"Authorization": "Bearer expired_token_12345"})
        
        # Test GET cart
        get_response = api_client.get(f"{base_url}/cart")
        assert get_response.status_code == 401
        
        # Test PUT cart
        preorder_data = {
            "id": "test_id",
            "reservationId": "test_reservation",
            "address": "Test Address",
            "date": "2024-12-31",
            "timeSlot": "12:00 - 13:00",
            "state": "SUBMITTED",
            "dishItems": []
        }
        
        put_response = api_client.put(f"{base_url}/cart", json=preorder_data)
        assert put_response.status_code == 401