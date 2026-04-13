#!/usr/bin/env python3
"""
Test runner for the Schieber card game.
This script discovers and runs all tests in the tests directory.
"""
import unittest
import sys
import os

# Add the tests directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'tests')))

# Discover and run all tests
def run_tests():
    """Discover and run all tests."""
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Discover all tests in the tests directory
    test_suite = loader.discover('tests')
    
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = runner.run(test_suite)
    
    # Return True if all tests passed, False otherwise
    return result.wasSuccessful()

if __name__ == "__main__":
    # Run the tests and exit with appropriate code
    success = run_tests()
    sys.exit(0 if success else 1)