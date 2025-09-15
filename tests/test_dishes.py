"""
Dishes API Tests.

This module contains comprehensive tests for dishes endpoints
including popular dishes, dish listing, filtering, and dish details.
"""

import pytest
import requests
from typing import Dict, Any, List

from tests.utils.api_client import APIClient, AuthenticatedAPIClient
from tests.utils.validators import validator
from tests.config import api_config, test_config


class TestDishesEndpoints:
    """Test suite for dishes endpoints."""
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_get_popular_dishes(self, api_client: APIClient):
        """Test retrieving popular dishes."""
        response = api_client.get(api_config.dishes_endpoints["popular"])
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert isinstance(response_data, list), "Expected list of dishes"
        
        # Validate each dish in the response
        if response_data:  # If there are dishes
            validator.validate_list_response(response_data, "dish_response")
            
            # Check that all dishes have required fields
            for dish in response_data:
                assert "name" in dish
                assert "price" in dish
                
                # Validate price format
                assert dish["price"].startswith("$"), "Price should start with $"
    
    @pytest.mark.positive
    def test_get_dishes_list(self, api_client: APIClient):
        """Test retrieving dishes list."""
        response = api_client.get(api_config.dishes_endpoints["list"])
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert "content" in response_data, "Expected content field in response"
        
        # Validate menu response structure
        validator.validate_response(response_data, "cart_response")  # Using cart_response as it has content structure
        
        dishes = response_data["content"]
        if dishes:
            # Validate each dish
            for dish in dishes:
                assert "name" in dish
                assert "price" in dish
    
    @pytest.mark.positive
    @pytest.mark.parametrize("dish_type", [
        "APPETIZER",
        "MAIN_COURSE", 
        "DESSERT"
    ])
    def test_get_dishes_by_type(self, api_client: APIClient, dish_type: str):
        """Test retrieving dishes filtered by type."""
        params = {"dishType": dish_type}
        
        response = api_client.get(
            api_config.dishes_endpoints["list"],
            params=params
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert "content" in response_data
        
        # If dishes are returned, they should match the requested type
        dishes = response_data["content"]
        for dish in dishes:
            if "dishType" in dish:
                assert dish["dishType"] == dish_type, f"Expected {dish_type}, got {dish['dishType']}"
    
    @pytest.mark.positive
    @pytest.mark.parametrize("sort_param", [
        "popularity,asc",
        "popularity,desc",
        "price,asc",
        "price,desc"
    ])
    def test_get_dishes_with_sorting(self, api_client: APIClient, sort_param: str):
        """Test retrieving dishes with different sorting options."""
        params = {"sort": sort_param}
        
        response = api_client.get(
            api_config.dishes_endpoints["list"],
            params=params
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert "content" in response_data
        
        # Validate that sorting is applied (basic check)
        dishes = response_data["content"]
        if len(dishes) > 1:
            # For price sorting, we can validate the order
            if "price" in sort_param:
                prices = []
                for dish in dishes:
                    if "price" in dish:
                        # Extract numeric value from price string like "$12.99"
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
    
    @pytest.mark.positive
    def test_get_dish_by_id(self, api_client: APIClient, mock_dish_id: str):
        """Test retrieving a specific dish by ID."""
        dish_url = api_config.dishes_endpoints["detail"].format(id=mock_dish_id)
        response = api_client.get(dish_url)
        
        # Note: This might return 404 if the dish doesn't exist in test environment
        if response.status_code == 200:
            response_data = response.json()
            
            # Validate extended dish response
            validator.validate_response(response_data, "dish_extended_response")
            
            # Check required fields
            assert "id" in response_data
            assert "name" in response_data
            assert "price" in response_data
            assert "description" in response_data
            
            # Validate business rules
            business_rules = {
                "id_matches": {
                    "field": "id",
                    "value": mock_dish_id,
                    "condition": "equals"
                },
                "name_not_empty": {
                    "field": "name",
                    "condition": "not_empty"
                },
                "description_not_empty": {
                    "field": "description",
                    "condition": "not_empty"
                }
            }
            errors = validator.validate_business_rules(response_data, business_rules)
            assert not errors, f"Business rule violations: {errors}"
        
        elif response.status_code == 404:
            # This is acceptable in test environment
            response_data = response.json()
            assert "detail" in response_data or "message" in response_data
        
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    @pytest.mark.negative
    def test_get_dish_invalid_id(self, api_client: APIClient):
        """Test retrieving dish with invalid ID."""
        invalid_ids = [
            "invalid-id",
            "123",
            "nonexistent123456789012345678901234",
            ""
        ]
        
        for invalid_id in invalid_ids:
            dish_url = api_config.dishes_endpoints["detail"].format(id=invalid_id)
            response = api_client.get(dish_url)
            
            # Should return 404 or 400
            assert response.status_code in [400, 404], f"Expected 400 or 404 for ID '{invalid_id}', got {response.status_code}"
    
    @pytest.mark.negative
    def test_get_dishes_invalid_type_filter(self, api_client: APIClient):
        """Test dishes endpoint with invalid dish type filter."""
        invalid_types = [
            "INVALID_TYPE",
            "123",
            "main course",  # Should be MAIN_COURSE
            ""
        ]
        
        for invalid_type in invalid_types:
            params = {"dishType": invalid_type}
            response = api_client.get(
                api_config.dishes_endpoints["list"],
                params=params
            )
            
            # Should either return 400 or empty results
            assert response.status_code in [200, 400], f"Unexpected status for invalid type '{invalid_type}'"
            
            if response.status_code == 200:
                response_data = response.json()
                # Should return empty results or handle gracefully
                assert "content" in response_data
    
    @pytest.mark.negative
    def test_get_dishes_invalid_sort_parameter(self, api_client: APIClient):
        """Test dishes endpoint with invalid sort parameters."""
        invalid_sorts = [
            "invalid,asc",
            "price,invalid",
            "popularity",  # Missing direction
            "price,asc,extra"
        ]
        
        for invalid_sort in invalid_sorts:
            params = {"sort": invalid_sort}
            response = api_client.get(
                api_config.dishes_endpoints["list"],
                params=params
            )
            
            # Should handle gracefully or return error
            assert response.status_code in [200, 400], f"Unexpected status for invalid sort '{invalid_sort}'"
    
    @pytest.mark.positive
    def test_dishes_pagination_parameters(self, api_client: APIClient):
        """Test dishes endpoint with pagination parameters."""
        # Test with page and size parameters (if supported)
        params = {
            "page": 0,
            "size": 5
        }
        
        response = api_client.get(
            api_config.dishes_endpoints["list"],
            params=params
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert "content" in response_data
        
        # If pagination is implemented, check the structure
        dishes = response_data["content"]
        if "totalElements" in response_data:
            # Full pagination response
            assert "totalPages" in response_data
            assert "size" in response_data
            assert "number" in response_data
            
            # Validate pagination response
            validator.validate_pagination_response(response_data, "dish_response")
    
    @pytest.mark.performance
    def test_dishes_endpoint_response_time(self, api_client: APIClient):
        """Test dishes endpoint response time."""
        import time
        
        start_time = time.time()
        response = api_client.get(api_config.dishes_endpoints["list"])
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should respond within reasonable time
        assert response_time < 5.0, f"Response time too slow: {response_time}s"
        assert response.status_code == 200
    
    @pytest.mark.integration
    def test_dishes_data_consistency(self, api_client: APIClient):
        """Test data consistency between popular dishes and full list."""
        # Get popular dishes
        popular_response = api_client.get(api_config.dishes_endpoints["popular"])
        assert popular_response.status_code == 200
        popular_dishes = popular_response.json()
        
        # Get full dishes list
        list_response = api_client.get(api_config.dishes_endpoints["list"])
        assert list_response.status_code == 200
        list_data = list_response.json()
        all_dishes = list_data.get("content", [])
        
        # Popular dishes should be a subset of all dishes (by name)
        if popular_dishes and all_dishes:
            popular_names = {dish.get("name") for dish in popular_dishes if "name" in dish}
            all_names = {dish.get("name") for dish in all_dishes if "name" in dish}
            
            # All popular dish names should exist in the full list
            missing_dishes = popular_names - all_names
            assert not missing_dishes, f"Popular dishes not found in full list: {missing_dishes}"
    
    @pytest.mark.security
    def test_dishes_no_sensitive_data_exposure(self, api_client: APIClient):
        """Test that dishes endpoints don't expose sensitive data."""
        response = api_client.get(api_config.dishes_endpoints["list"])
        assert response.status_code == 200
        
        response_text = response.text.lower()
        
        # Check for sensitive information that shouldn't be exposed
        sensitive_keywords = [
            "password", "secret", "key", "token", "database",
            "connection", "config", "admin", "internal"
        ]
        
        for keyword in sensitive_keywords:
            assert keyword not in response_text, f"Sensitive keyword '{keyword}' found in dishes response"
    
    @pytest.mark.regression
    def test_dishes_response_structure_stability(self, api_client: APIClient):
        """Test that dishes response structure remains stable."""
        response = api_client.get(api_config.dishes_endpoints["list"])
        assert response.status_code == 200
        
        response_data = response.json()
        
        # Check for expected top-level structure
        expected_fields = ["content"]
        for field in expected_fields:
            assert field in response_data, f"Expected field '{field}' missing from response"
        
        # If there are dishes, check their structure
        dishes = response_data.get("content", [])
        if dishes:
            first_dish = dishes[0]
            expected_dish_fields = ["name", "price"]
            
            for field in expected_dish_fields:
                assert field in first_dish, f"Expected dish field '{field}' missing"
    
    @pytest.mark.positive
    def test_dishes_combined_filters(self, api_client: APIClient):
        """Test dishes endpoint with combined filters."""
        params = {
            "dishType": "MAIN_COURSE",
            "sort": "price,asc"
        }
        
        response = api_client.get(
            api_config.dishes_endpoints["list"],
            params=params
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        response_data = response.json()
        assert "content" in response_data
        
        # Validate that both filters are applied
        dishes = response_data["content"]
        for dish in dishes:
            if "dishType" in dish:
                assert dish["dishType"] == "MAIN_COURSE"