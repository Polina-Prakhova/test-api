"""
Bookings API Tests.

This module contains comprehensive tests for bookings endpoints
including table availability, client bookings, and waiter bookings.
"""

import pytest
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta

from tests.utils.api_client import APIClient, AuthenticatedAPIClient
from tests.utils.validators import validator
from tests.utils.test_data import test_data
from tests.config import api_config, test_config


class TestBookingsEndpoints:
    """Test suite for bookings endpoints."""
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_get_available_tables(self, api_client: APIClient, mock_location_id: str):
        """Test retrieving available tables."""
        params = {
            "locationId": mock_location_id,
            "date": "2024-12-31",
            "time": "12:00",
            "guests": "4"
        }
        
        response = api_client.get(
            api_config.bookings_endpoints["tables"],
            params=params
        )
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert isinstance(response_data, list), "Expected list of available tables"
        
        # Validate each table in the response
        if response_data:
            validator.validate_list_response(response_data, "table_response")
            
            # Check that all tables have required fields
            for table in response_data:
                assert "locationId" in table
                assert "tableNumber" in table
                assert "capacity" in table
                
                # Validate business rules
                business_rules = {
                    "location_id_matches": {
                        "field": "locationId",
                        "value": mock_location_id,
                        "condition": "equals"
                    },
                    "table_number_not_empty": {
                        "field": "tableNumber",
                        "condition": "not_empty"
                    },
                    "capacity_positive": {
                        "field": "capacity",
                        "condition": "positive_number"
                    }
                }
                
                # Convert capacity to int for validation
                if "capacity" in table:
                    try:
                        table["capacity"] = int(table["capacity"])
                    except ValueError:
                        pass
                
                errors = validator.validate_business_rules(table, business_rules)
                assert not errors, f"Business rule violations for table: {errors}"
    
    @pytest.mark.positive
    def test_get_tables_without_filters(self, api_client: APIClient):
        """Test retrieving tables without any filters."""
        response = api_client.get(api_config.bookings_endpoints["tables"])
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert isinstance(response_data, list), "Expected list of tables"
        
        # Should return all available tables
        if response_data:
            for table in response_data:
                assert "tableNumber" in table
                assert "capacity" in table
    
    @pytest.mark.positive
    @pytest.mark.parametrize("guest_count", ["1", "2", "4", "6", "8"])
    def test_get_tables_by_guest_count(self, api_client: APIClient, mock_location_id: str, guest_count: str):
        """Test retrieving tables filtered by guest count."""
        params = {
            "locationId": mock_location_id,
            "guests": guest_count
        }
        
        response = api_client.get(
            api_config.bookings_endpoints["tables"],
            params=params
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        
        # Tables returned should have capacity >= guest count
        for table in response_data:
            if "capacity" in table:
                try:
                    table_capacity = int(table["capacity"])
                    guest_count_int = int(guest_count)
                    assert table_capacity >= guest_count_int, \
                        f"Table capacity {table_capacity} should be >= guest count {guest_count_int}"
                except ValueError:
                    # Skip validation if capacity is not a valid number
                    pass
    
    @pytest.mark.positive
    def test_client_booking_success(
        self,
        authenticated_client: AuthenticatedAPIClient,
        reservation_data: Dict[str, str]
    ):
        """Test successful client booking."""
        response = authenticated_client.post(
            api_config.bookings_endpoints["client"],
            data=reservation_data
        )
        
        # Note: This might fail if authentication is not working or if the booking system is not fully implemented
        if response.status_code in [200, 201]:
            response_data = response.json()
            
            # Validate reservation response
            validator.validate_response(response_data, "reservation_response")
            
            # Check required fields
            assert "id" in response_data
            assert "status" in response_data
            assert "date" in response_data
            
            # Validate business rules
            business_rules = {
                "id_not_empty": {
                    "field": "id",
                    "condition": "not_empty"
                },
                "status_not_empty": {
                    "field": "status",
                    "condition": "not_empty"
                },
                "date_matches": {
                    "field": "date",
                    "value": reservation_data["date"],
                    "condition": "equals"
                }
            }
            errors = validator.validate_business_rules(response_data, business_rules)
            assert not errors, f"Business rule violations: {errors}"
        
        elif response.status_code == 401:
            pytest.skip("Authentication required for client booking")
        
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.positive
    def test_waiter_booking_success(
        self,
        authenticated_client: AuthenticatedAPIClient,
        waiter_reservation_data: Dict[str, str]
    ):
        """Test successful waiter booking."""
        response = authenticated_client.post(
            api_config.bookings_endpoints["waiter"],
            data=waiter_reservation_data
        )
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            
            # Validate reservation response
            validator.validate_response(response_data, "reservation_response")
            
            # Check required fields
            assert "id" in response_data
            assert "status" in response_data
            
            # Waiter booking should include customer information
            if "userInfo" in response_data:
                assert waiter_reservation_data["customerName"] in response_data["userInfo"]
        
        elif response.status_code == 401:
            pytest.skip("Authentication required for waiter booking")
        
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.negative
    def test_client_booking_without_auth(self, api_client: APIClient, reservation_data: Dict[str, str]):
        """Test client booking without authentication."""
        response = api_client.post(
            api_config.bookings_endpoints["client"],
            data=reservation_data
        )
        
        # Should require authentication
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    @pytest.mark.negative
    def test_waiter_booking_without_auth(self, api_client: APIClient, waiter_reservation_data: Dict[str, str]):
        """Test waiter booking without authentication."""
        response = api_client.post(
            api_config.bookings_endpoints["waiter"],
            data=waiter_reservation_data
        )
        
        # Should require authentication
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    @pytest.mark.negative
    def test_client_booking_invalid_data(
        self,
        authenticated_client: AuthenticatedAPIClient,
        invalid_data_variants: Dict[str, Dict[str, Any]]
    ):
        """Test client booking with invalid data."""
        # Test with empty data
        response = authenticated_client.post(
            api_config.bookings_endpoints["client"],
            data={}
        )
        
        if response.status_code != 401:  # Skip if not authenticated
            assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    @pytest.mark.negative
    @pytest.mark.parametrize("missing_field", [
        "locationId",
        "tableNumber", 
        "date",
        "guestsNumber",
        "timeFrom",
        "timeTo"
    ])
    def test_client_booking_missing_fields(
        self,
        authenticated_client: AuthenticatedAPIClient,
        reservation_data: Dict[str, str],
        missing_field: str
    ):
        """Test client booking with missing required fields."""
        incomplete_data = reservation_data.copy()
        del incomplete_data[missing_field]
        
        response = authenticated_client.post(
            api_config.bookings_endpoints["client"],
            data=incomplete_data
        )
        
        if response.status_code != 401:  # Skip if not authenticated
            assert response.status_code in [400, 422], f"Expected 400 or 422 for missing {missing_field}, got {response.status_code}"
    
    @pytest.mark.negative
    def test_booking_invalid_date_format(self, authenticated_client: AuthenticatedAPIClient):
        """Test booking with invalid date formats."""
        invalid_dates = [
            "2024/12/31",  # Wrong format
            "31-12-2024",  # Wrong format
            "2024-13-01",  # Invalid month
            "2024-12-32",  # Invalid day
            "invalid-date",
            ""
        ]
        
        base_data = test_data.generate_reservation_data()
        
        for invalid_date in invalid_dates:
            booking_data = base_data.copy()
            booking_data["date"] = invalid_date
            
            response = authenticated_client.post(
                api_config.bookings_endpoints["client"],
                data=booking_data
            )
            
            if response.status_code != 401:  # Skip if not authenticated
                assert response.status_code in [400, 422], f"Invalid date '{invalid_date}' was accepted"
    
    @pytest.mark.negative
    def test_booking_invalid_time_format(self, authenticated_client: AuthenticatedAPIClient):
        """Test booking with invalid time formats."""
        invalid_times = [
            "25:00",  # Invalid hour
            "12:60",  # Invalid minute
            "12-30",  # Wrong format
            "12:30:00",  # Seconds not expected
            "invalid-time",
            ""
        ]
        
        base_data = test_data.generate_reservation_data()
        
        for invalid_time in invalid_times:
            booking_data = base_data.copy()
            booking_data["timeFrom"] = invalid_time
            
            response = authenticated_client.post(
                api_config.bookings_endpoints["client"],
                data=booking_data
            )
            
            if response.status_code != 401:  # Skip if not authenticated
                assert response.status_code in [400, 422], f"Invalid time '{invalid_time}' was accepted"
    
    @pytest.mark.negative
    def test_booking_past_date(self, authenticated_client: AuthenticatedAPIClient):
        """Test booking with past date."""
        past_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        booking_data = test_data.generate_reservation_data(date=past_date)
        
        response = authenticated_client.post(
            api_config.bookings_endpoints["client"],
            data=booking_data
        )
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should not allow booking in the past
            assert response.status_code in [400, 422], f"Past date booking was accepted"
    
    @pytest.mark.negative
    def test_booking_invalid_guest_count(self, authenticated_client: AuthenticatedAPIClient):
        """Test booking with invalid guest counts."""
        invalid_guest_counts = [
            "0",      # Zero guests
            "-1",     # Negative guests
            "100",    # Too many guests
            "abc",    # Non-numeric
            ""        # Empty
        ]
        
        base_data = test_data.generate_reservation_data()
        
        for invalid_count in invalid_guest_counts:
            booking_data = base_data.copy()
            booking_data["guestsNumber"] = invalid_count
            
            response = authenticated_client.post(
                api_config.bookings_endpoints["client"],
                data=booking_data
            )
            
            if response.status_code != 401:  # Skip if not authenticated
                assert response.status_code in [400, 422], f"Invalid guest count '{invalid_count}' was accepted"
    
    @pytest.mark.negative
    def test_get_tables_invalid_parameters(self, api_client: APIClient):
        """Test getting tables with invalid parameters."""
        invalid_params_list = [
            {"guests": "0"},
            {"guests": "-1"},
            {"guests": "abc"},
            {"date": "invalid-date"},
            {"time": "25:00"},
            {"locationId": "invalid-id"}
        ]
        
        for invalid_params in invalid_params_list:
            response = api_client.get(
                api_config.bookings_endpoints["tables"],
                params=invalid_params
            )
            
            # Should handle invalid parameters gracefully
            assert response.status_code in [200, 400], f"Unexpected status for params {invalid_params}"
    
    @pytest.mark.integration
    def test_booking_flow_integration(self, authenticated_client: AuthenticatedAPIClient):
        """Test complete booking flow from table search to booking."""
        # Step 1: Search for available tables
        search_params = {
            "locationId": test_config.TEST_LOCATION_ID,
            "date": "2024-12-31",
            "time": "12:00",
            "guests": "4"
        }
        
        tables_response = authenticated_client.get(
            api_config.bookings_endpoints["tables"],
            params=search_params
        )
        
        assert tables_response.status_code == 200
        available_tables = tables_response.json()
        
        if available_tables:
            # Step 2: Book the first available table
            first_table = available_tables[0]
            
            booking_data = {
                "locationId": first_table.get("locationId", test_config.TEST_LOCATION_ID),
                "tableNumber": first_table.get("tableNumber", "1"),
                "date": "2024-12-31",
                "guestsNumber": "4",
                "timeFrom": "12:00",
                "timeTo": "14:00"
            }
            
            booking_response = authenticated_client.post(
                api_config.bookings_endpoints["client"],
                data=booking_data
            )
            
            if booking_response.status_code not in [401]:  # Skip if not authenticated
                assert booking_response.status_code in [200, 201], f"Booking failed with status {booking_response.status_code}"
    
    @pytest.mark.performance
    def test_tables_endpoint_response_time(self, api_client: APIClient):
        """Test tables endpoint response time."""
        import time
        
        start_time = time.time()
        response = api_client.get(api_config.bookings_endpoints["tables"])
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should respond within reasonable time
        assert response_time < 5.0, f"Response time too slow: {response_time}s"
        assert response.status_code == 200
    
    @pytest.mark.security
    def test_booking_authorization(self, api_client: APIClient):
        """Test that booking endpoints require proper authorization."""
        booking_data = test_data.generate_reservation_data()
        
        # Test client booking without auth
        response = api_client.post(
            api_config.bookings_endpoints["client"],
            data=booking_data
        )
        assert response.status_code == 401, "Client booking should require authentication"
        
        # Test waiter booking without auth
        waiter_data = test_data.generate_waiter_reservation_data()
        response = api_client.post(
            api_config.bookings_endpoints["waiter"],
            data=waiter_data
        )
        assert response.status_code == 401, "Waiter booking should require authentication"
    
    @pytest.mark.security
    def test_booking_data_validation(self, authenticated_client: AuthenticatedAPIClient):
        """Test that booking endpoints properly validate input data."""
        # Test SQL injection attempt
        malicious_data = test_data.generate_reservation_data()
        malicious_data["locationId"] = "'; DROP TABLE reservations; --"
        
        response = authenticated_client.post(
            api_config.bookings_endpoints["client"],
            data=malicious_data
        )
        
        if response.status_code != 401:  # Skip if not authenticated
            # Should not cause server error
            assert response.status_code in [400, 422], "SQL injection attempt should be rejected"
    
    @pytest.mark.regression
    def test_booking_response_structure(self, authenticated_client: AuthenticatedAPIClient):
        """Test that booking response structure is consistent."""
        booking_data = test_data.generate_reservation_data()
        
        response = authenticated_client.post(
            api_config.bookings_endpoints["client"],
            data=booking_data
        )
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            
            # Check for expected fields in booking response
            expected_fields = ["id", "status"]
            for field in expected_fields:
                assert field in response_data, f"Expected field '{field}' missing from booking response"
        
        elif response.status_code != 401:  # Skip if not authenticated
            # Even error responses should have consistent structure
            response_data = response.json()
            assert "detail" in response_data or "message" in response_data, "Error response should have detail or message"