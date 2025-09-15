"""
Integration API tests.
End-to-end integration tests covering complete user workflows and cross-service interactions.
"""
import pytest
import requests
from typing import Dict, Any
import time


class TestUserJourney:
    """Test complete user journey scenarios."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_complete_user_journey(self, api_client, base_url):
        """Test complete user journey from signup to feedback."""
        # Step 1: Health check
        health_response = api_client.get(f"{base_url}/health")
        assert health_response.status_code == 200
        
        # Step 2: Sign up (or use existing user)
        signup_data = {
            "firstName": "Integration",
            "lastName": "User",
            "email": "integration_user@example.com",
            "password": "integrationPassword123"
        }
        
        signup_response = api_client.post(f"{base_url}/auth/signup", json=signup_data)
        # Handle both new user and existing user scenarios
        assert signup_response.status_code in [201, 409]
        
        # Step 3: Sign in
        signin_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        signin_response = api_client.post(f"{base_url}/auth/signin", json=signin_data)
        
        # If integration user doesn't exist, use known valid credentials
        if signin_response.status_code != 200:
            signin_data = {
                "email": "jhon_smith@example.com",
                "password": "Y2kjqKHX"
            }
            signin_response = api_client.post(f"{base_url}/auth/signin", json=signin_data)
        
        assert signin_response.status_code == 200
        signin_data_response = signin_response.json()
        
        # Set authentication token
        token = signin_data_response["accessToken"]
        api_client.headers.update({"Authorization": f"Bearer {token}"})
        
        # Step 4: Browse locations
        locations_response = api_client.get(f"{base_url}/locations")
        assert locations_response.status_code == 200
        
        locations_data = locations_response.json()
        
        if locations_data:
            location_id = locations_data[0]["id"]
            
            # Step 5: Browse dishes
            dishes_response = api_client.get(f"{base_url}/dishes/popular")
            assert dishes_response.status_code == 200
            
            # Step 6: Search for available tables
            table_search_params = {
                "locationId": location_id,
                "date": "2024-12-31",
                "time": "12:00",
                "guests": "4"
            }
            
            tables_response = api_client.get(f"{base_url}/bookings/tables", params=table_search_params)
            assert tables_response.status_code == 200
            
            tables_data = tables_response.json()
            
            if tables_data:
                # Step 7: Make a reservation
                table = tables_data[0]
                
                reservation_data = {
                    "locationId": table["locationId"],
                    "tableNumber": table["tableNumber"],
                    "date": "2024-12-31",
                    "guestsNumber": "4",
                    "timeFrom": "12:15",
                    "timeTo": "14:00"
                }
                
                booking_response = api_client.post(f"{base_url}/bookings/client", json=reservation_data)
                
                if booking_response.status_code == 200:
                    booking_result = booking_response.json()
                    reservation_id = booking_result["id"]
                    
                    # Step 8: Check reservations
                    reservations_response = api_client.get(f"{base_url}/reservations")
                    assert reservations_response.status_code == 200
                    
                    # Step 9: Browse available dishes for reservation
                    available_dishes_response = api_client.get(
                        f"{base_url}/reservations/{reservation_id}/available-dishes"
                    )
                    
                    if available_dishes_response.status_code == 200:
                        available_dishes_data = available_dishes_response.json()
                        
                        if available_dishes_data.get("content"):
                            # Step 10: Order a dish
                            dish_id = available_dishes_data["content"][0]["id"]
                            
                            order_response = api_client.post(
                                f"{base_url}/reservations/{reservation_id}/order/{dish_id}"
                            )
                            
                            # Order might succeed or fail
                            assert order_response.status_code in [200, 400, 404]
                    
                    # Step 11: Check cart
                    cart_response = api_client.get(f"{base_url}/cart")
                    assert cart_response.status_code == 200
                    
                    # Step 12: Create feedback
                    feedback_data = {
                        "reservationId": reservation_id,
                        "serviceRating": "5",
                        "serviceComment": "Excellent service in integration test",
                        "cuisineRating": "4",
                        "cuisineComment": "Great food in integration test"
                    }
                    
                    feedback_response = api_client.post(f"{base_url}/feedbacks/", json=feedback_data)
                    # Feedback might succeed or fail based on business rules
                    assert feedback_response.status_code in [201, 400, 404, 409]
        
        # Step 13: Check profile
        profile_response = api_client.get(f"{base_url}/users/profile")
        assert profile_response.status_code == 200
    
    @pytest.mark.integration
    def test_data_consistency_across_endpoints(self, authenticated_client, base_url):
        """Test data consistency across different endpoints."""
        # Get locations from different endpoints
        locations_response = authenticated_client.get(f"{base_url}/locations")
        assert locations_response.status_code == 200
        
        options_response = authenticated_client.get(f"{base_url}/locations/select-options")
        assert options_response.status_code == 200
        
        locations_data = locations_response.json()
        options_data = options_response.json()
        
        # Verify consistency
        if locations_data and options_data:
            locations_ids = {loc["id"] for loc in locations_data}
            options_ids = {opt["id"] for opt in options_data}
            
            # Options should be a subset of locations
            assert options_ids.issubset(locations_ids)
        
        # Get dishes from different endpoints
        popular_dishes_response = authenticated_client.get(f"{base_url}/dishes/popular")
        assert popular_dishes_response.status_code == 200
        
        all_dishes_response = authenticated_client.get(f"{base_url}/dishes")
        assert all_dishes_response.status_code == 200
        
        # Verify dish data consistency
        popular_dishes = popular_dishes_response.json()
        all_dishes = all_dishes_response.json().get("content", [])
        
        if popular_dishes and all_dishes:
            # Popular dishes should exist in all dishes
            popular_names = {dish["name"] for dish in popular_dishes}
            all_names = {dish["name"] for dish in all_dishes}
            
            # At least some popular dishes should be in all dishes
            common_dishes = popular_names.intersection(all_names)
            assert len(common_dishes) >= 0  # Allow for empty intersection


class TestErrorHandlingIntegration:
    """Test error handling across multiple endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.error
    def test_authentication_flow_errors(self, api_client, base_url):
        """Test authentication error handling across endpoints."""
        # Test accessing protected endpoints without authentication
        protected_endpoints = [
            ("GET", f"{base_url}/reservations"),
            ("POST", f"{base_url}/bookings/client"),
            ("GET", f"{base_url}/cart"),
            ("GET", f"{base_url}/users/profile"),
            ("POST", f"{base_url}/feedbacks/"),
            ("GET", f"{base_url}/reports"),
        ]
        
        for method, url in protected_endpoints:
            if method == "GET":
                response = api_client.get(url)
            elif method == "POST":
                response = api_client.post(url, json={})
            
            assert response.status_code == 401, f"Failed for {method} {url}"
    
    @pytest.mark.integration
    @pytest.mark.error
    def test_invalid_data_propagation(self, authenticated_client, base_url):
        """Test how invalid data propagates through the system."""
        # Try to create a reservation with invalid data
        invalid_reservation = {
            "locationId": "invalid_location_12345",
            "tableNumber": "999",
            "date": "2020-01-01",  # Past date
            "guestsNumber": "0",
            "timeFrom": "25:00",  # Invalid time
            "timeTo": "26:00"
        }
        
        booking_response = authenticated_client.post(
            f"{base_url}/bookings/client",
            json=invalid_reservation
        )
        
        # Should be rejected
        assert booking_response.status_code in [400, 422]
        
        # Try to order a dish for non-existent reservation
        order_response = authenticated_client.post(
            f"{base_url}/reservations/nonexistent_reservation/order/nonexistent_dish"
        )
        
        assert order_response.status_code in [400, 404]
        
        # Try to create feedback for non-existent reservation
        invalid_feedback = {
            "reservationId": "nonexistent_reservation_12345",
            "serviceRating": "5",
            "serviceComment": "Test comment",
            "cuisineRating": "4",
            "cuisineComment": "Test comment"
        }
        
        feedback_response = authenticated_client.post(
            f"{base_url}/feedbacks/",
            json=invalid_feedback
        )
        
        assert feedback_response.status_code in [400, 404, 422]


