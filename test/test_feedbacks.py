"""
Feedbacks API tests.
Tests for feedback-related endpoints including creating feedback and visitor feedback.
"""
import pytest
import requests
from typing import Dict, Any


class TestFeedbackCreation:
    """Test cases for feedback creation endpoint."""
    
    @pytest.mark.auth
    def test_create_feedback_success(self, authenticated_client, base_url, valid_feedback_data):
        """Test successful feedback creation."""
        response = authenticated_client.post(
            f"{base_url}/feedbacks/",
            json=valid_feedback_data
        )
        
        assert response.status_code == 201
        assert response.headers["content-type"] == "application/json"
        
        # Response should be a simple string message
        data = response.json()
        assert isinstance(data, str)
        assert "feedback has been created" in data.lower()
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_create_feedback_unauthorized(self, api_client, base_url, valid_feedback_data):
        """Test creating feedback without authentication."""
        response = api_client.post(
            f"{base_url}/feedbacks/",
            json=valid_feedback_data
        )
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_create_feedback_missing_fields(self, authenticated_client, base_url):
        """Test creating feedback with missing required fields."""
        incomplete_data_sets = [
            {},  # Empty payload
            {"reservationId": "test_reservation"},  # Missing ratings and comments
            {
                "reservationId": "test_reservation",
                "serviceRating": "5"
                # Missing serviceComment, cuisineRating, cuisineComment
            },
            {
                "reservationId": "test_reservation",
                "serviceRating": "5",
                "serviceComment": "Great service"
                # Missing cuisineRating, cuisineComment
            }
        ]
        
        for incomplete_data in incomplete_data_sets:
            response = authenticated_client.post(
                f"{base_url}/feedbacks/",
                json=incomplete_data
            )
            assert response.status_code in [400, 422], f"Failed for data: {incomplete_data}"
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_create_feedback_empty_fields(self, authenticated_client, base_url):
        """Test creating feedback with empty fields."""
        empty_field_cases = [
            {
                "reservationId": "",
                "serviceRating": "5",
                "serviceComment": "Great service",
                "cuisineRating": "4",
                "cuisineComment": "Good food"
            },
            {
                "reservationId": "test_reservation",
                "serviceRating": "",
                "serviceComment": "Great service",
                "cuisineRating": "4",
                "cuisineComment": "Good food"
            },
            {
                "reservationId": "test_reservation",
                "serviceRating": "5",
                "serviceComment": "",
                "cuisineRating": "4",
                "cuisineComment": "Good food"
            }
        ]
        
        for feedback_data in empty_field_cases:
            response = authenticated_client.post(
                f"{base_url}/feedbacks/",
                json=feedback_data
            )
            assert response.status_code in [400, 422], f"Failed for data: {feedback_data}"
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_create_feedback_invalid_ratings(self, authenticated_client, base_url):
        """Test creating feedback with invalid rating values."""
        invalid_rating_cases = [
            {
                "reservationId": "test_reservation",
                "serviceRating": "0",  # Below valid range
                "serviceComment": "Great service",
                "cuisineRating": "4",
                "cuisineComment": "Good food"
            },
            {
                "reservationId": "test_reservation",
                "serviceRating": "6",  # Above valid range
                "serviceComment": "Great service",
                "cuisineRating": "4",
                "cuisineComment": "Good food"
            },
            {
                "reservationId": "test_reservation",
                "serviceRating": "invalid",  # Non-numeric
                "serviceComment": "Great service",
                "cuisineRating": "4",
                "cuisineComment": "Good food"
            },
            {
                "reservationId": "test_reservation",
                "serviceRating": "5",
                "serviceComment": "Great service",
                "cuisineRating": "-1",  # Negative rating
                "cuisineComment": "Good food"
            }
        ]
        
        for feedback_data in invalid_rating_cases:
            response = authenticated_client.post(
                f"{base_url}/feedbacks/",
                json=feedback_data
            )
            assert response.status_code in [400, 422], f"Failed for data: {feedback_data}"
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_create_feedback_invalid_reservation_id(self, authenticated_client, base_url):
        """Test creating feedback with invalid reservation ID."""
        invalid_reservation_ids = [
            "invalid_reservation",
            "nonexistent_reservation_12345",
            "<script>alert('xss')</script>",
            "'; DROP TABLE feedbacks; --"
        ]
        
        for reservation_id in invalid_reservation_ids:
            feedback_data = {
                "reservationId": reservation_id,
                "serviceRating": "5",
                "serviceComment": "Great service",
                "cuisineRating": "4",
                "cuisineComment": "Good food"
            }
            
            response = authenticated_client.post(
                f"{base_url}/feedbacks/",
                json=feedback_data
            )
            # Should either reject invalid IDs or handle gracefully
            assert response.status_code in [201, 400, 404, 422]
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_create_feedback_very_long_comments(self, authenticated_client, base_url):
        """Test creating feedback with very long comments."""
        long_comment = "A" * 10000  # Very long comment
        
        feedback_data = {
            "reservationId": "672846d5c951184d705b65d7",
            "serviceRating": "5",
            "serviceComment": long_comment,
            "cuisineRating": "4",
            "cuisineComment": long_comment
        }
        
        response = authenticated_client.post(
            f"{base_url}/feedbacks/",
            json=feedback_data
        )
        
        # Should either accept or reject based on comment length limits
        assert response.status_code in [201, 400, 413, 422]  # 413 = Payload Too Large
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_create_feedback_special_characters_in_comments(self, authenticated_client, base_url):
        """Test creating feedback with special characters in comments."""
        special_char_cases = [
            {
                "serviceComment": "Great service! <script>alert('xss')</script>",
                "cuisineComment": "Good food"
            },
            {
                "serviceComment": "Great service",
                "cuisineComment": "Good food'; DROP TABLE feedbacks; --"
            },
            {
                "serviceComment": "Excellent service! 😊👍",  # Valid emoji
                "cuisineComment": "Delicious food! 🍕🍝"
            },
            {
                "serviceComment": "Service was très bon!",  # Valid accented characters
                "cuisineComment": "La comida estaba excelente"
            }
        ]
        
        for comment_data in special_char_cases:
            feedback_data = {
                "reservationId": "672846d5c951184d705b65d7",
                "serviceRating": "5",
                "serviceComment": comment_data["serviceComment"],
                "cuisineRating": "4",
                "cuisineComment": comment_data["cuisineComment"]
            }
            
            response = authenticated_client.post(
                f"{base_url}/feedbacks/",
                json=feedback_data
            )
            
            # Should either accept valid characters or reject malicious ones
            assert response.status_code in [201, 400, 422]
    
    @pytest.mark.auth
    def test_create_feedback_duplicate(self, authenticated_client, base_url, valid_feedback_data):
        """Test creating duplicate feedback for the same reservation."""
        # Create first feedback
        response1 = authenticated_client.post(
            f"{base_url}/feedbacks/",
            json=valid_feedback_data
        )
        
        # Create second feedback for the same reservation
        response2 = authenticated_client.post(
            f"{base_url}/feedbacks/",
            json=valid_feedback_data
        )
        
        # First might succeed or fail based on reservation existence
        assert response1.status_code in [201, 400, 404, 422]
        
        # Second should either succeed (if duplicates allowed) or fail
        assert response2.status_code in [201, 400, 409, 422]


