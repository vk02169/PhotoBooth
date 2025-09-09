"""
Unit tests for the PhotoBooth upload module (uploaders/upload.py).

This module tests the upload functionality including Google Drive upload,
configuration-based upload decisions, and uploader lifecycle management.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock dependencies before importing
sys.modules['googledriveuploader'] = MagicMock()

from uploaders.upload import uploadImages, cleanupUploaders


class TestUploadFunctions(unittest.TestCase):
    """Test cases for upload module functions."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset global variables
        import uploaders.upload as upload_module
        upload_module.picasa_uploader = None
        upload_module.drive_uploader = None
        
        # Create mock configurator
        self.mock_config = Mock()
        self.mock_config.isUploadToPicasa.return_value = False
        self.mock_config.isUploadToDrive.return_value = False
        
        # Sample image array for testing
        self.test_images = [
            "/path/to/image1.jpg",
            "/path/to/image2.jpg",
            "/path/to/image3.jpg"
        ]
    
    def tearDown(self):
        """Clean up after each test method."""
        # Reset global variables
        import uploaders.upload as upload_module
        upload_module.picasa_uploader = None
        upload_module.drive_uploader = None
    
    @patch('uploaders.upload.Configurator')
    @patch('uploaders.upload.logging')
    def test_upload_images_no_uploads_configured(self, mock_logging, mock_configurator_class):
        """Test uploadImages when no upload services are configured."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        uploadImages(self.test_images)
        
        # Verify configuration was checked
        self.mock_config.isUploadToPicasa.assert_called_once()
        self.mock_config.isUploadToDrive.assert_called_once()
        
        # Verify appropriate log messages
        mock_logging.info.assert_any_call("Upload to Picasa OFF in configuration")
        mock_logging.info.assert_any_call("Upload to Google OFF in configuration")
    
    @patch('uploaders.upload.Configurator')
    @patch('uploaders.upload.logging')
    def test_upload_images_picasa_enabled(self, mock_logging, mock_configurator_class):
        """Test uploadImages when Picasa upload is enabled."""
        self.mock_config.isUploadToPicasa.return_value = True
        mock_configurator_class.instance.return_value = self.mock_config
        
        uploadImages(self.test_images)
        
        # Verify Picasa upload was logged (but not actually executed due to commented code)
        mock_logging.info.assert_any_call("Uploading to Picasa...")
        mock_logging.info.assert_any_call("Upload to Google OFF in configuration")
    
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('uploaders.upload.Configurator')
    @patch('uploaders.upload.logging')
    def test_upload_images_drive_enabled(self, mock_logging, mock_configurator_class, mock_drive_uploader_class):
        """Test uploadImages when Google Drive upload is enabled."""
        self.mock_config.isUploadToDrive.return_value = True
        mock_configurator_class.instance.return_value = self.mock_config
        
        # Mock the GoogleDriveUploader
        mock_drive_uploader = Mock()
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        uploadImages(self.test_images)
        
        # Verify Google Drive uploader was created and used
        mock_drive_uploader_class.instance.assert_called_once()
        mock_drive_uploader.kickOff.assert_called_once_with(self.test_images)
        
        # Verify appropriate log messages
        mock_logging.info.assert_any_call("Uploading to Google Drive...")
        mock_logging.info.assert_any_call("Upload to Picasa OFF in configuration")
    
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('uploaders.upload.Configurator')
    @patch('uploaders.upload.logging')
    def test_upload_images_both_enabled(self, mock_logging, mock_configurator_class, mock_drive_uploader_class):
        """Test uploadImages when both upload services are enabled."""
        self.mock_config.isUploadToPicasa.return_value = True
        self.mock_config.isUploadToDrive.return_value = True
        mock_configurator_class.instance.return_value = self.mock_config
        
        # Mock the GoogleDriveUploader
        mock_drive_uploader = Mock()
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        uploadImages(self.test_images)
        
        # Verify both services were attempted
        mock_logging.info.assert_any_call("Uploading to Picasa...")
        mock_logging.info.assert_any_call("Uploading to Google Drive...")
        
        # Verify Google Drive uploader was used
        mock_drive_uploader.kickOff.assert_called_once_with(self.test_images)
    
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('uploaders.upload.Configurator')
    def test_upload_images_drive_uploader_singleton(self, mock_configurator_class, mock_drive_uploader_class):
        """Test that GoogleDriveUploader is created only once (singleton pattern)."""
        self.mock_config.isUploadToDrive.return_value = True
        mock_configurator_class.instance.return_value = self.mock_config
        
        mock_drive_uploader = Mock()
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        # Call uploadImages multiple times
        uploadImages(self.test_images)
        uploadImages(self.test_images)
        uploadImages(self.test_images)
        
        # Verify GoogleDriveUploader.instance() was called only once
        mock_drive_uploader_class.instance.assert_called_once()
        
        # Verify kickOff was called multiple times with the same uploader instance
        self.assertEqual(mock_drive_uploader.kickOff.call_count, 3)
    
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('uploaders.upload.Configurator')
    def test_upload_images_empty_array(self, mock_configurator_class, mock_drive_uploader_class):
        """Test uploadImages with empty image array."""
        self.mock_config.isUploadToDrive.return_value = True
        mock_configurator_class.instance.return_value = self.mock_config
        
        mock_drive_uploader = Mock()
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        uploadImages([])
        
        # Should still call kickOff with empty array
        mock_drive_uploader.kickOff.assert_called_once_with([])
    
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('uploaders.upload.Configurator')
    def test_upload_images_none_array(self, mock_configurator_class, mock_drive_uploader_class):
        """Test uploadImages with None as image array."""
        self.mock_config.isUploadToDrive.return_value = True
        mock_configurator_class.instance.return_value = self.mock_config
        
        mock_drive_uploader = Mock()
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        uploadImages(None)
        
        # Should still call kickOff with None
        mock_drive_uploader.kickOff.assert_called_once_with(None)
    
    def test_cleanup_uploaders_no_uploaders(self):
        """Test cleanupUploaders when no uploaders have been created."""
        # Should not raise any exceptions
        cleanupUploaders()
    
    def test_cleanup_uploaders_with_drive_uploader(self):
        """Test cleanupUploaders when drive uploader exists."""
        import uploaders.upload as upload_module
        
        # Create mock uploader and assign to global variable
        mock_drive_uploader = Mock()
        upload_module.drive_uploader = mock_drive_uploader
        
        cleanupUploaders()
        
        # Verify cleanup was called
        mock_drive_uploader.cleanup.assert_called_once()
    
    def test_cleanup_uploaders_with_picasa_uploader(self):
        """Test cleanupUploaders when picasa uploader exists."""
        import uploaders.upload as upload_module
        
        # Create mock uploader and assign to global variable
        mock_picasa_uploader = Mock()
        upload_module.picasa_uploader = mock_picasa_uploader
        
        cleanupUploaders()
        
        # Verify cleanup was called
        mock_picasa_uploader.cleanup.assert_called_once()
    
    def test_cleanup_uploaders_with_both_uploaders(self):
        """Test cleanupUploaders when both uploaders exist."""
        import uploaders.upload as upload_module
        
        # Create mock uploaders and assign to global variables
        mock_picasa_uploader = Mock()
        mock_drive_uploader = Mock()
        upload_module.picasa_uploader = mock_picasa_uploader
        upload_module.drive_uploader = mock_drive_uploader
        
        cleanupUploaders()
        
        # Verify cleanup was called on both
        mock_picasa_uploader.cleanup.assert_called_once()
        mock_drive_uploader.cleanup.assert_called_once()
    
    def test_cleanup_uploaders_exception_handling(self):
        """Test cleanupUploaders handles exceptions gracefully."""
        import uploaders.upload as upload_module
        
        # Create mock uploader that raises exception on cleanup
        mock_drive_uploader = Mock()
        mock_drive_uploader.cleanup.side_effect = Exception("Cleanup failed")
        upload_module.drive_uploader = mock_drive_uploader
        
        # Should not raise exception
        try:
            cleanupUploaders()
        except Exception:
            self.fail("cleanupUploaders should handle exceptions gracefully")


class TestUploadIntegration(unittest.TestCase):
    """Integration tests for upload functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Reset global variables
        import uploaders.upload as upload_module
        upload_module.picasa_uploader = None
        upload_module.drive_uploader = None
        
        self.test_images = [
            "/tmp/photo1.jpg",
            "/tmp/photo2.jpg"
        ]
    
    def tearDown(self):
        """Clean up after tests."""
        import uploaders.upload as upload_module
        upload_module.picasa_uploader = None
        upload_module.drive_uploader = None
    
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('uploaders.upload.Configurator')
    @patch('uploaders.upload.logging')
    def test_complete_upload_workflow(self, mock_logging, mock_configurator_class, mock_drive_uploader_class):
        """Test complete upload workflow from start to cleanup."""
        # Configure mocks
        mock_config = Mock()
        mock_config.isUploadToPicasa.return_value = False
        mock_config.isUploadToDrive.return_value = True
        mock_configurator_class.instance.return_value = mock_config
        
        mock_drive_uploader = Mock()
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        # Execute workflow
        uploadImages(self.test_images)
        cleanupUploaders()
        
        # Verify complete workflow
        mock_drive_uploader.kickOff.assert_called_once_with(self.test_images)
        mock_drive_uploader.cleanup.assert_called_once()
        
        # Verify logging
        mock_logging.info.assert_any_call("Uploading to Google Drive...")
        mock_logging.info.assert_any_call("Upload to Picasa OFF in configuration")
    
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('uploaders.upload.Configurator')
    def test_multiple_upload_sessions(self, mock_configurator_class, mock_drive_uploader_class):
        """Test multiple upload sessions with the same uploader instance."""
        # Configure mocks
        mock_config = Mock()
        mock_config.isUploadToPicasa.return_value = False
        mock_config.isUploadToDrive.return_value = True
        mock_configurator_class.instance.return_value = mock_config
        
        mock_drive_uploader = Mock()
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        # Execute multiple upload sessions
        session1_images = ["/tmp/session1_photo1.jpg", "/tmp/session1_photo2.jpg"]
        session2_images = ["/tmp/session2_photo1.jpg"]
        session3_images = ["/tmp/session3_photo1.jpg", "/tmp/session3_photo2.jpg", "/tmp/session3_photo3.jpg"]
        
        uploadImages(session1_images)
        uploadImages(session2_images)
        uploadImages(session3_images)
        
        # Verify uploader was created only once
        mock_drive_uploader_class.instance.assert_called_once()
        
        # Verify all sessions were uploaded
        expected_calls = [
            unittest.mock.call(session1_images),
            unittest.mock.call(session2_images),
            unittest.mock.call(session3_images)
        ]
        mock_drive_uploader.kickOff.assert_has_calls(expected_calls)
        
        # Cleanup
        cleanupUploaders()
        mock_drive_uploader.cleanup.assert_called_once()
    
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('uploaders.upload.Configurator')
    def test_configuration_changes_during_runtime(self, mock_configurator_class, mock_drive_uploader_class):
        """Test behavior when configuration changes during runtime."""
        mock_config = Mock()
        mock_configurator_class.instance.return_value = mock_config
        
        mock_drive_uploader = Mock()
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        # First call with drive upload enabled
        mock_config.isUploadToPicasa.return_value = False
        mock_config.isUploadToDrive.return_value = True
        uploadImages(self.test_images)
        
        # Second call with drive upload disabled
        mock_config.isUploadToDrive.return_value = False
        uploadImages(self.test_images)
        
        # Verify uploader was created and used only once
        mock_drive_uploader_class.instance.assert_called_once()
        mock_drive_uploader.kickOff.assert_called_once_with(self.test_images)


