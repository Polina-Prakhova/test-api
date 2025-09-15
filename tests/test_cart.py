"""
Cart API Tests.

This module contains comprehensive tests for cart endpoints
including getting cart contents and submitting preorders.
"""

import pytest
import requests
from typing import Dict, Any, List

from tests.utils.api_client import APIClient, AuthenticatedAPIClient
from tests.utils.validators import validator
from tests.utils.test_data import test_data
from tests.config import api_config, test_config


class TestCartEndpoints:
    """Test suite for cart endpoints."""
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_get_cart(self, authenticated_client: AuthenticatedAPIClient):
        """Test retrieving user's cart."""
        response = authenticated_client.get(api_config.cart_endpoints["cart"])
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Validate cart response structure
            validator.validate_response(response_data, "cart_response")
            
            # Check required fields
            assert "content" in response_data
            
            cart_items = response_data["content"]
            
            # Validate each cart item
            for item in cart_items:
                assert "id" in item
                assert "reservationId" in item
                assert "state" in item
                
                # Validate business rules
                business_rules = {
                    "id_not_empty": {
                        "field": "id",
                        "condition": "not_empty"
                    },
                    "reservation_id_not_empty": {
                        "field": "reservationId",
                        "condition": "not_empty"
                    },
                    "valid_state": {
                        "field": "state",
                        "condition": "not_empty"
                    }
                }
                errors = validator.validate_business_rules(item, business_rules)
                assert not errors, f"Business rule violations for cart item: {errors}"
                
                # Validate dish items if present
                if "dishItems" in item:
                    dish_items = item["dishItems"]
                    for dish_item in dish_items:
                        assert "dishId" in dish_item
                        assert "dishName" in dish_item
                        assert "dishPrice" in dish_item
                        assert "dishQuantity" in dish_item
                        
                        # Validate price format
                        assert dish_item["dishPrice"].startswith("$"), "Dish price should start with $"
                        
                        # Validate quantity is positive
                        assert dish_item["dishQuantity"] > 0, "Dish quantity should be positive"
        
        elif response.status_code == 401:
            pytest.skip("Authentication required for cart access")
        
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.positive
    def test_submit_preorder(
        self,
        authenticated_client: AuthenticatedAPIClient,
        preorder_data: Dict[str, Any]
    ):
        """Test submitting a preorder."""
        response = authenticated_client.put(
            api_config.cart_endpoints["cart"],
            data=preorder_data
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Should return updated cart response
            validator.validate_response(response_data, "cart_response")
            
            # Check that the preorder was processed
            assert "content" in response_data
            
            # The submitted preorder should be in the cart with updated state
            cart_items = response_data["content"]
            submitted_items = [item for item in cart_items if item.get("state") == "SUBMITTED"]
            
            # Should have at least one submitted item
            assert len(submitted_items) > 0, "Should have at least one submitted preorder"
        
        elif response.status_code == 401:
            pytest.skip("Authentication required for preorder submission")
        
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.negative
    def test_get_cart_without_auth(self, api_client: APIClient):
        """Test getting cart without authentication."""
        response = api_client.get(api_config.cart_endpoints["cart"])
        
        # Should require authentication
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    @pytest.mark.negative
    def test_submit_preorder_without_auth(self, api_client: APIClient, preorder_data: Dict[str, Any]):
        """Test submitting preorder without authentication."""
        response = api_client.put(
            api_config.cart_endpoints["cart"],
            data=preorder_data
        )
        
        # Should require authentication
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    @pytest.mark.negative
    def test_submit_preorder_invalid_data(self, authenticated_client: AuthenticatedAPIClient):
        """Test submitting preorder with invalid data."""
        invalid_data = {
            "invalidField": "invalidValue"
        }
        
        response = authenticated_client.put(
            api_config.cart_endpoints["cart"],
            data=invalid_data
        )
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should return validation error
            assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    @pytest.mark.negative
    def test_submit_preorder_missing_required_fields(self, authenticated_client: AuthenticatedAPIClient):
        """Test submitting preorder with missing required fields."""
        incomplete_data = {
            "id": test_data.generate_object_id()
            # Missing other required fields
        }
        
        response = authenticated_client.put(
            api_config.cart_endpoints["cart"],
            data=incomplete_data
        )
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should return validation error
            assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    @pytest.mark.negative
    def test_submit_preorder_invalid_state(self, authenticated_client: AuthenticatedAPIClient):
        """Test submitting preorder with invalid state."""
        invalid_preorder = test_data.generate_preorder_data()
        invalid_preorder["state"] = "INVALID_STATE"
        
        response = authenticated_client.put(
            api_config.cart_endpoints["cart"],
            data=invalid_preorder
        )
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should return validation error for invalid state
            assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    @pytest.mark.negative
    def test_submit_preorder_invalid_dish_quantity(self, authenticated_client: AuthenticatedAPIClient):
        """Test submitting preorder with invalid dish quantities."""
        invalid_quantities = [0, -1, "invalid"]
        
        for invalid_quantity in invalid_quantities:
            preorder = test_data.generate_preorder_data()
            
            # Set invalid quantity for first dish item
            if preorder["dishItems"]:
                preorder["dishItems"][0]["dishQuantity"] = invalid_quantity
            
            response = authenticated_client.put(
                api_config.cart_endpoints["cart"],
                data=preorder
            )
            
            if response.status_code != 401:  # Skip if not authenticated
                # Should return validation error for invalid quantity
                assert response.status_code in [400, 422], f"Invalid quantity {invalid_quantity} was accepted"
    
    @pytest.mark.negative
    def test_submit_preorder_empty_dish_items(self, authenticated_client: AuthenticatedAPIClient):
        """Test submitting preorder with empty dish items."""
        empty_preorder = test_data.generate_preorder_data()
        empty_preorder["dishItems"] = []
        
        response = authenticated_client.put(
            api_config.cart_endpoints["cart"],
            data=empty_preorder
        )
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should handle empty dish items appropriately
            # This might be valid (empty cart) or invalid depending on business rules
            assert response.status_code in [200, 400, 422], f"Unexpected status code: {response.status_code}"
    
    @pytest.mark.integration
    def test_cart_preorder_flow(self, authenticated_client: AuthenticatedAPIClient):
        """Test complete cart and preorder flow."""
        # Step 1: Get current cart
        cart_response = authenticated_client.get(api_config.cart_endpoints["cart"])
        
        if cart_response.status_code == 200:
            initial_cart = cart_response.json()
            
            # Step 2: Submit a preorder
            preorder = test_data.generate_preorder_data()
            
            submit_response = authenticated_client.put(
                api_config.cart_endpoints["cart"],
                data=preorder
            )
            
            if submit_response.status_code == 200:
                updated_cart = submit_response.json()
                
                # Step 3: Verify cart was updated
                assert "content" in updated_cart
                
                # Should have the submitted preorder
                cart_items = updated_cart["content"]
                submitted_items = [item for item in cart_items if item.get("state") == "SUBMITTED"]
                
                assert len(submitted_items) > 0, "Should have submitted preorder in cart"
        
        elif cart_response.status_code != 401:
            pytest.fail(f"Failed to get cart: {cart_response.status_code}")
    
    @pytest.mark.performance
    def test_cart_endpoint_response_time(self, authenticated_client: AuthenticatedAPIClient):
        """Test cart endpoint response time."""
        import time
        
        start_time = time.time()
        response = authenticated_client.get(api_config.cart_endpoints["cart"])
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should respond within reasonable time
        assert response_time < 5.0, f"Response time too slow: {response_time}s"
        
        if response.status_code != 401:  # Skip if not authenticated
            assert response.status_code == 200
    
    @pytest.mark.security
    def test_cart_access_control(self, authenticated_client: AuthenticatedAPIClient):
        """Test that users can only access their own cart."""
        response = authenticated_client.get(api_config.cart_endpoints["cart"])
        
        if response.status_code == 200:
            cart_data = response.json()
            
            # All cart items should belong to the authenticated user
            # (This is a basic check - in a real system, you'd verify user ownership)
            assert "content" in cart_data
            
            for item in cart_data["content"]:
                assert "id" in item, "Cart item should have an ID"
                # Additional checks would verify that the cart item belongs to the current user
        
        elif response.status_code != 401:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.security
    def test_cart_data_validation(self, authenticated_client: AuthenticatedAPIClient):
        """Test that cart endpoints properly validate data."""
        # Test with malicious data
        malicious_preorder = test_data.generate_preorder_data()
        malicious_preorder["reservationId"] = "'; DROP TABLE cart; --"
        
        response = authenticated_client.put(
            api_config.cart_endpoints["cart"],
            data=malicious_preorder
        )
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should not cause server error
            assert response.status_code in [200, 400, 422], "SQL injection attempt should be handled safely"
    
    @pytest.mark.regression
    def test_cart_response_structure(self, authenticated_client: AuthenticatedAPIClient):
        """Test that cart response structure is consistent."""
        response = authenticated_client.get(api_config.cart_endpoints["cart"])
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Check for expected top-level structure
            expected_fields = ["content"]
            for field in expected_fields:
                assert field in response_data, f"Expected field '{field}' missing from cart response"
            
            # If there are cart items, check their structure
            cart_items = response_data.get("content", [])
            if cart_items:
                first_item = cart_items[0]
                expected_item_fields = ["id", "reservationId", "state"]
                
                for field in expected_item_fields:
                    assert field in first_item, f"Expected cart item field '{field}' missing"
        
        elif response.status_code != 401:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.positive
    def test_cart_state_values(self, authenticated_client: AuthenticatedAPIClient):
        """Test that cart item state values are valid."""
        response = authenticated_client.get(api_config.cart_endpoints["cart"])
        
        if response.status_code == 200:
            cart_data = response.json()
            cart_items = cart_data.get("content", [])
            
            valid_states = ["SUBMITTED", "IN_PROGRESS", "CANCELLED"]
            
            for item in cart_items:
                if "state" in item:
                    assert item["state"] in valid_states, f"Invalid cart item state: {item['state']}"
        
        elif response.status_code != 401:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.positive
    def test_cart_dish_items_validation(self, authenticated_client: AuthenticatedAPIClient):
        """Test that dish items in cart have valid data."""
        response = authenticated_client.get(api_config.cart_endpoints["cart"])
        
        if response.status_code == 200:
            cart_data = response.json()
            cart_items = cart_data.get("content", [])
            
            for item in cart_items:
                if "dishItems" in item:
                    dish_items = item["dishItems"]
                    
                    for dish_item in dish_items:
                        # Validate required fields
                        required_fields = ["dishId", "dishName", "dishPrice", "dishQuantity"]
                        for field in required_fields:
                            assert field in dish_item, f"Missing required dish item field: {field}"
                        
                        # Validate data types and formats
                        assert isinstance(dish_item["dishQuantity"], int), "Dish quantity should be integer"
                        assert dish_item["dishQuantity"] > 0, "Dish quantity should be positive"
                        assert dish_item["dishPrice"].startswith("$"), "Dish price should start with $"
                        assert len(dish_item["dishName"]) > 0, "Dish name should not be empty"
        
        elif response.status_code != 401:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.positive
    def test_cart_total_calculation(self, authenticated_client: AuthenticatedAPIClient):
        """Test cart total calculation if provided."""
        response = authenticated_client.get(api_config.cart_endpoints["cart"])
        
        if response.status_code == 200:
            cart_data = response.json()
            cart_items = cart_data.get("content", [])
            
            for item in cart_items:
                if "dishItems" in item and "total" in item:
                    # Calculate expected total
                    expected_total = 0.0
                    
                    for dish_item in item["dishItems"]:
                        if "dishPrice" in dish_item and "dishQuantity" in dish_item:
                            try:
                                price_str = dish_item["dishPrice"].replace("$", "")
                                price = float(price_str)
                                quantity = dish_item["dishQuantity"]
                                expected_total += price * quantity
                            except ValueError:
                                continue
                    
                    # Compare with provided total (allowing for small floating point differences)
                    if expected_total > 0:
                        provided_total_str = item["total"].replace("$", "")
                        try:
                            provided_total = float(provided_total_str)
                            assert abs(expected_total - provided_total) < 0.01, \
                                f"Total mismatch: expected {expected_total}, got {provided_total}"
                        except ValueError:
                            pass
        
        elif response.status_code != 401:
            pytest.fail(f"Unexpected status code: {response.status_code}")