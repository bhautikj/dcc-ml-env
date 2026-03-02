from src.utils.workspace import Workspace, WorkspaceAuxDirs, ModelType, ToolType
from src.utils.symlink_utils import create_symlinks, SymlinkMode
from pathlib import Path
from glob import glob
import json, stat, os

class ToolBase():
    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self._setup_tool_directories() 
        self._create_tool_symlinks()
        self._handle_checkpoint_symlinks()
        self._manage_config_files()
        self._create_launcher_script()

    def _setup_tool_directories():
        raise NotImplementedError("Calling on base class, not implemented")
    
    def _create_tool_symlinks():
        raise NotImplementedError("Calling on base class, not implemented")
    
    def _handle_checkpoint_symlinks():
        raise NotImplementedError("Calling on base class, not implemented")
    
    def _manage_config_files():
        raise NotImplementedError("Calling on base class, not implemented")
    
    def _create_launcher_script():
        raise NotImplementedError("Calling on base class, not implemented")