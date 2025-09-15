"""
Test data generation utilities.

This module provides functions to generate test data for API testing,
including user data, reservation data, and other test entities.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List
from faker import Faker

fake = Faker()


class TestDataGenerator:
    """Generator for test data used in API tests."""
    
    @staticmethod
    def generate_user_data(
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        password: str = None
    ) -> Dict[str, str]:
        """
        Generate user registration data.
        
        Args:
            first_name: User's first name (generated if not provided)
            last_name: User's last name (generated if not provided)
            email: User's email (generated if not provided)
            password: User's password (generated if not provided)
            
        Returns:
            Dictionary with user data
        """
        return {
            "firstName": first_name or fake.first_name(),
            "lastName": last_name or fake.last_name(),
            "email": email or fake.email(),
            "password": password or TestDataGenerator.generate_password()
        }
    
    @staticmethod
    def generate_signin_data(email: str = None, password: str = None) -> Dict[str, str]:
        """
        Generate sign-in data.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dictionary with sign-in data
        """
        return {
            "email": email or fake.email(),
            "password": password or TestDataGenerator.generate_password()
        }
    
    @staticmethod
    def generate_password(length: int = 8) -> str:
        """
        Generate a random password.
        
        Args:
            length: Password length
            
        Returns:
            Generated password
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def generate_reservation_data(
        location_id: str = None,
        table_number: str = None,
        date: str = None,
        guests_number: str = None,
        time_from: str = None,
        time_to: str = None
    ) -> Dict[str, str]:
        """
        Generate reservation data.
        
        Args:
            location_id: Location ID
            table_number: Table number
            date: Reservation date
            guests_number: Number of guests
            time_from: Start time
            time_to: End time
            
        Returns:
            Dictionary with reservation data
        """
        # Generate future date if not provided
        if not date:
            future_date = fake.date_between(start_date='+1d', end_date='+30d')
            date = future_date.strftime('%Y-%m-%d')
        
        # Generate time slots if not provided
        if not time_from:
            hour = random.randint(10, 20)
            minute = random.choice([0, 15, 30, 45])
            time_from = f"{hour:02d}:{minute:02d}"
        
        if not time_to:
            # Add 1-3 hours to start time
            start_hour, start_minute = map(int, time_from.split(':'))
            duration_hours = random.randint(1, 3)
            end_hour = start_hour + duration_hours
            time_to = f"{end_hour:02d}:{start_minute:02d}"
        
        return {
            "locationId": location_id or TestDataGenerator.generate_object_id(),
            "tableNumber": table_number or str(random.randint(1, 20)),
            "date": date,
            "guestsNumber": guests_number or str(random.randint(1, 8)),
            "timeFrom": time_from,
            "timeTo": time_to
        }
    
    @staticmethod
    def generate_waiter_reservation_data(
        client_type: str = "CUSTOMER",
        customer_name: str = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        Generate waiter reservation data.
        
        Args:
            client_type: Type of client
            customer_name: Customer name
            **kwargs: Additional reservation data
            
        Returns:
            Dictionary with waiter reservation data
        """
        data = TestDataGenerator.generate_reservation_data(**kwargs)
        data.update({
            "clientType": client_type,
            "customerName": customer_name or fake.name()
        })
        return data
    
    @staticmethod
    def generate_feedback_data(
        reservation_id: str = None,
        service_rating: str = None,
        service_comment: str = None,
        cuisine_rating: str = None,
        cuisine_comment: str = None
    ) -> Dict[str, str]:
        """
        Generate feedback data.
        
        Args:
            reservation_id: Reservation ID
            service_rating: Service rating (1-5)
            service_comment: Service comment
            cuisine_rating: Cuisine rating (1-5)
            cuisine_comment: Cuisine comment
            
        Returns:
            Dictionary with feedback data
        """
        return {
            "reservationId": reservation_id or TestDataGenerator.generate_object_id(),
            "serviceRating": service_rating or str(random.randint(1, 5)),
            "serviceComment": service_comment or fake.text(max_nb_chars=200),
            "cuisineRating": cuisine_rating or str(random.randint(1, 5)),
            "cuisineComment": cuisine_comment or fake.text(max_nb_chars=200)
        }
    
    @staticmethod
    def generate_profile_update_data(
        first_name: str = None,
        last_name: str = None,
        base64_image: str = None
    ) -> Dict[str, str]:
        """
        Generate profile update data.
        
        Args:
            first_name: First name
            last_name: Last name
            base64_image: Base64 encoded image
            
        Returns:
            Dictionary with profile update data
        """
        return {
            "firstName": first_name or fake.first_name(),
            "lastName": last_name or fake.last_name(),
            "base64encodedImage": base64_image or TestDataGenerator.generate_base64_image()
        }
    
    @staticmethod
    def generate_password_change_data(
        old_password: str = None,
        new_password: str = None
    ) -> Dict[str, str]:
        """
        Generate password change data.
        
        Args:
            old_password: Current password
            new_password: New password
            
        Returns:
            Dictionary with password change data
        """
        return {
            "oldPassword": old_password or TestDataGenerator.generate_password(),
            "newPassword": new_password or TestDataGenerator.generate_password()
        }
    
    @staticmethod
    def generate_object_id() -> str:
        """Generate a MongoDB-like object ID."""
        return ''.join(random.choice('0123456789abcdef') for _ in range(24))
    
    @staticmethod
    def generate_base64_image() -> str:
        """Generate a sample base64 encoded image string."""
        # This is a minimal 1x1 pixel PNG image in base64
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    @staticmethod
    def generate_dish_item_data(
        dish_id: str = None,
        dish_name: str = None,
        dish_price: str = None,
        dish_quantity: int = None,
        dish_image_url: str = None
    ) -> Dict[str, Any]:
        """
        Generate dish item data for cart/orders.
        
        Args:
            dish_id: Dish ID
            dish_name: Dish name
            dish_price: Dish price
            dish_quantity: Quantity
            dish_image_url: Image URL
            
        Returns:
            Dictionary with dish item data
        """
        return {
            "dishId": dish_id or TestDataGenerator.generate_object_id(),
            "dishName": dish_name or fake.word().title() + " " + fake.word().title(),
            "dishPrice": dish_price or f"${random.randint(5, 50)}.{random.randint(0, 99):02d}",
            "dishQuantity": dish_quantity or random.randint(1, 5),
            "dishImageUrl": dish_image_url or fake.image_url()
        }
    
    @staticmethod
    def generate_preorder_data(
        reservation_id: str = None,
        address: str = None,
        date: str = None,
        time_slot: str = None,
        dish_items: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate preorder data.
        
        Args:
            reservation_id: Reservation ID
            address: Location address
            date: Order date
            time_slot: Time slot
            dish_items: List of dish items
            
        Returns:
            Dictionary with preorder data
        """
        if not dish_items:
            dish_items = [TestDataGenerator.generate_dish_item_data()]
        
        return {
            "id": TestDataGenerator.generate_object_id(),
            "reservationId": reservation_id or TestDataGenerator.generate_object_id(),
            "address": address or fake.address(),
            "date": date or fake.date_between(start_date='+1d', end_date='+7d').strftime('%Y-%m-%d'),
            "timeSlot": time_slot or f"{random.randint(10, 20)}:00 - {random.randint(11, 21)}:00",
            "dishItems": dish_items,
            "state": "SUBMITTED"
        }
    
    @staticmethod
    def generate_invalid_data_variants() -> Dict[str, Dict[str, Any]]:
        """
        Generate various invalid data variants for negative testing.
        
        Returns:
            Dictionary with different types of invalid data
        """
        return {
            "empty_strings": {
                "firstName": "",
                "lastName": "",
                "email": "",
                "password": ""
            },
            "null_values": {
                "firstName": None,
                "lastName": None,
                "email": None,
                "password": None
            },
            "invalid_email": {
                "firstName": fake.first_name(),
                "lastName": fake.last_name(),
                "email": "invalid-email",
                "password": TestDataGenerator.generate_password()
            },
            "short_password": {
                "firstName": fake.first_name(),
                "lastName": fake.last_name(),
                "email": fake.email(),
                "password": "123"
            },
            "long_strings": {
                "firstName": "a" * 1000,
                "lastName": "b" * 1000,
                "email": "c" * 1000 + "@example.com",
                "password": "d" * 1000
            },
            "special_characters": {
                "firstName": "!@#$%^&*()",
                "lastName": "<script>alert('xss')</script>",
                "email": "test@<script>.com",
                "password": "'; DROP TABLE users; --"
            }
        }


# Global test data generator instance
test_data = TestDataGenerator()