class TestUploadErrorHandling(unittest.TestCase):
    """Test error handling in upload functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        import uploaders.upload as upload_module
        upload_module.picasa_uploader = None
        upload_module.drive_uploader = None
    
    def tearDown(self):
        """Clean up after tests."""
        import uploaders.upload as upload_module
        upload_module.picasa_uploader = None
        upload_module.drive_uploader = None
    
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('uploaders.upload.Configurator')
    def test_uploader_creation_failure(self, mock_configurator_class, mock_drive_uploader_class):
        """Test handling of uploader creation failure."""
        mock_config = Mock()
        mock_config.isUploadToPicasa.return_value = False
        mock_config.isUploadToDrive.return_value = True
        mock_configurator_class.instance.return_value = mock_config
        
        # Make uploader creation fail
        mock_drive_uploader_class.instance.side_effect = Exception("Failed to create uploader")
        
        # Should handle exception gracefully
        with self.assertRaises(Exception):
            uploadImages(self.test_images)
    
    @patch('uploaders.upload.GoogleDriveUploader')
    @patch('uploaders.upload.Configurator')
    def test_upload_kickoff_failure(self, mock_configurator_class, mock_drive_uploader_class):
        """Test handling of upload kickoff failure."""
        mock_config = Mock()
        mock_config.isUploadToPicasa.return_value = False
        mock_config.isUploadToDrive.return_value = True
        mock_configurator_class.instance.return_value = mock_config
        
        mock_drive_uploader = Mock()
        mock_drive_uploader.kickOff.side_effect = Exception("Upload failed")
        mock_drive_uploader_class.instance.return_value = mock_drive_uploader
        
        # Should propagate the exception
        with self.assertRaises(Exception):
            uploadImages(self.test_images)
    
    @patch('uploaders.upload.Configurator')
    def test_configuration_access_failure(self, mock_configurator_class):
        """Test handling of configuration access failure."""
        # Make configurator fail
        mock_configurator_class.instance.side_effect = Exception("Config error")
        
        # Should propagate the exception
        with self.assertRaises(Exception):
            uploadImages(self.test_images)


if __name__ == '__main__':
    unittest.main(verbosity=2)