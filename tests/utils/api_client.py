"""
API Client utility for making HTTP requests.

This module provides a centralized HTTP client with authentication,
retry logic, and response validation capabilities.
"""

import json
import time
from typing import Dict, Any, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

from tests.config import api_config, test_config

logger = logging.getLogger(__name__)


class APIClient:
    """HTTP client for API testing with authentication and retry logic."""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or api_config.BASE_URL
        self.timeout = timeout or api_config.TIMEOUT
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=api_config.MAX_RETRIES,
            backoff_factor=api_config.RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def set_auth_token(self, token: str) -> None:
        """Set authentication token for requests."""
        self.access_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def clear_auth_token(self) -> None:
        """Clear authentication token."""
        self.access_token = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
    
    def _make_request(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with error handling and logging.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Request URL
            data: Request body data
            params: Query parameters
            headers: Additional headers
            files: Files to upload
            **kwargs: Additional request arguments
            
        Returns:
            Response object
        """
        # Prepare headers
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        
        # Prepare request arguments
        request_kwargs = {
            "timeout": self.timeout,
            "headers": request_headers,
            **kwargs
        }
        
        if params:
            request_kwargs["params"] = params
        
        if files:
            # Remove Content-Type header for file uploads
            if "Content-Type" in request_headers:
                del request_headers["Content-Type"]
            request_kwargs["files"] = files
        elif data:
            request_kwargs["json"] = data
        
        # Log request
        logger.info(f"Making {method} request to {url}")
        if data:
            logger.debug(f"Request data: {json.dumps(data, indent=2)}")
        if params:
            logger.debug(f"Request params: {params}")
        
        # Make request
        try:
            response = self.session.request(method, url, **request_kwargs)
            
            # Log response
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            try:
                response_json = response.json()
                logger.debug(f"Response body: {json.dumps(response_json, indent=2)}")
            except (json.JSONDecodeError, ValueError):
                logger.debug(f"Response body (non-JSON): {response.text}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """Make GET request."""
        return self._make_request("GET", url, params=params, headers=headers, **kwargs)
    
    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """Make POST request."""
        return self._make_request(
            "POST", url, data=data, params=params, headers=headers, files=files, **kwargs
        )
    
    def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """Make PUT request."""
        return self._make_request("PUT", url, data=data, params=params, headers=headers, **kwargs)
    
    def delete(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """Make DELETE request."""
        return self._make_request("DELETE", url, params=params, headers=headers, **kwargs)
    
    def patch(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """Make PATCH request."""
        return self._make_request("PATCH", url, data=data, params=params, headers=headers, **kwargs)


class AuthenticatedAPIClient(APIClient):
    """API client with automatic authentication."""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        """Initialize authenticated API client."""
        super().__init__(base_url, timeout)
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with the API using test credentials."""
        auth_data = {
            "email": test_config.TEST_USER_EMAIL,
            "password": test_config.TEST_USER_PASSWORD
        }
        
        try:
            response = self.post(api_config.auth_endpoints["signin"], data=auth_data)
            if response.status_code == 200:
                token_data = response.json()
                self.set_auth_token(token_data["accessToken"])
                logger.info("Successfully authenticated with API")
            else:
                logger.warning(f"Authentication failed with status {response.status_code}")
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise


# Global client instances
api_client = APIClient()
authenticated_client = AuthenticatedAPIClient()