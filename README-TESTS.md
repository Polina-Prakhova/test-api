# Restaurant API Test Suite

This is a comprehensive test suite for the Restaurant API, covering all endpoints with thorough validation, error handling, and integration testing.

## Overview

The test suite includes:
- **Authentication Tests** - User signup, signin, and validation
- **Health Check Tests** - System health and basic functionality
- **Dishes Tests** - Popular dishes, dish listing, and details
- **Locations Tests** - Location management and related services
- **Bookings Tests** - Table availability and reservation booking
- **Reservations Tests** - Reservation management and dish ordering
- **Cart Tests** - Shopping cart functionality
- **Profile Tests** - User profile management
- **Feedbacks Tests** - Feedback creation and visitor feedback
- **Reports Tests** - Report generation and retrieval
- **Integration Tests** - End-to-end workflows and cross-service testing

## Test Structure

```
test/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── test_auth.py               # Authentication endpoint tests
├── test_health.py             # Health check and basic endpoint tests
├── test_dishes.py             # Dishes endpoint tests
├── test_locations.py          # Locations endpoint tests
├── test_bookings.py           # Bookings endpoint tests
├── test_reservations.py       # Reservations endpoint tests
├── test_cart.py               # Cart endpoint tests
├── test_profile.py            # Profile endpoint tests
├── test_feedbacks.py          # Feedbacks endpoint tests
├── test_reports.py            # Reports endpoint tests
└── test_integration.py        # Integration and end-to-end tests
```

## Test Categories

### Functional Tests
- **Happy Path Testing** - Normal operation scenarios
- **Validation Testing** - Input validation and data integrity
- **Business Logic Testing** - Core functionality verification

### Non-Functional Tests
- **Error Handling** - Error scenarios and edge cases
- **Security Testing** - Authentication, authorization, and injection attacks
- **Performance Testing** - Response times and concurrent requests
- **Integration Testing** - Cross-service workflows

### Test Markers
- `@pytest.mark.auth` - Authentication-related tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.validation` - Validation tests
- `@pytest.mark.error` - Error scenario tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.security` - Security tests

## Setup and Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
# Install dependencies
pip install -r requirements-updated.txt

# Or use the basic requirements
pip install -r requirements.txt
```

### Configuration
The tests use the following default configuration:
- **Base URL**: `http://localhost:8080`
- **Valid User Credentials**: 
  - Email: `jhon_smith@example.com`
  - Password: `Y2kjqKHX`

You can modify these in `conftest.py` or use environment variables.

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Authentication tests only
pytest -m auth

# Integration tests only
pytest -m integration

# Error scenario tests
pytest -m error

# Validation tests
pytest -m validation
```

### Run Specific Test Files
```bash
# Run authentication tests
pytest test/test_auth.py

# Run integration tests
pytest test/test_integration.py

# Run with verbose output
pytest test/test_auth.py -v
```

### Run Tests in Parallel
```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

### Generate Reports
```bash
# Generate HTML report
pytest --html=reports/report.html --self-contained-html

# Generate coverage report
pytest --cov=test --cov-report=html:reports/coverage

# Generate JSON report
pytest --json-report --json-report-file=reports/report.json
```

## Test Data and Fixtures

### Common Fixtures
- `base_url` - API base URL
- `api_client` - HTTP client for requests
- `authenticated_client` - Pre-authenticated HTTP client
- `valid_user_credentials` - Valid login credentials
- `valid_signup_data` - Valid user registration data
- `sample_location_id` - Sample location ID for testing
- `sample_dish_id` - Sample dish ID for testing
- `sample_reservation_id` - Sample reservation ID for testing

### Test Data
The tests use realistic test data including:
- Valid and invalid email formats
- Various password combinations
- Realistic names and addresses
- Valid and invalid date/time formats
- Proper and malformed JSON payloads

## API Endpoints Covered

### Authentication Endpoints
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User login
- `GET /auth/validate` - Authentication validation

### Basic Endpoints
- `GET /health` - Health check
- `GET /` - Root endpoint

### Dishes Endpoints
- `GET /dishes/popular` - Popular dishes
- `GET /dishes` - All dishes with filtering
- `GET /dishes/{id}` - Dish details

