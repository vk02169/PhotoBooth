"""
Demo test to show the test framework is working correctly.

This is a simple test that demonstrates the test infrastructure
without depending on the actual PhotoBooth code.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch


class TestDemo(unittest.TestCase):
    """Demo test cases to verify test framework functionality."""
    
    def test_basic_assertion(self):
        """Test basic assertion functionality."""
        self.assertEqual(2 + 2, 4)
        self.assertTrue(True)
        self.assertFalse(False)
    
    def test_mock_functionality(self):
        """Test that mocking works correctly."""
        mock_obj = Mock()
        mock_obj.method.return_value = "mocked_result"
        
        result = mock_obj.method("test_arg")
        
        self.assertEqual(result, "mocked_result")
        mock_obj.method.assert_called_once_with("test_arg")
    
    def test_patch_functionality(self):
        """Test that patching works correctly."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            result = os.path.exists("/fake/path")
            
            self.assertTrue(result)
            mock_exists.assert_called_once_with("/fake/path")
    
    def test_temporary_files(self):
        """Test temporary file handling."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content")
            temp_path = temp_file.name
        
        # Verify file exists and has content
        self.assertTrue(os.path.exists(temp_path))
        
        with open(temp_path, 'r') as f:
            content = f.read()
        
        self.assertEqual(content, "test content")
        
        # Cleanup
        os.unlink(temp_path)
        self.assertFalse(os.path.exists(temp_path))
    
    def test_exception_handling(self):
        """Test exception handling in tests."""
        with self.assertRaises(ValueError):
            raise ValueError("Test exception")
        
        with self.assertRaises(KeyError):
            {}["nonexistent_key"]
    
    def test_list_operations(self):
        """Test list operations."""
        test_list = [1, 2, 3, 4, 5]
        
        self.assertIn(3, test_list)
        self.assertNotIn(6, test_list)
        self.assertEqual(len(test_list), 5)
        self.assertEqual(test_list[0], 1)
        self.assertEqual(test_list[-1], 5)
    
    def test_string_operations(self):
        """Test string operations."""
        test_string = "PhotoBooth Test"
        
        self.assertTrue(test_string.startswith("Photo"))
        self.assertTrue(test_string.endswith("Test"))
        self.assertIn("Booth", test_string)
        self.assertEqual(test_string.lower(), "photobooth test")
        self.assertEqual(len(test_string), 15)


class TestDemoWithSetup(unittest.TestCase):
    """Demo test cases with setup and teardown."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data = {
            "name": "PhotoBooth",
            "version": "1.0",
            "components": ["camera", "gui", "upload"]
        }
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_setup_data(self):
        """Test that setup data is available."""
        self.assertIsInstance(self.test_data, dict)
        self.assertEqual(self.test_data["name"], "PhotoBooth")
        self.assertIn("camera", self.test_data["components"])
    
    def test_temp_directory(self):
        """Test that temporary directory is created."""
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertTrue(os.path.isdir(self.temp_dir))
        
        # Create a test file in temp directory
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        self.assertTrue(os.path.exists(test_file))


if __name__ == '__main__':
    unittest.main(verbosity=2)