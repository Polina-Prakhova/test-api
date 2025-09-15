"""
Configuration module for API tests.

This module contains all configuration settings, environment variables,
and constants used across the test suite.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class APIConfig:
    """API configuration settings."""
    
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    TIMEOUT: int = int(os.getenv("TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "1"))
    
    @property
    def api_base_url(self) -> str:
        """Get the complete API base URL."""
        return f"{self.BASE_URL}"
    
    @property
    def auth_endpoints(self) -> dict:
        """Get authentication endpoints."""
        return {
            "signup": f"{self.api_base_url}/auth/signup",
            "signin": f"{self.api_base_url}/auth/signin",
            "validate": f"{self.api_base_url}/auth/validate"
        }
    
    @property
    def dishes_endpoints(self) -> dict:
        """Get dishes endpoints."""
        return {
            "popular": f"{self.api_base_url}/dishes/popular",
            "list": f"{self.api_base_url}/dishes",
            "detail": f"{self.api_base_url}/dishes/{{id}}"
        }
    
    @property
    def locations_endpoints(self) -> dict:
        """Get locations endpoints."""
        return {
            "list": f"{self.api_base_url}/locations",
            "select_options": f"{self.api_base_url}/locations/select-options",
            "speciality_dishes": f"{self.api_base_url}/locations/{{id}}/speciality-dishes",
            "feedbacks": f"{self.api_base_url}/locations/{{id}}/feedbacks"
        }
    
    @property
    def bookings_endpoints(self) -> dict:
        """Get bookings endpoints."""
        return {
            "tables": f"{self.api_base_url}/bookings/tables",
            "client": f"{self.api_base_url}/bookings/client",
            "waiter": f"{self.api_base_url}/bookings/waiter"
        }
    
    @property
    def reservations_endpoints(self) -> dict:
        """Get reservations endpoints."""
        return {
            "list": f"{self.api_base_url}/reservations",
            "detail": f"{self.api_base_url}/reservations/{{id}}",
            "available_dishes": f"{self.api_base_url}/reservations/{{reservationId}}/available-dishes",
            "order_dish": f"{self.api_base_url}/reservations/{{reservationId}}/order/{{dishId}}"
        }
    
    @property
    def cart_endpoints(self) -> dict:
        """Get cart endpoints."""
        return {
            "cart": f"{self.api_base_url}/cart"
        }
    
    @property
    def profile_endpoints(self) -> dict:
        """Get profile endpoints."""
        return {
            "profile": f"{self.api_base_url}/users/profile",
            "password": f"{self.api_base_url}/users/profile/password"
        }
    
    @property
    def feedbacks_endpoints(self) -> dict:
        """Get feedbacks endpoints."""
        return {
            "create": f"{self.api_base_url}/feedbacks/",
            "visitor": f"{self.api_base_url}/feedbacks/visitor"
        }
    
    @property
    def reports_endpoints(self) -> dict:
        """Get reports endpoints."""
        return {
            "reports": f"{self.api_base_url}/reports"
        }
    
    @property
    def health_endpoints(self) -> dict:
        """Get health check endpoints."""
        return {
            "health": f"{self.api_base_url}/health",
            "root": f"{self.api_base_url}/"
        }


class TestConfig:
    """Test configuration settings."""
    
    # Test user credentials
    TEST_USER_EMAIL: str = os.getenv("TEST_USER_EMAIL", "jhon_smith@example.com")
    TEST_USER_PASSWORD: str = os.getenv("TEST_USER_PASSWORD", "Y2kjqKHX")
    TEST_USER_FIRST_NAME: str = os.getenv("TEST_USER_FIRST_NAME", "John")
    TEST_USER_LAST_NAME: str = os.getenv("TEST_USER_LAST_NAME", "Smith")
    
    # Test data
    EXISTING_USER_EMAIL: str = "existing@example.com"
    
    # Test IDs (these would typically come from test data setup)
    TEST_LOCATION_ID: str = "672846d5c951184d705b65d7"
    TEST_DISH_ID: str = "322846d5c951184d705b65d2"
    TEST_RESERVATION_ID: str = "672846d5c951184d705b65d8"
    TEST_TABLE_NUMBER: str = "1"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "tests/logs/test.log")


# Global configuration instances
api_config = APIConfig()
test_config = TestConfig()