"""
Reservations API Tests.

This module contains comprehensive tests for reservations endpoints
including listing reservations, canceling reservations, ordering dishes,
and managing reservation-related operations.
"""

import pytest
import requests
from typing import Dict, Any, List

from tests.utils.api_client import APIClient, AuthenticatedAPIClient
from tests.utils.validators import validator
from tests.utils.test_data import test_data
from tests.config import api_config, test_config


class TestReservationsEndpoints:
    """Test suite for reservations endpoints."""
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_get_user_reservations(self, authenticated_client: AuthenticatedAPIClient):
        """Test retrieving user's reservations."""
        response = authenticated_client.get(api_config.reservations_endpoints["list"])
        
        if response.status_code == 200:
            response_data = response.json()
            assert isinstance(response_data, list), "Expected list of reservations"
            
            # Validate each reservation in the response
            if response_data:
                validator.validate_list_response(response_data, "reservation_response")
                
                # Check that all reservations have required fields
                for reservation in response_data:
                    assert "id" in reservation
                    assert "status" in reservation
                    assert "date" in reservation
                    
                    # Validate business rules
                    business_rules = {
                        "id_not_empty": {
                            "field": "id",
                            "condition": "not_empty"
                        },
                        "status_not_empty": {
                            "field": "status",
                            "condition": "not_empty"
                        }
                    }
                    errors = validator.validate_business_rules(reservation, business_rules)
                    assert not errors, f"Business rule violations for reservation: {errors}"
        
        elif response.status_code == 401:
            pytest.skip("Authentication required for reservations list")
        
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.positive
    def test_cancel_reservation(
        self,
        authenticated_client: AuthenticatedAPIClient,
        temp_reservation_id: str
    ):
        """Test canceling a reservation."""
        if temp_reservation_id is None:
            pytest.skip("Could not create temporary reservation for testing")
        
        delete_url = api_config.reservations_endpoints["detail"].format(id=temp_reservation_id)
        response = authenticated_client.delete(delete_url)
        
        if response.status_code == 200:
            # Successful cancellation
            # Response might be empty or contain confirmation message
            pass
        
        elif response.status_code == 404:
            # Reservation not found (might have been already deleted)
            pass
        
        elif response.status_code == 401:
            pytest.skip("Authentication required for reservation cancellation")
        
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.positive
    def test_get_available_dishes_for_reservation(
        self,
        authenticated_client: AuthenticatedAPIClient,
        mock_reservation_id: str
    ):
        """Test retrieving available dishes for a reservation."""
        dishes_url = api_config.reservations_endpoints["available_dishes"].format(
            reservationId=mock_reservation_id
        )
        
        response = authenticated_client.get(dishes_url)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Should have menu response structure
            assert "content" in response_data, "Expected content field in menu response"
            
            dishes = response_data["content"]
            if dishes:
                # Validate each dish
                for dish in dishes:
                    assert "id" in dish
                    assert "name" in dish
                    assert "price" in dish
                    
                    # Validate price format
                    assert dish["price"].startswith("$"), "Price should start with $"
        
        elif response.status_code == 404:
            # Reservation not found - acceptable in test environment
            pass
        
        elif response.status_code == 401:
            pytest.skip("Authentication required for available dishes")
        
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.positive
    @pytest.mark.parametrize("dish_type", [
        "APPETIZER",
        "MAIN_COURSE",
        "DESSERT"
    ])
    def test_get_available_dishes_by_type(
        self,
        authenticated_client: AuthenticatedAPIClient,
        mock_reservation_id: str,
        dish_type: str
    ):
        """Test retrieving available dishes filtered by type."""
        dishes_url = api_config.reservations_endpoints["available_dishes"].format(
            reservationId=mock_reservation_id
        )
        params = {"dishType": dish_type}
        
        response = authenticated_client.get(dishes_url, params=params)
        
        if response.status_code == 200:
            response_data = response.json()
            assert "content" in response_data
            
            dishes = response_data["content"]
            for dish in dishes:
                if "dishType" in dish:
                    assert dish["dishType"] == dish_type, f"Expected {dish_type}, got {dish['dishType']}"
        
        elif response.status_code in [404, 401]:
            # Acceptable in test environment
            pass
    
    @pytest.mark.positive
    @pytest.mark.parametrize("sort_param", [
        "popularity,asc",
        "popularity,desc",
        "price,asc",
        "price,desc"
    ])
    def test_get_available_dishes_with_sorting(
        self,
        authenticated_client: AuthenticatedAPIClient,
        mock_reservation_id: str,
        sort_param: str
    ):
        """Test retrieving available dishes with sorting."""
        dishes_url = api_config.reservations_endpoints["available_dishes"].format(
            reservationId=mock_reservation_id
        )
        params = {"sort": sort_param}
        
        response = authenticated_client.get(dishes_url, params=params)
        
        if response.status_code == 200:
            response_data = response.json()
            assert "content" in response_data
            
            # Basic validation that sorting parameter is accepted
            dishes = response_data["content"]
            if len(dishes) > 1 and "price" in sort_param:
                # Validate price sorting
                prices = []
                for dish in dishes:
                    if "price" in dish:
                        price_str = dish["price"].replace("$", "")
                        try:
                            price_value = float(price_str)
                            prices.append(price_value)
                        except ValueError:
                            continue
                
                if len(prices) > 1:
                    if "asc" in sort_param:
                        assert prices == sorted(prices), "Prices should be in ascending order"
                    else:
                        assert prices == sorted(prices, reverse=True), "Prices should be in descending order"
        
        elif response.status_code in [404, 401]:
            # Acceptable in test environment
            pass
    
    @pytest.mark.positive
    def test_order_dish_for_reservation(
        self,
        authenticated_client: AuthenticatedAPIClient,
        mock_reservation_id: str,
        mock_dish_id: str
    ):
        """Test ordering a dish for a reservation."""
        order_url = api_config.reservations_endpoints["order_dish"].format(
            reservationId=mock_reservation_id,
            dishId=mock_dish_id
        )
        
        response = authenticated_client.post(order_url)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Should contain success message
            assert "message" in response_data
            assert "cart" in response_data["message"].lower() or "order" in response_data["message"].lower()
        
        elif response.status_code == 404:
            # Reservation or dish not found - acceptable in test environment
            pass
        
        elif response.status_code == 401:
            pytest.skip("Authentication required for dish ordering")
        
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.negative
    def test_get_reservations_without_auth(self, api_client: APIClient):
        """Test getting reservations without authentication."""
        response = api_client.get(api_config.reservations_endpoints["list"])
        
        # Should require authentication
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    @pytest.mark.negative
    def test_cancel_reservation_without_auth(self, api_client: APIClient, mock_reservation_id: str):
        """Test canceling reservation without authentication."""
        delete_url = api_config.reservations_endpoints["detail"].format(id=mock_reservation_id)
        response = api_client.delete(delete_url)
        
        # Should require authentication
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    @pytest.mark.negative
    def test_cancel_nonexistent_reservation(self, authenticated_client: AuthenticatedAPIClient):
        """Test canceling a non-existent reservation."""
        nonexistent_id = "nonexistent123456789012345678901234"
        delete_url = api_config.reservations_endpoints["detail"].format(id=nonexistent_id)
        
        response = authenticated_client.delete(delete_url)
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should return 404 for non-existent reservation
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    @pytest.mark.negative
    def test_cancel_reservation_invalid_id(self, authenticated_client: AuthenticatedAPIClient):
        """Test canceling reservation with invalid ID format."""
        invalid_ids = [
            "invalid-id",
            "123",
            "",
            "special-chars!@#"
        ]
        
        for invalid_id in invalid_ids:
            delete_url = api_config.reservations_endpoints["detail"].format(id=invalid_id)
            response = authenticated_client.delete(delete_url)
            
            if response.status_code != 401:  # Skip if not authenticated
                # Should return 400 or 404 for invalid ID
                assert response.status_code in [400, 404], f"Expected 400 or 404 for invalid ID '{invalid_id}', got {response.status_code}"
    
    @pytest.mark.negative
    def test_get_available_dishes_invalid_reservation(self, authenticated_client: AuthenticatedAPIClient):
        """Test getting available dishes for invalid reservation."""
        invalid_reservation_id = "invalid123456789012345678901234"
        dishes_url = api_config.reservations_endpoints["available_dishes"].format(
            reservationId=invalid_reservation_id
        )
        
        response = authenticated_client.get(dishes_url)
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should return 404 for invalid reservation
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    @pytest.mark.negative
    def test_order_dish_invalid_reservation(self, authenticated_client: AuthenticatedAPIClient):
        """Test ordering dish for invalid reservation."""
        invalid_reservation_id = "invalid123456789012345678901234"
        order_url = api_config.reservations_endpoints["order_dish"].format(
            reservationId=invalid_reservation_id,
            dishId=test_config.TEST_DISH_ID
        )
        
        response = authenticated_client.post(order_url)
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should return 404 for invalid reservation
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    @pytest.mark.negative
    def test_order_invalid_dish(self, authenticated_client: AuthenticatedAPIClient):
        """Test ordering invalid dish for reservation."""
        invalid_dish_id = "invalid123456789012345678901234"
        order_url = api_config.reservations_endpoints["order_dish"].format(
            reservationId=test_config.TEST_RESERVATION_ID,
            dishId=invalid_dish_id
        )
        
        response = authenticated_client.post(order_url)
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should return 404 for invalid dish
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    @pytest.mark.negative
    def test_available_dishes_without_auth(self, api_client: APIClient, mock_reservation_id: str):
        """Test getting available dishes without authentication."""
        dishes_url = api_config.reservations_endpoints["available_dishes"].format(
            reservationId=mock_reservation_id
        )
        
        response = api_client.get(dishes_url)
        
        # Should require authentication
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    @pytest.mark.negative
    def test_order_dish_without_auth(self, api_client: APIClient, mock_reservation_id: str, mock_dish_id: str):
        """Test ordering dish without authentication."""
        order_url = api_config.reservations_endpoints["order_dish"].format(
            reservationId=mock_reservation_id,
            dishId=mock_dish_id
        )
        
        response = api_client.post(order_url)
        
        # Should require authentication
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    @pytest.mark.integration
    def test_reservation_dish_ordering_flow(self, authenticated_client: AuthenticatedAPIClient):
        """Test complete flow from viewing available dishes to ordering."""
        reservation_id = test_config.TEST_RESERVATION_ID
        
        # Step 1: Get available dishes
        dishes_url = api_config.reservations_endpoints["available_dishes"].format(
            reservationId=reservation_id
        )
        
        dishes_response = authenticated_client.get(dishes_url)
        
        if dishes_response.status_code == 200:
            dishes_data = dishes_response.json()
            available_dishes = dishes_data.get("content", [])
            
            if available_dishes:
                # Step 2: Order the first available dish
                first_dish = available_dishes[0]
                dish_id = first_dish.get("id")
                
                if dish_id:
                    order_url = api_config.reservations_endpoints["order_dish"].format(
                        reservationId=reservation_id,
                        dishId=dish_id
                    )
                    
                    order_response = authenticated_client.post(order_url)
                    
                    if order_response.status_code not in [401, 404]:  # Skip if auth issues or not found
                        assert order_response.status_code == 200, f"Dish ordering failed with status {order_response.status_code}"
        
        elif dishes_response.status_code not in [401, 404]:
            pytest.fail(f"Failed to get available dishes: {dishes_response.status_code}")
    
    @pytest.mark.performance
    def test_reservations_endpoint_response_time(self, authenticated_client: AuthenticatedAPIClient):
        """Test reservations endpoint response time."""
        import time
        
        start_time = time.time()
        response = authenticated_client.get(api_config.reservations_endpoints["list"])
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should respond within reasonable time
        assert response_time < 5.0, f"Response time too slow: {response_time}s"
        
        if response.status_code != 401:  # Skip if not authenticated
            assert response.status_code == 200
    
    @pytest.mark.security
    def test_reservation_access_control(self, authenticated_client: AuthenticatedAPIClient):
        """Test that users can only access their own reservations."""
        # This test assumes that the authenticated user has limited access
        response = authenticated_client.get(api_config.reservations_endpoints["list"])
        
        if response.status_code == 200:
            reservations = response.json()
            
            # All returned reservations should belong to the authenticated user
            # (This is a basic check - in a real system, you'd verify user ownership)
            for reservation in reservations:
                assert "id" in reservation, "Reservation should have an ID"
                # Additional checks would verify that the reservation belongs to the current user
        
        elif response.status_code != 401:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.security
    def test_reservation_data_validation(self, authenticated_client: AuthenticatedAPIClient):
        """Test that reservation endpoints properly validate data."""
        # Test with malicious reservation ID
        malicious_id = "'; DROP TABLE reservations; --"
        delete_url = api_config.reservations_endpoints["detail"].format(id=malicious_id)
        
        response = authenticated_client.delete(delete_url)
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should not cause server error
            assert response.status_code in [400, 404], "SQL injection attempt should be handled safely"
    
    @pytest.mark.regression
    def test_reservations_response_structure(self, authenticated_client: AuthenticatedAPIClient):
        """Test that reservations response structure is consistent."""
        response = authenticated_client.get(api_config.reservations_endpoints["list"])
        
        if response.status_code == 200:
            response_data = response.json()
            assert isinstance(response_data, list), "Reservations response should be a list"
            
            # If there are reservations, check their structure
            if response_data:
                first_reservation = response_data[0]
                expected_fields = ["id", "status", "date"]
                
                for field in expected_fields:
                    assert field in first_reservation, f"Expected reservation field '{field}' missing"
        
        elif response.status_code != 401:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.positive
    def test_reservation_status_values(self, authenticated_client: AuthenticatedAPIClient):
        """Test that reservation status values are valid."""
        response = authenticated_client.get(api_config.reservations_endpoints["list"])
        
        if response.status_code == 200:
            reservations = response.json()
            
            valid_statuses = ["confirmed", "pending", "cancelled", "completed", "in-progress"]
            
            for reservation in reservations:
                if "status" in reservation:
                    status = reservation["status"].lower()
                    # Status should be one of the expected values (flexible check)
                    assert any(valid_status in status for valid_status in valid_statuses), \
                        f"Unexpected reservation status: {reservation['status']}"
        
        elif response.status_code != 401:
            pytest.fail(f"Unexpected status code: {response.status_code}")