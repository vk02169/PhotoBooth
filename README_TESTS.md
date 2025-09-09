# PhotoBooth Test Suite

This document describes the comprehensive test suite for the PhotoBooth application, including unit tests, integration tests, and testing utilities.

## Overview

The test suite provides comprehensive coverage of the PhotoBooth application functionality, including:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows and component interactions
- **Mock Hardware**: Simulate Raspberry Pi hardware for testing without physical devices
- **Test Utilities**: Helper functions and fixtures for consistent testing

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # pytest configuration and fixtures
├── fixtures/                   # Test data and configuration files
│   ├── __init__.py
│   └── sample_config.conf      # Sample configuration for testing
├── mocks/                      # Mock implementations
│   ├── __init__.py
│   └── mock_hardware.py        # Hardware mocks (camera, GPIO, etc.)
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_camera.py          # Camera module tests
│   ├── test_configurator.py    # Configuration system tests
│   ├── test_gui_utils.py       # GUI utility tests
│   └── test_upload.py          # Upload functionality tests
└── integration/                # Integration tests
    ├── __init__.py
    └── test_photo_capture_workflow.py  # End-to-end workflow tests
```

## Running Tests

### Prerequisites

Install required testing dependencies:

```bash
pip install pytest pytest-cov
```

### Quick Start

Run all tests:
```bash
python run_tests.py
```

### Test Runner Options

The `run_tests.py` script provides various options:

```bash
# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run with coverage report
python run_tests.py --coverage

# Run specific test file
python run_tests.py --test tests/unit/test_camera.py

# Run tests matching a pattern
python run_tests.py --pattern camera

# List all available tests
python run_tests.py --list

# Use unittest instead of pytest
python run_tests.py --unittest

# Verbose output
python run_tests.py --verbose
```

### Using pytest directly

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/ -m unit

# Run integration tests only
pytest tests/integration/ -m integration

# Run with coverage
pytest tests/ --cov=corecam --cov=coregui --cov=uploaders --cov-report=html

# Run specific test
pytest tests/unit/test_camera.py::TestBoothCamera::test_singleton_pattern
```

### Using unittest

```bash
# Discover and run all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run specific test module
python -m unittest tests.unit.test_camera -v
```

## Test Categories

### Unit Tests

#### Camera Module Tests (`test_camera.py`)
- **BoothCamera class**: Singleton pattern, initialization, configuration integration
- **Camera operations**: Capture, preview control, flash integration
- **Error handling**: Exception handling during capture operations
- **CameraFlash class**: GPIO control, configuration-based flash behavior

#### Configuration Tests (`test_configurator.py`)
- **Singleton pattern**: Ensures single configuration instance
- **Configuration loading**: File parsing, default value handling
- **Data type conversion**: Boolean, integer, float, and string parsing
- **Error handling**: Malformed files, missing values, permission errors

#### GUI Utilities Tests (`test_gui_utils.py`)
- **CountdownText class**: Progressive text display, timing, canvas operations
- **BlinkingText class**: Blinking animation, frequency control
- **Utility functions**: Image archiving, timestamp generation, error handling

#### Upload Tests (`test_upload.py`)
- **Upload coordination**: Service selection based on configuration
- **Google Drive integration**: Uploader lifecycle, error handling
- **Singleton management**: Uploader instance reuse
- **Cleanup operations**: Graceful shutdown of background processes

### Integration Tests

#### Photo Capture Workflow (`test_photo_capture_workflow.py`)
- **Complete photo session**: Camera → Flash → Capture → Archive → Upload
- **Multi-photo workflows**: Sequential photo capture with proper state management
- **Configuration variations**: Different flash, upload, and GUI settings
- **Error scenarios**: Hardware failures, upload errors, configuration issues
- **GUI integration**: Countdown displays, status messages, user feedback

## Mock Hardware

The test suite includes comprehensive hardware mocking to enable testing without physical Raspberry Pi hardware:

