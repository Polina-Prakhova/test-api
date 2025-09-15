"""
Reservations API tests.
Tests for reservation management endpoints including listing, cancellation, and ordering.
"""
import pytest
import requests
from typing import Dict, Any


class TestReservationsListing:
    """Test cases for reservations listing endpoint."""
    
    @pytest.mark.auth
    def test_get_reservations_success(self, authenticated_client, base_url):
        """Test successful retrieval of user reservations."""
        response = authenticated_client.get(f"{base_url}/reservations")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        # Validate reservation structure if reservations exist
        if data:
            reservation = data[0]
            required_fields = [
                "id", "status", "locationAddress", "date",
                "timeSlot", "preOrder", "guestsNumber", "feedbackId"
            ]
            for field in required_fields:
                assert field in reservation
                assert isinstance(reservation[field], str)
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_get_reservations_unauthorized(self, api_client, base_url):
        """Test getting reservations without authentication."""
        response = api_client.get(f"{base_url}/reservations")
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    def test_reservations_response_structure(self, authenticated_client, base_url):
        """Test reservations response structure."""
        response = authenticated_client.get(f"{base_url}/reservations")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return an array
        assert isinstance(data, list)
        
        # Each reservation should have the correct structure
        for reservation in data:
            assert isinstance(reservation, dict)
            
            # Check required fields exist
            required_fields = [
                "id", "status", "locationAddress", "date",
                "timeSlot", "preOrder", "guestsNumber", "feedbackId"
            ]
            for field in required_fields:
                assert field in reservation
                assert isinstance(reservation[field], str)
            
            # Validate status values
            valid_statuses = ["confirmed", "pending", "cancelled", "completed", "in-progress"]
            assert reservation["status"] in valid_statuses
            
            # Validate date format (should be YYYY-MM-DD)
            date_parts = reservation["date"].split("-")
            assert len(date_parts) == 3
            assert len(date_parts[0]) == 4  # Year
            assert len(date_parts[1]) == 2  # Month
            assert len(date_parts[2]) == 2  # Day
    
    @pytest.mark.auth
    def test_reservations_data_integrity(self, authenticated_client, base_url):
        """Test reservations data integrity."""
        response = authenticated_client.get(f"{base_url}/reservations")
        
        if response.status_code == 200:
            data = response.json()
            
            for reservation in data:
                # ID should be non-empty
                assert len(reservation["id"]) > 0
                
                # Location address should be meaningful
                assert len(reservation["locationAddress"]) > 5
                
                # Time slot should contain time information
                assert ":" in reservation["timeSlot"] or "-" in reservation["timeSlot"]
                
                # Guests number should be numeric
                try:
                    guests = int(reservation["guestsNumber"])
                    assert guests > 0
                except ValueError:
                    pytest.fail(f"Guests number should be numeric: {reservation['guestsNumber']}")


