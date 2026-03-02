"""
Workspace management class for DCC-ml-env system.
Handles YAML configuration loading and workspace setup.
"""
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Enumeration of model types."""
    CHECKPOINT = "CHECKPOINT"
    FINETUNE = "FINETUNE"
    LORA = "LORA"
    OTHER = "OTHER"

class ToolType(Enum):
    """Enumeration of tool types."""
    COMFYUI = "comfyui"
    WAN2GP = "wan2gp"
    RIFE = "rife"

def get_tool_type_from_string(tool_type_str: str) -> ToolType:
    """Convert a string representation to ToolType enum.
    
    Args:
        tool_type_str: String representation of tool type
        
    Returns:
        ToolType enum value
        
    Raises:
        ValueError: If tool type string is not recognized
    """
    for tool_type in ToolType:
        if tool_type.value == tool_type_str:
            return tool_type
    raise ValueError(f"Unknown tool type: {tool_type_str}")

class WorkspaceAuxDirs(Enum):
    """Enumeration of auxillary directories inside the working directory."""
    BINARIES = "bin"
    MODELS = "models"
    CONFIG = "config"
    VAR = "var"
    TMP = "tmp"
    IN = "in"
    OUT = "out"

class Workspace:
    """Workspace manager that loads YAML configuration"""
    def __init__(self, config_path: str, config_dir: Optional[str] = None):
        """
        Initialize a workspace from a YAML configuration file.
        
        Args:
            config_path: Path to the YAML configuration file
            config_dir: Optional custom configuration directory path
        """
        self.config_path = config_path
        self.config_dir = config_dir
        self.config = self._load_config()
        self._validate_and_setup()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load and parse the YAML configuration file.
        
        Returns:
            Parsed configuration dictionary
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            yaml.YAMLError: If the YAML is invalid
            ValueError: If the configuration structure is invalid
        """
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            
            # Validate required fields
            if not isinstance(config, dict):
                raise ValueError("Configuration must be a dictionary")
            
            if 'working_directory' not in config:
                raise ValueError("Configuration must contain 'working_directory' field")
            
            if 'tools' not in config:
                raise ValueError("Configuration must contain 'tools' field")
            
            if not isinstance(config['tools'], list):
                raise ValueError("'tools' field must be a list")
            
            logger.info(f"Successfully loaded configuration from {self.config_path}")
            return config
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in configuration file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def _validate_and_setup(self):
        """
        Validate the configuration and set up the workspace.
        """
        # Create working directory if it doesn't exist
        working_dir = Path(self.config['working_directory'])
        try:
            working_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured working directory exists: {working_dir}")
        except Exception as e:
            logger.error(f"Failed to create working directory {working_dir}: {e}")
            raise
        
        # Create auxiliary directories from WorkspaceAuxDirs enum
        for dir_name in WorkspaceAuxDirs:
            aux_dir_path = working_dir / dir_name.value
            try:
                aux_dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Ensured auxiliary directory exists: {aux_dir_path}")
            except Exception as e:
                logger.error(f"Failed to create auxiliary directory {aux_dir_path}: {e}")
                raise
    
    def get_working_directory(self) -> Path:
        """
        Get the working directory path.
        
        Returns:
            Path object of the working directory
        """
        return Path(self.config['working_directory'])
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get the list of tools from the configuration.
        
        Returns:
            List of tool dictionaries
        """
        return self.config.get('tools', [])
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get the list of models from the configuration.
        
        Returns:
            List of model dictionaries
        """
        models = []
        for tool in self.config.get('tools', []):
            tool_models = tool.get('models', [])
            models.extend(tool_models)
        return models
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config