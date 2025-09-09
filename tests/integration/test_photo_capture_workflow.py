"""
Integration tests for the complete PhotoBooth photo capture workflow.

This module tests the end-to-end functionality of taking photos,
including camera initialization, flash control, image capture,
archiving, and upload processes.
"""

import unittest
import tempfile
import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock, call

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock hardware and GUI dependencies
sys.modules['picamera'] = MagicMock()
sys.modules['RPi'] = MagicMock()
sys.modules['RPi.GPIO'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['resizeimage'] = MagicMock()
sys.modules['googledriveuploader'] = MagicMock()


class TestPhotoCapturWorkflow(unittest.TestCase):
    """Integration tests for complete photo capture workflow."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset singleton instances
        from corecam.camera import BoothCamera
        from corecam.camflash import CameraFlash
        BoothCamera._BoothCamera__instance__ = None
        CameraFlash._CameraFlash__instance__ = None
        
        # Reset upload module globals
        import uploaders.upload as upload_module
        upload_module.picasa_uploader = None
        upload_module.drive_uploader = None
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock configuration
        self.mock_config = Mock()
        self.setup_default_config()
        
        # Create test image files
        self.create_test_images()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Reset singleton instances
        from corecam.camera import BoothCamera
        from corecam.camflash import CameraFlash
        BoothCamera._BoothCamera__instance__ = None
        CameraFlash._CameraFlash__instance__ = None
        
        # Reset upload module globals
        import uploaders.upload as upload_module
        upload_module.picasa_uploader = None
        upload_module.drive_uploader = None
        
        # Clean up temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def setup_default_config(self):
        """Set up default configuration values."""
        # Camera configuration
        self.mock_config.getResolution.return_value = (1920, 1080)
        self.mock_config.getPreviewAlpha.return_value = 200
        self.mock_config.getScreenWidth.return_value = 1024
        self.mock_config.getScreenHeight.return_value = 768
        self.mock_config.getISO.return_value = 400
        self.mock_config.getSharpness.return_value = 0
        
        # File configuration
        self.mock_config.getDefaultImageFilename.return_value = "photobooth_image.jpg"
        self.mock_config.getInstallDir.return_value = self.temp_dir
        self.mock_config.getArchiveDir.return_value = os.path.join(self.temp_dir, "archive")
        self.mock_config.getModuloBase.return_value = 10
        
        # Flash configuration
        self.mock_config.getFlashDisposition.return_value = True
        self.mock_config.getFlashGPIOAssignment.return_value = 18
        self.mock_config.getFlashOnTime.return_value = 0.1
        
        # Upload configuration
        self.mock_config.isUploadToPicasa.return_value = False
        self.mock_config.isUploadToDrive.return_value = True
        
        # Fun command configuration
        self.mock_config.getFunCommand.return_value = "convert {0} -sepia-tone 80% {1}"
        
        # GUI configuration
        self.mock_config.getCountdownText.return_value = ["3", "2", "1", "SMILE!"]
        self.mock_config.getNumPics.return_value = 4
    
    def create_test_images(self):
        """Create test image files."""
        # Create archive directory
        archive_dir = os.path.join(self.temp_dir, "archive")
        os.makedirs(archive_dir, exist_ok=True)
        
        # Create a test image file
        self.test_image_path = os.path.join(self.temp_dir, "photobooth_image.jpg")
        with open(self.test_image_path, 'w') as f:
            f.write("fake image data")
    
    @patch('coregui.util.archiveImage')
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camera.Configurator')
    @patch('uploaders.upload.Configurator')
    @patch('corecam.camera.time')
    def test_complete_single_photo_workflow(self, mock_time, mock_upload_config, 
                                          mock_camera_config, mock_gpio, 
                                          mock_drive_uploader_class, mock_archive):
        """Test complete workflow for taking a single photo."""
        # Setup mocks
        mock_camera_config.instance.return_value = self.mock_config
        mock_upload_config.instance.return_value = self.mock_config
        
        mock_archive.return_value = ("archived_image_001.jpg", "fun_image_001.jpg")
        
        mock_drive_uploader = Mock()
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        # Import modules after mocking
        from corecam.camera import BoothCamera
        from uploaders.upload import uploadImages
        
        # Execute workflow
        camera = BoothCamera.instance()
        
        # Mock the capture method
        with patch.object(camera, 'capture') as mock_capture:
            mock_capture.return_value = True
            
            # Take photo
            result = camera.snap()
            
            # Upload the result
            if result:
                archived_file, fun_file = result
                uploadImages([archived_file, fun_file])
        
        # Verify camera operations
        mock_capture.assert_called_once_with(self.test_image_path)
        
        # Verify flash sequence
        expected_gpio_calls = [
            call.setmode(mock_gpio.BOARD),
            call.setup(18, mock_gpio.OUT),
            call.output(18, mock_gpio.HIGH),  # Flash on
            call.setmode(mock_gpio.BOARD),
            call.setup(18, mock_gpio.OUT),
            call.output(18, mock_gpio.LOW),   # Flash off
            call.cleanup()
        ]
        mock_gpio.assert_has_calls(expected_gpio_calls)
        
        # Verify timing
        mock_time.sleep.assert_called_once_with(0.1)
        
        # Verify archiving
        mock_archive.assert_called_once_with(self.test_image_path)
        
        # Verify upload
        mock_drive_uploader.kickOff.assert_called_once_with(["archived_image_001.jpg", "fun_image_001.jpg"])
    
    @patch('coregui.util.archiveImage')
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camera.Configurator')
    @patch('uploaders.upload.Configurator')
    @patch('corecam.camera.time')
    def test_multiple_photos_workflow(self, mock_time, mock_upload_config,
                                    mock_camera_config, mock_gpio,
                                    mock_drive_uploader_class, mock_archive):
        """Test workflow for taking multiple photos in sequence."""
        # Setup mocks
        mock_camera_config.instance.return_value = self.mock_config
        mock_upload_config.instance.return_value = self.mock_config
        
        # Mock archive to return different filenames for each photo
        mock_archive.side_effect = [
            ("archived_001.jpg", "fun_001.jpg"),
            ("archived_002.jpg", "fun_002.jpg"),
            ("archived_003.jpg", "fun_003.jpg"),
            ("archived_004.jpg", "fun_004.jpg")
        ]
        
        mock_drive_uploader = Mock()
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        # Import modules
        from corecam.camera import BoothCamera
        from uploaders.upload import uploadImages
        
        # Execute workflow for multiple photos
        camera = BoothCamera.instance()
        all_photos = []
        
        with patch.object(camera, 'capture') as mock_capture:
            mock_capture.return_value = True
            
            # Take 4 photos
            for i in range(4):
                result = camera.snap()
                if result:
                    all_photos.extend(result)
            
            # Upload all photos at once
            uploadImages(all_photos)
        
        # Verify multiple captures
        self.assertEqual(mock_capture.call_count, 4)
        
        # Verify multiple flash sequences
        self.assertEqual(mock_gpio.output.call_count, 8)  # 4 on + 4 off
        
        # Verify multiple archive operations
        self.assertEqual(mock_archive.call_count, 4)
        
        # Verify upload with all photos
        expected_photos = [
            "archived_001.jpg", "fun_001.jpg",
            "archived_002.jpg", "fun_002.jpg", 
            "archived_003.jpg", "fun_003.jpg",
            "archived_004.jpg", "fun_004.jpg"
        ]
        mock_drive_uploader.kickOff.assert_called_once_with(expected_photos)
    
    @patch('coregui.util.archiveImage')
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camera.Configurator')
    @patch('uploaders.upload.Configurator')
    @patch('corecam.camera.time')
    def test_workflow_with_flash_disabled(self, mock_time, mock_upload_config,
                                        mock_camera_config, mock_gpio, mock_archive):
        """Test workflow when flash is disabled."""
        # Disable flash in configuration
        self.mock_config.getFlashDisposition.return_value = False
        
        mock_camera_config.instance.return_value = self.mock_config
        mock_upload_config.instance.return_value = self.mock_config
        mock_archive.return_value = ("archived.jpg", "fun.jpg")
        
        # Import modules
        from corecam.camera import BoothCamera
        
        # Execute workflow
        camera = BoothCamera.instance()
        
        with patch.object(camera, 'capture') as mock_capture:
            mock_capture.return_value = True
            result = camera.snap()
        
        # Verify no GPIO operations for flash
        mock_gpio.setmode.assert_not_called()
        mock_gpio.setup.assert_not_called()
        mock_gpio.output.assert_not_called()
        mock_gpio.cleanup.assert_not_called()
        
        # Verify capture still occurred
        mock_capture.assert_called_once()
        
        # Verify archiving still occurred
        mock_archive.assert_called_once()
    
    @patch('coregui.util.archiveImage')
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camera.Configurator')
    @patch('uploaders.upload.Configurator')
    @patch('corecam.camera.time')
    def test_workflow_with_uploads_disabled(self, mock_time, mock_upload_config,
                                          mock_camera_config, mock_gpio, mock_archive):
        """Test workflow when all uploads are disabled."""
        # Disable all uploads
        self.mock_config.isUploadToPicasa.return_value = False
        self.mock_config.isUploadToDrive.return_value = False
        
        mock_camera_config.instance.return_value = self.mock_config
        mock_upload_config.instance.return_value = self.mock_config
        mock_archive.return_value = ("archived.jpg", "fun.jpg")
        
        # Import modules
        from corecam.camera import BoothCamera
        from uploaders.upload import uploadImages
        
        # Execute workflow
        camera = BoothCamera.instance()
        
        with patch.object(camera, 'capture') as mock_capture:
            mock_capture.return_value = True
            result = camera.snap()
            
            # Try to upload (should do nothing)
            if result:
                uploadImages(list(result))
        
        # Verify photo was taken and archived
        mock_capture.assert_called_once()
        mock_archive.assert_called_once()
        
        # Verify flash operations occurred
        mock_gpio.output.assert_any_call(18, mock_gpio.HIGH)
        mock_gpio.output.assert_any_call(18, mock_gpio.LOW)
    
    @patch('coregui.util.printExceptionTrace')
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camera.Configurator')
    @patch('corecam.camera.time')
    def test_workflow_with_camera_error(self, mock_time, mock_camera_config,
                                      mock_gpio, mock_print_exception):
        """Test workflow when camera capture fails."""
        mock_camera_config.instance.return_value = self.mock_config
        
        # Import modules
        from corecam.camera import BoothCamera
        
        # Execute workflow with camera error
        camera = BoothCamera.instance()
        
        with patch.object(camera, 'capture') as mock_capture:
            mock_capture.side_effect = Exception("Camera hardware error")
            
            result = camera.snap()
        
        # Verify error handling
        mock_print_exception.assert_called_once()
        self.assertIsNone(result)
        
        # Verify flash was still attempted
        mock_gpio.output.assert_any_call(18, mock_gpio.HIGH)
        mock_gpio.output.assert_any_call(18, mock_gpio.LOW)
    
    @patch('coregui.util.archiveImage')
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camera.Configurator')
    @patch('uploaders.upload.Configurator')
    @patch('corecam.camera.time')
    def test_workflow_with_upload_error(self, mock_time, mock_upload_config,
                                      mock_camera_config, mock_gpio,
                                      mock_drive_uploader_class, mock_archive):
        """Test workflow when upload fails."""
        mock_camera_config.instance.return_value = self.mock_config
        mock_upload_config.instance.return_value = self.mock_config
        mock_archive.return_value = ("archived.jpg", "fun.jpg")
        
        # Make upload fail
        mock_drive_uploader = Mock()
        mock_drive_uploader.kickOff.side_effect = Exception("Upload failed")
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        # Import modules
        from corecam.camera import BoothCamera
        from uploaders.upload import uploadImages
        
        # Execute workflow
        camera = BoothCamera.instance()
        
        with patch.object(camera, 'capture') as mock_capture:
            mock_capture.return_value = True
            result = camera.snap()
            
            # Upload should fail
            with self.assertRaises(Exception):
                uploadImages(list(result))
        
        # Verify photo was taken successfully
        mock_capture.assert_called_once()
        mock_archive.assert_called_once()
        
        # Verify upload was attempted
        mock_drive_uploader.kickOff.assert_called_once()


class TestPhotoBoothGUIIntegration(unittest.TestCase):
    """Integration tests for GUI components with photo capture."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_canvas = Mock()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_countdown_before_photo_capture(self, mock_clear_canvas, mock_sleep):
        """Test countdown display before photo capture."""
        from coregui.util import CountdownText
        
        # Simulate countdown before photo
        countdown = CountdownText(
            text="3,2,1,SMILE!",
            font=("Arial", 48, "bold"),
            fill="white",
            canvas=self.mock_canvas,
            x=512,
            y=384
        )
        
        # Verify countdown was displayed
        self.assertTrue(self.mock_canvas.create_text.called)
        self.assertTrue(self.mock_canvas.update.called)
        self.assertTrue(mock_sleep.called)
        self.assertTrue(mock_clear_canvas.called)
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_blinking_text_after_photo(self, mock_clear_canvas, mock_sleep):
        """Test blinking text display after photo capture."""
        from coregui.util import BlinkingText
        
        # Simulate blinking text after photo
        blinking = BlinkingText(
            text="Photo Saved!",
            font=("Arial", 32, "bold"),
            fill="green",
            blink_freq=0.5,
            num_blinks=3,
            canvas=self.mock_canvas,
            x=512,
            y=400
        )
        
        # Verify blinking text was displayed
        self.assertTrue(self.mock_canvas.create_text.called)
        self.assertTrue(self.mock_canvas.update.called)


class TestPhotoBoothSystemIntegration(unittest.TestCase):
    """System-level integration tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Reset all singletons
        from corecam.camera import BoothCamera
        from corecam.camflash import CameraFlash
        BoothCamera._BoothCamera__instance__ = None
        CameraFlash._CameraFlash__instance__ = None
        
        import uploaders.upload as upload_module
        upload_module.picasa_uploader = None
        upload_module.drive_uploader = None
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('coregui.util.archiveImage')
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('corecam.camflash.GPIO')
    @patch('corecam.camera.Configurator')
    @patch('uploaders.upload.Configurator')
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    @patch('corecam.camera.time')
    def test_complete_photobooth_session(self, mock_camera_time, mock_clear_canvas,
                                       mock_gui_sleep, mock_upload_config,
                                       mock_camera_config, mock_gpio,
                                       mock_drive_uploader_class, mock_archive):
        """Test a complete PhotoBooth session with GUI and photo capture."""
        # Setup configuration
        mock_config = Mock()
        mock_config.getResolution.return_value = (1920, 1080)
        mock_config.getPreviewAlpha.return_value = 200
        mock_config.getScreenWidth.return_value = 1024
        mock_config.getScreenHeight.return_value = 768
        mock_config.getISO.return_value = 400
        mock_config.getSharpness.return_value = 0
        mock_config.getDefaultImageFilename.return_value = "session_photo.jpg"
        mock_config.getInstallDir.return_value = self.temp_dir
        mock_config.getFlashDisposition.return_value = True
        mock_config.getFlashGPIOAssignment.return_value = 18
        mock_config.getFlashOnTime.return_value = 0.1
        mock_config.isUploadToPicasa.return_value = False
        mock_config.isUploadToDrive.return_value = True
        mock_config.getNumPics.return_value = 4
        
        mock_camera_config.instance.return_value = mock_config
        mock_upload_config.instance.return_value = mock_config
        
        # Setup archive mock
        mock_archive.side_effect = [
            (f"archived_{i:03d}.jpg", f"fun_{i:03d}.jpg") for i in range(1, 5)
        ]
        
        # Setup upload mock
        mock_drive_uploader = Mock()
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        # Import modules
        from corecam.camera import BoothCamera
        from coregui.util import CountdownText, BlinkingText
        from uploaders.upload import uploadImages, cleanupUploaders
        
        # Simulate complete session
        mock_canvas = Mock()
        camera = BoothCamera.instance()
        session_photos = []
        
        with patch.object(camera, 'capture') as mock_capture:
            mock_capture.return_value = True
            
            # Show countdown
            countdown = CountdownText(
                text="3,2,1",
                font=("Arial", 48),
                fill="white",
                canvas=mock_canvas,
                x=512,
                y=384
            )
            
            # Take photos
            for i in range(4):
                result = camera.snap()
                if result:
                    session_photos.extend(result)
            
            # Show completion message
            completion = BlinkingText(
                text="Session Complete!",
                font=("Arial", 32),
                fill="green",
                blink_freq=0.5,
                num_blinks=3,
                canvas=mock_canvas,
                x=512,
                y=400
            )
            
            # Upload photos
            uploadImages(session_photos)
            
            # Cleanup
            cleanupUploaders()
        
        # Verify complete workflow
        self.assertEqual(mock_capture.call_count, 4)
        self.assertEqual(mock_archive.call_count, 4)
        mock_drive_uploader.kickOff.assert_called_once_with(session_photos)
        mock_drive_uploader.cleanup.assert_called_once()
        
        # Verify GUI interactions
        self.assertTrue(mock_canvas.create_text.called)
        self.assertTrue(mock_canvas.update.called)
        
        # Verify expected number of photos
        self.assertEqual(len(session_photos), 8)  # 4 archived + 4 fun versions


if __name__ == '__main__':
    unittest.main(verbosity=2)