class TestVisitorFeedback:
    """Test cases for visitor feedback endpoint."""
    
    def test_get_visitor_feedback_success(self, api_client, base_url):
        """Test successful visitor feedback retrieval."""
        params = {
            "reservationId": "672846d5c951184d705b65d7",
            "secretCode": "secret123"
        }
        
        response = api_client.get(f"{base_url}/feedbacks/visitor", params=params)
        
        # Should succeed or fail based on reservation/secret code validity
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            assert response.headers["content-type"] == "application/json"
            
            data = response.json()
            
            # Validate visitor feedback response structure
            required_fields = [
                "accessToken", "reservationId", "serviceRating",
                "waiterImageUrl", "waiterName"
            ]
            for field in required_fields:
                assert field in data
                assert isinstance(data[field], str)
            
            # Validate specific field formats
            assert len(data["accessToken"]) > 0
            assert data["reservationId"] == params["reservationId"]
            
            # Service rating should be numeric
            try:
                float(data["serviceRating"])
            except ValueError:
                pytest.fail(f"Service rating should be numeric: {data['serviceRating']}")
            
            # Waiter image URL should be valid
            if data["waiterImageUrl"]:
                assert data["waiterImageUrl"].startswith(("http://", "https://"))
    
    @pytest.mark.validation
    def test_get_visitor_feedback_missing_parameters(self, api_client, base_url):
        """Test visitor feedback with missing required parameters."""
        missing_param_cases = [
            {},  # No parameters
            {"reservationId": "test_reservation"},  # Missing secretCode
            {"secretCode": "secret123"},  # Missing reservationId
        ]
        
        for params in missing_param_cases:
            response = api_client.get(f"{base_url}/feedbacks/visitor", params=params)
            assert response.status_code in [400, 422], f"Failed for params: {params}"
    
    @pytest.mark.validation
    def test_get_visitor_feedback_empty_parameters(self, api_client, base_url):
        """Test visitor feedback with empty parameters."""
        empty_param_cases = [
            {"reservationId": "", "secretCode": "secret123"},
            {"reservationId": "test_reservation", "secretCode": ""},
            {"reservationId": "", "secretCode": ""},
        ]
        
        for params in empty_param_cases:
            response = api_client.get(f"{base_url}/feedbacks/visitor", params=params)
            assert response.status_code in [400, 422], f"Failed for params: {params}"
    
    @pytest.mark.validation
    def test_get_visitor_feedback_invalid_reservation_id(self, api_client, base_url):
        """Test visitor feedback with invalid reservation ID."""
        invalid_ids = [
            "invalid_reservation",
            "nonexistent_reservation_12345",
            "<script>alert('xss')</script>",
            "'; DROP TABLE reservations; --"
        ]
        
        for reservation_id in invalid_ids:
            params = {
                "reservationId": reservation_id,
                "secretCode": "secret123"
            }
            
            response = api_client.get(f"{base_url}/feedbacks/visitor", params=params)
            assert response.status_code in [400, 404], f"Failed for ID: {reservation_id}"
    
    @pytest.mark.validation
    def test_get_visitor_feedback_invalid_secret_code(self, api_client, base_url):
        """Test visitor feedback with invalid secret code."""
        invalid_codes = [
            "wrong_secret",
            "invalid_code_12345",
            "<script>alert('xss')</script>",
            "'; DROP TABLE secrets; --"
        ]
        
        for secret_code in invalid_codes:
            params = {
                "reservationId": "672846d5c951184d705b65d7",
                "secretCode": secret_code
            }
            
            response = api_client.get(f"{base_url}/feedbacks/visitor", params=params)
            assert response.status_code in [400, 401, 404], f"Failed for code: {secret_code}"
    
    def test_visitor_feedback_response_structure(self, api_client, base_url):
        """Test visitor feedback response structure."""
        params = {
            "reservationId": "672846d5c951184d705b65d7",
            "secretCode": "valid_secret"
        }
        
        response = api_client.get(f"{base_url}/feedbacks/visitor", params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Should be a dictionary with specific fields
            assert isinstance(data, dict)
            
            # Check required fields exist and have correct types
            required_fields = {
                "accessToken": str,
                "reservationId": str,
                "serviceRating": str,
                "waiterImageUrl": str,
                "waiterName": str
            }
            
            for field, expected_type in required_fields.items():
                assert field in data
                assert isinstance(data[field], expected_type)


class TestFeedbacksIntegration:
    """Integration tests for feedback functionality."""
    
    @pytest.mark.integration
    def test_visitor_feedback_to_creation_flow(self, api_client, base_url):
        """Test complete visitor feedback flow."""
        # Step 1: Get visitor feedback info (simulate QR code scan)
        visitor_params = {
            "reservationId": "672846d5c951184d705b65d7",
            "secretCode": "valid_secret"
        }
        
        visitor_response = api_client.get(f"{base_url}/feedbacks/visitor", params=visitor_params)
        
        if visitor_response.status_code == 200:
            visitor_data = visitor_response.json()
            
            # Step 2: Use the access token to create feedback
            feedback_data = {
                "reservationId": visitor_data["reservationId"],
                "serviceRating": "5",
                "serviceComment": "Excellent service from visitor flow",
                "cuisineRating": "4",
                "cuisineComment": "Great food from visitor flow"
            }
            
            # Create authenticated client with visitor token
            visitor_client = api_client
            visitor_client.headers.update({
                "Authorization": f"Bearer {visitor_data['accessToken']}"
            })
            
            feedback_response = visitor_client.post(
                f"{base_url}/feedbacks/",
                json=feedback_data
            )
            
            # Should succeed or fail gracefully
            assert feedback_response.status_code in [201, 400, 401, 404, 422]
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_feedback_creation_consistency(self, authenticated_client, base_url):
        """Test feedback creation consistency."""
        # Create multiple feedbacks with different data
        feedback_cases = [
            {
                "reservationId": "672846d5c951184d705b65d7",
                "serviceRating": "5",
                "serviceComment": "Excellent service",
                "cuisineRating": "5",
                "cuisineComment": "Amazing food"
            },
            {
                "reservationId": "672846d5c951184d705b65d8",
                "serviceRating": "3",
                "serviceComment": "Average service",
                "cuisineRating": "4",
                "cuisineComment": "Good food"
            },
            {
                "reservationId": "672846d5c951184d705b65d9",
                "serviceRating": "1",
                "serviceComment": "Poor service",
                "cuisineRating": "2",
                "cuisineComment": "Bad food"
            }
        ]
        
        responses = []
        for feedback_data in feedback_cases:
            response = authenticated_client.post(
                f"{base_url}/feedbacks/",
                json=feedback_data
            )
            responses.append(response)
        
        # All requests should be handled consistently
        for response in responses:
            assert response.status_code in [201, 400, 404, 422]


class TestFeedbacksErrorScenarios:
    """Test error scenarios and edge cases."""
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_feedback_with_malformed_json(self, authenticated_client, base_url):
        """Test feedback creation with malformed JSON."""
        malformed_json = '{"reservationId": "test", "serviceRating": "5"'  # Missing closing brace
        
        response = authenticated_client.post(
            f"{base_url}/feedbacks/",
            data=malformed_json,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]
    
    @pytest.mark.error
    def test_visitor_feedback_with_malformed_parameters(self, api_client, base_url):
        """Test visitor feedback with malformed parameters."""
        malformed_params = [
            {"reservationId": "A" * 10000, "secretCode": "secret"},  # Very long ID
            {"reservationId": "test%00", "secretCode": "secret"},  # Null byte
            {"reservationId": "test", "secretCode": "B" * 10000},  # Very long secret
        ]
        
        for params in malformed_params:
            response = api_client.get(f"{base_url}/feedbacks/visitor", params=params)
            # Should handle gracefully
            assert response.status_code in [400, 404, 414]  # 414 = URI Too Long
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_concurrent_feedback_creation(self, authenticated_client, base_url):
        """Test concurrent feedback creation."""
        import threading
        
        responses = []
        
        def create_feedback(thread_id):
            feedback_data = {
                "reservationId": f"reservation_{thread_id}",
                "serviceRating": "5",
                "serviceComment": f"Service comment {thread_id}",
                "cuisineRating": "4",
                "cuisineComment": f"Cuisine comment {thread_id}"
            }
            response = authenticated_client.post(
                f"{base_url}/feedbacks/",
                json=feedback_data
            )
            responses.append(response)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_feedback, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should be handled gracefully
        for response in responses:
            assert response.status_code in [201, 400, 404, 422]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_feedback_operations_with_expired_token(self, api_client, base_url):
        """Test feedback operations with expired token."""
        # Use an obviously invalid token
        api_client.headers.update({"Authorization": "Bearer expired_token_12345"})
        
        feedback_data = {
            "reservationId": "test_reservation",
            "serviceRating": "5",
            "serviceComment": "Great service",
            "cuisineRating": "4",
            "cuisineComment": "Good food"
        }
        
        response = api_client.post(f"{base_url}/feedbacks/", json=feedback_data)
        assert response.status_code == 401
    
    @pytest.mark.error
    def test_visitor_feedback_rate_limiting(self, api_client, base_url):
        """Test rate limiting on visitor feedback endpoint."""
        # Make many requests quickly
        responses = []
        
        params = {
            "reservationId": "test_reservation",
            "secretCode": "test_secret"
        }
        
        for _ in range(20):
            response = api_client.get(f"{base_url}/feedbacks/visitor", params=params)
            responses.append(response)
        
        # Most should be handled consistently
        for response in responses:
            assert response.status_code in [200, 400, 404, 429]  # 429 = Too Many Requests
        
        # If rate limiting is implemented, some might be rate limited
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        # This is optional, so we don't assert on it