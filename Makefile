# Makefile for executing Maven commands

.PHONY: install test e2e

# Define the Maven command for installation without running tests
install:
	@echo "Running Maven install (skipping tests)..."
	mvn install -DskipTests

# Define the Maven command for running tests
test:
	@echo "Running Maven tests..."
	mvn test

# Define the e2e target that runs both install and test
e2e: install test
	@echo "End-to-end process completed."
