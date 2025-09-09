"""
Unit tests for the PhotoBooth configuration module (camconfig.py).

This module tests the Configurator class which manages all application
configuration including camera settings, display settings, and file paths.
"""

import unittest
import tempfile
import os
import sys
import configparser
from unittest.mock import Mock, patch, MagicMock, mock_open

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock tkinter before importing
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()

from coregui.camconfig import Configurator


class TestConfigurator(unittest.TestCase):
    """Test cases for the Configurator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset singleton instance
        Configurator._Configurator__instance = None
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.temp_dir, "test_config.conf")
        
        # Sample configuration content
        self.sample_config = """
[PHOTO]
countdown_text = 3,2,1,SMILE!
num_pics = 4
archive_dir = /home/pi/photobooth/archive
modulo_base = 10
screen_width = 1024
screen_height = 768
show_exit_configure_btns = True

[CAMERA_ATTRIBUTES]
res_pixels_X = 1920
res_pixels_Y = 1080
base_image_ext = .jpg
preview_alpha = 200
iso = 400
sharpness = 0

[FLASH]
flash_disposition = True
flash_gpio_assignment = 18
flash_on_time = 0.1

[FUN_STUFF]
fun_cmd = convert {0} -sepia-tone 80% {1}

[UPLOAD]
upload_disposition = True
upload_service = googledrive
"""
    
    def tearDown(self):
        """Clean up after each test method."""
        # Reset singleton instance
        Configurator._Configurator__instance = None
        
        # Clean up temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_singleton_pattern(self):
        """Test that Configurator follows singleton pattern correctly."""
        config1 = Configurator.instance()
        config2 = Configurator.instance()
        
        self.assertIs(config1, config2)
        self.assertIsInstance(config1, Configurator)
    
    @patch('coregui.camconfig.os.path.exists')
    def test_initialization_with_existing_config(self, mock_exists):
        """Test initialization when configuration file exists."""
        mock_exists.return_value = True
        
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            config = Configurator.instance()
            
            # Verify config parser was initialized
            self.assertIsInstance(config.config, configparser.ConfigParser)
    
    @patch('coregui.camconfig.os.path.exists')
    def test_initialization_without_config(self, mock_exists):
        """Test initialization when configuration file doesn't exist."""
        mock_exists.return_value = False
        
        with patch.object(Configurator, 'createDefaultConfiguration') as mock_create_default:
            config = Configurator.instance()
            mock_create_default.assert_called_once()
    
    def test_get_resolution(self):
        """Test getting camera resolution from configuration."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                resolution = config.getResolution()
                self.assertEqual(resolution, (1920, 1080))
    
    def test_get_preview_alpha(self):
        """Test getting preview alpha value."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                alpha = config.getPreviewAlpha()
                self.assertEqual(alpha, 200)
    
    def test_get_screen_dimensions(self):
        """Test getting screen width and height."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                width = config.getScreenWidth()
                height = config.getScreenHeight()
                
                self.assertEqual(width, 1024)
                self.assertEqual(height, 768)
    
    def test_get_camera_attributes(self):
        """Test getting various camera attributes."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                iso = config.getISO()
                sharpness = config.getSharpness()
                
                self.assertEqual(iso, 400)
                self.assertEqual(sharpness, 0)
    
    def test_get_flash_configuration(self):
        """Test getting flash-related configuration."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                flash_disposition = config.getFlashDisposition()
                gpio_pin = config.getFlashGPIOAssignment()
                flash_time = config.getFlashOnTime()
                
                self.assertTrue(flash_disposition)
                self.assertEqual(gpio_pin, 18)
                self.assertEqual(flash_time, 0.1)
    
    def test_get_photo_configuration(self):
        """Test getting photo-related configuration."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                num_pics = config.getNumPics()
                archive_dir = config.getArchiveDir()
                modulo_base = config.getModuloBase()
                
                self.assertEqual(num_pics, 4)
                self.assertEqual(archive_dir, "/home/pi/photobooth/archive")
                self.assertEqual(modulo_base, 10)
    
    def test_get_countdown_text(self):
        """Test getting countdown text configuration."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                countdown_text = config.getCountdownText()
                expected = ["3", "2", "1", "SMILE!"]
                self.assertEqual(countdown_text, expected)
    
    def test_get_fun_command(self):
        """Test getting fun command for image processing."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                fun_cmd = config.getFunCommand()
                expected = "convert {0} -sepia-tone 80% {1}"
                self.assertEqual(fun_cmd, expected)
    
    def test_get_upload_configuration(self):
        """Test getting upload-related configuration."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                upload_disposition = config.getUploadDisposition()
                upload_service = config.getUploadService()
                
                self.assertTrue(upload_disposition)
                self.assertEqual(upload_service, "googledrive")
    
    def test_get_default_image_filename(self):
        """Test getting default image filename."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                filename = config.getDefaultImageFilename()
                # Should combine base name with extension
                self.assertTrue(filename.endswith('.jpg'))
    
    def test_get_install_dir(self):
        """Test getting installation directory."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                with patch('os.getcwd', return_value='/home/pi/photobooth'):
                    config = Configurator.instance()
                    
                    install_dir = config.getInstallDir()
                    self.assertEqual(install_dir, '/home/pi/photobooth')
    
    def test_show_buttons_configuration(self):
        """Test getting show buttons configuration."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                show_buttons = config.getShowButtons()
                self.assertTrue(show_buttons)
    
    def test_configuration_with_missing_values(self):
        """Test configuration handling when some values are missing."""
        incomplete_config = """
[PHOTO]
num_pics = 2

[CAMERA_ATTRIBUTES]
res_pixels_X = 1280
"""
        
        with patch('builtins.open', mock_open(read_data=incomplete_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                # Should handle missing values gracefully
                num_pics = config.getNumPics()
                self.assertEqual(num_pics, 2)
                
                # Missing values should return defaults or raise appropriate errors
                with self.assertRaises((configparser.NoOptionError, configparser.NoSectionError)):
                    config.getFlashDisposition()
    
    def test_boolean_configuration_parsing(self):
        """Test parsing of boolean configuration values."""
        bool_config = """
[PHOTO]
show_exit_configure_btns = False

[FLASH]
flash_disposition = True

[UPLOAD]
upload_disposition = false
"""
        
        with patch('builtins.open', mock_open(read_data=bool_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                show_buttons = config.getShowButtons()
                flash_disposition = config.getFlashDisposition()
                upload_disposition = config.getUploadDisposition()
                
                self.assertFalse(show_buttons)
                self.assertTrue(flash_disposition)
                self.assertFalse(upload_disposition)
    
    def test_numeric_configuration_parsing(self):
        """Test parsing of numeric configuration values."""
        numeric_config = """
[PHOTO]
num_pics = 6
modulo_base = 5
screen_width = 800
screen_height = 600

[CAMERA_ATTRIBUTES]
iso = 800
sharpness = 25
preview_alpha = 150

[FLASH]
flash_gpio_assignment = 22
flash_on_time = 0.2
"""
        
        with patch('builtins.open', mock_open(read_data=numeric_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                # Test integer values
                self.assertEqual(config.getNumPics(), 6)
                self.assertEqual(config.getModuloBase(), 5)
                self.assertEqual(config.getScreenWidth(), 800)
                self.assertEqual(config.getScreenHeight(), 600)
                self.assertEqual(config.getISO(), 800)
                self.assertEqual(config.getSharpness(), 25)
                self.assertEqual(config.getPreviewAlpha(), 150)
                self.assertEqual(config.getFlashGPIOAssignment(), 22)
                
                # Test float values
                self.assertEqual(config.getFlashOnTime(), 0.2)
    
    @patch('coregui.camconfig.os.path.exists')
    def test_create_default_configuration(self, mock_exists):
        """Test creation of default configuration file."""
        mock_exists.return_value = False
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch.object(Configurator, 'saveConfiguration') as mock_save:
                config = Configurator.instance()
                
                # Verify default configuration was created
                mock_save.assert_called_once()
    
    def test_save_configuration(self):
        """Test saving configuration to file."""
        with patch('builtins.open', mock_open(read_data=self.sample_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                # Mock the file writing
                with patch('builtins.open', mock_open()) as mock_file:
                    config.saveConfiguration()
                    
                    # Verify file was opened for writing
                    mock_file.assert_called_once()
    
    def test_configuration_file_path(self):
        """Test configuration file path handling."""
        config = Configurator.instance()
        
        # Test default configuration filename
        self.assertEqual(config.conf_filename, "vkphotobooth.conf")
    
    def test_section_and_option_constants(self):
        """Test that configuration section and option constants are defined."""
        # Test section constants
        self.assertEqual(Configurator.CONF_PHOTO_SECTION, "PHOTO")
        self.assertEqual(Configurator.CONF_CAMERA_SECTION, "CAMERA_ATTRIBUTES")
        self.assertEqual(Configurator.CONF_FUN_SECTION, "FUN_STUFF")
        
        # Test option constants
        self.assertEqual(Configurator.OPTION_COUNTDOWN_TEXT, "countdown_text")
        self.assertEqual(Configurator.OPTION_NUMPICS, "num_pics")
        self.assertEqual(Configurator.OPTION_ARCHIVE_DIR, "archive_dir")
        self.assertEqual(Configurator.OPTION_WIDTH, "screen_width")
        self.assertEqual(Configurator.OPTION_HEIGHT, "screen_height")
        self.assertEqual(Configurator.FUN_CMD, "fun_cmd")


class TestConfiguratorEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for Configurator."""
    
    def setUp(self):
        """Set up test fixtures."""
        Configurator._Configurator__instance = None
    
    def tearDown(self):
        """Clean up after tests."""
        Configurator._Configurator__instance = None
    
    def test_malformed_configuration_file(self):
        """Test handling of malformed configuration file."""
        malformed_config = """
[PHOTO
num_pics = 4
invalid_line_without_equals
[CAMERA_ATTRIBUTES]
res_pixels_X = not_a_number
"""
        
        with patch('builtins.open', mock_open(read_data=malformed_config)):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                # Should handle malformed config gracefully
                with self.assertRaises((configparser.Error, ValueError)):
                    config = Configurator.instance()
    
    def test_empty_configuration_file(self):
        """Test handling of empty configuration file."""
        with patch('builtins.open', mock_open(read_data="")):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                config = Configurator.instance()
                
                # Should handle empty config by creating defaults
                self.assertIsInstance(config.config, configparser.ConfigParser)
    
    def test_file_permission_errors(self):
        """Test handling of file permission errors."""
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with patch('coregui.camconfig.os.path.exists', return_value=True):
                # Should handle permission errors gracefully
                with self.assertRaises(PermissionError):
                    config = Configurator.instance()


if __name__ == '__main__':
    unittest.main(verbosity=2)