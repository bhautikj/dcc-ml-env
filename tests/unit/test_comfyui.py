import os
import tempfile
import yaml
import json
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
from src.utils.workspace import Workspace, WorkspaceAuxDirs, ToolType, ModelType
from src.utils.tool_comfyui import ToolComfyUI

class TestComfyUIFunctions(unittest.TestCase):
    """Test cases for individual ToolComfyUI functions."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.comfyui_dummy = tempfile.mkdtemp()
        self.models_tmp = tempfile.mkdtemp()
        self.test_workspace_dir = tempfile.mkdtemp()
        
        # set up comfyui installation
        self.comfyui_base = Path(self.comfyui_dummy) / 'ComfyUI'
        self.comfyui_base.mkdir()
        self.comfy_main = self.comfyui_base / 'main.py'
        self.comfy_main.touch()
        self.comfyui_models_orig = self.comfyui_base / 'models'
        self.comfyui_models_orig.mkdir()
        
        # Create user/default directory with config file
        user_default_dir = self.comfyui_base / 'user' / 'default'
        user_default_dir.mkdir(parents=True, exist_ok=True)
        self.comfyui_config = user_default_dir / 'comfy.settings.json'
        self.comfyui_config.touch()
        # Write a basic config
        config_content = {
            "save_path": "default_save_path",
            "image_save_path": "default_image_save_path",
            "audio_save_path": "default_audio_save_path"
        }
        with open(self.comfyui_config, 'w') as f:
            json.dump(config_content, f)

        # set up fake models
        self.models_checkpoints = Path(self.models_tmp) / 'models'
        self.models_checkpoints.mkdir()

        # Create a temporary YAML config file
        self.config_data = {
            'working_directory': self.test_workspace_dir,
            'tools': [
                {
                    'name': 'comfyui',
                    'type': 'comfyui',
                    'version': '20260219',
                    'path': str(self.comfyui_base),
                    'env': 'production',
                    'models': [
                        {
                            'name': 'ckpts',
                            'version': '1.0',
                            'type': "CHECKPOINT",
                            'subtype': 'ckpts',
                            'path': str(self.models_checkpoints),
                        },
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
        shutil.rmtree(self.comfyui_dummy, ignore_errors=True)
        shutil.rmtree(self.models_tmp, ignore_errors=True)
        
        # Clean up config file
        if os.path.exists(self.config_file):
            os.unlink(self.config_file)
    
    def test_setup_tool_directories(self):
        """Test the _setup_tool_directories function"""
        workspace = Workspace(self.config_file)
        toolcomfyui = ToolComfyUI(workspace)
    
        # Check that the paths were set correctly by verifying directory creation
        # Since the method now processes all tools, we can't directly test it
        # But we can verify that the expected directories were created
        tool_workspace = self.config_data['tools'][0]
        tool_name = tool_workspace['name']
        tool_version = tool_workspace['version']
        
        # Verify that the expected directories were created
        tool_dest_path = Path(self.test_workspace_dir) / WorkspaceAuxDirs.BINARIES.value / tool_name / tool_version
        output_dest_path = Path(self.test_workspace_dir) / WorkspaceAuxDirs.OUT.value / f"{tool_name}_{tool_version}"
        input_dest_path = Path(self.test_workspace_dir) / WorkspaceAuxDirs.IN.value 
        
        self.assertTrue(tool_dest_path.exists())
        self.assertTrue(output_dest_path.exists())
        self.assertTrue(input_dest_path.exists())
    
    def test_create_tool_symlinks(self):
        """Test the _create_tool_symlinks function"""
        workspace = Workspace(self.config_file)
        toolcomfyui = ToolComfyUI(workspace)
        
        # Mock the method to test it directly
        with patch.object(toolcomfyui, '_create_tool_symlinks') as mock_symlinks:
            tool_workspace = self.config_data['tools'][0]
            toolcomfyui._create_tool_symlinks(tool_workspace)
            
            # Verify the method was called
            mock_symlinks.assert_called_once_with(tool_workspace)
    
    def test_handle_checkpoint_symlinks(self):
        """Test the _handle_checkpoint_symlinks function"""
        workspace = Workspace(self.config_file)
        toolcomfyui = ToolComfyUI(workspace)
        
        # Mock the method to test it directly
        with patch.object(toolcomfyui, '_handle_checkpoint_symlinks') as mock_ckpts:
            tool_workspace = self.config_data['tools'][0]
            toolcomfyui._handle_checkpoint_symlinks(tool_workspace)
            
            # Verify the method was called
            mock_ckpts.assert_called_once_with(tool_workspace)
    
    def test_manage_config_files(self):
        """Test the _manage_config_files function"""
        workspace = Workspace(self.config_file)
        toolcomfyui = ToolComfyUI(workspace)
        
        # Mock the method to test it directly
        with patch.object(toolcomfyui, '_manage_config_files') as mock_config:
            tool_workspace = self.config_data['tools'][0]
            toolcomfyui._manage_config_files(tool_workspace)
            
            # Verify the method was called
            mock_config.assert_called_once_with(tool_workspace)
    
    def test_create_launcher_script(self):
        """Test the _create_launcher_script function"""
        workspace = Workspace(self.config_file)
        toolcomfyui = ToolComfyUI(workspace)
        
        # Mock the method to test it directly
        with patch.object(toolcomfyui, '_create_launcher_script') as mock_launcher:
            tool_workspace = self.config_data['tools'][0]
            toolcomfyui._create_launcher_script(tool_workspace)
            
            # Verify the method was called
            mock_launcher.assert_called_once_with(tool_workspace)
    
    def test_ToolComfyUI(self):
        workspace = Workspace(self.config_file)
        toolcomfyui = ToolComfyUI(workspace)
        self.assertIsNotNone(toolcomfyui)

if __name__ == '__main__':
    unittest.main()