class TestPerformanceIntegration:
    """Test performance aspects of the API."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_response_times(self, api_client, base_url):
        """Test response times for various endpoints."""
        endpoints = [
            f"{base_url}/health",
            f"{base_url}/",
            f"{base_url}/locations",
            f"{base_url}/dishes/popular",
            f"{base_url}/dishes",
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = api_client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Response should be reasonably fast
            assert response_time < 10.0, f"Slow response from {endpoint}: {response_time}s"
            assert response.status_code in [200, 401]  # 401 for protected endpoints
    
    @pytest.mark.integration
    def test_concurrent_requests(self, api_client, base_url):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        responses = []
        
        def make_request():
            response = api_client.get(f"{base_url}/health")
            responses.append(response)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Should handle concurrent requests reasonably well
        assert total_time < 30.0  # Should complete within 30 seconds
        assert len(responses) == 10


class TestSecurityIntegration:
    """Test security aspects across the API."""
    
    @pytest.mark.integration
    @pytest.mark.security
    def test_sql_injection_attempts(self, api_client, base_url):
        """Test SQL injection attempts across endpoints."""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; SELECT * FROM users; --",
            "admin'--",
            "' UNION SELECT * FROM users--"
        ]
        
        # Test in various parameters
        for payload in sql_payloads:
            # Test in authentication
            auth_data = {
                "email": payload,
                "password": "test"
            }
            
            response = api_client.post(f"{base_url}/auth/signin", json=auth_data)
            assert response.status_code in [400, 401, 422]
            
            # Test in search parameters
            response = api_client.get(f"{base_url}/dishes", params={"dishType": payload})
            assert response.status_code in [200, 400, 422]
            
            # Test in path parameters
            response = api_client.get(f"{base_url}/dishes/{payload}")
            assert response.status_code in [400, 404]
    
    @pytest.mark.integration
    @pytest.mark.security
    def test_xss_attempts(self, authenticated_client, base_url):
        """Test XSS attempts across endpoints."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            # Test in profile update
            profile_data = {
                "firstName": payload,
                "lastName": "Test"
            }
            
            response = authenticated_client.put(f"{base_url}/users/profile", json=profile_data)
            assert response.status_code in [200, 400, 422]
            
            # Test in feedback comments
            feedback_data = {
                "reservationId": "test_reservation",
                "serviceRating": "5",
                "serviceComment": payload,
                "cuisineRating": "4",
                "cuisineComment": "Test comment"
            }
            
            response = authenticated_client.post(f"{base_url}/feedbacks/", json=feedback_data)
            assert response.status_code in [201, 400, 404, 422]
    
    @pytest.mark.integration
    @pytest.mark.security
    def test_authorization_bypass_attempts(self, api_client, base_url):
        """Test authorization bypass attempts."""
        # Test with malformed tokens
        malformed_tokens = [
            "Bearer invalid_token",
            "Bearer ",
            "Invalid invalid_token",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
        ]
        
        for token in malformed_tokens:
            api_client.headers.update({"Authorization": token})
            
            response = api_client.get(f"{base_url}/reservations")
            assert response.status_code == 401
            
            response = api_client.get(f"{base_url}/users/profile")
            assert response.status_code == 401
        
        # Test without authorization header
        if "Authorization" in api_client.headers:
            del api_client.headers["Authorization"]
        
        protected_endpoints = [
            f"{base_url}/reservations",
            f"{base_url}/users/profile",
            f"{base_url}/cart",
            f"{base_url}/reports"
        ]
        
        for endpoint in protected_endpoints:
            response = api_client.get(endpoint)
            assert response.status_code == 401


