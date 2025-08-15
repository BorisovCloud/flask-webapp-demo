#!/usr/bin/env python3
"""
Test runner script for the Flask web application.
This script runs all tests and generates coverage reports.
"""

import logging
import os
import sys
import unittest

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)


def run_tests():
    """Run all tests in the tests directory."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    # Return success/failure
    return result.wasSuccessful()


def run_specific_test_suite(suite_name):
    """Run a specific test suite."""
    loader = unittest.TestLoader()

    if suite_name == "unit":
        # Run only unit tests (utils and integration)
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromName("tests.test_utils"))
        suite.addTests(loader.loadTestsFromName("tests.test_integration"))
    elif suite_name == "routes":
        # Run only route tests
        suite = loader.loadTestsFromName("tests.test_routes")
    elif suite_name == "e2e":
        # Run only end-to-end tests
        suite = loader.loadTestsFromName("tests.test_e2e")
    else:
        print(f"Unknown test suite: {suite_name}")
        return False

    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run tests for Flask web application")
    parser.add_argument(
        "--suite",
        choices=["unit", "routes", "e2e", "all"],
        default="all",
        help="Test suite to run",
    )

    args = parser.parse_args()

    if args.suite == "all":
        success = run_tests()
    else:
        success = run_specific_test_suite(args.suite)

    sys.exit(0 if success else 1)