class TestReservationCancellation:
    """Test cases for reservation cancellation endpoint."""
    
    @pytest.mark.auth
    def test_cancel_reservation_success(self, authenticated_client, base_url, sample_reservation_id):
        """Test successful reservation cancellation."""
        response = authenticated_client.delete(f"{base_url}/reservations/{sample_reservation_id}")
        
        # Should return success (200) or not found (404) if reservation doesn't exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            # Some APIs return a response body, others don't
            if response.content:
                # If there's content, it should be valid JSON
                data = response.json()
                assert isinstance(data, (dict, str))
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_cancel_reservation_unauthorized(self, api_client, base_url, sample_reservation_id):
        """Test cancelling reservation without authentication."""
        response = api_client.delete(f"{base_url}/reservations/{sample_reservation_id}")
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_cancel_nonexistent_reservation(self, authenticated_client, base_url):
        """Test cancelling non-existent reservation."""
        nonexistent_id = "nonexistent_reservation_12345"
        response = authenticated_client.delete(f"{base_url}/reservations/{nonexistent_id}")
        
        assert response.status_code == 404
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_cancel_reservation_invalid_id(self, authenticated_client, base_url):
        """Test cancelling reservation with invalid ID format."""
        invalid_ids = [
            "",
            "invalid_id",
            "123",
            "<script>alert('xss')</script>",
            "'; DROP TABLE reservations; --"
        ]
        
        for reservation_id in invalid_ids:
            response = authenticated_client.delete(f"{base_url}/reservations/{reservation_id}")
            assert response.status_code in [400, 404], f"Failed for ID: {reservation_id}"
    
    @pytest.mark.auth
    def test_cancel_reservation_twice(self, authenticated_client, base_url, sample_reservation_id):
        """Test cancelling the same reservation twice."""
        # First cancellation
        response1 = authenticated_client.delete(f"{base_url}/reservations/{sample_reservation_id}")
        
        # Second cancellation (should fail or be idempotent)
        response2 = authenticated_client.delete(f"{base_url}/reservations/{sample_reservation_id}")
        
        # First might succeed or fail if reservation doesn't exist
        assert response1.status_code in [200, 404]
        
        # Second should fail (already cancelled) or be idempotent
        assert response2.status_code in [200, 404, 409]


class TestReservationAvailableDishes:
    """Test cases for reservation available dishes endpoint."""
    
    @pytest.mark.auth
    def test_get_available_dishes_success(self, authenticated_client, base_url, sample_reservation_id):
        """Test successful retrieval of available dishes for reservation."""
        response = authenticated_client.get(
            f"{base_url}/reservations/{sample_reservation_id}/available-dishes"
        )
        
        assert response.status_code in [200, 404]  # 404 if reservation doesn't exist
        
        if response.status_code == 200:
            assert response.headers["content-type"] == "application/json"
            
            data = response.json()
            assert "content" in data
            assert isinstance(data["content"], list)
            
            # Validate dish structure if dishes exist
            if data["content"]:
                dish = data["content"][0]
                required_fields = ["id", "name", "previewImageUrl", "price", "state", "weight"]
                for field in required_fields:
                    assert field in dish
                    assert isinstance(dish[field], str)
    
    @pytest.mark.auth
    def test_get_available_dishes_with_dish_type_filter(self, authenticated_client, base_url, sample_reservation_id):
        """Test getting available dishes with dish type filter."""
        dish_types = ["APPETIZER", "MAIN_COURSE", "DESSERT"]
        
        for dish_type in dish_types:
            response = authenticated_client.get(
                f"{base_url}/reservations/{sample_reservation_id}/available-dishes",
                params={"dishType": dish_type}
            )
            
            # Should succeed or return 404 if reservation doesn't exist
            assert response.status_code in [200, 404]
    
    @pytest.mark.auth
    def test_get_available_dishes_with_sort(self, authenticated_client, base_url, sample_reservation_id):
        """Test getting available dishes with sorting."""
        sort_options = [
            "popularity,asc",
            "popularity,desc",
            "price,asc",
            "price,desc"
        ]
        
        for sort_option in sort_options:
            response = authenticated_client.get(
                f"{base_url}/reservations/{sample_reservation_id}/available-dishes",
                params={"sort": sort_option}
            )
            
            assert response.status_code in [200, 404]
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_get_available_dishes_unauthorized(self, api_client, base_url, sample_reservation_id):
        """Test getting available dishes without authentication."""
        response = api_client.get(
            f"{base_url}/reservations/{sample_reservation_id}/available-dishes"
        )
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_get_available_dishes_invalid_reservation(self, authenticated_client, base_url):
        """Test getting available dishes for invalid reservation ID."""
        invalid_ids = [
            "invalid_id",
            "nonexistent_reservation",
            "",
            "<script>alert('xss')</script>"
        ]
        
        for reservation_id in invalid_ids:
            response = authenticated_client.get(
                f"{base_url}/reservations/{reservation_id}/available-dishes"
            )
            assert response.status_code in [400, 404], f"Failed for ID: {reservation_id}"


