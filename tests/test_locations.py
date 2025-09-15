"""
Locations API Tests.

This module contains comprehensive tests for locations endpoints
including location listing, speciality dishes, feedbacks, and select options.
"""

import pytest
import requests
from typing import Dict, Any, List

from tests.utils.api_client import APIClient
from tests.utils.validators import validator
from tests.config import api_config, test_config


class TestLocationsEndpoints:
    """Test suite for locations endpoints."""
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_get_locations_list(self, api_client: APIClient):
        """Test retrieving locations list."""
        response = api_client.get(api_config.locations_endpoints["list"])
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert isinstance(response_data, list), "Expected list of locations"
        
        # Validate each location in the response
        if response_data:  # If there are locations
            validator.validate_list_response(response_data, "location_response")
            
            # Check that all locations have required fields
            for location in response_data:
                assert "id" in location
                assert "address" in location
                
                # Validate business rules
                business_rules = {
                    "id_not_empty": {
                        "field": "id",
                        "condition": "not_empty"
                    },
                    "address_not_empty": {
                        "field": "address",
                        "condition": "not_empty"
                    }
                }
                errors = validator.validate_business_rules(location, business_rules)
                assert not errors, f"Business rule violations for location: {errors}"
    
    @pytest.mark.positive
    def test_get_location_select_options(self, api_client: APIClient):
        """Test retrieving location select options."""
        response = api_client.get(api_config.locations_endpoints["select_options"])
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert isinstance(response_data, list), "Expected list of location options"
        
        # Validate each location option
        if response_data:
            validator.validate_list_response(response_data, "location_brief")
            
            for location in response_data:
                assert "id" in location
                assert "address" in location
                
                # Select options should be minimal - no extra fields needed
                assert len(location.keys()) >= 2, "Location option should have at least id and address"
    
    @pytest.mark.positive
    def test_get_location_speciality_dishes(self, api_client: APIClient, mock_location_id: str):
        """Test retrieving speciality dishes for a location."""
        speciality_url = api_config.locations_endpoints["speciality_dishes"].format(id=mock_location_id)
        response = api_client.get(speciality_url)
        
        # Note: This might return 404 if the location doesn't exist in test environment
        if response.status_code == 200:
            response_data = response.json()
            assert isinstance(response_data, list), "Expected list of speciality dishes"
            
            # Validate each dish
            if response_data:
                validator.validate_list_response(response_data, "dish_response")
                
                for dish in response_data:
                    assert "name" in dish
                    assert "price" in dish
        
        elif response.status_code == 404:
            # This is acceptable in test environment
            response_data = response.json()
            assert "detail" in response_data or "message" in response_data
        
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.positive
    @pytest.mark.parametrize("feedback_type", [
        "CUISINE_EXPERIENCE",
        "SERVICE_QUALITY"
    ])
    def test_get_location_feedbacks(self, api_client: APIClient, mock_location_id: str, feedback_type: str):
        """Test retrieving feedbacks for a location by type."""
        feedbacks_url = api_config.locations_endpoints["feedbacks"].format(id=mock_location_id)
        params = {"type": feedback_type}
        
        response = api_client.get(feedbacks_url, params=params)
        
        # Note: This might return 404 if the location doesn't exist
        if response.status_code == 200:
            response_data = response.json()
            
            # Should be a paginated response
            validator.validate_pagination_response(response_data, "feedback_response")
            
            # Check content structure
            assert "content" in response_data
            feedbacks = response_data["content"]
            
            # Validate each feedback
            for feedback in feedbacks:
                if "type" in feedback:
                    assert feedback["type"] == feedback_type, f"Expected {feedback_type}, got {feedback['type']}"
        
        elif response.status_code == 404:
            # Acceptable in test environment
            pass
        
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.positive
    def test_get_location_feedbacks_with_pagination(self, api_client: APIClient, mock_location_id: str):
        """Test retrieving location feedbacks with pagination parameters."""
        feedbacks_url = api_config.locations_endpoints["feedbacks"].format(id=mock_location_id)
        params = {
            "type": "SERVICE_QUALITY",
            "page": 0,
            "size": 5
        }
        
        response = api_client.get(feedbacks_url, params=params)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Validate pagination structure
            pagination_fields = ["totalPages", "totalElements", "size", "number", "content"]
            for field in pagination_fields:
                if field in response_data:  # Some fields might be optional
                    if field == "size":
                        assert response_data[field] <= 5, "Size should not exceed requested size"
                    elif field == "number":
                        assert response_data[field] == 0, "Should be first page"
        
        elif response.status_code == 404:
            # Acceptable in test environment
            pass
    
    @pytest.mark.positive
    def test_get_location_feedbacks_with_sorting(self, api_client: APIClient, mock_location_id: str):
        """Test retrieving location feedbacks with sorting."""
        feedbacks_url = api_config.locations_endpoints["feedbacks"].format(id=mock_location_id)
        params = {
            "type": "CUISINE_EXPERIENCE",
            "sort": ["date,desc"]
        }
        
        response = api_client.get(feedbacks_url, params=params)
        
        if response.status_code == 200:
            response_data = response.json()
            assert "content" in response_data
            
            feedbacks = response_data["content"]
            if len(feedbacks) > 1:
                # Check if sorting is applied (basic validation)
                dates = [feedback.get("date") for feedback in feedbacks if "date" in feedback]
                if len(dates) > 1:
                    # Should be in descending order
                    assert dates == sorted(dates, reverse=True), "Feedbacks should be sorted by date descending"
        
        elif response.status_code == 404:
            # Acceptable in test environment
            pass
    
    @pytest.mark.negative
    def test_get_location_speciality_dishes_invalid_id(self, api_client: APIClient):
        """Test retrieving speciality dishes with invalid location ID."""
        invalid_ids = [
            "invalid-id",
            "123",
            "nonexistent123456789012345678901234",
            ""
        ]
        
        for invalid_id in invalid_ids:
            speciality_url = api_config.locations_endpoints["speciality_dishes"].format(id=invalid_id)
            response = api_client.get(speciality_url)
            
            # Should return 404 or 400
            assert response.status_code in [400, 404], f"Expected 400 or 404 for ID '{invalid_id}', got {response.status_code}"
    
    @pytest.mark.negative
    def test_get_location_feedbacks_invalid_type(self, api_client: APIClient, mock_location_id: str):
        """Test retrieving location feedbacks with invalid type."""
        feedbacks_url = api_config.locations_endpoints["feedbacks"].format(id=mock_location_id)
        
        invalid_types = [
            "INVALID_TYPE",
            "cuisine",  # Should be CUISINE_EXPERIENCE
            "service",  # Should be SERVICE_QUALITY
            "123",
            ""
        ]
        
        for invalid_type in invalid_types:
            params = {"type": invalid_type}
            response = api_client.get(feedbacks_url, params=params)
            
            # Should return 400 for invalid type (required parameter)
            assert response.status_code in [400, 404], f"Expected 400 or 404 for invalid type '{invalid_type}'"
    
    @pytest.mark.negative
    def test_get_location_feedbacks_missing_type(self, api_client: APIClient, mock_location_id: str):
        """Test retrieving location feedbacks without required type parameter."""
        feedbacks_url = api_config.locations_endpoints["feedbacks"].format(id=mock_location_id)
        
        response = api_client.get(feedbacks_url)
        
        # Type is required parameter, should return 400
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    @pytest.mark.negative
    def test_get_location_feedbacks_invalid_pagination(self, api_client: APIClient, mock_location_id: str):
        """Test location feedbacks with invalid pagination parameters."""
        feedbacks_url = api_config.locations_endpoints["feedbacks"].format(id=mock_location_id)
        
        invalid_params_list = [
            {"type": "SERVICE_QUALITY", "page": -1},
            {"type": "SERVICE_QUALITY", "size": 0},
            {"type": "SERVICE_QUALITY", "size": -1},
            {"type": "SERVICE_QUALITY", "page": "invalid"},
            {"type": "SERVICE_QUALITY", "size": "invalid"}
        ]
        
        for invalid_params in invalid_params_list:
            response = api_client.get(feedbacks_url, params=invalid_params)
            
            # Should handle invalid pagination gracefully
            assert response.status_code in [200, 400, 404], f"Unexpected status for params {invalid_params}"
    
    @pytest.mark.integration
    def test_locations_data_consistency(self, api_client: APIClient):
        """Test data consistency between locations list and select options."""
        # Get full locations list
        list_response = api_client.get(api_config.locations_endpoints["list"])
        assert list_response.status_code == 200
        full_locations = list_response.json()
        
        # Get location select options
        options_response = api_client.get(api_config.locations_endpoints["select_options"])
        assert options_response.status_code == 200
        location_options = options_response.json()
        
        if full_locations and location_options:
            # Extract IDs from both responses
            full_ids = {loc.get("id") for loc in full_locations if "id" in loc}
            option_ids = {opt.get("id") for opt in location_options if "id" in opt}
            
            # Select options should be a subset of full locations
            missing_ids = option_ids - full_ids
            assert not missing_ids, f"Select option IDs not found in full list: {missing_ids}"
            
            # Addresses should match for same IDs
            full_addresses = {loc["id"]: loc["address"] for loc in full_locations if "id" in loc and "address" in loc}
            option_addresses = {opt["id"]: opt["address"] for opt in location_options if "id" in opt and "address" in opt}
            
            for location_id in option_addresses:
                if location_id in full_addresses:
                    assert full_addresses[location_id] == option_addresses[location_id], \
                        f"Address mismatch for location {location_id}"
    
    @pytest.mark.performance
    def test_locations_endpoint_response_time(self, api_client: APIClient):
        """Test locations endpoint response time."""
        import time
        
        start_time = time.time()
        response = api_client.get(api_config.locations_endpoints["list"])
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should respond within reasonable time
        assert response_time < 5.0, f"Response time too slow: {response_time}s"
        assert response.status_code == 200
    
    @pytest.mark.security
    def test_locations_no_sensitive_data_exposure(self, api_client: APIClient):
        """Test that locations endpoints don't expose sensitive data."""
        response = api_client.get(api_config.locations_endpoints["list"])
        assert response.status_code == 200
        
        response_text = response.text.lower()
        
        # Check for sensitive information that shouldn't be exposed
        sensitive_keywords = [
            "password", "secret", "key", "token", "database",
            "connection", "config", "admin", "internal", "credential"
        ]
        
        for keyword in sensitive_keywords:
            assert keyword not in response_text, f"Sensitive keyword '{keyword}' found in locations response"
    
    @pytest.mark.regression
    def test_locations_response_structure_stability(self, api_client: APIClient):
        """Test that locations response structure remains stable."""
        response = api_client.get(api_config.locations_endpoints["list"])
        assert response.status_code == 200
        
        response_data = response.json()
        assert isinstance(response_data, list), "Locations response should be a list"
        
        # If there are locations, check their structure
        if response_data:
            first_location = response_data[0]
            expected_fields = ["id", "address"]
            
            for field in expected_fields:
                assert field in first_location, f"Expected location field '{field}' missing"
    
    @pytest.mark.positive
    def test_location_rating_validation(self, api_client: APIClient):
        """Test that location ratings are valid when present."""
        response = api_client.get(api_config.locations_endpoints["list"])
        assert response.status_code == 200
        
        locations = response.json()
        
        for location in locations:
            if "rating" in location:
                rating = location["rating"]
                
                # Rating should be a valid number string
                try:
                    rating_value = float(rating)
                    assert 0 <= rating_value <= 5, f"Rating {rating_value} should be between 0 and 5"
                except ValueError:
                    pytest.fail(f"Invalid rating format: {rating}")
    
    @pytest.mark.positive
    def test_location_capacity_validation(self, api_client: APIClient):
        """Test that location capacity values are valid when present."""
        response = api_client.get(api_config.locations_endpoints["list"])
        assert response.status_code == 200
        
        locations = response.json()
        
        for location in locations:
            if "totalCapacity" in location:
                capacity = location["totalCapacity"]
                
                # Capacity should be a positive number
                try:
                    capacity_value = int(capacity)
                    assert capacity_value > 0, f"Capacity {capacity_value} should be positive"
                except ValueError:
                    pytest.fail(f"Invalid capacity format: {capacity}")
            
            if "averageOccupancy" in location:
                occupancy = location["averageOccupancy"]
                
                # Occupancy should be a valid percentage or number
                try:
                    if occupancy.endswith("%"):
                        occupancy_value = float(occupancy[:-1])
                        assert 0 <= occupancy_value <= 100, f"Occupancy percentage {occupancy_value} should be between 0 and 100"
                    else:
                        occupancy_value = float(occupancy)
                        assert occupancy_value >= 0, f"Occupancy {occupancy_value} should be non-negative"
                except ValueError:
                    pytest.fail(f"Invalid occupancy format: {occupancy}")