"""
Pytest configuration and fixtures.

This module contains pytest fixtures and configuration used across
all test modules in the test suite.
"""

import pytest
import logging
import os
from typing import Dict, Any, Generator

from tests.config import api_config, test_config
from tests.utils.api_client import APIClient, AuthenticatedAPIClient
from tests.utils.test_data import TestDataGenerator


# Configure logging
logging.basicConfig(
    level=getattr(logging, test_config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(test_config.LOG_FILE, mode='a') if test_config.LOG_FILE else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def api_client() -> APIClient:
    """Provide an unauthenticated API client."""
    return APIClient()


@pytest.fixture(scope="session")
def authenticated_client() -> AuthenticatedAPIClient:
    """Provide an authenticated API client."""
    try:
        return AuthenticatedAPIClient()
    except Exception as e:
        logger.warning(f"Could not create authenticated client: {e}")
        # Return regular client if authentication fails
        return APIClient()


@pytest.fixture(scope="function")
def test_user_data() -> Dict[str, str]:
    """Provide test user data for registration."""
    return TestDataGenerator.generate_user_data()


@pytest.fixture(scope="function")
def valid_signin_data() -> Dict[str, str]:
    """Provide valid sign-in data."""
    return {
        "email": test_config.TEST_USER_EMAIL,
        "password": test_config.TEST_USER_PASSWORD
    }


@pytest.fixture(scope="function")
def invalid_signin_data() -> Dict[str, str]:
    """Provide invalid sign-in data."""
    return TestDataGenerator.generate_signin_data(
        email="invalid@example.com",
        password="wrongpassword"
    )


@pytest.fixture(scope="function")
def reservation_data() -> Dict[str, str]:
    """Provide test reservation data."""
    return TestDataGenerator.generate_reservation_data(
        location_id=test_config.TEST_LOCATION_ID
    )


@pytest.fixture(scope="function")
def waiter_reservation_data() -> Dict[str, str]:
    """Provide test waiter reservation data."""
    return TestDataGenerator.generate_waiter_reservation_data(
        location_id=test_config.TEST_LOCATION_ID
    )


@pytest.fixture(scope="function")
def feedback_data() -> Dict[str, str]:
    """Provide test feedback data."""
    return TestDataGenerator.generate_feedback_data(
        reservation_id=test_config.TEST_RESERVATION_ID
    )


@pytest.fixture(scope="function")
def profile_update_data() -> Dict[str, str]:
    """Provide test profile update data."""
    return TestDataGenerator.generate_profile_update_data()


@pytest.fixture(scope="function")
def password_change_data() -> Dict[str, str]:
    """Provide test password change data."""
    return TestDataGenerator.generate_password_change_data(
        old_password=test_config.TEST_USER_PASSWORD
    )


@pytest.fixture(scope="function")
def preorder_data() -> Dict[str, Any]:
    """Provide test preorder data."""
    return TestDataGenerator.generate_preorder_data(
        reservation_id=test_config.TEST_RESERVATION_ID
    )


@pytest.fixture(scope="function")
def invalid_data_variants() -> Dict[str, Dict[str, Any]]:
    """Provide various invalid data variants for negative testing."""
    return TestDataGenerator.generate_invalid_data_variants()


@pytest.fixture(scope="session")
def endpoints() -> Dict[str, Dict[str, str]]:
    """Provide all API endpoints."""
    return {
        "auth": api_config.auth_endpoints,
        "dishes": api_config.dishes_endpoints,
        "locations": api_config.locations_endpoints,
        "bookings": api_config.bookings_endpoints,
        "reservations": api_config.reservations_endpoints,
        "cart": api_config.cart_endpoints,
        "profile": api_config.profile_endpoints,
        "feedbacks": api_config.feedbacks_endpoints,
        "reports": api_config.reports_endpoints,
        "health": api_config.health_endpoints
    }


@pytest.fixture(autouse=True)
def log_test_info(request):
    """Automatically log test information."""
    logger.info(f"Starting test: {request.node.name}")
    yield
    logger.info(f"Finished test: {request.node.name}")


@pytest.fixture(scope="function")
def cleanup_test_user(api_client: APIClient):
    """Cleanup fixture to remove test users after tests."""
    created_users = []
    
    def register_user_for_cleanup(email: str):
        """Register a user email for cleanup."""
        created_users.append(email)
    
    yield register_user_for_cleanup
    
    # Cleanup logic would go here if the API supported user deletion
    # For now, we just log the users that were created
    if created_users:
        logger.info(f"Test users created (manual cleanup may be required): {created_users}")


@pytest.fixture(scope="function")
def auth_token(authenticated_client: AuthenticatedAPIClient) -> str:
    """Provide authentication token."""
    return authenticated_client.access_token


@pytest.fixture(scope="function")
def temp_reservation_id(authenticated_client: AuthenticatedAPIClient, reservation_data: Dict[str, str]) -> Generator[str, None, None]:
    """Create a temporary reservation and provide its ID."""
    # Create reservation
    response = authenticated_client.post(
        api_config.bookings_endpoints["client"],
        data=reservation_data
    )
    
    if response.status_code in [200, 201]:
        reservation_id = response.json().get("id")
        yield reservation_id
        
        # Cleanup: Delete reservation
        try:
            delete_url = api_config.reservations_endpoints["detail"].format(id=reservation_id)
            authenticated_client.delete(delete_url)
            logger.info(f"Cleaned up reservation: {reservation_id}")
        except Exception as e:
            logger.warning(f"Failed to cleanup reservation {reservation_id}: {e}")
    else:
        logger.warning(f"Failed to create temporary reservation: {response.status_code}")
        yield None


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests."""
    logger.info("Setting up test environment")
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(test_config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create reports directory
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    yield
    
    logger.info("Test environment cleanup completed")


@pytest.fixture(scope="function")
def mock_location_id() -> str:
    """Provide a mock location ID for testing."""
    return test_config.TEST_LOCATION_ID


@pytest.fixture(scope="function")
def mock_dish_id() -> str:
    """Provide a mock dish ID for testing."""
    return test_config.TEST_DISH_ID


@pytest.fixture(scope="function")
def mock_reservation_id() -> str:
    """Provide a mock reservation ID for testing."""
    return test_config.TEST_RESERVATION_ID


# Pytest hooks
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add smoke marker to tests with 'smoke' in name
        if "smoke" in item.name.lower():
            item.add_marker(pytest.mark.smoke)
        
        # Add negative marker to tests with 'invalid' or 'error' in name
        if any(keyword in item.name.lower() for keyword in ["invalid", "error", "fail", "negative"]):
            item.add_marker(pytest.mark.negative)
        else:
            item.add_marker(pytest.mark.positive)
        
        # Add module-specific markers
        if "auth" in item.module.__name__:
            item.add_marker(pytest.mark.auth)
        elif "dish" in item.module.__name__:
            item.add_marker(pytest.mark.dishes)
        elif "location" in item.module.__name__:
            item.add_marker(pytest.mark.locations)
        elif "booking" in item.module.__name__:
            item.add_marker(pytest.mark.bookings)
        elif "reservation" in item.module.__name__:
            item.add_marker(pytest.mark.reservations)
        elif "cart" in item.module.__name__:
            item.add_marker(pytest.mark.cart)
        elif "profile" in item.module.__name__:
            item.add_marker(pytest.mark.profile)
        elif "feedback" in item.module.__name__:
            item.add_marker(pytest.mark.feedbacks)
        elif "report" in item.module.__name__:
            item.add_marker(pytest.mark.reporting)