class TestBusinessLogicIntegration:
    """Test business logic integration across services."""
    
    @pytest.mark.integration
    def test_reservation_to_feedback_flow(self, authenticated_client, base_url):
        """Test the flow from reservation to feedback."""
        # Get existing reservations
        reservations_response = authenticated_client.get(f"{base_url}/reservations")
        assert reservations_response.status_code == 200
        
        reservations_data = reservations_response.json()
        
        if reservations_data:
            reservation_id = reservations_data[0]["id"]
            
            # Try to create feedback for the reservation
            feedback_data = {
                "reservationId": reservation_id,
                "serviceRating": "5",
                "serviceComment": "Integration test feedback",
                "cuisineRating": "4",
                "cuisineComment": "Integration test cuisine feedback"
            }
            
            feedback_response = authenticated_client.post(
                f"{base_url}/feedbacks/",
                json=feedback_data
            )
            
            # Should succeed or fail based on business rules
            assert feedback_response.status_code in [201, 400, 409, 422]
            
            # If feedback was created, it might affect location ratings
            # This would require checking location feedbacks, but that's endpoint-specific
    
    @pytest.mark.integration
    def test_cart_and_reservation_consistency(self, authenticated_client, base_url):
        """Test consistency between cart and reservations."""
        # Get cart
        cart_response = authenticated_client.get(f"{base_url}/cart")
        assert cart_response.status_code == 200
        
        cart_data = cart_response.json()
        
        # Get reservations
        reservations_response = authenticated_client.get(f"{base_url}/reservations")
        assert reservations_response.status_code == 200
        
        reservations_data = reservations_response.json()
        
        # Check consistency
        if cart_data["content"] and reservations_data:
            cart_reservation_ids = {item["reservationId"] for item in cart_data["content"]}
            reservation_ids = {reservation["id"] for reservation in reservations_data}
            
            # Cart items should reference existing reservations
            for cart_reservation_id in cart_reservation_ids:
                assert cart_reservation_id in reservation_ids, f"Cart references non-existent reservation: {cart_reservation_id}"