#!/usr/bin/env python3
"""
PhotoBooth Test Runner

This script provides a convenient way to run the PhotoBooth test suite
with various options and configurations.
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_command(cmd, description=""):
    """Run a command and return the result."""
    if description:
        print(f"\n{description}")
        print("=" * len(description))
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def check_dependencies():
    """Check if required test dependencies are available."""
    required_packages = ['pytest', 'unittest']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Install with: pip install pytest")
        return False
    
    return True


def run_unit_tests(verbose=False, pattern=None):
    """Run unit tests."""
    cmd = ['python', '-m', 'pytest', 'tests/unit/', '-m', 'unit']
    
    if verbose:
        cmd.append('-v')
    
    if pattern:
        cmd.extend(['-k', pattern])
    
    return run_command(cmd, "Running Unit Tests")


def run_integration_tests(verbose=False, pattern=None):
    """Run integration tests."""
    cmd = ['python', '-m', 'pytest', 'tests/integration/', '-m', 'integration']
    
    if verbose:
        cmd.append('-v')
    
    if pattern:
        cmd.extend(['-k', pattern])
    
    return run_command(cmd, "Running Integration Tests")


def run_all_tests(verbose=False, pattern=None):
    """Run all tests."""
    cmd = ['python', '-m', 'pytest', 'tests/']
    
    if verbose:
        cmd.append('-v')
    
    if pattern:
        cmd.extend(['-k', pattern])
    
    return run_command(cmd, "Running All Tests")


def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test function."""
    cmd = ['python', '-m', 'pytest', test_path]
    
    if verbose:
        cmd.append('-v')
    
    return run_command(cmd, f"Running Specific Test: {test_path}")


def run_with_coverage():
    """Run tests with coverage report."""
    try:
        import pytest_cov
    except ImportError:
        print("pytest-cov not installed. Install with: pip install pytest-cov")
        return False
    
    cmd = [
        'python', '-m', 'pytest', 'tests/',
        '--cov=corecam',
        '--cov=coregui', 
        '--cov=uploaders',
        '--cov-report=html',
        '--cov-report=term-missing'
    ]
    
    success = run_command(cmd, "Running Tests with Coverage")
    
    if success:
        print("\nCoverage report generated in htmlcov/index.html")
    
    return success


def run_unittest_discovery():
    """Run tests using unittest discovery as fallback."""
    cmd = ['python', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v']
    return run_command(cmd, "Running Tests with unittest")


def list_tests():
    """List all available tests."""
    cmd = ['python', '-m', 'pytest', '--collect-only', '-q', 'tests/']
    return run_command(cmd, "Available Tests")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="PhotoBooth Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run only unit tests
  python run_tests.py --integration      # Run only integration tests
  python run_tests.py --coverage         # Run with coverage report
  python run_tests.py --list             # List all tests
  python run_tests.py --test tests/unit/test_camera.py  # Run specific test file
  python run_tests.py --pattern camera   # Run tests matching pattern
  python run_tests.py --unittest         # Use unittest instead of pytest
        """
    )
    
    parser.add_argument(
        '--unit', action='store_true',
        help='Run only unit tests'
    )
    
    parser.add_argument(
        '--integration', action='store_true',
        help='Run only integration tests'
    )
    
    parser.add_argument(
        '--coverage', action='store_true',
        help='Run tests with coverage report'
    )
    
    parser.add_argument(
        '--test', type=str,
        help='Run a specific test file or test function'
    )
    
    parser.add_argument(
        '--pattern', type=str,
        help='Run tests matching the given pattern'
    )
    
    parser.add_argument(
        '--list', action='store_true',
        help='List all available tests'
    )
    
    parser.add_argument(
        '--unittest', action='store_true',
        help='Use unittest discovery instead of pytest'
    )
    
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Change to project directory
    os.chdir(project_root)
    
    # Check dependencies
    if not args.unittest and not check_dependencies():
        print("Falling back to unittest...")
        args.unittest = True
    
    success = True
    
    try:
        if args.list:
            success = list_tests()
        elif args.unittest:
            success = run_unittest_discovery()
        elif args.coverage:
            success = run_with_coverage()
        elif args.test:
            success = run_specific_test(args.test, args.verbose)
        elif args.unit:
            success = run_unit_tests(args.verbose, args.pattern)
        elif args.integration:
            success = run_integration_tests(args.verbose, args.pattern)
        else:
            success = run_all_tests(args.verbose, args.pattern)
    
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        success = False
    except Exception as e:
        print(f"Error running tests: {e}")
        success = False
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed or encountered errors")
        sys.exit(1)


if __name__ == '__main__':
    main()