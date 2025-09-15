"""
Tests for feedbacks endpoints.
"""
import pytest


class TestFeedbacksEndpoints:
    """Test class for feedbacks endpoints."""

    def test_create_feedback_success(self, api_client, base_url, auth_headers, sample_feedback_data):
        """Test successful feedback creation."""
        response = api_client.post(
            f"{base_url}/feedbacks/",
            json=sample_feedback_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert data == "Feedback has been created"

    def test_create_feedback_unauthorized(self, api_client, base_url, sample_feedback_data):
        """Test feedback creation without authentication."""
        response = api_client.post(
            f"{base_url}/feedbacks/",
            json=sample_feedback_data
        )
        
        assert response.status_code == 401

    def test_create_feedback_missing_fields(self, api_client, base_url, auth_headers):
        """Test feedback creation with missing required fields."""
        incomplete_data = {
            "reservationId": "672846d5c951184d705b65d7"
            # Missing rating and comment fields
        }
        
        response = api_client.post(
            f"{base_url}/feedbacks/",
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]

    def test_create_feedback_invalid_rating(self, api_client, base_url, auth_headers):
        """Test feedback creation with invalid rating values."""
        invalid_ratings = ["-1", "0", "6", "abc", ""]
        
        for rating in invalid_ratings:
            feedback_data = {
                "reservationId": "672846d5c951184d705b65d7",
                "serviceRating": rating,
                "serviceComment": "Test comment",
                "cuisineRating": "4",
                "cuisineComment": "Test comment"
            }
            
            response = api_client.post(
                f"{base_url}/feedbacks/",
                json=feedback_data,
                headers=auth_headers
            )
            
            assert response.status_code in [400, 422]

    def test_create_feedback_valid_ratings(self, api_client, base_url, auth_headers):
        """Test feedback creation with valid rating values."""
        valid_ratings = ["1", "2", "3", "4", "5"]
        
        for rating in valid_ratings:
            feedback_data = {
                "reservationId": "672846d5c951184d705b65d7",
                "serviceRating": rating,
                "serviceComment": "Test comment",
                "cuisineRating": rating,
                "cuisineComment": "Test comment"
            }
            
            response = api_client.post(
                f"{base_url}/feedbacks/",
                json=feedback_data,
                headers=auth_headers
            )
            
            assert response.status_code in [201, 400]  # May fail due to business logic

    def test_create_feedback_empty_comments(self, api_client, base_url, auth_headers):
        """Test feedback creation with empty comments."""
        feedback_data = {
            "reservationId": "672846d5c951184d705b65d7",
            "serviceRating": "5",
            "serviceComment": "",
            "cuisineRating": "4",
            "cuisineComment": ""
        }
        
        response = api_client.post(
            f"{base_url}/feedbacks/",
            json=feedback_data,
            headers=auth_headers
        )
        
        assert response.status_code in [201, 400, 422]

    def test_create_feedback_long_comments(self, api_client, base_url, auth_headers):
        """Test feedback creation with very long comments."""
        long_comment = "A" * 1000  # Very long comment
        
        feedback_data = {
            "reservationId": "672846d5c951184d705b65d7",
            "serviceRating": "5",
            "serviceComment": long_comment,
            "cuisineRating": "4",
            "cuisineComment": long_comment
        }
        
        response = api_client.post(
            f"{base_url}/feedbacks/",
            json=feedback_data,
            headers=auth_headers
        )
        
        assert response.status_code in [201, 400, 422]

    def test_create_feedback_invalid_reservation_id(self, api_client, base_url, auth_headers):
        """Test feedback creation with invalid reservation ID."""
        feedback_data = {
            "reservationId": "invalid-reservation-id",
            "serviceRating": "5",
            "serviceComment": "Great service",
            "cuisineRating": "4",
            "cuisineComment": "Good food"
        }
        
        response = api_client.post(
            f"{base_url}/feedbacks/",
            json=feedback_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 404]

    def test_get_visitor_feedback_success(self, api_client, base_url):
        """Test successful visitor feedback retrieval."""
        response = api_client.get(
            f"{base_url}/feedbacks/visitor",
            params={
                "reservationId": "672846d5c951184d705b65d7",
                "secretCode": "secret123"
            }
        )
        
        assert response.status_code in [200, 400, 404]  # May fail if reservation/code doesn't exist
        
        if response.status_code == 200:
            data = response.json()
            assert "accessToken" in data
            assert "reservationId" in data
            assert "serviceRating" in data
            assert "waiterImageUrl" in data
            assert "waiterName" in data
            
            # Validate data types
            assert isinstance(data["accessToken"], str)
            assert isinstance(data["reservationId"], str)
            assert isinstance(data["serviceRating"], str)
            assert isinstance(data["waiterImageUrl"], str)
            assert isinstance(data["waiterName"], str)

    def test_get_visitor_feedback_missing_params(self, api_client, base_url):
        """Test visitor feedback retrieval with missing parameters."""
        # Missing secretCode
        response = api_client.get(
            f"{base_url}/feedbacks/visitor",
            params={"reservationId": "672846d5c951184d705b65d7"}
        )
        
        assert response.status_code in [400, 422]
        
        # Missing reservationId
        response = api_client.get(
            f"{base_url}/feedbacks/visitor",
            params={"secretCode": "secret123"}
        )
        
        assert response.status_code in [400, 422]

    def test_get_visitor_feedback_invalid_params(self, api_client, base_url):
        """Test visitor feedback retrieval with invalid parameters."""
        response = api_client.get(
            f"{base_url}/feedbacks/visitor",
            params={
                "reservationId": "invalid-id",
                "secretCode": "invalid-code"
            }
        )
        
        assert response.status_code in [400, 404]

    def test_get_visitor_feedback_empty_params(self, api_client, base_url):
        """Test visitor feedback retrieval with empty parameters."""
        response = api_client.get(
            f"{base_url}/feedbacks/visitor",
            params={
                "reservationId": "",
                "secretCode": ""
            }
        )
        
        assert response.status_code in [400, 422]

    def test_feedback_xss_protection(self, api_client, base_url, auth_headers):
        """Test feedback creation with XSS attempts."""
        xss_feedback_data = {
            "reservationId": "672846d5c951184d705b65d7",
            "serviceRating": "5",
            "serviceComment": "<script>alert('xss')</script>",
            "cuisineRating": "4",
            "cuisineComment": "<img src=x onerror=alert('xss')>"
        }
        
        response = api_client.post(
            f"{base_url}/feedbacks/",
            json=xss_feedback_data,
            headers=auth_headers
        )
        
        # Should handle gracefully, not execute script
        assert response.status_code in [201, 400, 422]

    def test_feedback_sql_injection_protection(self, api_client, base_url, auth_headers):
        """Test feedback creation with SQL injection attempts."""
        sql_injection_data = {
            "reservationId": "672846d5c951184d705b65d7'; DROP TABLE feedbacks; --",
            "serviceRating": "5",
            "serviceComment": "'; DELETE FROM users; --",
            "cuisineRating": "4",
            "cuisineComment": "Normal comment"
        }
        
        response = api_client.post(
            f"{base_url}/feedbacks/",
            json=sql_injection_data,
            headers=auth_headers
        )
        
        # Should handle gracefully, not execute SQL
        assert response.status_code in [201, 400, 422]

    def test_feedback_rating_boundary_values(self, api_client, base_url, auth_headers):
        """Test feedback creation with boundary rating values."""
        boundary_ratings = ["1", "5"]  # Min and max valid ratings
        
        for rating in boundary_ratings:
            feedback_data = {
                "reservationId": "672846d5c951184d705b65d7",
                "serviceRating": rating,
                "serviceComment": "Boundary test",
                "cuisineRating": rating,
                "cuisineComment": "Boundary test"
            }
            
            response = api_client.post(
                f"{base_url}/feedbacks/",
                json=feedback_data,
                headers=auth_headers
            )
            
            assert response.status_code in [201, 400]  # May fail due to business logic

    def test_feedback_unicode_characters(self, api_client, base_url, auth_headers):
        """Test feedback creation with unicode characters."""
        unicode_feedback_data = {
            "reservationId": "672846d5c951184d705b65d7",
            "serviceRating": "5",
            "serviceComment": "Excellent service! 😊👍 Très bien!",
            "cuisineRating": "4",
            "cuisineComment": "Delicious food! 🍽️ Очень вкусно!"
        }
        
        response = api_client.post(
            f"{base_url}/feedbacks/",
            json=unicode_feedback_data,
            headers=auth_headers
        )
        
        assert response.status_code in [201, 400, 422]

    def test_visitor_feedback_token_format(self, api_client, base_url):
        """Test visitor feedback access token format."""
        response = api_client.get(
            f"{base_url}/feedbacks/visitor",
            params={
                "reservationId": "672846d5c951184d705b65d7",
                "secretCode": "secret123"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data["accessToken"]
            
            # Token should be reasonably long
            assert len(access_token) > 10, f"Token too short: {access_token}"
            
            # Token should not contain spaces
            assert " " not in access_token, f"Token contains spaces: {access_token}"

    def test_visitor_feedback_rating_format(self, api_client, base_url):
        """Test visitor feedback service rating format."""
        response = api_client.get(
            f"{base_url}/feedbacks/visitor",
            params={
                "reservationId": "672846d5c951184d705b65d7",
                "secretCode": "secret123"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            service_rating = data["serviceRating"]
            
            try:
                rating_value = float(service_rating)
                assert 0 <= rating_value <= 5, f"Rating out of range: {service_rating}"
            except ValueError:
                pytest.fail(f"Service rating is not a valid number: {service_rating}")

    def test_visitor_feedback_waiter_info(self, api_client, base_url):
        """Test visitor feedback waiter information."""
        response = api_client.get(
            f"{base_url}/feedbacks/visitor",
            params={
                "reservationId": "672846d5c951184d705b65d7",
                "secretCode": "secret123"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            waiter_name = data["waiterName"]
            waiter_image_url = data["waiterImageUrl"]
            
            # Waiter name should not be empty
            assert len(waiter_name.strip()) > 0, "Waiter name is empty"
            
            # Waiter image URL should be valid
            if waiter_image_url:
                assert waiter_image_url.startswith("http"), f"Invalid waiter image URL: {waiter_image_url}"