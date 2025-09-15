"""
Tests for bookings endpoints.
"""
import pytest


class TestBookingsEndpoints:
    """Test class for bookings endpoints."""

    def test_get_available_tables(self, api_client, base_url, sample_location_id):
        """Test getting available tables."""
        response = api_client.get(
            f"{base_url}/bookings/tables",
            params={
                "locationId": sample_location_id,
                "date": "2024-12-01",
                "time": "12:00",
                "guests": "4"
            }
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # If there are available tables
            table = data[0]
            assert "locationId" in table
            assert "locationAddress" in table
            assert "tableNumber" in table
            assert "capacity" in table
            assert "availableSlots" in table
            assert isinstance(table["availableSlots"], list)

    def test_get_available_tables_no_params(self, api_client, base_url):
        """Test getting available tables without parameters."""
        response = api_client.get(f"{base_url}/bookings/tables")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_available_tables_partial_params(self, api_client, base_url, sample_location_id):
        """Test getting available tables with partial parameters."""
        response = api_client.get(
            f"{base_url}/bookings/tables",
            params={
                "locationId": sample_location_id,
                "date": "2024-12-01"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_book_table_client_success(self, api_client, base_url, auth_headers, sample_reservation_data):
        """Test successful table booking by client."""
        response = api_client.post(
            f"{base_url}/bookings/client",
            json=sample_reservation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "id" in data
        assert "status" in data
        assert "locationAddress" in data
        assert "date" in data
        assert "timeSlot" in data
        assert "guestsNumber" in data

    def test_book_table_client_unauthorized(self, api_client, base_url, sample_reservation_data):
        """Test table booking by client without authentication."""
        response = api_client.post(
            f"{base_url}/bookings/client",
            json=sample_reservation_data
        )
        
        assert response.status_code == 401

    def test_book_table_client_invalid_data(self, api_client, base_url, auth_headers):
        """Test table booking with invalid data."""
        invalid_data = {
            "locationId": "",
            "tableNumber": "",
            "date": "invalid-date",
            "guestsNumber": "-1",
            "timeFrom": "25:00",
            "timeTo": "26:00"
        }
        
        response = api_client.post(
            f"{base_url}/bookings/client",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]

    def test_book_table_client_missing_fields(self, api_client, base_url, auth_headers):
        """Test table booking with missing required fields."""
        incomplete_data = {
            "locationId": "672846d5c951184d705b65d7"
            # Missing other required fields
        }
        
        response = api_client.post(
            f"{base_url}/bookings/client",
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]

    def test_book_table_waiter_success(self, api_client, base_url, auth_headers):
        """Test successful table booking by waiter."""
        waiter_reservation_data = {
            "clientType": "CUSTOMER",
            "customerName": "John Doe",
            "date": "2024-12-10",
            "guestsNumber": "4",
            "locationId": "672846d5c951184d705b65d7",
            "tableNumber": "1",
            "timeFrom": "12:00",
            "timeTo": "14:00"
        }
        
        response = api_client.post(
            f"{base_url}/bookings/waiter",
            json=waiter_reservation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "id" in data
        assert "status" in data
        assert "locationAddress" in data
        assert "date" in data
        assert "timeSlot" in data
        assert "guestsNumber" in data
        assert "userInfo" in data

    def test_book_table_waiter_unauthorized(self, api_client, base_url):
        """Test table booking by waiter without authentication."""
        waiter_reservation_data = {
            "clientType": "CUSTOMER",
            "customerName": "John Doe",
            "date": "2024-12-10",
            "guestsNumber": "4",
            "locationId": "672846d5c951184d705b65d7",
            "tableNumber": "1",
            "timeFrom": "12:00",
            "timeTo": "14:00"
        }
        
        response = api_client.post(
            f"{base_url}/bookings/waiter",
            json=waiter_reservation_data
        )
        
        assert response.status_code == 401

    def test_tables_response_structure(self, api_client, base_url, sample_location_id):
        """Test tables response structure and data validation."""
        response = api_client.get(
            f"{base_url}/bookings/tables",
            params={"locationId": sample_location_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        if data:
            table = data[0]
            required_fields = [
                "locationId", "locationAddress", "tableNumber", 
                "capacity", "availableSlots"
            ]
            
            for field in required_fields:
                assert field in table, f"Missing field: {field}"
            
            # Validate data types
            assert isinstance(table["availableSlots"], list)
            assert isinstance(table["capacity"], str)
            assert isinstance(table["tableNumber"], str)

    def test_table_capacity_validation(self, api_client, base_url, sample_location_id):
        """Test that table capacity values are valid."""
        response = api_client.get(
            f"{base_url}/bookings/tables",
            params={"locationId": sample_location_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for table in data:
                capacity = table["capacity"]
                try:
                    capacity_value = int(capacity)
                    assert capacity_value > 0, f"Invalid capacity: {capacity}"
                except ValueError:
                    pytest.fail(f"Capacity is not a valid number: {capacity}")

    def test_available_slots_format(self, api_client, base_url, sample_location_id):
        """Test that available slots are in correct format."""
        response = api_client.get(
            f"{base_url}/bookings/tables",
            params={"locationId": sample_location_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            for table in data:
                slots = table["availableSlots"]
                for slot in slots:
                    # Slots should be in format "HH:MM-HH:MM"
                    assert isinstance(slot, str)
                    if "-" in slot:
                        start_time, end_time = slot.split("-")
                        # Basic time format validation
                        assert ":" in start_time and ":" in end_time

    def test_booking_date_validation(self, api_client, base_url, auth_headers):
        """Test booking with various date formats."""
        test_dates = [
            "2024-12-31",  # Valid format
            "2024-02-29",  # Leap year
            "2024-13-01",  # Invalid month
            "2024-12-32",  # Invalid day
            "invalid-date"  # Invalid format
        ]
        
        for test_date in test_dates:
            reservation_data = {
                "locationId": "672846d5c951184d705b65d7",
                "tableNumber": "1",
                "date": test_date,
                "guestsNumber": "4",
                "timeFrom": "12:15",
                "timeTo": "14:00"
            }
            
            response = api_client.post(
                f"{base_url}/bookings/client",
                json=reservation_data,
                headers=auth_headers
            )
            
            if test_date in ["2024-12-31", "2024-02-29"]:
                assert response.status_code in [200, 400]  # May fail due to business logic
            else:
                assert response.status_code in [400, 422]

    def test_booking_time_validation(self, api_client, base_url, auth_headers):
        """Test booking with various time formats."""
        test_times = [
            ("12:00", "14:00"),  # Valid
            ("09:30", "11:30"),  # Valid
            ("25:00", "26:00"),  # Invalid hours
            ("12:60", "14:60"),  # Invalid minutes
            ("14:00", "12:00"),  # End before start
            ("invalid", "time")  # Invalid format
        ]
        
        for time_from, time_to in test_times:
            reservation_data = {
                "locationId": "672846d5c951184d705b65d7",
                "tableNumber": "1",
                "date": "2024-12-31",
                "guestsNumber": "4",
                "timeFrom": time_from,
                "timeTo": time_to
            }
            
            response = api_client.post(
                f"{base_url}/bookings/client",
                json=reservation_data,
                headers=auth_headers
            )
            
            if time_from in ["12:00", "09:30"] and time_to in ["14:00", "11:30"]:
                assert response.status_code in [200, 400]  # May fail due to business logic
            else:
                assert response.status_code in [400, 422]

    def test_booking_guests_validation(self, api_client, base_url, auth_headers):
        """Test booking with various guest numbers."""
        test_guests = ["1", "4", "8", "0", "-1", "abc", "100"]
        
        for guests in test_guests:
            reservation_data = {
                "locationId": "672846d5c951184d705b65d7",
                "tableNumber": "1",
                "date": "2024-12-31",
                "guestsNumber": guests,
                "timeFrom": "12:15",
                "timeTo": "14:00"
            }
            
            response = api_client.post(
                f"{base_url}/bookings/client",
                json=reservation_data,
                headers=auth_headers
            )
            
            if guests in ["1", "4", "8"]:
                assert response.status_code in [200, 400]  # May fail due to business logic
            else:
                assert response.status_code in [400, 422]