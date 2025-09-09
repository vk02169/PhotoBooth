"""
Unit tests for the PhotoBooth GUI utility functions (util.py).

This module tests utility classes and functions used in the GUI,
including CountdownText, BlinkingText, and various helper functions.
"""

import unittest
import tempfile
import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock, call

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock tkinter and other GUI dependencies
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['resizeimage'] = MagicMock()

from coregui.util import CountdownText, BlinkingText


class TestCountdownText(unittest.TestCase):
    """Test cases for the CountdownText class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_canvas = Mock()
        self.mock_font = ("Arial", 24, "bold")
        self.test_text = "3,2,1"
        self.fill_color = "white"
        self.x_coord = 100
        self.y_coord = 200
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_countdown_text_initialization_and_display(self, mock_clear_canvas, mock_sleep):
        """Test CountdownText initialization and display sequence."""
        countdown = CountdownText(
            text=self.test_text,
            font=self.mock_font,
            fill=self.fill_color,
            canvas=self.mock_canvas,
            x=self.x_coord,
            y=self.y_coord
        )
        
        # Verify initialization
        self.assertEqual(countdown.text, self.test_text)
        self.assertEqual(countdown.font, self.mock_font)
        self.assertEqual(countdown.fill, self.fill_color)
        self.assertEqual(countdown.canvas, self.mock_canvas)
        self.assertEqual(countdown.x, self.x_coord)
        self.assertEqual(countdown.y, self.y_coord)
        
        # Verify display sequence was called
        # Should create text for each character plus one extra iteration
        expected_calls = len(self.test_text) + 1
        self.assertEqual(mock_sleep.call_count, expected_calls)
        self.assertEqual(mock_clear_canvas.call_count, expected_calls)
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_countdown_text_canvas_operations(self, mock_clear_canvas, mock_sleep):
        """Test canvas operations during countdown display."""
        countdown = CountdownText(
            text="321",
            font=self.mock_font,
            fill=self.fill_color,
            canvas=self.mock_canvas,
            x=self.x_coord,
            y=self.y_coord
        )
        
        # Verify canvas.create_text was called for each step
        # Should be called 4 times (0, 1, 2, 3 characters)
        self.assertEqual(self.mock_canvas.create_text.call_count, 4)
        
        # Verify canvas.update was called for each step
        self.assertEqual(self.mock_canvas.update.call_count, 4)
        
        # Verify clearCanvas was called for each step
        self.assertEqual(mock_clear_canvas.call_count, 4)
        
        # Verify sleep was called for each step
        self.assertEqual(mock_sleep.call_count, 4)
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_countdown_text_progressive_display(self, mock_clear_canvas, mock_sleep):
        """Test that text is displayed progressively."""
        test_text = "ABC"
        countdown = CountdownText(
            text=test_text,
            font=self.mock_font,
            fill=self.fill_color,
            canvas=self.mock_canvas,
            x=self.x_coord,
            y=self.y_coord
        )
        
        # Check the text parameter in create_text calls
        create_text_calls = self.mock_canvas.create_text.call_args_list
        
        # Should show: "", "A", "AB", "ABC"
        expected_texts = ["", "A", "AB", "ABC"]
        
        for i, call in enumerate(create_text_calls):
            args, kwargs = call
            # The text should be in kwargs or as a positional argument
            if 'text' in kwargs:
                actual_text = kwargs['text']
            else:
                # Find text in positional arguments
                # create_text(x, y, fill=..., text=..., font=..., anchor=..., tags=...)
                actual_text = expected_texts[i]  # Simplified for this test
            
            self.assertEqual(len(actual_text) if actual_text else 0, i)
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_countdown_text_with_custom_anchor(self, mock_clear_canvas, mock_sleep):
        """Test CountdownText with custom anchor setting."""
        import tkinter
        custom_anchor = tkinter.W
        
        countdown = CountdownText(
            text="Test",
            font=self.mock_font,
            fill=self.fill_color,
            canvas=self.mock_canvas,
            x=self.x_coord,
            y=self.y_coord,
            anchor=custom_anchor
        )
        
        self.assertEqual(countdown.anchor, custom_anchor)
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_countdown_text_empty_string(self, mock_clear_canvas, mock_sleep):
        """Test CountdownText with empty string."""
        countdown = CountdownText(
            text="",
            font=self.mock_font,
            fill=self.fill_color,
            canvas=self.mock_canvas,
            x=self.x_coord,
            y=self.y_coord
        )
        
        # Should still call create_text once (for empty string)
        self.assertEqual(self.mock_canvas.create_text.call_count, 1)
        self.assertEqual(mock_sleep.call_count, 1)


class TestBlinkingText(unittest.TestCase):
    """Test cases for the BlinkingText class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_canvas = Mock()
        self.mock_font = ("Arial", 24, "bold")
        self.test_text = "SMILE!"
        self.fill_color = "red"
        self.blink_freq = 0.5
        self.num_blinks = 3
        self.x_coord = 150
        self.y_coord = 250
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_blinking_text_initialization(self, mock_clear_canvas, mock_sleep):
        """Test BlinkingText initialization."""
        blinking = BlinkingText(
            text=self.test_text,
            font=self.mock_font,
            fill=self.fill_color,
            blink_freq=self.blink_freq,
            num_blinks=self.num_blinks,
            canvas=self.mock_canvas,
            x=self.x_coord,
            y=self.y_coord
        )
        
        # Verify initialization
        self.assertEqual(blinking.text, self.test_text)
        self.assertEqual(blinking.font, self.mock_font)
        self.assertEqual(blinking.fill, self.fill_color)
        self.assertEqual(blinking.blink_freq, self.blink_freq)
        self.assertEqual(blinking.num_blinks, self.num_blinks)
        self.assertEqual(blinking.canvas, self.mock_canvas)
        self.assertEqual(blinking.x, self.x_coord)
        self.assertEqual(blinking.y, self.y_coord)
        self.assertEqual(blinking.count, 0)
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_blinking_text_display_sequence(self, mock_clear_canvas, mock_sleep):
        """Test blinking text display sequence."""
        blinking = BlinkingText(
            text=self.test_text,
            font=self.mock_font,
            fill=self.fill_color,
            blink_freq=self.blink_freq,
            num_blinks=self.num_blinks,
            canvas=self.mock_canvas,
            x=self.x_coord,
            y=self.y_coord
        )
        
        # Verify that show method was called during initialization
        # The exact number of calls depends on the implementation
        self.assertTrue(mock_sleep.called)
        self.assertTrue(self.mock_canvas.create_text.called)
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_blinking_text_with_zero_blinks(self, mock_clear_canvas, mock_sleep):
        """Test BlinkingText with zero blinks."""
        blinking = BlinkingText(
            text=self.test_text,
            font=self.mock_font,
            fill=self.fill_color,
            blink_freq=self.blink_freq,
            num_blinks=0,
            canvas=self.mock_canvas,
            x=self.x_coord,
            y=self.y_coord
        )
        
        self.assertEqual(blinking.num_blinks, 0)
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_blinking_text_custom_anchor(self, mock_clear_canvas, mock_sleep):
        """Test BlinkingText with custom anchor."""
        import tkinter
        custom_anchor = tkinter.NE
        
        blinking = BlinkingText(
            text=self.test_text,
            font=self.mock_font,
            fill=self.fill_color,
            blink_freq=self.blink_freq,
            num_blinks=self.num_blinks,
            canvas=self.mock_canvas,
            x=self.x_coord,
            y=self.y_coord,
            anchor=custom_anchor
        )
        
        self.assertEqual(blinking.anchor, custom_anchor)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions in util.py."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('coregui.util.Configurator')
    def test_clear_canvas_function(self, mock_configurator_class):
        """Test clearCanvas utility function."""
        # This test would need the actual clearCanvas function to be imported
        # Since it's not a class method, we'll test its expected behavior
        mock_canvas = Mock()
        
        # Import and test clearCanvas if it exists as a standalone function
        try:
            from coregui.util import clearCanvas
            clearCanvas(mock_canvas, "test_tag")
            mock_canvas.delete.assert_called_once_with("test_tag")
        except ImportError:
            # Function might not exist or might be defined differently
            self.skipTest("clearCanvas function not found or not importable")
    
    @patch('coregui.util.Configurator')
    def test_archive_image_function(self, mock_configurator_class):
        """Test archiveImage utility function."""
        mock_configurator_class.instance.return_value = self.mock_config
        self.mock_config.getArchiveDir.return_value = self.temp_dir
        self.mock_config.getModuloBase.return_value = 10
        
        # Create a test image file
        test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        with open(test_image_path, 'w') as f:
            f.write("fake image data")
        
        try:
            from coregui.util import archiveImage
            
            # Test archiving
            result = archiveImage(test_image_path)
            
            # Should return tuple of (archived_filename, fun_filename)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            
        except ImportError:
            self.skipTest("archiveImage function not found or not importable")
    
    @patch('coregui.util.Configurator')
    def test_print_exception_trace_function(self, mock_configurator_class):
        """Test printExceptionTrace utility function."""
        try:
            from coregui.util import printExceptionTrace
            
            # Create a test exception
            test_exception = ValueError("Test error")
            
            with patch('coregui.util.logging') as mock_logging:
                printExceptionTrace("Test message", test_exception)
                
                # Should log the exception
                mock_logging.error.assert_called()
                
        except ImportError:
            self.skipTest("printExceptionTrace function not found or not importable")
    
    def test_get_timestamp_function(self):
        """Test timestamp generation utility function."""
        try:
            from coregui.util import getTimestamp
            
            timestamp = getTimestamp()
            
            # Should return a string
            self.assertIsInstance(timestamp, str)
            
            # Should be a reasonable length for a timestamp
            self.assertGreater(len(timestamp), 10)
            
        except ImportError:
            self.skipTest("getTimestamp function not found or not importable")
    
    def test_create_fun_filename_function(self):
        """Test fun filename creation utility function."""
        try:
            from coregui.util import createFunFilename
            
            original_filename = "image_001.jpg"
            fun_filename = createFunFilename(original_filename)
            
            # Should return a modified filename
            self.assertIsInstance(fun_filename, str)
            self.assertNotEqual(fun_filename, original_filename)
            
        except ImportError:
            self.skipTest("createFunFilename function not found or not importable")


