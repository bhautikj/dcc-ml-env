"""
Unit tests for Workspace class.
"""
import os
import tempfile
import yaml
from pathlib import Path
import unittest
from src.utils.workspace import Workspace, ToolType, ModelType

class TestWorkspace(unittest.TestCase):
    """Test cases for Workspace class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create a temporary YAML config file
        self.config_data = {
            'working_directory': '/tmp/test_workspace',
            'tools': [
                {
                    'name': 'comfyui',
                    'version': '3.6',
                    'models': [
                        {
                            'name': 'ckpts',
                            'version': '1.0',
                            'type': "CHECKPOINT",
                            'subtype': 'ckpts',
                            'path': '/usr/lib/model-checkpoints',
                        }
                    ]
                }
            ]
        }
        
        # Write config to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.config_data, f)
            self.config_file = f.name
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary directory and its contents
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Clean up config file
        if os.path.exists(self.config_file):
            os.unlink(self.config_file)
    
    def _create_test_config(self, config_data):
        """Helper method to create a temporary config file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            return f.name
    
    def test_workspace_creation_from_valid_config(self):
        """Test that Workspace can be created with valid YAML config."""
        # Test creating workspace
        workspace = Workspace(self.config_file)
        
        # Verify workspace properties
        self.assertEqual(workspace.get_working_directory(), Path('/tmp/test_workspace'))
        self.assertEqual(len(workspace.get_tools()), 1)
        self.assertEqual(len(workspace.get_models()), 1)
        
    def test_workspace_loads_config_from_disk(self):
        """Test that Workspace loads configuration from disk."""
        
        # Create a new config file with the same structure
        config_data = {
            'working_directory': '/tmp/test_workspace',
            'tools': [
                {
                    'name': 'wan2gp',
                    'type': 'wan2gp',
                    'version': '20260212',
                    'path': '/usr/bin/wan2gp',
                    'env': 'production',
                    'models': [
                        {
                            'name': 'ckpts',
                            'version': '1.0',
                            'type': "CHECKPOINT",
                            'subtype': 'ckpts',
                            'path': '/usr/lib/model-checkpoints',
                        }
                    ]
                }
            ]
        }
        
        # Write config to temporary file
        config_file = self._create_test_config(config_data)
        
        try:
            # Test creating workspace
            workspace = Workspace(config_file)
            
            # Verify workspace properties
            self.assertEqual(workspace.get_working_directory(), Path('/tmp/test_workspace'))
            self.assertEqual(len(workspace.get_tools()), 1)
            self.assertEqual(len(workspace.get_models()), 1)
            
        finally:
            # Clean up
            os.unlink(config_file)
    
    def test_workspace_creation_with_multiple_tools_and_models(self):
        """Test workspace creation with multiple tools and models."""
        
        # Create config with multiple tools and models
        config_data = {
            'working_directory': '/tmp/test_workspace',
            'tools': [
                {
                    'name': 'wan2gp',
                    'type': 'wan2gp',
                    'version': '20260212',
                    'path': '/usr/bin/wan2gp',
                    'env': 'production',
                    'models': [
                        {
                            'name': 'ckpts',
                            'version': '1.0',
                            'type': "CHECKPOINT",
                            'subtype': 'ckpts',
                            'path': '/usr/lib/model-checkpoints',
                        },
                        {
                            'name': 'loras',
                            'version': '1.0',
                            'type': "LORA",
                            'subtype': 'lora',
                            'path': '/usr/lib/model-loras',
                        }
                    ]
                },
                {
                    'name': 'wan2gp',
                    'version': '1.0',
                    'models': [
                        {
                            'name': 'lora-wan',
                            'version': '1.0',
                            'type': "CHECKPOINT",
                            'subtype': 'lora',
                            'path': '/usr/lib/model-lora-wan',
                        }
                    ]
                }
            ]
        }
        
        # Write config to temporary file
        config_file = self._create_test_config(config_data)
        
        try:
            # Test creating workspace
            workspace = Workspace(config_file)
            
            # Verify workspace properties
            self.assertEqual(workspace.get_working_directory(), Path('/tmp/test_workspace'))
            self.assertEqual(len(workspace.get_tools()), 2)
            self.assertEqual(len(workspace.get_models()), 3)
            
        finally:
            # Clean up
            os.unlink(config_file)
    
    def test_workspace_creates_auxiliary_directories(self):
        """Test that workspace creates auxiliary directories from WorkspaceAuxDirs enum."""

        # Create a temporary directory for the test
        test_working_dir = Path(self.test_dir) / "test_workspace"
        
        # Create config with a working directory
        config_data = {
            'working_directory': str(test_working_dir),
            'tools': [
                {
                    'name': 'wan2gp',
                    'type': 'wan2gp',
                    'version': '20260212',
                    'path': '/usr/bin/wan2gp',
                    'env': 'production',
                    'models': []
                }
            ]
        }
        
        # Write config to temporary file
        config_file = self._create_test_config(config_data)
        
        try:
            # Test creating workspace - this should create auxiliary directories
            workspace = Workspace(config_file)
            
            # Verify that the working directory was created
            self.assertTrue(test_working_dir.exists())
            self.assertTrue(test_working_dir.is_dir())
            
            # Verify that all auxiliary directories were created
            from src.utils.workspace import WorkspaceAuxDirs
            aux_dirs = [dir_name.value for dir_name in WorkspaceAuxDirs]
            for aux_dir in aux_dirs:
                aux_dir_path = test_working_dir / aux_dir
                self.assertTrue(aux_dir_path.exists(), f"Auxiliary directory {aux_dir} was not created")
                self.assertTrue(aux_dir_path.is_dir(), f"Auxiliary directory {aux_dir} is not a directory")
            
        finally:
            # Clean up
            os.unlink(config_file)
            
    def test_workspace_handles_invalid_config_file(self):
        """Test that Workspace properly handles invalid configuration files."""
        # Create an invalid config file
        invalid_config_data = {
            'working_directory': '/tmp/test_workspace',
            'tools': [
                {
                    'name': 'wan2gp',
                    'type': 'wan2gp',
                    'version': '20260212',
                    'path': '/usr/bin/wan2gp',
                    'env': 'production',
                    # Missing models section
                }
            ]
        }
        
        config_file = self._create_test_config(invalid_config_data)
        
        try:
            # Test creating workspace - should not raise an exception
            workspace = Workspace(config_file)
            
            # Verify workspace properties
            self.assertEqual(workspace.get_working_directory(), Path('/tmp/test_workspace'))
            self.assertEqual(len(workspace.get_tools()), 1)
            # Note: The models count may be 0 or 1 depending on implementation
            
        finally:
            # Clean up
            os.unlink(config_file)

if __name__ == '__main__':
    unittest.main()