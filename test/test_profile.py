"""
Tests for profile endpoints.
"""
import pytest


class TestProfileEndpoints:
    """Test class for profile endpoints."""

    def test_get_profile(self, api_client, base_url, auth_headers):
        """Test getting user profile."""
        response = api_client.get(
            f"{base_url}/users/profile",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "firstName" in data
        assert "lastName" in data
        assert "imageUrl" in data
        
        # Validate data types
        assert isinstance(data["firstName"], str)
        assert isinstance(data["lastName"], str)
        assert isinstance(data["imageUrl"], str)

    def test_get_profile_unauthorized(self, api_client, base_url):
        """Test getting profile without authentication."""
        response = api_client.get(f"{base_url}/users/profile")
        
        assert response.status_code == 401

    def test_update_profile_success(self, api_client, base_url, auth_headers, sample_profile_update_data):
        """Test successful profile update."""
        response = api_client.put(
            f"{base_url}/users/profile",
            json=sample_profile_update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "Profile has been successfully updated"

    def test_update_profile_unauthorized(self, api_client, base_url, sample_profile_update_data):
        """Test profile update without authentication."""
        response = api_client.put(
            f"{base_url}/users/profile",
            json=sample_profile_update_data
        )
        
        assert response.status_code == 401

    def test_update_profile_partial_data(self, api_client, base_url, auth_headers):
        """Test profile update with partial data."""
        partial_data = {
            "firstName": "UpdatedFirstName"
            # Missing lastName and base64encodedImage
        }
        
        response = api_client.put(
            f"{base_url}/users/profile",
            json=partial_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400, 422]

    def test_update_profile_empty_data(self, api_client, base_url, auth_headers):
        """Test profile update with empty data."""
        empty_data = {}
        
        response = api_client.put(
            f"{base_url}/users/profile",
            json=empty_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400, 422]

    def test_update_profile_invalid_image(self, api_client, base_url, auth_headers):
        """Test profile update with invalid base64 image."""
        invalid_image_data = {
            "firstName": "John",
            "lastName": "Doe",
            "base64encodedImage": "invalid-base64-data"
        }
        
        response = api_client.put(
            f"{base_url}/users/profile",
            json=invalid_image_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400, 422]

    def test_change_password_success(self, api_client, base_url, auth_headers, sample_password_change_data):
        """Test successful password change."""
        response = api_client.put(
            f"{base_url}/users/profile/password",
            json=sample_password_change_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "Password has been successfully updated"

    def test_change_password_unauthorized(self, api_client, base_url, sample_password_change_data):
        """Test password change without authentication."""
        response = api_client.put(
            f"{base_url}/users/profile/password",
            json=sample_password_change_data
        )
        
        assert response.status_code == 401

    def test_change_password_wrong_old_password(self, api_client, base_url, auth_headers):
        """Test password change with wrong old password."""
        wrong_password_data = {
            "oldPassword": "WrongOldPassword",
            "newPassword": "NewPassword123"
        }
        
        response = api_client.put(
            f"{base_url}/users/profile/password",
            json=wrong_password_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 401, 403]

    def test_change_password_missing_fields(self, api_client, base_url, auth_headers):
        """Test password change with missing fields."""
        incomplete_data = {
            "oldPassword": "Y2kjqKHX"
            # Missing newPassword
        }
        
        response = api_client.put(
            f"{base_url}/users/profile/password",
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]

    def test_change_password_empty_passwords(self, api_client, base_url, auth_headers):
        """Test password change with empty passwords."""
        empty_password_data = {
            "oldPassword": "",
            "newPassword": ""
        }
        
        response = api_client.put(
            f"{base_url}/users/profile/password",
            json=empty_password_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]

    def test_change_password_same_passwords(self, api_client, base_url, auth_headers):
        """Test password change with same old and new passwords."""
        same_password_data = {
            "oldPassword": "Y2kjqKHX",
            "newPassword": "Y2kjqKHX"
        }
        
        response = api_client.put(
            f"{base_url}/users/profile/password",
            json=same_password_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400]  # May be allowed or rejected

    def test_profile_response_structure(self, api_client, base_url, auth_headers):
        """Test profile response structure and data validation."""
        response = api_client.get(
            f"{base_url}/users/profile",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert isinstance(data, dict)
        required_fields = ["firstName", "lastName", "imageUrl"]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
            assert data[field] is not None, f"Field {field} is None"

    def test_profile_image_url_format(self, api_client, base_url, auth_headers):
        """Test that profile image URL is in correct format."""
        response = api_client.get(
            f"{base_url}/users/profile",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        image_url = data["imageUrl"]
        if image_url:  # If image URL is provided
            assert image_url.startswith("http"), f"Invalid image URL: {image_url}"

    def test_profile_name_validation(self, api_client, base_url, auth_headers):
        """Test profile name field validation."""
        response = api_client.get(
            f"{base_url}/users/profile",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        first_name = data["firstName"]
        last_name = data["lastName"]
        
        # Names should not be empty
        assert len(first_name.strip()) > 0, "First name is empty"
        assert len(last_name.strip()) > 0, "Last name is empty"

    def test_update_profile_name_length_validation(self, api_client, base_url, auth_headers):
        """Test profile update with various name lengths."""
        test_cases = [
            {"firstName": "A", "lastName": "B"},  # Very short names
            {"firstName": "A" * 50, "lastName": "B" * 50},  # Long names
            {"firstName": "", "lastName": ""},  # Empty names
            {"firstName": "   ", "lastName": "   "},  # Whitespace names
        ]
        
        for test_data in test_cases:
            response = api_client.put(
                f"{base_url}/users/profile",
                json=test_data,
                headers=auth_headers
            )
            
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]

    def test_update_profile_special_characters(self, api_client, base_url, auth_headers):
        """Test profile update with special characters in names."""
        special_char_data = {
            "firstName": "John-Paul",
            "lastName": "O'Connor"
        }
        
        response = api_client.put(
            f"{base_url}/users/profile",
            json=special_char_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400, 422]

    def test_password_strength_validation(self, api_client, base_url, auth_headers):
        """Test password change with various password strengths."""
        weak_passwords = [
            "123",  # Too short
            "password",  # Common password
            "12345678",  # Only numbers
            "abcdefgh",  # Only letters
        ]
        
        for weak_password in weak_passwords:
            password_data = {
                "oldPassword": "Y2kjqKHX",
                "newPassword": weak_password
            }
            
            response = api_client.put(
                f"{base_url}/users/profile/password",
                json=password_data,
                headers=auth_headers
            )
            
            # Should either accept or reject based on password policy
            assert response.status_code in [200, 400, 422]

    def test_profile_xss_protection(self, api_client, base_url, auth_headers):
        """Test profile update with XSS attempts."""
        xss_data = {
            "firstName": "<script>alert('xss')</script>",
            "lastName": "<img src=x onerror=alert('xss')>"
        }
        
        response = api_client.put(
            f"{base_url}/users/profile",
            json=xss_data,
            headers=auth_headers
        )
        
        # Should handle gracefully, not execute script
        assert response.status_code in [200, 400, 422]