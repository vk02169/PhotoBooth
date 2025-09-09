"""
Mock hardware components for PhotoBooth testing.

This module provides mock implementations of hardware-dependent components
like camera, GPIO, and other Raspberry Pi specific modules.
"""

from unittest.mock import Mock, MagicMock
import time


class MockPiCamera:
    """Mock implementation of PiCamera for testing."""
    
    def __init__(self):
        self.resolution = (1920, 1080)
        self.preview_alpha = 200
        self.preview_fullscreen = False
        self.preview_window = (0, 40, 1024, 675)
        self.iso = 400
        self.sharpness = 0
        self._preview_started = False
        self._closed = False
    
    def capture(self, filename, format=None, use_video_port=False, **kwargs):
        """Mock image capture."""
        if self._closed:
            raise RuntimeError("Camera is closed")
        
        # Simulate capture delay
        time.sleep(0.01)
        
        # Create a fake image file
        with open(filename, 'w') as f:
            f.write("mock image data")
        
        return True
    
    def start_preview(self, **kwargs):
        """Mock preview start."""
        if self._closed:
            raise RuntimeError("Camera is closed")
        self._preview_started = True
    
    def stop_preview(self):
        """Mock preview stop."""
        if self._closed:
            raise RuntimeError("Camera is closed")
        self._preview_started = False
    
    def close(self):
        """Mock camera close."""
        if self._preview_started:
            self.stop_preview()
        self._closed = True


class MockGPIO:
    """Mock implementation of RPi.GPIO for testing."""
    
    # Constants
    BOARD = 10
    BCM = 11
    OUT = 1
    IN = 0
    HIGH = 1
    LOW = 0
    PUD_UP = 22
    PUD_DOWN = 21
    
    _mode = None
    _pins = {}
    _warnings = True
    
    @classmethod
    def setmode(cls, mode):
        """Set GPIO mode."""
        cls._mode = mode
    
    @classmethod
    def getmode(cls):
        """Get current GPIO mode."""
        return cls._mode
    
    @classmethod
    def setup(cls, pin, direction, pull_up_down=None, initial=None):
        """Setup GPIO pin."""
        if cls._mode is None:
            raise RuntimeError("GPIO mode not set")
        
        cls._pins[pin] = {
            'direction': direction,
            'pull_up_down': pull_up_down,
            'value': initial if initial is not None else cls.LOW
        }
    
    @classmethod
    def output(cls, pin, value):
        """Set GPIO pin output value."""
        if pin not in cls._pins:
            raise RuntimeError(f"Pin {pin} not setup")
        
        if cls._pins[pin]['direction'] != cls.OUT:
            raise RuntimeError(f"Pin {pin} not setup as output")
        
        cls._pins[pin]['value'] = value
    
    @classmethod
    def input(cls, pin):
        """Read GPIO pin input value."""
        if pin not in cls._pins:
            raise RuntimeError(f"Pin {pin} not setup")
        
        return cls._pins[pin]['value']
    
    @classmethod
    def cleanup(cls, pin=None):
        """Cleanup GPIO pins."""
        if pin is None:
            cls._pins.clear()
            cls._mode = None
        else:
            if pin in cls._pins:
                del cls._pins[pin]
    
    @classmethod
    def setwarnings(cls, enabled):
        """Enable/disable GPIO warnings."""
        cls._warnings = enabled


class MockGoogleDriveUploader:
    """Mock implementation of Google Drive uploader."""
    
    _instance = None
    
    def __init__(self):
        if MockGoogleDriveUploader._instance is not None:
            raise Exception("GoogleDriveUploader is a singleton")
        MockGoogleDriveUploader._instance = self
        self.uploaded_files = []
        self.upload_errors = []
    
    @classmethod
    def instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls()
        return cls._instance
    
    def kickOff(self, files):
        """Mock upload kickoff."""
        if not isinstance(files, list):
            files = [files] if files else []
        
        for file in files:
            # Simulate upload delay
            time.sleep(0.01)
            
            # Simulate occasional upload failures
            if "error" in str(file).lower():
                self.upload_errors.append(file)
                raise Exception(f"Upload failed for {file}")
            else:
                self.uploaded_files.append(file)
    
    def cleanup(self):
        """Mock cleanup."""
        # Reset state
        self.uploaded_files.clear()
        self.upload_errors.clear()
    
    @classmethod
    def reset(cls):
        """Reset singleton instance."""
        cls._instance = None


def setup_mock_hardware():
    """Setup all mock hardware components."""
    import sys
    
    # Mock picamera
    mock_picamera = MagicMock()
    mock_picamera.PiCamera = MockPiCamera
    sys.modules['picamera'] = mock_picamera
    
    # Mock RPi.GPIO
    mock_rpi = MagicMock()
    mock_rpi.GPIO = MockGPIO
    sys.modules['RPi'] = mock_rpi
    sys.modules['RPi.GPIO'] = MockGPIO
    
    # Mock Google Drive uploader
    mock_uploader = MagicMock()
    mock_uploader.GoogleDriveUploader = MockGoogleDriveUploader
    sys.modules['googledriveuploader'] = mock_uploader
    
    return {
        'camera': MockPiCamera,
        'gpio': MockGPIO,
        'uploader': MockGoogleDriveUploader
    }


def teardown_mock_hardware():
    """Cleanup mock hardware components."""
    MockGPIO.cleanup()
    MockGoogleDriveUploader.reset()


# Convenience functions for common test scenarios
def create_mock_camera_with_error():
    """Create a mock camera that raises errors."""
    camera = MockPiCamera()
    original_capture = camera.capture
    
    def error_capture(*args, **kwargs):
        raise Exception("Camera hardware error")
    
    camera.capture = error_capture
    return camera


def create_mock_gpio_with_error():
    """Create a mock GPIO that raises errors."""
    gpio = MockGPIO()
    original_output = gpio.output
    
    @classmethod
    def error_output(cls, pin, value):
        raise Exception("GPIO hardware error")
    
    gpio.output = error_output
    return gpio