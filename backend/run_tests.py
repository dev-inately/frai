#!/usr/bin/env python3
"""
Simple test runner for the AI Contract Generator backend.
"""
import subprocess
import sys
import os

def run_tests():
    """Run the test suite with pytest."""
    print("🧪 Running AI Contract Generator Backend Tests")
    print("=" * 60)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"], check=True)
    
    # Run tests
    test_args = [
        sys.executable, "-m", "pytest",
        "test_main.py",
        "-v",
        "--tb=short",
        "--asyncio-mode=auto"
    ]
    
    # Add coverage if available
    try:
        import pytest_cov
        test_args.extend(["--cov=app", "--cov-report=term-missing"])
    except ImportError:
        pass
    
    print("Running tests...")
    result = subprocess.run(test_args)
    
    if result.returncode == 0:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result.returncode

def run_specific_test(test_name):
    """Run a specific test by name."""
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 60)
    
    test_args = [
        sys.executable, "-m", "pytest",
        f"test_main.py::{test_name}",
        "-v",
        "--tb=short",
        "--asyncio-mode=auto"
    ]
    
    result = subprocess.run(test_args)
    return result.returncode

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        exit_code = run_specific_test(test_name)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code)
