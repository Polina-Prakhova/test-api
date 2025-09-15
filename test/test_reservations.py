"""
Tests for reservations endpoints.
"""
import pytest


class TestReservationsEndpoints:
    """Test class for reservations endpoints."""

    def test_get_user_reservations(self, api_client, base_url, auth_headers):
        """Test getting user reservations."""
        response = api_client.get(
            f"{base_url}/reservations",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # If there are reservations
            reservation = data[0]
            assert "id" in reservation
            assert "status" in reservation
            assert "locationAddress" in reservation
            assert "date" in reservation
            assert "timeSlot" in reservation
            assert "guestsNumber" in reservation

    def test_get_reservations_unauthorized(self, api_client, base_url):
        """Test getting reservations without authentication."""
        response = api_client.get(f"{base_url}/reservations")
        
        assert response.status_code == 401

    def test_delete_reservation_success(self, api_client, base_url, auth_headers):
        """Test successful reservation deletion."""
        # First, we need a reservation ID. In a real scenario, this would come from creating a reservation
        # For testing purposes, we'll use a sample ID
        reservation_id = "672846d5c951184d705b65d7"
        
        response = api_client.delete(
            f"{base_url}/reservations/{reservation_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]  # 404 if reservation doesn't exist

    def test_delete_reservation_unauthorized(self, api_client, base_url):
        """Test reservation deletion without authentication."""
        reservation_id = "672846d5c951184d705b65d7"
        
        response = api_client.delete(f"{base_url}/reservations/{reservation_id}")
        
        assert response.status_code == 401

    def test_delete_nonexistent_reservation(self, api_client, base_url, auth_headers):
        """Test deleting a nonexistent reservation."""
        nonexistent_id = "999999999999999999999999"
        
        response = api_client.delete(
            f"{base_url}/reservations/{nonexistent_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_get_available_dishes_for_reservation(self, api_client, base_url, auth_headers):
        """Test getting available dishes for a reservation."""
        reservation_id = "672846d5c951184d705b65d8"
        
        response = api_client.get(
            f"{base_url}/reservations/{reservation_id}/available-dishes",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]  # 404 if reservation doesn't exist
        
        if response.status_code == 200:
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

    def test_get_available_dishes_with_dish_type_filter(self, api_client, base_url, auth_headers):
        """Test getting available dishes with dish type filter."""
        reservation_id = "672846d5c951184d705b65d8"
        dish_types = ["APPETIZER", "MAIN_COURSE", "DESSERT"]
        
        for dish_type in dish_types:
            response = api_client.get(
                f"{base_url}/reservations/{reservation_id}/available-dishes",
                params={"dishType": dish_type},
                headers=auth_headers
            )
            
            assert response.status_code in [200, 404]

    def test_get_available_dishes_with_sort(self, api_client, base_url, auth_headers):
        """Test getting available dishes with sorting."""
        reservation_id = "672846d5c951184d705b65d8"
        sort_options = [
            "popularity,asc",
            "popularity,desc",
            "price,asc",
            "price,desc"
        ]
        
        for sort_option in sort_options:
            response = api_client.get(
                f"{base_url}/reservations/{reservation_id}/available-dishes",
                params={"sort": sort_option},
                headers=auth_headers
            )
            
            assert response.status_code in [200, 404]

    def test_get_available_dishes_unauthorized(self, api_client, base_url):
        """Test getting available dishes without authentication."""
        reservation_id = "672846d5c951184d705b65d8"
        
        response = api_client.get(
            f"{base_url}/reservations/{reservation_id}/available-dishes"
        )
        
        assert response.status_code == 401

    def test_order_dish_for_reservation(self, api_client, base_url, auth_headers):
        """Test ordering a dish for a reservation."""
        reservation_id = "672846d5c951184d705b65d8"
        dish_id = "672846d5c951184d705b65d8"
        
        response = api_client.post(
            f"{base_url}/reservations/{reservation_id}/order/{dish_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]  # 404 if reservation or dish doesn't exist
        
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert data["message"] == "Dish has been placed to cart"

    def test_order_dish_unauthorized(self, api_client, base_url):
        """Test ordering a dish without authentication."""
        reservation_id = "672846d5c951184d705b65d8"
        dish_id = "672846d5c951184d705b65d8"
        
        response = api_client.post(
            f"{base_url}/reservations/{reservation_id}/order/{dish_id}"
        )
        
        assert response.status_code == 401

    def test_order_dish_invalid_reservation(self, api_client, base_url, auth_headers):
        """Test ordering a dish for invalid reservation."""
        invalid_reservation_id = "invalid-reservation-id"
        dish_id = "672846d5c951184d705b65d8"
        
        response = api_client.post(
            f"{base_url}/reservations/{invalid_reservation_id}/order/{dish_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [400, 404]

    def test_order_dish_invalid_dish(self, api_client, base_url, auth_headers):
        """Test ordering an invalid dish for reservation."""
        reservation_id = "672846d5c951184d705b65d8"
        invalid_dish_id = "invalid-dish-id"
        
        response = api_client.post(
            f"{base_url}/reservations/{reservation_id}/order/{invalid_dish_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [400, 404]

    def test_reservations_response_structure(self, api_client, base_url, auth_headers):
        """Test reservations response structure and data validation."""
        response = api_client.get(
            f"{base_url}/reservations",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        if data:
            reservation = data[0]
            required_fields = [
                "id", "status", "locationAddress", "date", 
                "timeSlot", "guestsNumber"
            ]
            
            for field in required_fields:
                assert field in reservation, f"Missing field: {field}"
            
            # Validate data types
            assert isinstance(reservation["id"], str)
            assert isinstance(reservation["status"], str)
            assert isinstance(reservation["locationAddress"], str)
            assert isinstance(reservation["date"], str)
            assert isinstance(reservation["timeSlot"], str)
            assert isinstance(reservation["guestsNumber"], str)

    def test_reservation_status_values(self, api_client, base_url, auth_headers):
        """Test that reservation status values are valid."""
        response = api_client.get(
            f"{base_url}/reservations",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        valid_statuses = ["confirmed", "pending", "cancelled", "completed", "in-progress"]
        
        if data:
            for reservation in data:
                status = reservation["status"]
                assert status in valid_statuses, f"Invalid reservation status: {status}"

    def test_reservation_date_format(self, api_client, base_url, auth_headers):
        """Test that reservation dates are in correct format."""
        response = api_client.get(
            f"{base_url}/reservations",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for reservation in data:
                date = reservation["date"]
                # Date should be in YYYY-MM-DD format
                assert len(date) == 10, f"Invalid date format: {date}"
                assert date.count("-") == 2, f"Invalid date format: {date}"

    def test_reservation_time_slot_format(self, api_client, base_url, auth_headers):
        """Test that reservation time slots are in correct format."""
        response = api_client.get(
            f"{base_url}/reservations",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for reservation in data:
                time_slot = reservation["timeSlot"]
                # Time slot should contain a dash or hyphen
                assert "-" in time_slot or "–" in time_slot, f"Invalid time slot format: {time_slot}"

    def test_reservation_guests_number_validation(self, api_client, base_url, auth_headers):
        """Test that reservation guest numbers are valid."""
        response = api_client.get(
            f"{base_url}/reservations",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for reservation in data:
                guests_number = reservation["guestsNumber"]
                try:
                    guests_value = int(guests_number)
                    assert guests_value > 0, f"Invalid guests number: {guests_number}"
                except ValueError:
                    pytest.fail(f"Guests number is not a valid integer: {guests_number}")

    def test_available_dishes_response_structure(self, api_client, base_url, auth_headers):
        """Test available dishes response structure."""
        reservation_id = "672846d5c951184d705b65d8"
        
        response = api_client.get(
            f"{base_url}/reservations/{reservation_id}/available-dishes",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "content" in data
            assert isinstance(data["content"], list)
            
            if data["content"]:
                dish = data["content"][0]
                required_fields = ["id", "name", "previewImageUrl", "price", "state", "weight"]
                
                for field in required_fields:
                    assert field in dish, f"Missing dish field: {field}"