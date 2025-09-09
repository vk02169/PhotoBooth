"""
Unit tests for the PhotoBooth camera module (corecam).

This module tests the BoothCamera class and related camera functionality,
including singleton pattern, configuration, image capture, and flash integration.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock, call
import logging

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock hardware dependencies before importing
sys.modules['picamera'] = MagicMock()
sys.modules['RPi'] = MagicMock()
sys.modules['RPi.GPIO'] = MagicMock()

from corecam.camera import BoothCamera, getCamera
from corecam.camflash import CameraFlash


class TestBoothCamera(unittest.TestCase):
    """Test cases for the BoothCamera class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset singleton instances
        BoothCamera._BoothCamera__instance__ = None
        CameraFlash._CameraFlash__instance__ = None
        
        # Create mock configurator
        self.mock_config = Mock()
        self.mock_config.getResolution.return_value = (1920, 1080)
        self.mock_config.getPreviewAlpha.return_value = 200
        self.mock_config.getScreenWidth.return_value = 1024
        self.mock_config.getScreenHeight.return_value = 768
        self.mock_config.getISO.return_value = 400
        self.mock_config.getSharpness.return_value = 0
        self.mock_config.getDefaultImageFilename.return_value = "test_image.jpg"
        self.mock_config.getInstallDir.return_value = "/tmp"
        self.mock_config.getFlashOnTime.return_value = 0.1
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method."""
        # Reset singleton instances
        BoothCamera._BoothCamera__instance__ = None
        CameraFlash._CameraFlash__instance__ = None
        
        # Clean up temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('corecam.camera.Configurator')
    def test_singleton_pattern(self, mock_configurator_class):
        """Test that BoothCamera follows singleton pattern correctly."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        # First instance creation
        camera1 = BoothCamera.instance()
        self.assertIsInstance(camera1, BoothCamera)
        
        # Second instance should return the same object
        camera2 = BoothCamera.instance()
        self.assertIs(camera1, camera2)
        
        # Direct instantiation should raise exception
        with self.assertRaises(Exception) as context:
            BoothCamera()
        self.assertIn("Singleton", str(context.exception))
    
    @patch('corecam.camera.Configurator')
    def test_camera_initialization(self, mock_configurator_class):
        """Test camera initialization with configuration values."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        camera = BoothCamera.instance()
        
        # Verify configuration values are set correctly
        self.assertEqual(camera.resolution, (1920, 1080))
        self.assertEqual(camera.preview_alpha, 200)
        self.assertEqual(camera.iso, 400)
        self.assertEqual(camera.sharpness, 0)
        self.assertFalse(camera.preview_fullscreen)
        self.assertEqual(camera.preview_window, (0, 40, 1024, 675))
    
    @patch('corecam.camera.Configurator')
    def test_get_camera_function(self, mock_configurator_class):
        """Test the getCamera() convenience function."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        camera = getCamera()
        self.assertIsInstance(camera, BoothCamera)
        
        # Should return the same instance
        camera2 = getCamera()
        self.assertIs(camera, camera2)
    
    @patch('corecam.camera.Configurator')
    def test_capture_method(self, mock_configurator_class):
        """Test the capture method with logging."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        camera = BoothCamera.instance()
        
        # Mock the parent capture method
        with patch.object(camera.__class__.__bases__[0], 'capture') as mock_parent_capture:
            mock_parent_capture.return_value = True
            
            with patch('corecam.camera.logging') as mock_logging:
                result = camera.capture("test_image.jpg")
                
                # Verify parent capture was called
                mock_parent_capture.assert_called_once_with("test_image.jpg")
                
                # Verify logging occurred
                mock_logging.info.assert_called_once()
                log_message = mock_logging.info.call_args[0][0]
                self.assertIn("BoothCamera.capture()", log_message)
                self.assertIn("resolution= (1920, 1080)", log_message)
                self.assertIn("ISO=400", log_message)
                self.assertIn("sharpness=0", log_message)
    
    @patch('corecam.camera.Configurator')
    def test_preview_methods(self, mock_configurator_class):
        """Test preview start and stop methods."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        camera = BoothCamera.instance()
        
        # Mock parent methods
        with patch.object(camera.__class__.__bases__[0], 'start_preview') as mock_start:
            with patch.object(camera.__class__.__bases__[0], 'stop_preview') as mock_stop:
                
                camera.start_preview()
                mock_start.assert_called_once()
                
                camera.stop_preview()
                mock_stop.assert_called_once()
    
    @patch('corecam.camera.Configurator')
    def test_close_method(self, mock_configurator_class):
        """Test camera close method."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        camera = BoothCamera.instance()
        
        with patch.object(camera.__class__.__bases__[0], 'close') as mock_close:
            camera.close()
            mock_close.assert_called_once()
    
    @patch('corecam.camera.archiveImage')
    @patch('corecam.camera.CameraFlash')
    @patch('corecam.camera.Configurator')
    @patch('corecam.camera.time')
    def test_snap_success(self, mock_time, mock_configurator_class, mock_flash_class, mock_archive):
        """Test successful snap operation."""
        # Setup mocks
        mock_configurator_class.instance.return_value = self.mock_config
        
        mock_flash = Mock()
        mock_flash_class.instance.return_value = mock_flash
        
        mock_archive.return_value = ("archived_image.jpg", "fun_image.jpg")
        
        camera = BoothCamera.instance()
        
        # Mock the capture method
        with patch.object(camera, 'capture') as mock_capture:
            mock_capture.return_value = True
            
            result = camera.snap()
            
            # Verify flash operations
            mock_flash.fireFlash.assert_called_once()
            mock_flash.flashOff.assert_called_once()
            
            # Verify timing
            mock_time.sleep.assert_called_once_with(0.1)
            
            # Verify capture was called with correct path
            mock_capture.assert_called_once_with("/tmp/test_image.jpg")
            
            # Verify archiving
            mock_archive.assert_called_once_with("/tmp/test_image.jpg")
            
            # Verify return value
            self.assertEqual(result, ("archived_image.jpg", "fun_image.jpg"))
    
    @patch('corecam.camera.printExceptionTrace')
    @patch('corecam.camera.CameraFlash')
    @patch('corecam.camera.Configurator')
    def test_snap_exception_handling(self, mock_configurator_class, mock_flash_class, mock_print_exception):
        """Test snap method exception handling."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        mock_flash = Mock()
        mock_flash_class.instance.return_value = mock_flash
        
        camera = BoothCamera.instance()
        
        # Mock capture to raise an exception
        with patch.object(camera, 'capture') as mock_capture:
            mock_capture.side_effect = Exception("Camera error")
            
            result = camera.snap()
            
            # Verify exception handling
            mock_print_exception.assert_called_once()
            self.assertIsNone(result)
    
    @patch('corecam.camera.Configurator')
    def test_camera_configuration_integration(self, mock_configurator_class):
        """Test integration with configuration system."""
        # Test with different configuration values
        self.mock_config.getResolution.return_value = (2592, 1944)
        self.mock_config.getISO.return_value = 800
        self.mock_config.getSharpness.return_value = 25
        
        mock_configurator_class.instance.return_value = self.mock_config
        
        camera = BoothCamera.instance()
        
        self.assertEqual(camera.resolution, (2592, 1944))
        self.assertEqual(camera.iso, 800)
        self.assertEqual(camera.sharpness, 25)
    
    @patch('corecam.camera.Configurator')
    def test_preview_window_calculation(self, mock_configurator_class):
        """Test preview window size calculation."""
        self.mock_config.getScreenWidth.return_value = 800
        self.mock_config.getScreenHeight.return_value = 600
        
        mock_configurator_class.instance.return_value = self.mock_config
        
        camera = BoothCamera.instance()
        
        # Expected: (0, 40, 800, 507) = (0, 40, width, height - 93)
        expected_window = (0, 40, 800, 507)
        self.assertEqual(camera.preview_window, expected_window)


