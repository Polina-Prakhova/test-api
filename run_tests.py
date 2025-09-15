#!/usr/bin/env python3
"""
Test runner script for Restaurant API tests.
Provides convenient ways to run different test suites and generate reports.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description=""):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    if description:
        print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ Command failed with exit code {result.returncode}")
        return False
    else:
        print(f"\n✅ Command completed successfully")
        return True


def setup_reports_directory():
    """Create reports directory if it doesn't exist."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    print(f"📁 Reports directory: {reports_dir.absolute()}")


def run_all_tests():
    """Run all tests with comprehensive reporting."""
    setup_reports_directory()
    
    command = (
        "pytest "
        "--html=reports/report.html "
        "--self-contained-html "
        "--json-report "
        "--json-report-file=reports/report.json "
        "--cov=test "
        "--cov-report=html:reports/coverage "
        "--cov-report=term-missing "
        "-v"
    )
    
    return run_command(command, "All tests with reports")


def run_smoke_tests():
    """Run smoke tests (basic functionality)."""
    setup_reports_directory()
    
    command = (
        "pytest "
        "-m 'not slow and not integration' "
        "--html=reports/smoke_report.html "
        "--self-contained-html "
        "-v"
    )
    
    return run_command(command, "Smoke tests")


def run_integration_tests():
    """Run integration tests."""
    setup_reports_directory()
    
    command = (
        "pytest "
        "-m integration "
        "--html=reports/integration_report.html "
        "--self-contained-html "
        "-v"
    )
    
    return run_command(command, "Integration tests")


def run_auth_tests():
    """Run authentication tests."""
    setup_reports_directory()
    
    command = (
        "pytest "
        "test/test_auth.py "
        "--html=reports/auth_report.html "
        "--self-contained-html "
        "-v"
    )
    
    return run_command(command, "Authentication tests")


def run_security_tests():
    """Run security tests."""
    setup_reports_directory()
    
    command = (
        "pytest "
        "-m security "
        "--html=reports/security_report.html "
        "--self-contained-html "
        "-v"
    )
    
    return run_command(command, "Security tests")


def run_parallel_tests():
    """Run tests in parallel."""
    setup_reports_directory()
    
    command = (
        "pytest "
        "-n auto "
        "--html=reports/parallel_report.html "
        "--self-contained-html "
        "-v"
    )
    
    return run_command(command, "Parallel test execution")


def run_specific_test(test_path):
    """Run a specific test file or test method."""
    setup_reports_directory()
    
    command = (
        f"pytest "
        f"{test_path} "
        f"--html=reports/specific_report.html "
        f"--self-contained-html "
        f"-v"
    )
    
    return run_command(command, f"Specific test: {test_path}")


def run_coverage_only():
    """Run tests with coverage analysis only."""
    setup_reports_directory()
    
    command = (
        "pytest "
        "--cov=test "
        "--cov-report=html:reports/coverage "
        "--cov-report=term-missing "
        "--cov-fail-under=80 "
        "-q"
    )
    
    return run_command(command, "Coverage analysis")


def run_performance_tests():
    """Run performance-related tests."""
    setup_reports_directory()
    
    command = (
        "pytest "
        "-m 'slow or integration' "
        "--html=reports/performance_report.html "
        "--self-contained-html "
        "--tb=short "
        "-v"
    )
    
    return run_command(command, "Performance tests")


def run_validation_tests():
    """Run validation tests."""
    setup_reports_directory()
    
    command = (
        "pytest "
        "-m validation "
        "--html=reports/validation_report.html "
        "--self-contained-html "
        "-v"
    )
    
    return run_command(command, "Validation tests")


def run_error_tests():
    """Run error scenario tests."""
    setup_reports_directory()
    
    command = (
        "pytest "
        "-m error "
        "--html=reports/error_report.html "
        "--self-contained-html "
        "-v"
    )
    
    return run_command(command, "Error scenario tests")


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "pytest",
        "requests",
        "pytest-html",
        "pytest-cov"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements-updated.txt")
        return False
    
    print("\n✅ All dependencies are installed")
    return True


def show_test_info():
    """Show information about available tests."""
    print("\n📊 Test Suite Information")
    print("=" * 60)
    
    # Count test files
    test_files = list(Path("test").glob("test_*.py"))
    print(f"Test files: {len(test_files)}")
    
    for test_file in sorted(test_files):
        print(f"  - {test_file.name}")
    
    # Show available markers
    print(f"\n🏷️  Available test markers:")
    markers = [
        "auth - Authentication tests",
        "integration - Integration tests", 
        "validation - Validation tests",
        "error - Error scenario tests",
        "slow - Slow running tests",
        "security - Security tests"
    ]
    
    for marker in markers:
        print(f"  - {marker}")
    
    print(f"\n📁 Reports will be generated in: {Path('reports').absolute()}")


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Restaurant API Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all tests
  python run_tests.py --smoke                  # Run smoke tests
  python run_tests.py --integration            # Run integration tests
  python run_tests.py --auth                   # Run auth tests
  python run_tests.py --security               # Run security tests
  python run_tests.py --parallel               # Run tests in parallel
  python run_tests.py --coverage               # Run coverage analysis
  python run_tests.py --specific test_auth.py  # Run specific test
  python run_tests.py --info                   # Show test information
        """
    )
    
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--auth", action="store_true", help="Run authentication tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--validation", action="store_true", help="Run validation tests")
    parser.add_argument("--error", action="store_true", help="Run error scenario tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--coverage", action="store_true", help="Run coverage analysis only")
    parser.add_argument("--specific", type=str, help="Run specific test file or method")
    parser.add_argument("--info", action="store_true", help="Show test information")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies")
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Check dependencies first if requested
    if args.check_deps:
        if not check_dependencies():
            sys.exit(1)
        return
    
    # Show test information
    if args.info:
        show_test_info()
        return
    
    # Ensure we're in the right directory
    if not Path("test").exists():
        print("❌ Test directory not found. Please run from the project root.")
        sys.exit(1)
    
    success = True
    
    # Run requested test suites
    if args.all:
        success &= run_all_tests()
    
    if args.smoke:
        success &= run_smoke_tests()
    
    if args.integration:
        success &= run_integration_tests()
    
    if args.auth:
        success &= run_auth_tests()
    
    if args.security:
        success &= run_security_tests()
    
    if args.validation:
        success &= run_validation_tests()
    
    if args.error:
        success &= run_error_tests()
    
    if args.performance:
        success &= run_performance_tests()
    
    if args.parallel:
        success &= run_parallel_tests()
    
    if args.coverage:
        success &= run_coverage_only()
    
    if args.specific:
        success &= run_specific_test(args.specific)
    
    # Final status
    if success:
        print(f"\n🎉 All requested test suites completed successfully!")
        print(f"📊 Check reports in: {Path('reports').absolute()}")
    else:
        print(f"\n💥 Some test suites failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()