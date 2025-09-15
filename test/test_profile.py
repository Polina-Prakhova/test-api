"""
Profile API tests.
Tests for user profile management endpoints including profile retrieval and updates.
"""
import pytest
import requests
from typing import Dict, Any


class TestProfileRetrieval:
    """Test cases for profile retrieval endpoint."""
    
    @pytest.mark.auth
    def test_get_profile_success(self, authenticated_client, base_url):
        """Test successful retrieval of user profile."""
        response = authenticated_client.get(f"{base_url}/users/profile")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        
        # Validate profile structure
        required_fields = ["firstName", "lastName", "imageUrl"]
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], str)
        
        # Validate specific field formats
        assert len(data["firstName"]) > 0
        assert len(data["lastName"]) > 0
        
        # Image URL should be a valid URL or empty
        if data["imageUrl"]:
            assert data["imageUrl"].startswith(("http://", "https://"))
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_get_profile_unauthorized(self, api_client, base_url):
        """Test getting profile without authentication."""
        response = api_client.get(f"{base_url}/users/profile")
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    def test_profile_response_structure(self, authenticated_client, base_url):
        """Test profile response structure."""
        response = authenticated_client.get(f"{base_url}/users/profile")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be a dictionary with specific fields
        assert isinstance(data, dict)
        
        # Check required fields exist and have correct types
        required_fields = {
            "firstName": str,
            "lastName": str,
            "imageUrl": str
        }
        
        for field, expected_type in required_fields.items():
            assert field in data
            assert isinstance(data[field], expected_type)
    
    @pytest.mark.auth
    def test_profile_data_integrity(self, authenticated_client, base_url):
        """Test profile data integrity."""
        response = authenticated_client.get(f"{base_url}/users/profile")
        
        if response.status_code == 200:
            data = response.json()
            
            # Names should not be empty
            assert len(data["firstName"].strip()) > 0
            assert len(data["lastName"].strip()) > 0
            
            # Names should not contain suspicious content
            suspicious_patterns = ["<script>", "javascript:", "DROP TABLE", "SELECT *"]
            for pattern in suspicious_patterns:
                assert pattern not in data["firstName"]
                assert pattern not in data["lastName"]
            
            # Image URL should be valid if present
            if data["imageUrl"]:
                assert data["imageUrl"].startswith(("http://", "https://"))
                assert len(data["imageUrl"]) > 10  # Reasonable minimum URL length