class TestCameraFlash(unittest.TestCase):
    """Test cases for the CameraFlash class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset singleton instance
        CameraFlash._CameraFlash__instance__ = None
        
        # Create mock configurator
        self.mock_config = Mock()
        self.mock_config.getFlashGPIOAssignment.return_value = 18
        self.mock_config.getFlashDisposition.return_value = True
    
    def tearDown(self):
        """Clean up after each test method."""
        CameraFlash._CameraFlash__instance__ = None
    
    @patch('corecam.camflash.Configurator')
    def test_flash_singleton_pattern(self, mock_configurator_class):
        """Test that CameraFlash follows singleton pattern correctly."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        flash1 = CameraFlash.instance()
        flash2 = CameraFlash.instance()
        
        self.assertIs(flash1, flash2)
        
        # Direct instantiation should raise exception
        with self.assertRaises(Exception) as context:
            CameraFlash()
        self.assertIn("Singleton", str(context.exception))
    
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camflash.Configurator')
    def test_fire_flash_enabled(self, mock_configurator_class, mock_gpio):
        """Test firing flash when flash is enabled."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        flash = CameraFlash.instance()
        flash.fireFlash()
        
        # Verify GPIO operations
        mock_gpio.setmode.assert_called_with(mock_gpio.BOARD)
        mock_gpio.setup.assert_called_with(18, mock_gpio.OUT)
        mock_gpio.output.assert_called_with(18, mock_gpio.HIGH)
    
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camflash.Configurator')
    def test_fire_flash_disabled(self, mock_configurator_class, mock_gpio):
        """Test firing flash when flash is disabled."""
        self.mock_config.getFlashDisposition.return_value = False
        mock_configurator_class.instance.return_value = self.mock_config
        
        flash = CameraFlash.instance()
        flash.fireFlash()
        
        # Verify no GPIO operations occurred
        mock_gpio.setmode.assert_not_called()
        mock_gpio.setup.assert_not_called()
        mock_gpio.output.assert_not_called()
    
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camflash.Configurator')
    def test_flash_off_enabled(self, mock_configurator_class, mock_gpio):
        """Test turning off flash when flash is enabled."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        flash = CameraFlash.instance()
        flash.flashOff()
        
        # Verify GPIO operations
        mock_gpio.setmode.assert_called_with(mock_gpio.BOARD)
        mock_gpio.setup.assert_called_with(18, mock_gpio.OUT)
        mock_gpio.output.assert_called_with(18, mock_gpio.LOW)
        mock_gpio.cleanup.assert_called_once()
    
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camflash.Configurator')
    def test_flash_off_disabled(self, mock_configurator_class, mock_gpio):
        """Test turning off flash when flash is disabled."""
        self.mock_config.getFlashDisposition.return_value = False
        mock_configurator_class.instance.return_value = self.mock_config
        
        flash = CameraFlash.instance()
        flash.flashOff()
        
        # Verify no GPIO operations occurred
        mock_gpio.setmode.assert_not_called()
        mock_gpio.setup.assert_not_called()
        mock_gpio.output.assert_not_called()
        mock_gpio.cleanup.assert_not_called()
    
    @patch('corecam.camflash.Configurator')
    def test_gpio_pin_configuration(self, mock_configurator_class):
        """Test GPIO pin configuration from config."""
        self.mock_config.getFlashGPIOAssignment.return_value = 22
        mock_configurator_class.instance.return_value = self.mock_config
        
        flash = CameraFlash.instance()
        
        self.assertEqual(flash.gpio_pin, 22)