### Locations Endpoints
- `GET /locations` - All locations
- `GET /locations/select-options` - Location options
- `GET /locations/{id}/speciality-dishes` - Location speciality dishes
- `GET /locations/{id}/feedbacks` - Location feedbacks

### Bookings Endpoints
- `GET /bookings/tables` - Available tables
- `POST /bookings/client` - Client booking
- `POST /bookings/waiter` - Waiter booking

### Reservations Endpoints
- `GET /reservations` - User reservations
- `DELETE /reservations/{id}` - Cancel reservation
- `GET /reservations/{id}/available-dishes` - Available dishes
- `POST /reservations/{id}/order/{dishId}` - Order dish

### Cart Endpoints
- `GET /cart` - Get cart
- `PUT /cart` - Submit cart/preorder

### Profile Endpoints
- `GET /users/profile` - Get profile
- `PUT /users/profile` - Update profile
- `PUT /users/profile/password` - Change password

### Feedbacks Endpoints
- `POST /feedbacks/` - Create feedback
- `GET /feedbacks/visitor` - Visitor feedback

### Reports Endpoints
- `GET /reports` - Get reports
- `POST /reports` - Create report

## Test Scenarios

### Authentication Flow Testing
- Successful signup and signin
- Invalid credentials handling
- Token validation and expiration
- Authorization for protected endpoints

### Request Validation Testing
- Missing required fields
- Invalid field formats
- Empty and null values
- Field length limits
- Special characters and encoding

### Response Verification Testing
- Correct HTTP status codes
- Response structure validation
- Data type verification
- Content validation

### Error Scenario Testing
- Invalid input handling
- Non-existent resource access
- Unauthorized access attempts
- Malformed requests
- Server error simulation

### Security Testing
- SQL injection attempts
- XSS attack prevention
- Authorization bypass attempts
- Token manipulation
- Input sanitization

### Integration Testing
- Complete user journeys
- Cross-service data consistency
- Workflow validation
- Business logic verification

## Best Practices

### Test Organization
- One test class per major functionality
- Descriptive test method names
- Proper test categorization with markers
- Logical test grouping

### Test Data Management
- Use fixtures for common test data
- Avoid hardcoded values where possible
- Clean up test data when necessary
- Use realistic test scenarios

### Assertions
- Clear and specific assertions
- Meaningful error messages
- Multiple assertion points per test
- Proper exception handling

### Error Handling
- Test both success and failure scenarios
- Validate error responses
- Check error message content
- Verify proper HTTP status codes

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the API server is running
   - Check the base URL configuration
   - Verify network connectivity

2. **Authentication Failures**
   - Check if test credentials are valid
   - Verify token format and expiration
   - Ensure proper authorization headers

3. **Test Data Issues**
   - Verify test data exists in the system
   - Check for data dependencies
   - Ensure proper test isolation

4. **Timeout Issues**
   - Increase timeout values in pytest.ini
   - Check server performance
   - Optimize test execution

### Debug Mode
```bash
# Run tests with debug output
pytest -s -v --tb=long

# Run specific test with debugging
pytest test/test_auth.py::TestAuthSignin::test_signin_success -s -v
```

### Logging
Tests include comprehensive logging. Check the console output or log files for detailed information about test execution.

## Contributing

### Adding New Tests
1. Follow the existing test structure
2. Use appropriate test markers
3. Include both positive and negative test cases
4. Add proper documentation
5. Update this README if needed

### Test Guidelines
- Write clear, descriptive test names
- Include docstrings for test methods
- Use appropriate assertions
- Handle edge cases
- Follow PEP 8 style guidelines

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements-updated.txt
      - name: Run tests
        run: pytest --html=reports/report.html --cov=test
```

## Reports and Coverage

The test suite generates comprehensive reports:
- **HTML Report** - Visual test results (`reports/report.html`)
- **Coverage Report** - Code coverage analysis (`reports/coverage/`)
- **JSON Report** - Machine-readable results (`reports/report.json`)

## Performance Considerations

- Tests are designed to run efficiently
- Parallel execution supported with pytest-xdist
- Fixtures are scoped appropriately
- Database cleanup is handled automatically
- Network timeouts are configured reasonably

## Support

For issues or questions about the test suite:
1. Check this documentation
2. Review test logs and error messages
3. Verify API server status
4. Check test configuration
5. Consult pytest documentation for advanced usage