class TestDishOrdering:
    """Test cases for dish ordering endpoint."""
    
    @pytest.mark.auth
    def test_order_dish_success(self, authenticated_client, base_url, sample_reservation_id, sample_dish_id):
        """Test successful dish ordering."""
        response = authenticated_client.post(
            f"{base_url}/reservations/{sample_reservation_id}/order/{sample_dish_id}"
        )
        
        # Should succeed or fail based on reservation/dish existence
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert response.headers["content-type"] == "application/json"
            
            data = response.json()
            assert "message" in data
            assert "cart" in data["message"].lower() or "order" in data["message"].lower()
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_order_dish_unauthorized(self, api_client, base_url, sample_reservation_id, sample_dish_id):
        """Test ordering dish without authentication."""
        response = api_client.post(
            f"{base_url}/reservations/{sample_reservation_id}/order/{sample_dish_id}"
        )
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_order_dish_invalid_reservation(self, authenticated_client, base_url, sample_dish_id):
        """Test ordering dish with invalid reservation ID."""
        invalid_reservation_id = "invalid_reservation_12345"
        
        response = authenticated_client.post(
            f"{base_url}/reservations/{invalid_reservation_id}/order/{sample_dish_id}"
        )
        
        assert response.status_code in [400, 404]
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_order_dish_invalid_dish(self, authenticated_client, base_url, sample_reservation_id):
        """Test ordering invalid dish."""
        invalid_dish_id = "invalid_dish_12345"
        
        response = authenticated_client.post(
            f"{base_url}/reservations/{sample_reservation_id}/order/{invalid_dish_id}"
        )
        
        assert response.status_code in [400, 404]
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_order_dish_special_characters(self, authenticated_client, base_url):
        """Test ordering dish with special characters in IDs."""
        special_ids = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE orders; --",
            "../../../etc/passwd"
        ]
        
        for special_id in special_ids:
            response = authenticated_client.post(
                f"{base_url}/reservations/{special_id}/order/{special_id}"
            )
            assert response.status_code in [400, 404]
    
    @pytest.mark.auth
    def test_order_same_dish_multiple_times(self, authenticated_client, base_url, sample_reservation_id, sample_dish_id):
        """Test ordering the same dish multiple times."""
        responses = []
        
        # Try to order the same dish multiple times
        for _ in range(3):
            response = authenticated_client.post(
                f"{base_url}/reservations/{sample_reservation_id}/order/{sample_dish_id}"
            )
            responses.append(response)
        
        # All requests should be handled gracefully
        for response in responses:
            assert response.status_code in [200, 400, 404, 409]


