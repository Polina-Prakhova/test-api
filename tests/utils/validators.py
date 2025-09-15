"""
Response validation utilities.

This module provides functions to validate API responses against
expected schemas and business rules.
"""

import json
from typing import Dict, Any, List, Optional, Union
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)


class ResponseValidator:
    """Validator for API responses."""
    
    # Common schema components
    COMMON_SCHEMAS = {
        "object_id": {
            "type": "string",
            "pattern": "^[a-f0-9]{24}$"
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "date": {
            "type": "string",
            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
        },
        "time": {
            "type": "string",
            "pattern": "^\\d{2}:\\d{2}$"
        },
        "price": {
            "type": "string",
            "pattern": "^\\$\\d+(\\.\\d{2})?$"
        },
        "rating": {
            "type": "string",
            "pattern": "^[1-5]$"
        }
    }
    
    # Response schemas
    SCHEMAS = {
        "signup_success": {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        },
        
        "signup_fail": {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        },
        
        "signin_response": {
            "type": "object",
            "properties": {
                "accessToken": {"type": "string"},
                "username": {"type": "string"},
                "role": {"type": "string", "enum": ["CLIENT", "ADMIN", "WAITER"]}
            },
            "required": ["accessToken", "username", "role"]
        },
        
        "dish_response": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "price": COMMON_SCHEMAS["price"],
                "weight": {"type": "string"},
                "previewImageUrl": {"type": "string", "format": "uri"},
                "state": {"type": "string"}
            },
            "required": ["name", "price"]
        },
        
        "dish_extended_response": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "price": COMMON_SCHEMAS["price"],
                "weight": {"type": "string"},
                "imageUrl": {"type": "string", "format": "uri"},
                "calories": {"type": "string"},
                "proteins": {"type": "string"},
                "fats": {"type": "string"},
                "carbohydrates": {"type": "string"},
                "vitamins": {"type": "string"},
                "dishType": {"type": "string", "enum": ["APPETIZER", "MAIN_COURSE", "DESSERT"]},
                "state": {"type": "string"}
            },
            "required": ["id", "name", "price"]
        },
        
        "location_response": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "address": {"type": "string"},
                "description": {"type": "string"},
                "totalCapacity": {"type": "string"},
                "averageOccupancy": {"type": "string"},
                "imageUrl": {"type": "string", "format": "uri"},
                "rating": {"type": "string"}
            },
            "required": ["id", "address"]
        },
        
        "location_brief": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "address": {"type": "string"}
            },
            "required": ["id", "address"]
        },
        
        "table_response": {
            "type": "object",
            "properties": {
                "locationId": {"type": "string"},
                "locationAddress": {"type": "string"},
                "tableNumber": {"type": "string"},
                "capacity": {"type": "string"},
                "availableSlots": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["locationId", "tableNumber", "capacity"]
        },
        
        "reservation_response": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "status": {"type": "string"},
                "locationAddress": {"type": "string"},
                "date": COMMON_SCHEMAS["date"],
                "timeSlot": {"type": "string"},
                "preOrder": {"type": "string"},
                "guestsNumber": {"type": "string"},
                "feedbackId": {"type": "string"},
                "userInfo": {"type": "string"}
            },
            "required": ["id", "status", "date"]
        },
        
        "feedback_response": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "rate": {"type": "string"},
                "comment": {"type": "string"},
                "userName": {"type": "string"},
                "userAvatarUrl": {"type": "string", "format": "uri"},
                "date": {"type": "string"},
                "type": {"type": "string", "enum": ["CUISINE_EXPERIENCE", "SERVICE_QUALITY"]},
                "locationId": {"type": "string"}
            },
            "required": ["id", "rate", "comment"]
        },
        
        "profile_response": {
            "type": "object",
            "properties": {
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "imageUrl": {"type": "string", "format": "uri"}
            },
            "required": ["firstName", "lastName"]
        },
        
        "cart_response": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "reservationId": {"type": "string"},
                            "address": {"type": "string"},
                            "date": COMMON_SCHEMAS["date"],
                            "timeSlot": {"type": "string"},
                            "state": {"type": "string", "enum": ["SUBMITTED", "IN_PROGRESS", "CANCELLED"]},
                            "dishItems": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "dishId": {"type": "string"},
                                        "dishName": {"type": "string"},
                                        "dishPrice": COMMON_SCHEMAS["price"],
                                        "dishQuantity": {"type": "integer"},
                                        "dishImageUrl": {"type": "string", "format": "uri"}
                                    },
                                    "required": ["dishId", "dishName", "dishPrice", "dishQuantity"]
                                }
                            }
                        },
                        "required": ["id", "reservationId", "state"]
                    }
                }
            },
            "required": ["content"]
        },
        
        "error_response": {
            "type": "object",
            "properties": {
                "detail": {"type": "string"}
            },
            "required": ["detail"]
        },
        
        "health_response": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["ok"]}
            },
            "required": ["status"]
        },
        
        "root_response": {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        }
    }
    
    @classmethod
    def validate_response(
        self,
        response_data: Dict[str, Any],
        schema_name: str,
        strict: bool = True
    ) -> bool:
        """
        Validate response data against a schema.
        
        Args:
            response_data: Response data to validate
            schema_name: Name of the schema to use
            strict: Whether to raise exception on validation failure
            
        Returns:
            True if validation passes
            
        Raises:
            ValidationError: If validation fails and strict=True
        """
        if schema_name not in self.SCHEMAS:
            logger.warning(f"Schema '{schema_name}' not found")
            return False
        
        schema = self.SCHEMAS[schema_name]
        
        try:
            validate(instance=response_data, schema=schema)
            logger.debug(f"Response validation passed for schema '{schema_name}'")
            return True
        except ValidationError as e:
            logger.error(f"Response validation failed for schema '{schema_name}': {str(e)}")
            if strict:
                raise
            return False
    
    @classmethod
    def validate_list_response(
        self,
        response_data: List[Dict[str, Any]],
        item_schema_name: str,
        strict: bool = True
    ) -> bool:
        """
        Validate list response where each item should match a schema.
        
        Args:
            response_data: List of response items
            item_schema_name: Schema name for individual items
            strict: Whether to raise exception on validation failure
            
        Returns:
            True if all items pass validation
        """
        if not isinstance(response_data, list):
            logger.error("Expected list response")
            if strict:
                raise ValidationError("Expected list response")
            return False
        
        for i, item in enumerate(response_data):
            try:
                self.validate_response(item, item_schema_name, strict=True)
            except ValidationError as e:
                logger.error(f"Validation failed for item {i}: {str(e)}")
                if strict:
                    raise
                return False
        
        return True
    
    @classmethod
    def validate_pagination_response(
        self,
        response_data: Dict[str, Any],
        content_schema_name: str,
        strict: bool = True
    ) -> bool:
        """
        Validate paginated response structure.
        
        Args:
            response_data: Paginated response data
            content_schema_name: Schema name for content items
            strict: Whether to raise exception on validation failure
            
        Returns:
            True if validation passes
        """
        pagination_schema = {
            "type": "object",
            "properties": {
                "content": {
                    "type": "array",
                    "items": self.SCHEMAS.get(content_schema_name, {})
                },
                "totalPages": {"type": "integer"},
                "totalElements": {"type": "integer"},
                "size": {"type": "integer"},
                "number": {"type": "integer"},
                "first": {"type": "boolean"},
                "last": {"type": "boolean"},
                "numberOfElements": {"type": "integer"},
                "empty": {"type": "boolean"}
            },
            "required": ["content"]
        }
        
        try:
            validate(instance=response_data, schema=pagination_schema)
            logger.debug("Pagination response validation passed")
            return True
        except ValidationError as e:
            logger.error(f"Pagination response validation failed: {str(e)}")
            if strict:
                raise
            return False
    
    @classmethod
    def validate_jwt_token(self, token: str) -> bool:
        """
        Validate JWT token format.
        
        Args:
            token: JWT token string
            
        Returns:
            True if token format is valid
        """
        if not token or not isinstance(token, str):
            return False
        
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        # Each part should be base64-encoded (allowing URL-safe base64)
        import re
        base64_pattern = re.compile(r'^[A-Za-z0-9_-]+$')
        
        for part in parts:
            if not base64_pattern.match(part):
                return False
        
        return True
    
    @classmethod
    def validate_business_rules(
        self,
        response_data: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> List[str]:
        """
        Validate business rules against response data.
        
        Args:
            response_data: Response data to validate
            rules: Dictionary of business rules to check
            
        Returns:
            List of validation errors (empty if all rules pass)
        """
        errors = []
        
        for rule_name, rule_config in rules.items():
            field = rule_config.get('field')
            expected_value = rule_config.get('value')
            condition = rule_config.get('condition', 'equals')
            
            if field not in response_data:
                errors.append(f"Missing required field: {field}")
                continue
            
            actual_value = response_data[field]
            
            if condition == 'equals' and actual_value != expected_value:
                errors.append(f"{rule_name}: Expected {expected_value}, got {actual_value}")
            elif condition == 'not_equals' and actual_value == expected_value:
                errors.append(f"{rule_name}: Expected not {expected_value}, got {actual_value}")
            elif condition == 'contains' and expected_value not in str(actual_value):
                errors.append(f"{rule_name}: Expected '{actual_value}' to contain '{expected_value}'")
            elif condition == 'not_empty' and not actual_value:
                errors.append(f"{rule_name}: Field '{field}' should not be empty")
            elif condition == 'positive_number' and (not isinstance(actual_value, (int, float)) or actual_value <= 0):
                errors.append(f"{rule_name}: Field '{field}' should be a positive number")
        
        return errors


# Global validator instance
validator = ResponseValidator()