class TestCameraIntegration(unittest.TestCase):
    """Integration tests for camera and flash components."""
    
    def setUp(self):
        """Set up test fixtures."""
        BoothCamera._BoothCamera__instance__ = None
        CameraFlash._CameraFlash__instance__ = None
        
        self.mock_config = Mock()
        self.mock_config.getResolution.return_value = (1920, 1080)
        self.mock_config.getPreviewAlpha.return_value = 200
        self.mock_config.getScreenWidth.return_value = 1024
        self.mock_config.getScreenHeight.return_value = 768
        self.mock_config.getISO.return_value = 400
        self.mock_config.getSharpness.return_value = 0
        self.mock_config.getDefaultImageFilename.return_value = "test.jpg"
        self.mock_config.getInstallDir.return_value = "/tmp"
        self.mock_config.getFlashOnTime.return_value = 0.1
        self.mock_config.getFlashGPIOAssignment.return_value = 18
        self.mock_config.getFlashDisposition.return_value = True
    
    def tearDown(self):
        """Clean up after tests."""
        BoothCamera._BoothCamera__instance__ = None
        CameraFlash._CameraFlash__instance__ = None
    
    @patch('corecam.camera.archiveImage')
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camera.Configurator')
    @patch('corecam.camera.time')
    def test_complete_photo_capture_workflow(self, mock_time, mock_configurator_class, mock_gpio, mock_archive):
        """Test complete photo capture workflow with flash."""
        mock_configurator_class.instance.return_value = self.mock_config
        mock_archive.return_value = ("archived.jpg", "fun.jpg")
        
        camera = BoothCamera.instance()
        
        with patch.object(camera, 'capture') as mock_capture:
            mock_capture.return_value = True
            
            result = camera.snap()
            
            # Verify flash sequence
            expected_calls = [
                call.setmode(mock_gpio.BOARD),
                call.setup(18, mock_gpio.OUT),
                call.output(18, mock_gpio.HIGH),  # Flash on
                call.setmode(mock_gpio.BOARD),
                call.setup(18, mock_gpio.OUT),
                call.output(18, mock_gpio.LOW),   # Flash off
                call.cleanup()
            ]
            
            mock_gpio.assert_has_calls(expected_calls)
            
            # Verify timing and capture
            mock_time.sleep.assert_called_once_with(0.1)
            mock_capture.assert_called_once_with("/tmp/test.jpg")
            
            # Verify result
            self.assertEqual(result, ("archived.jpg", "fun.jpg"))


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.DEBUG)
    
    # Run the tests
    unittest.main(verbosity=2)