### MockPiCamera
- Simulates PiCamera behavior
- Supports capture, preview, and configuration operations
- Includes error simulation for testing failure scenarios

### MockGPIO
- Simulates RPi.GPIO functionality
- Supports pin setup, input/output operations
- Maintains pin state for verification

### MockGoogleDriveUploader
- Simulates upload operations
- Tracks uploaded files for verification
- Supports error simulation

## Test Configuration

### pytest.ini
- Test discovery patterns
- Output formatting
- Timeout settings
- Warning filters
- Custom markers

### conftest.py
- Shared fixtures for common test data
- Automatic singleton reset between tests
- Mock hardware setup
- Custom test markers

## Coverage Reports

Generate coverage reports to identify untested code:

```bash
# Generate HTML coverage report
python run_tests.py --coverage

# View coverage report
open htmlcov/index.html
```

Coverage reports include:
- Line-by-line coverage analysis
- Branch coverage information
- Missing coverage identification
- Module-level coverage summaries

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Long-running tests
- `@pytest.mark.hardware`: Tests requiring hardware simulation

Run specific marker groups:
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m "not slow"    # Skip slow tests
```

## Best Practices

### Writing Tests

1. **Use descriptive test names**: Test names should clearly describe what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Mock external dependencies**: Use mocks for hardware, network, and file system operations
4. **Test edge cases**: Include boundary conditions and error scenarios
5. **Keep tests independent**: Each test should be able to run in isolation

### Test Organization

1. **Group related tests**: Use test classes to group related functionality
2. **Use fixtures**: Share common setup code using pytest fixtures
3. **Separate unit and integration tests**: Keep different test types in separate directories
4. **Document test purpose**: Include docstrings explaining test objectives

### Mock Usage

1. **Mock at the boundary**: Mock external systems, not internal logic
2. **Verify interactions**: Assert that mocks are called with expected parameters
3. **Reset state**: Ensure mocks are reset between tests
4. **Use realistic mocks**: Mock behavior should match real system behavior

## Continuous Integration

The test suite is designed to run in CI/CD environments:

```bash
# CI-friendly test execution
python run_tests.py --unittest  # Fallback to unittest if pytest unavailable
python -m unittest discover -s tests -p "test_*.py"  # Pure unittest execution
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure project root is in Python path
2. **Mock failures**: Verify hardware mocks are properly initialized
3. **Singleton conflicts**: Check that singletons are reset between tests
4. **File permissions**: Ensure test has write access to temporary directories

### Debug Mode

Run tests with verbose output and debugging:

```bash
python run_tests.py --verbose
pytest tests/ -v -s  # -s shows print statements
```

### Test Isolation

If tests interfere with each other:

1. Check singleton reset in `conftest.py`
2. Verify temporary file cleanup
3. Ensure mock state is reset between tests

## Contributing

When adding new functionality:

1. **Write tests first**: Use TDD approach when possible
2. **Maintain coverage**: Ensure new code is adequately tested
3. **Update documentation**: Keep test documentation current
4. **Follow patterns**: Use existing test patterns and conventions

### Adding New Tests

1. Create test file in appropriate directory (`unit/` or `integration/`)
2. Follow naming convention: `test_<module_name>.py`
3. Use appropriate fixtures and mocks
4. Add markers for test categorization
5. Update this documentation if needed

## Performance Testing

For performance-critical components, consider adding performance tests:

```python
import time
import pytest

@pytest.mark.slow
def test_camera_capture_performance():
    """Test that camera capture completes within acceptable time."""
    start_time = time.time()
    # ... test code ...
    duration = time.time() - start_time
    assert duration < 2.0, f"Capture took too long: {duration}s"
```

## Security Testing

For security-sensitive operations:

```python
def test_configuration_file_permissions():
    """Test that configuration files have appropriate permissions."""
    # Test file permission validation
    # Test input sanitization
    # Test path traversal prevention
```

This comprehensive test suite ensures the PhotoBooth application is reliable, maintainable, and ready for production use.