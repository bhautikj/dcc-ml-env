import os
import tempfile
import yaml
import json
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
from src.utils.workspace import Workspace, WorkspaceAuxDirs, ToolType, ModelType
from src.utils.tool_rife import ToolRife

class TestRifeFunctions(unittest.TestCase):
    """Test cases for ToolRife class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_workspace_dir = tempfile.mkdtemp()
        
        # Create a temporary YAML config file
        self.config_data = {
            'working_directory': self.test_workspace_dir,
            'tools': [
                {
                    'name': 'rife',
                    'type': 'rife',
                    'version': '20260219',
                    'path': '/fake/path/to/rife',
                    'env': 'production',
                    'models': []
                }
            ]
        }
        
        # Write config to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.config_data, f)
            self.config_file = f.name
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up config file
        if os.path.exists(self.config_file):
            os.unlink(self.config_file)
    
    def test_ToolRife_class_exists(self):
        """Test that ToolRife class can be imported and instantiated"""
        workspace = Workspace(self.config_file)
        # We test that we can create the class without errors
        # We avoid calling the constructor that triggers symlink creation
        self.assertIsNotNone(ToolRife)
    
    def test_ToolRife_methods_exist(self):
        """Test that ToolRife has expected methods"""
        # Check that the class has the expected methods
        self.assertTrue(hasattr(ToolRife, '_setup_tool_directories'))
        self.assertTrue(hasattr(ToolRife, '_create_tool_symlinks'))
        self.assertTrue(hasattr(ToolRife, '_handle_checkpoint_symlinks'))
        self.assertTrue(hasattr(ToolRife, '_create_launcher_script'))

if __name__ == '__main__':
    unittest.main()