"""
Bookings API tests.
Tests for booking-related endpoints including table availability and reservations.
"""
import pytest
import requests
from typing import Dict, Any


class TestTableAvailability:
    """Test cases for table availability endpoint."""
    
    def test_get_tables_without_filters(self, api_client, base_url):
        """Test getting available tables without filters."""
        response = api_client.get(f"{base_url}/bookings/tables")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        # Validate table structure if tables are returned
        if data:
            table = data[0]
            required_fields = [
                "locationId", "locationAddress", "tableNumber",
                "capacity", "availableSlots"
            ]
            for field in required_fields:
                assert field in table
            
            # Validate field types
            assert isinstance(table["locationId"], str)
            assert isinstance(table["locationAddress"], str)
            assert isinstance(table["tableNumber"], str)
            assert isinstance(table["capacity"], str)
            assert isinstance(table["availableSlots"], list)
    
    def test_get_tables_with_location_filter(self, api_client, base_url, sample_location_id):
        """Test getting tables filtered by location."""
        params = {"locationId": sample_location_id}
        response = api_client.get(f"{base_url}/bookings/tables", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All returned tables should be for the specified location
        for table in data:
            assert table["locationId"] == sample_location_id
    
    def test_get_tables_with_date_filter(self, api_client, base_url):
        """Test getting tables filtered by date."""
        params = {"date": "2024-08-01"}
        response = api_client.get(f"{base_url}/bookings/tables", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_tables_with_time_filter(self, api_client, base_url):
        """Test getting tables filtered by time."""
        params = {"time": "12:00"}
        response = api_client.get(f"{base_url}/bookings/tables", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_tables_with_guests_filter(self, api_client, base_url):
        """Test getting tables filtered by number of guests."""
        params = {"guests": "4"}
        response = api_client.get(f"{base_url}/bookings/tables", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Tables should have capacity >= guests
        for table in data:
            try:
                table_capacity = int(table["capacity"])
                assert table_capacity >= 4
            except ValueError:
                # If capacity is not numeric, just continue
                pass
    
    def test_get_tables_with_all_filters(self, api_client, base_url, sample_location_id):
        """Test getting tables with all filters applied."""
        params = {
            "locationId": sample_location_id,
            "date": "2024-08-01",
            "time": "12:00",
            "guests": "4"
        }
        
        response = api_client.get(f"{base_url}/bookings/tables", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.validation
    def test_get_tables_invalid_date_format(self, api_client, base_url):
        """Test getting tables with invalid date format."""
        invalid_dates = [
            "invalid-date",
            "2024-13-01",  # Invalid month
            "2024-02-30",  # Invalid day
            "01-08-2024",  # Wrong format
            ""
        ]
        
        for date in invalid_dates:
            params = {"date": date}
            response = api_client.get(f"{base_url}/bookings/tables", params=params)
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.validation
    def test_get_tables_invalid_time_format(self, api_client, base_url):
        """Test getting tables with invalid time format."""
        invalid_times = [
            "invalid-time",
            "25:00",  # Invalid hour
            "12:60",  # Invalid minute
            "12",     # Missing minute
            ""
        ]
        
        for time in invalid_times:
            params = {"time": time}
            response = api_client.get(f"{base_url}/bookings/tables", params=params)
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.validation
    def test_get_tables_invalid_guests_number(self, api_client, base_url):
        """Test getting tables with invalid guests number."""
        invalid_guests = [
            "invalid",
            "0",      # Zero guests
            "-1",     # Negative guests
            "1000",   # Unrealistic number
            ""
        ]
        
        for guests in invalid_guests:
            params = {"guests": guests}
            response = api_client.get(f"{base_url}/bookings/tables", params=params)
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]


class TestClientBooking:
    """Test cases for client booking endpoint."""
    
    @pytest.mark.auth
    def test_book_table_success(self, authenticated_client, base_url, valid_reservation_data):
        """Test successful table booking by client."""
        response = authenticated_client.post(
            f"{base_url}/bookings/client",
            json=valid_reservation_data
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        
        # Validate reservation response structure
        required_fields = [
            "id", "status", "locationAddress", "date",
            "timeSlot", "preOrder", "guestsNumber", "feedbackId"
        ]
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], str)
        
        # Validate specific field values
        assert len(data["id"]) > 0
        assert data["status"] in ["confirmed", "pending", "in-progress"]
        assert data["date"] == valid_reservation_data["date"]
        assert data["guestsNumber"] == valid_reservation_data["guestsNumber"]
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_book_table_unauthorized(self, api_client, base_url, valid_reservation_data):
        """Test table booking without authentication."""
        response = api_client.post(
            f"{base_url}/bookings/client",
            json=valid_reservation_data
        )
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_book_table_missing_fields(self, authenticated_client, base_url):
        """Test table booking with missing required fields."""
        incomplete_data_sets = [
            {},  # Empty payload
            {"locationId": "123"},  # Missing other fields
            {"locationId": "123", "tableNumber": "1"},  # Missing date, guests, etc.
            {
                "locationId": "123",
                "tableNumber": "1",
                "date": "2024-12-31"
                # Missing guestsNumber, timeFrom, timeTo
            }
        ]
        
        for incomplete_data in incomplete_data_sets:
            response = authenticated_client.post(
                f"{base_url}/bookings/client",
                json=incomplete_data
            )
            assert response.status_code in [400, 422], f"Failed for data: {incomplete_data}"
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_book_table_invalid_data(self, authenticated_client, base_url):
        """Test table booking with invalid data."""
        invalid_data_sets = [
            {
                "locationId": "invalid_location",
                "tableNumber": "1",
                "date": "2024-12-31",
                "guestsNumber": "4",
                "timeFrom": "12:15",
                "timeTo": "14:00"
            },
            {
                "locationId": "672846d5c951184d705b65d7",
                "tableNumber": "999",  # Non-existent table
                "date": "2024-12-31",
                "guestsNumber": "4",
                "timeFrom": "12:15",
                "timeTo": "14:00"
            },
            {
                "locationId": "672846d5c951184d705b65d7",
                "tableNumber": "1",
                "date": "2020-01-01",  # Past date
                "guestsNumber": "4",
                "timeFrom": "12:15",
                "timeTo": "14:00"
            },
            {
                "locationId": "672846d5c951184d705b65d7",
                "tableNumber": "1",
                "date": "2024-12-31",
                "guestsNumber": "0",  # Invalid guest count
                "timeFrom": "12:15",
                "timeTo": "14:00"
            },
            {
                "locationId": "672846d5c951184d705b65d7",
                "tableNumber": "1",
                "date": "2024-12-31",
                "guestsNumber": "4",
                "timeFrom": "14:00",  # Time from after time to
                "timeTo": "12:15"
            }
        ]
        
        for invalid_data in invalid_data_sets:
            response = authenticated_client.post(
                f"{base_url}/bookings/client",
                json=invalid_data
            )
            assert response.status_code in [400, 422], f"Failed for data: {invalid_data}"


class TestWaiterBooking:
    """Test cases for waiter booking endpoint."""
    
    @pytest.mark.auth
    def test_waiter_book_table_success(self, authenticated_client, base_url):
        """Test successful table booking by waiter."""
        waiter_booking_data = {
            "clientType": "CUSTOMER",
            "customerName": "John Doe",
            "date": "2024-10-10",
            "guestsNumber": "4",
            "locationId": "582846d5c951184d705b65d1",
            "tableNumber": "1",
            "timeFrom": "12:00",
            "timeTo": "14:00"
        }
        
        response = authenticated_client.post(
            f"{base_url}/bookings/waiter",
            json=waiter_booking_data
        )
        
        assert response.status_code == 201
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        
        # Validate reservation response structure
        required_fields = [
            "id", "status", "locationAddress", "date",
            "timeSlot", "guestsNumber", "userInfo"
        ]
        for field in required_fields:
            assert field in data
        
        # Validate specific values
        assert data["date"] == waiter_booking_data["date"]
        assert data["guestsNumber"] == waiter_booking_data["guestsNumber"]
        assert waiter_booking_data["customerName"] in data["userInfo"]
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_waiter_book_table_unauthorized(self, api_client, base_url):
        """Test waiter booking without authentication."""
        waiter_booking_data = {
            "clientType": "CUSTOMER",
            "customerName": "John Doe",
            "date": "2024-10-10",
            "guestsNumber": "4",
            "locationId": "582846d5c951184d705b65d1",
            "tableNumber": "1",
            "timeFrom": "12:00",
            "timeTo": "14:00"
        }
        
        response = api_client.post(
            f"{base_url}/bookings/waiter",
            json=waiter_booking_data
        )
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_waiter_book_table_missing_fields(self, authenticated_client, base_url):
        """Test waiter booking with missing required fields."""
        incomplete_data_sets = [
            {},  # Empty payload
            {"clientType": "CUSTOMER"},  # Missing other fields
            {
                "clientType": "CUSTOMER",
                "customerName": "John Doe"
                # Missing location, date, etc.
            }
        ]
        
        for incomplete_data in incomplete_data_sets:
            response = authenticated_client.post(
                f"{base_url}/bookings/waiter",
                json=incomplete_data
            )
            assert response.status_code in [400, 422], f"Failed for data: {incomplete_data}"
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_waiter_book_table_invalid_client_type(self, authenticated_client, base_url):
        """Test waiter booking with invalid client type."""
        invalid_data = {
            "clientType": "INVALID_TYPE",
            "customerName": "John Doe",
            "date": "2024-10-10",
            "guestsNumber": "4",
            "locationId": "582846d5c951184d705b65d1",
            "tableNumber": "1",
            "timeFrom": "12:00",
            "timeTo": "14:00"
        }
        
        response = authenticated_client.post(
            f"{base_url}/bookings/waiter",
            json=invalid_data
        )
        
        assert response.status_code in [400, 422]


class TestBookingsIntegration:
    """Integration tests for booking flow."""
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_complete_booking_flow(self, authenticated_client, base_url, sample_location_id):
        """Test complete booking flow from table search to reservation."""
        # Step 1: Search for available tables
        search_params = {
            "locationId": sample_location_id,
            "date": "2024-12-31",
            "time": "12:00",
            "guests": "4"
        }
        
        tables_response = authenticated_client.get(
            f"{base_url}/bookings/tables",
            params=search_params
        )
        assert tables_response.status_code == 200
        
        tables_data = tables_response.json()
        
        # Step 2: If tables are available, make a booking
        if tables_data:
            table = tables_data[0]
            
            booking_data = {
                "locationId": table["locationId"],
                "tableNumber": table["tableNumber"],
                "date": search_params["date"],
                "guestsNumber": search_params["guests"],
                "timeFrom": "12:15",
                "timeTo": "14:00"
            }
            
            booking_response = authenticated_client.post(
                f"{base_url}/bookings/client",
                json=booking_data
            )
            
            # Booking might succeed or fail based on availability
            assert booking_response.status_code in [200, 400, 409]
            
            if booking_response.status_code == 200:
                booking_result = booking_response.json()
                assert "id" in booking_result
                assert booking_result["date"] == booking_data["date"]
    
    @pytest.mark.integration
    def test_table_availability_consistency(self, api_client, base_url):
        """Test consistency of table availability across requests."""
        # Make multiple requests for the same criteria
        params = {
            "date": "2024-08-01",
            "time": "12:00",
            "guests": "4"
        }
        
        responses = []
        for _ in range(3):
            response = api_client.get(f"{base_url}/bookings/tables", params=params)
            assert response.status_code == 200
            responses.append(response.json())
        
        # Results should be consistent (assuming no bookings made in between)
        first_result = responses[0]
        for result in responses[1:]:
            assert len(result) == len(first_result)
            # Note: Exact equality might not hold if availability changes


class TestBookingsErrorScenarios:
    """Test error scenarios and edge cases."""
    
    @pytest.mark.error
    def test_booking_with_malformed_json(self, authenticated_client, base_url):
        """Test booking with malformed JSON."""
        malformed_json = '{"locationId": "123", "tableNumber": "1"'  # Missing closing brace
        
        response = authenticated_client.post(
            f"{base_url}/bookings/client",
            data=malformed_json,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]
    
    @pytest.mark.error
    def test_booking_with_special_characters(self, authenticated_client, base_url):
        """Test booking with special characters in data."""
        special_char_data = {
            "locationId": "<script>alert('xss')</script>",
            "tableNumber": "'; DROP TABLE bookings; --",
            "date": "2024-12-31",
            "guestsNumber": "4",
            "timeFrom": "12:15",
            "timeTo": "14:00"
        }
        
        response = authenticated_client.post(
            f"{base_url}/bookings/client",
            json=special_char_data
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 422]
    
    @pytest.mark.error
    def test_concurrent_bookings(self, authenticated_client, base_url, valid_reservation_data):
        """Test concurrent booking attempts for the same table."""
        import threading
        
        responses = []
        
        def make_booking():
            response = authenticated_client.post(
                f"{base_url}/bookings/client",
                json=valid_reservation_data
            )
            responses.append(response)
        
        # Create multiple threads trying to book the same table
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_booking)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # At most one booking should succeed (or all might fail if table doesn't exist)
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count <= 1
        
        # All other responses should be errors
        for response in responses:
            assert response.status_code in [200, 400, 409, 422]
    
    @pytest.mark.error
    def test_booking_with_expired_token(self, api_client, base_url, valid_reservation_data):
        """Test booking with expired or invalid token."""
        # Use an obviously invalid token
        api_client.headers.update({"Authorization": "Bearer invalid_token_12345"})
        
        response = api_client.post(
            f"{base_url}/bookings/client",
            json=valid_reservation_data
        )
        
        assert response.status_code == 401
    
    @pytest.mark.error
    def test_table_search_with_extreme_values(self, api_client, base_url):
        """Test table search with extreme parameter values."""
        extreme_params = [
            {"guests": "999999"},  # Extremely large party
            {"date": "1900-01-01"},  # Very old date
            {"date": "2100-01-01"},  # Very future date
            {"time": "00:00"},  # Midnight
            {"time": "23:59"},  # Late night
        ]
        
        for params in extreme_params:
            response = api_client.get(f"{base_url}/bookings/tables", params=params)
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]