class TestReservationsIntegration:
    """Integration tests for reservations flow."""
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_reservation_management_flow(self, authenticated_client, base_url):
        """Test complete reservation management flow."""
        # Step 1: Get user reservations
        reservations_response = authenticated_client.get(f"{base_url}/reservations")
        assert reservations_response.status_code == 200
        
        reservations_data = reservations_response.json()
        
        # Step 2: If reservations exist, test available dishes
        if reservations_data:
            reservation_id = reservations_data[0]["id"]
            
            # Get available dishes
            dishes_response = authenticated_client.get(
                f"{base_url}/reservations/{reservation_id}/available-dishes"
            )
            
            # Should succeed or fail gracefully
            assert dishes_response.status_code in [200, 404]
            
            if dishes_response.status_code == 200:
                dishes_data = dishes_response.json()
                
                # Step 3: If dishes are available, try to order one
                if dishes_data.get("content"):
                    dish_id = dishes_data["content"][0]["id"]
                    
                    order_response = authenticated_client.post(
                        f"{base_url}/reservations/{reservation_id}/order/{dish_id}"
                    )
                    
                    # Should succeed or fail gracefully
                    assert order_response.status_code in [200, 400, 404, 409]
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_reservation_cancellation_flow(self, authenticated_client, base_url):
        """Test reservation cancellation flow."""
        # Step 1: Get user reservations
        reservations_response = authenticated_client.get(f"{base_url}/reservations")
        assert reservations_response.status_code == 200
        
        reservations_data = reservations_response.json()
        
        # Step 2: If reservations exist, try to cancel one
        if reservations_data:
            reservation_id = reservations_data[0]["id"]
            
            # Cancel reservation
            cancel_response = authenticated_client.delete(f"{base_url}/reservations/{reservation_id}")
            
            # Should succeed or fail gracefully
            assert cancel_response.status_code in [200, 404, 409]
            
            # Step 3: Verify reservation list is updated
            updated_reservations_response = authenticated_client.get(f"{base_url}/reservations")
            assert updated_reservations_response.status_code == 200
            
            updated_reservations_data = updated_reservations_response.json()
            
            # If cancellation succeeded, reservation should be removed or marked as cancelled
            if cancel_response.status_code == 200:
                # Either the reservation is removed or its status is updated
                remaining_reservation = None
                for reservation in updated_reservations_data:
                    if reservation["id"] == reservation_id:
                        remaining_reservation = reservation
                        break
                
                if remaining_reservation:
                    # If still present, should be marked as cancelled
                    assert remaining_reservation["status"] == "cancelled"


class TestReservationsErrorScenarios:
    """Test error scenarios and edge cases."""
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_concurrent_dish_ordering(self, authenticated_client, base_url, sample_reservation_id, sample_dish_id):
        """Test concurrent dish ordering for the same reservation."""
        import threading
        
        responses = []
        
        def order_dish():
            response = authenticated_client.post(
                f"{base_url}/reservations/{sample_reservation_id}/order/{sample_dish_id}"
            )
            responses.append(response)
        
        # Create multiple threads trying to order the same dish
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=order_dish)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should be handled gracefully
        for response in responses:
            assert response.status_code in [200, 400, 404, 409]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_reservation_operations_with_expired_token(self, api_client, base_url, sample_reservation_id):
        """Test reservation operations with expired token."""
        # Use an obviously invalid token
        api_client.headers.update({"Authorization": "Bearer expired_token_12345"})
        
        # Test various operations
        operations = [
            ("GET", f"{base_url}/reservations"),
            ("DELETE", f"{base_url}/reservations/{sample_reservation_id}"),
            ("GET", f"{base_url}/reservations/{sample_reservation_id}/available-dishes"),
            ("POST", f"{base_url}/reservations/{sample_reservation_id}/order/dish123")
        ]
        
        for method, url in operations:
            if method == "GET":
                response = api_client.get(url)
            elif method == "DELETE":
                response = api_client.delete(url)
            elif method == "POST":
                response = api_client.post(url)
            
            assert response.status_code == 401, f"Failed for {method} {url}"
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_malformed_reservation_requests(self, authenticated_client, base_url):
        """Test malformed reservation requests."""
        # Test with very long IDs
        long_id = "a" * 10000
        
        response = authenticated_client.get(f"{base_url}/reservations/{long_id}/available-dishes")
        assert response.status_code in [400, 404, 414]  # 414 = URI Too Long
        
        # Test with null bytes
        null_byte_id = "reservation%00id"
        response = authenticated_client.delete(f"{base_url}/reservations/{null_byte_id}")
        assert response.status_code in [400, 404]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_reservation_operations_rate_limiting(self, authenticated_client, base_url):
        """Test rate limiting on reservation operations."""
        # Make many requests quickly
        responses = []
        
        for _ in range(20):
            response = authenticated_client.get(f"{base_url}/reservations")
            responses.append(response)
        
        # Most should succeed, but rate limiting might kick in
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        # At least some should succeed
        assert success_count > 0
        
        # If rate limiting is implemented, some might be rate limited
        # This is optional, so we don't assert on it