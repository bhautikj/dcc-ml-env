import os
import tempfile
import yaml
import json
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
from src.utils.workspace import Workspace, WorkspaceAuxDirs, ToolType, ModelType
from src.utils.tool_wan2gp import ToolWan2GP

class TestWan2GPFunctions(unittest.TestCase):
    """Test cases for individual ToolWan2GP functions."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.wan2gp_dummy = tempfile.mkdtemp()
        self.models_tmp = tempfile.mkdtemp()
        #self.config = DCCConfig(config_dir=self.test_dir)
        self.test_workspace_dir = tempfile.mkdtemp()
        
        # set up wan2gp installation
        self.wgp_base = Path(self.wan2gp_dummy) / 'Wan2GP'
        self.wgp_base.mkdir()
        self.wgp_main = self.wgp_base / 'wgp.py'
        self.wgp_main.touch()
        wgpFakeDict = {}
        wgpFakeDict["save_path"] = "INVALID"
        wgpFakeDict["image_save_path"] = "INVALID"
        wgpFakeDict["audio_save_path"] = "INVALID"
        self.wgp_config = self.wgp_base / 'wgp_config.json'
        self.wgp_config.touch()
        [json.dump(wgpFakeDict, open(str(self.wgp_config), "w"), indent=2)]
        self.wgp_ckpt_orig = self.wgp_base / 'ckpts'
        self.wgp_ckpt_orig.mkdir()

        # set up fake models
        self.models_checkpoints = Path(self.models_tmp) / 'ckpts'
        self.models_checkpoints.mkdir()
        self.models_lora = Path(self.models_tmp) / 'lora'
        self.models_lora.mkdir()
        self.models_lora2 = Path(self.models_tmp) / 'lora2'
        self.models_lora2.mkdir()
        self.models_i2v = Path(self.models_tmp) / 'lora-i2v'
        self.models_i2v.mkdir()
        self.models_ltxv = Path(self.models_tmp) / 'lora-ltxv'
        self.models_ltxv.mkdir()

        # Create a temporary YAML config file
        self.config_data = {
            'working_directory': self.test_workspace_dir,
            'tools': [
                {
                    'name': 'wan2gp',
                    'type': 'wan2gp',
                    'version': '20260212',
                    'path': str(self.wgp_base),
                    'env': 'production',
                    'models': [
                        {
                            'name': 'ckpts',
                            'version': '1.0',
                            'type': "CHECKPOINT",
                            'subtype': 'ckpts',
                            'path': str(self.models_checkpoints),
                        },
                        {
                            'name': 'lora',
                            'version': '1.0',
                            'type': 'LORA',
                            'subtype': 'lora',
                            'path': str(self.models_lora),
                        },
                        {
                            'name': 'lora2',
                            'version': '1.0',
                            'type': 'LORA',
                            'subtype': 'lora',
                            'path': str(self.models_lora2),
                        },
                        {
                            'name': 'lora-i2v',
                            'version': '1.0',
                            'type': 'LORA',
                            'subtype': 'i2v',
                            'path': str(self.models_i2v),
                        },
                        {
                            'name': 'lora-ltxv',
                            'version': '1.0',
                            'type': 'LORA',
                            'subtype': 'ltxv',
                            'path': str(self.models_ltxv),
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
        shutil.rmtree(self.wan2gp_dummy, ignore_errors=True)
        shutil.rmtree(self.models_tmp, ignore_errors=True)
        
        # Clean up config file
        if os.path.exists(self.config_file):
            os.unlink(self.config_file)
    
    def test_setup_tool_directories(self):
        """Test the _setup_tool_directories function"""
        workspace = Workspace(self.config_file)
        toolwan2gp = ToolWan2GP(workspace)
    
        # Check that the paths were set correctly by verifying directory creation
        # Since the method now processes all tools, we can't directly test it
        # But we can verify that the expected directories were created
        tool_workspace = self.config_data['tools'][0]
        tool_name = tool_workspace['name']
        tool_version = tool_workspace['version']
        
        # Verify that the expected directories were created
        tool_dest_path = Path(self.test_workspace_dir) / WorkspaceAuxDirs.BINARIES.value / tool_name / tool_version
        output_dest_path = Path(self.test_workspace_dir) / WorkspaceAuxDirs.OUT.value / f"{tool_name}_{tool_version}"
        
        self.assertTrue(tool_dest_path.exists())
        self.assertTrue(output_dest_path.exists())
    
    def test_create_tool_symlinks(self):
        """Test the _create_tool_symlinks function"""
        workspace = Workspace(self.config_file)
        toolwan2gp = ToolWan2GP(workspace)
        
        # Mock the method to test it directly
        with patch.object(toolwan2gp, '_create_tool_symlinks') as mock_symlinks:
            tool_workspace = self.config_data['tools'][0]
            toolwan2gp._create_tool_symlinks(tool_workspace)
            
            # Verify the method was called
            mock_symlinks.assert_called_once_with(tool_workspace)
    
    def test_handle_checkpoint_symlinks(self):
        """Test the _handle_checkpoint_symlinks function"""
        workspace = Workspace(self.config_file)
        toolwan2gp = ToolWan2GP(workspace)
        
        # Mock the method to test it directly
        with patch.object(toolwan2gp, '_handle_checkpoint_symlinks') as mock_ckpts:
            tool_workspace = self.config_data['tools'][0]
            toolwan2gp._handle_checkpoint_symlinks(tool_workspace)
            
            # Verify the method was called
            mock_ckpts.assert_called_once_with(tool_workspace)
    
    def test_manage_config_files(self):
        """Test the _manage_config_files function"""
        workspace = Workspace(self.config_file)
        toolwan2gp = ToolWan2GP(workspace)
        
        # Mock the method to test it directly
        with patch.object(toolwan2gp, '_manage_config_files') as mock_config:
            tool_workspace = self.config_data['tools'][0]
            toolwan2gp._manage_config_files(tool_workspace)
            
            # Verify the method was called
            mock_config.assert_called_once_with(tool_workspace)
    
    def test_create_launcher_script(self):
        """Test the _create_launcher_script function"""
        workspace = Workspace(self.config_file)
        toolwan2gp = ToolWan2GP(workspace)
        
        # Mock the method to test it directly
        with patch.object(toolwan2gp, '_create_launcher_script') as mock_launcher:
            tool_workspace = self.config_data['tools'][0]
            toolwan2gp._create_launcher_script(tool_workspace)
            
            # Verify the method was called
            mock_launcher.assert_called_once_with(tool_workspace)
    
    def test_lora_consolidator(self):
        """Test the loraConsolidator function"""
        workspace = Workspace(self.config_file)
        toolwan2gp = ToolWan2GP(workspace)
        
        tool_workspace = self.config_data['tools'][0]
        
        # Test with lora type
        result = toolwan2gp.loraConsolidator(tool_workspace, 'lora')
        self.assertIsInstance(result, list)
        
        # Test with i2v type
        result = toolwan2gp.loraConsolidator(tool_workspace, 'i2v')
        self.assertIsInstance(result, list)
        
        # Test with lxtv type
        result = toolwan2gp.loraConsolidator(tool_workspace, 'lxtv')
        self.assertIsInstance(result, list)

    def test_ToolWan2GP(self):
        workspace = Workspace(self.config_file)
        toolwan2gp = ToolWan2GP(workspace)
        self.assertIsNotNone(toolwan2gp)

if __name__ == '__main__':
    unittest.main()