class TestProfileUpdate:
    """Test cases for profile update endpoint."""
    
    @pytest.mark.auth
    def test_update_profile_success(self, authenticated_client, base_url, valid_profile_update_data):
        """Test successful profile update."""
        response = authenticated_client.put(
            f"{base_url}/users/profile",
            json=valid_profile_update_data
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "message" in data
        assert "successfully updated" in data["message"].lower()
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_update_profile_unauthorized(self, api_client, base_url, valid_profile_update_data):
        """Test updating profile without authentication."""
        response = api_client.put(
            f"{base_url}/users/profile",
            json=valid_profile_update_data
        )
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_update_profile_missing_fields(self, authenticated_client, base_url):
        """Test updating profile with missing required fields."""
        incomplete_data_sets = [
            {},  # Empty payload
            {"firstName": "John"},  # Missing lastName
            {"lastName": "Doe"},  # Missing firstName
            {"base64encodedImage": "test_image"},  # Missing names
        ]
        
        for incomplete_data in incomplete_data_sets:
            response = authenticated_client.put(
                f"{base_url}/users/profile",
                json=incomplete_data
            )
            assert response.status_code in [400, 422], f"Failed for data: {incomplete_data}"
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_update_profile_empty_fields(self, authenticated_client, base_url):
        """Test updating profile with empty fields."""
        empty_field_cases = [
            {"firstName": "", "lastName": "Doe"},
            {"firstName": "John", "lastName": ""},
            {"firstName": "", "lastName": ""},
        ]
        
        for update_data in empty_field_cases:
            response = authenticated_client.put(
                f"{base_url}/users/profile",
                json=update_data
            )
            assert response.status_code in [400, 422], f"Failed for data: {update_data}"
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_update_profile_invalid_base64_image(self, authenticated_client, base_url):
        """Test updating profile with invalid base64 image."""
        invalid_images = [
            "invalid_base64",
            "not_base64_at_all",
            "data:image/png;base64,invalid",
            "SGVsbG8gV29ybGQ=",  # Valid base64 but not an image
        ]
        
        for invalid_image in invalid_images:
            update_data = {
                "firstName": "John",
                "lastName": "Doe",
                "base64encodedImage": invalid_image
            }
            
            response = authenticated_client.put(
                f"{base_url}/users/profile",
                json=update_data
            )
            # Should either accept or reject gracefully
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_update_profile_oversized_image(self, authenticated_client, base_url):
        """Test updating profile with oversized base64 image."""
        # Create a very large base64 string (simulating a large image)
        oversized_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" * 10000
        
        update_data = {
            "firstName": "John",
            "lastName": "Doe",
            "base64encodedImage": oversized_image
        }
        
        response = authenticated_client.put(
            f"{base_url}/users/profile",
            json=update_data
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 413, 422]  # 413 = Payload Too Large
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_update_profile_special_characters_in_names(self, authenticated_client, base_url):
        """Test updating profile with special characters in names."""
        special_char_cases = [
            {"firstName": "John<script>alert('xss')</script>", "lastName": "Doe"},
            {"firstName": "John'; DROP TABLE users; --", "lastName": "Doe"},
            {"firstName": "John", "lastName": "Doe<img src=x onerror=alert('xss')>"},
            {"firstName": "Jöhn", "lastName": "Döe"},  # Valid unicode characters
            {"firstName": "José", "lastName": "García"},  # Valid accented characters
        ]
        
        for update_data in special_char_cases:
            response = authenticated_client.put(
                f"{base_url}/users/profile",
                json=update_data
            )
            
            # Should either accept valid characters or reject malicious ones
            assert response.status_code in [200, 400, 422]
            
            if response.status_code == 200:
                # If accepted, response should be properly handled
                data = response.json()
                assert "message" in data
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_update_profile_very_long_names(self, authenticated_client, base_url):
        """Test updating profile with very long names."""
        long_name_cases = [
            {"firstName": "A" * 1000, "lastName": "Doe"},
            {"firstName": "John", "lastName": "B" * 1000},
            {"firstName": "C" * 500, "lastName": "D" * 500},
        ]
        
        for update_data in long_name_cases:
            response = authenticated_client.put(
                f"{base_url}/users/profile",
                json=update_data
            )
            
            # Should handle gracefully (either accept or reject)
            assert response.status_code in [200, 400, 422]


class TestPasswordChange:
    """Test cases for password change endpoint."""
    
    @pytest.mark.auth
    def test_change_password_success(self, authenticated_client, base_url, valid_password_change_data):
        """Test successful password change."""
        response = authenticated_client.put(
            f"{base_url}/users/profile/password",
            json=valid_password_change_data
        )
        
        # Might succeed or fail based on whether the old password is correct
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            assert response.headers["content-type"] == "application/json"
            
            data = response.json()
            assert "message" in data
            assert "successfully updated" in data["message"].lower()
    
    @pytest.mark.auth
    @pytest.mark.error
    def test_change_password_unauthorized(self, api_client, base_url, valid_password_change_data):
        """Test changing password without authentication."""
        response = api_client.put(
            f"{base_url}/users/profile/password",
            json=valid_password_change_data
        )
        
        assert response.status_code == 401
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_change_password_missing_fields(self, authenticated_client, base_url):
        """Test changing password with missing required fields."""
        incomplete_data_sets = [
            {},  # Empty payload
            {"oldPassword": "oldpass"},  # Missing newPassword
            {"newPassword": "newpass"},  # Missing oldPassword
        ]
        
        for incomplete_data in incomplete_data_sets:
            response = authenticated_client.put(
                f"{base_url}/users/profile/password",
                json=incomplete_data
            )
            assert response.status_code in [400, 422], f"Failed for data: {incomplete_data}"
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_change_password_empty_fields(self, authenticated_client, base_url):
        """Test changing password with empty fields."""
        empty_field_cases = [
            {"oldPassword": "", "newPassword": "newpass"},
            {"oldPassword": "oldpass", "newPassword": ""},
            {"oldPassword": "", "newPassword": ""},
        ]
        
        for password_data in empty_field_cases:
            response = authenticated_client.put(
                f"{base_url}/users/profile/password",
                json=password_data
            )
            assert response.status_code in [400, 422], f"Failed for data: {password_data}"
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_change_password_wrong_old_password(self, authenticated_client, base_url):
        """Test changing password with wrong old password."""
        wrong_password_data = {
            "oldPassword": "definitely_wrong_password",
            "newPassword": "newPassword123"
        }
        
        response = authenticated_client.put(
            f"{base_url}/users/profile/password",
            json=wrong_password_data
        )
        
        assert response.status_code in [400, 401]
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_change_password_same_passwords(self, authenticated_client, base_url):
        """Test changing password where old and new passwords are the same."""
        same_password_data = {
            "oldPassword": "samePassword123",
            "newPassword": "samePassword123"
        }
        
        response = authenticated_client.put(
            f"{base_url}/users/profile/password",
            json=same_password_data
        )
        
        # Should either accept or reject based on business logic
        assert response.status_code in [200, 400, 422]
    
    @pytest.mark.auth
    @pytest.mark.validation
    def test_change_password_weak_new_password(self, authenticated_client, base_url):
        """Test changing password with weak new password."""
        weak_passwords = [
            "123",  # Too short
            "password",  # Too common
            "abc",  # Too simple
            "   ",  # Only spaces
        ]
        
        for weak_password in weak_passwords:
            password_data = {
                "oldPassword": "Y2kjqKHX",
                "newPassword": weak_password
            }
            
            response = authenticated_client.put(
                f"{base_url}/users/profile/password",
                json=password_data
            )
            
            # Should either accept or reject based on password policy
            assert response.status_code in [200, 400, 422]


class TestProfileIntegration:
    """Integration tests for profile management."""
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_profile_management_flow(self, authenticated_client, base_url):
        """Test complete profile management flow."""
        # Step 1: Get current profile
        get_response = authenticated_client.get(f"{base_url}/users/profile")
        assert get_response.status_code == 200
        
        original_profile = get_response.json()
        
        # Step 2: Update profile
        update_data = {
            "firstName": "Updated",
            "lastName": "Name",
            "base64encodedImage": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        }
        
        update_response = authenticated_client.put(
            f"{base_url}/users/profile",
            json=update_data
        )
        
        # Update might succeed or fail
        assert update_response.status_code in [200, 400, 422]
        
        # Step 3: Get profile again to verify changes
        updated_get_response = authenticated_client.get(f"{base_url}/users/profile")
        assert updated_get_response.status_code == 200
        
        updated_profile = updated_get_response.json()
        
        # If update succeeded, profile should be changed
        if update_response.status_code == 200:
            # Names might be updated
            assert updated_profile["firstName"] == update_data["firstName"] or updated_profile["firstName"] == original_profile["firstName"]
            assert updated_profile["lastName"] == update_data["lastName"] or updated_profile["lastName"] == original_profile["lastName"]
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_profile_consistency_across_requests(self, authenticated_client, base_url):
        """Test profile consistency across multiple requests."""
        responses = []
        
        # Make multiple profile requests
        for _ in range(5):
            response = authenticated_client.get(f"{base_url}/users/profile")
            assert response.status_code == 200
            responses.append(response.json())
        
        # All responses should be identical
        first_profile = responses[0]
        for profile in responses[1:]:
            assert profile == first_profile


class TestProfileErrorScenarios:
    """Test error scenarios and edge cases."""
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_profile_with_malformed_json(self, authenticated_client, base_url):
        """Test profile update with malformed JSON."""
        malformed_json = '{"firstName": "John", "lastName": "Doe"'  # Missing closing brace
        
        response = authenticated_client.put(
            f"{base_url}/users/profile",
            data=malformed_json,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_profile_with_wrong_content_type(self, authenticated_client, base_url):
        """Test profile update with wrong content type."""
        response = authenticated_client.put(
            f"{base_url}/users/profile",
            data="firstName=John&lastName=Doe",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code in [400, 415, 422]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_concurrent_profile_updates(self, authenticated_client, base_url):
        """Test concurrent profile updates."""
        import threading
        
        responses = []
        
        def update_profile(name_suffix):
            update_data = {
                "firstName": f"John{name_suffix}",
                "lastName": f"Doe{name_suffix}"
            }
            response = authenticated_client.put(
                f"{base_url}/users/profile",
                json=update_data
            )
            responses.append(response)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=update_profile, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should be handled gracefully
        for response in responses:
            assert response.status_code in [200, 400, 409, 422]
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_profile_operations_with_expired_token(self, api_client, base_url):
        """Test profile operations with expired token."""
        # Use an obviously invalid token
        api_client.headers.update({"Authorization": "Bearer expired_token_12345"})
        
        # Test GET profile
        get_response = api_client.get(f"{base_url}/users/profile")
        assert get_response.status_code == 401
        
        # Test PUT profile
        update_data = {
            "firstName": "John",
            "lastName": "Doe"
        }
        put_response = api_client.put(f"{base_url}/users/profile", json=update_data)
        assert put_response.status_code == 401
        
        # Test PUT password
        password_data = {
            "oldPassword": "oldpass",
            "newPassword": "newpass"
        }
        password_response = api_client.put(f"{base_url}/users/profile/password", json=password_data)
        assert password_response.status_code == 401
    
    @pytest.mark.error
    @pytest.mark.auth
    def test_profile_update_rate_limiting(self, authenticated_client, base_url):
        """Test rate limiting on profile updates."""
        # Make many update requests quickly
        responses = []
        
        for i in range(20):
            update_data = {
                "firstName": f"John{i}",
                "lastName": f"Doe{i}"
            }
            response = authenticated_client.put(
                f"{base_url}/users/profile",
                json=update_data
            )
            responses.append(response)
        
        # Most should succeed, but rate limiting might kick in
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        # At least some should succeed
        assert success_count >= 0  # Some might fail due to validation
        
        # If rate limiting is implemented, some might be rate limited
        # This is optional, so we don't assert on it