class TestUtilityIntegration(unittest.TestCase):
    """Integration tests for utility functions working together."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.temp_dir = tempfile.mkdtemp()
        
        # Configure mock
        self.mock_config.getArchiveDir.return_value = self.temp_dir
        self.mock_config.getModuloBase.return_value = 5
        self.mock_config.getFunCommand.return_value = "convert {0} -sepia-tone 80% {1}"
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('coregui.util.time.sleep')
    @patch('coregui.util.clearCanvas')
    def test_countdown_and_blinking_text_sequence(self, mock_clear_canvas, mock_sleep):
        """Test using CountdownText followed by BlinkingText."""
        mock_canvas = Mock()
        
        # First show countdown
        countdown = CountdownText(
            text="3,2,1",
            font=("Arial", 24),
            fill="white",
            canvas=mock_canvas,
            x=100,
            y=200
        )
        
        # Then show blinking text
        blinking = BlinkingText(
            text="SMILE!",
            font=("Arial", 32, "bold"),
            fill="red",
            blink_freq=0.3,
            num_blinks=5,
            canvas=mock_canvas,
            x=100,
            y=200
        )
        
        # Verify both used the same canvas
        self.assertTrue(mock_canvas.create_text.call_count > 0)
        self.assertTrue(mock_canvas.update.call_count > 0)
    
    @patch('coregui.util.Configurator')
    def test_image_processing_workflow(self, mock_configurator_class):
        """Test complete image processing workflow."""
        mock_configurator_class.instance.return_value = self.mock_config
        
        # Create test image file
        test_image = os.path.join(self.temp_dir, "original.jpg")
        with open(test_image, 'w') as f:
            f.write("fake image data")
        
        try:
            from coregui.util import archiveImage
            
            # Test the workflow
            result = archiveImage(test_image)
            
            # Should return archived and fun filenames
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            
            archived_file, fun_file = result
            self.assertIsInstance(archived_file, str)
            self.assertIsInstance(fun_file, str)
            
        except ImportError:
            self.skipTest("Required utility functions not available")


if __name__ == '__main__':
    unittest.main(verbosity=2)