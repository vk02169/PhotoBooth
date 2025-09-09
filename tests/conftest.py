"""
pytest configuration file for PhotoBooth tests.

This file contains shared fixtures and configuration for all tests.
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import Mock, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock hardware dependencies globally
sys.modules['picamera'] = MagicMock()
sys.modules['RPi'] = MagicMock()
sys.modules['RPi.GPIO'] = MagicMock()

# Mock GUI dependencies globally
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()

# Mock image processing dependencies
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['resizeimage'] = MagicMock()

# Mock upload dependencies
sys.modules['googledriveuploader'] = MagicMock()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config():
    """Create a mock configuration object with default values."""
    config = Mock()
    
    # Camera configuration
    config.getResolution.return_value = (1920, 1080)
    config.getPreviewAlpha.return_value = 200
    config.getScreenWidth.return_value = 1024
    config.getScreenHeight.return_value = 768
    config.getISO.return_value = 400
    config.getSharpness.return_value = 0
    
    # File configuration
    config.getDefaultImageFilename.return_value = "photobooth_image.jpg"
    config.getInstallDir.return_value = "/tmp"
    config.getArchiveDir.return_value = "/tmp/archive"
    config.getModuloBase.return_value = 10
    
    # Flash configuration
    config.getFlashDisposition.return_value = True
    config.getFlashGPIOAssignment.return_value = 18
    config.getFlashOnTime.return_value = 0.1
    
    # Upload configuration
    config.isUploadToPicasa.return_value = False
    config.isUploadToDrive.return_value = True
    config.getUploadDisposition.return_value = True
    config.getUploadService.return_value = "googledrive"
    
    # GUI configuration
    config.getCountdownText.return_value = ["3", "2", "1", "SMILE!"]
    config.getNumPics.return_value = 4
    config.getShowButtons.return_value = True
    
    # Fun command configuration
    config.getFunCommand.return_value = "convert {0} -sepia-tone 80% {1}"
    
    return config


@pytest.fixture
def mock_canvas():
    """Create a mock tkinter Canvas object."""
    canvas = Mock()
    canvas.create_text.return_value = 1  # Mock text object ID
    canvas.update.return_value = None
    canvas.delete.return_value = None
    return canvas


@pytest.fixture
def sample_images(temp_dir):
    """Create sample image files for testing."""
    images = []
    for i in range(3):
        image_path = os.path.join(temp_dir, f"test_image_{i+1}.jpg")
        with open(image_path, 'w') as f:
            f.write(f"fake image data {i+1}")
        images.append(image_path)
    return images


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances before each test."""
    # Reset camera singletons
    try:
        from corecam.camera import BoothCamera
        BoothCamera._BoothCamera__instance__ = None
    except ImportError:
        pass
    
    try:
        from corecam.camflash import CameraFlash
        CameraFlash._CameraFlash__instance__ = None
    except ImportError:
        pass
    
    try:
        from coregui.camconfig import Configurator
        Configurator._Configurator__instance = None
    except ImportError:
        pass
    
    # Reset upload module globals
    try:
        import uploaders.upload as upload_module
        upload_module.picasa_uploader = None
        upload_module.drive_uploader = None
    except ImportError:
        pass
    
    yield
    
    # Reset again after test
    try:
        from corecam.camera import BoothCamera
        BoothCamera._BoothCamera__instance__ = None
    except ImportError:
        pass
    
    try:
        from corecam.camflash import CameraFlash
        CameraFlash._CameraFlash__instance__ = None
    except ImportError:
        pass
    
    try:
        from coregui.camconfig import Configurator
        Configurator._Configurator__instance = None
    except ImportError:
        pass
    
    try:
        import uploaders.upload as upload_module
        upload_module.picasa_uploader = None
        upload_module.drive_uploader = None
    except ImportError:
        pass


@pytest.fixture
def mock_gpio():
    """Create a mock GPIO object."""
    gpio = Mock()
    gpio.BOARD = 10
    gpio.OUT = 1
    gpio.HIGH = 1
    gpio.LOW = 0
    return gpio


@pytest.fixture
def mock_drive_uploader():
    """Create a mock Google Drive uploader."""
    uploader = Mock()
    uploader.kickOff.return_value = None
    uploader.cleanup.return_value = None
    return uploader


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "hardware: mark test as requiring hardware"
    )


# Custom test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
        
        # Add hardware marker to tests that use GPIO or camera
        if any(keyword in item.name.lower() for keyword in ['gpio', 'camera', 'flash', 'hardware']):
            item.add_marker(pytest.mark.hardware)