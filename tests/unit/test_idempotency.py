"""
Unit tests for idempotency checks in DCC-ml-env system.
"""
import os
import tempfile
import yaml
import shutil
from pathlib import Path
import unittest
from src.utils.workspace import Workspace
from src.utils.tool_wan2gp import ToolWan2GP
from src.utils.tool_comfyui import ToolComfyUI

class TestIdempotency(unittest.TestCase):
    """Test cases for idempotency in DCC-Workon system."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.test_dir) / "config"
        self.config_dir.mkdir()
        
        # Create temporary directories for tools
        self.wan2gp_dir = Path(self.test_dir) / "wan2gp"
        self.wan2gp_dir.mkdir()
        self.wan2gp_main = self.wan2gp_dir / 'wgp.py'
        self.wan2gp_main.touch()
        self.wan2gp_config = self.wan2gp_dir / 'wgp_config.json'
        self.wan2gp_config.touch()
        
        self.comfyui_dir = Path(self.test_dir) / "comfyui"
        self.comfyui_dir.mkdir()
        self.comfyui_main = self.comfyui_dir / 'main.py'
        self.comfyui_main.touch()
        
        # Create temporary directories for models
        self.models_dir = Path(self.test_dir) / "models"
        self.models_dir.mkdir()
        self.ckpt_dir = self.models_dir / "ckpts"
        self.ckpt_dir.mkdir()
        self.lora_dir = self.models_dir / "lora"
        self.lora_dir.mkdir()
        
        # Create a temporary YAML config file
        self.config_data = {
            'working_directory': str(Path(self.test_dir) / "workspace"),
            'tools': [
                {
                    'name': 'wan2gp',
                    'type': 'wan2gp',
                    'version': '20260216',
                    'path': str(self.wan2gp_dir),
                    'env': 'wan2gp',
                    'models': [
                        {
                            'name': 'ckpts',
                            'subtype': 'ckpts',
                            'path': str(self.ckpt_dir),
                        },
                        {
                            'name': 'lora',
                            'subtype': 'lora',
                            'path': str(self.lora_dir),
                        }
                    ]
                },
                {
                    'name': 'comfyui',
                    'type': 'comfyui',
                    'version': '20260219',
                    'path': str(self.comfyui_dir),
                    'env': 'comfyui',
                    'models': [
                        {
                            'name': 'ckpts',
                            'subtype': 'ckpts',
                            'path': str(self.ckpt_dir),
                        }
                    ]
                }
            ]
        }
        
        # Write config to temporary file
        self.config_file = str(self.config_dir / "test_config.yaml")
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config_data, f)
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_workspace_creation_is_idempotent(self):
        """Test that Workspace can be created multiple times on the same directory."""
        # Create workspace first time
        workspace1 = Workspace(self.config_file)
        
        # Create workspace second time (should be idempotent)
        workspace2 = Workspace(self.config_file)
        
        # Both workspaces should be valid and have same properties
        self.assertEqual(workspace1.get_working_directory(), workspace2.get_working_directory())
        self.assertEqual(len(workspace1.get_tools()), len(workspace2.get_tools()))
        self.assertEqual(len(workspace1.get_models()), len(workspace2.get_models()))
    
    def test_tool_setup_is_idempotent(self):
        """Test that tool setup can be run multiple times on the same workspace."""
        # Create workspace
        workspace = Workspace(self.config_file)
        
        # Setup tools first time
        tool_wan2gp_1 = ToolWan2GP(workspace)
        tool_comfyui_1 = ToolComfyUI(workspace)
        
        # Setup tools second time (should be idempotent)
        tool_wan2gp_2 = ToolWan2GP(workspace)
        tool_comfyui_2 = ToolComfyUI(workspace)
        
        # Both tool instances should be created successfully
        self.assertIsNotNone(tool_wan2gp_1)
        self.assertIsNotNone(tool_wan2gp_2)
        self.assertIsNotNone(tool_comfyui_1)
        self.assertIsNotNone(tool_comfyui_2)
    
    def test_yaml_updates_are_handled(self):
        """Test that when YAML is updated with new tools, they are properly added."""
        # Create workspace with initial config
        workspace = Workspace(self.config_file)
        
        # Get initial tools count
        initial_tools = workspace.get_tools()
        
        # Modify config to add a new tool
        updated_config_data = self.config_data.copy()
        updated_config_data['tools'].append({
            'name': 'rife',
            'type': 'rife',
            'version': '20221029',
            'path': '/fake/rife/path',
            'env': 'base'
        })
        
        # Write updated config
        updated_config_file = str(self.config_dir / "updated_config.yaml")
        with open(updated_config_file, 'w') as f:
            yaml.dump(updated_config_data, f)
        
        # Create new workspace with updated config
        updated_workspace = Workspace(updated_config_file)
        
        # Should have one more tool
        self.assertEqual(len(updated_workspace.get_tools()), len(initial_tools) + 1)

if __name__ == '__main__':
    unittest.main()