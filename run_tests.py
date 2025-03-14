#!/usr/bin/env python3
"""
Test runner script for RF Layout project.
Runs all tests and generates coverage report.
"""

import os
import sys
import subprocess

def run_tests():
    """Run the test suite with coverage reporting."""
    # Ensure we're in the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Install test dependencies if needed
    print("Installing test dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", ".[test]"])
    
    # Run tests with pytest
    print("\nRunning tests...")
    result = subprocess.run([
        sys.executable, 
        "-m", 
        "pytest",
        "--verbose",
        "--cov=rf_layout",
        "--cov-report=term-missing",
        "--cov-report=html",
        "rf_layout/tests/"
    ])
    
    if result.returncode != 0:
        print("\nTests failed!")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        print("\nCoverage report generated in htmlcov/index.html")

if __name__ == "__main__":
    run_tests()