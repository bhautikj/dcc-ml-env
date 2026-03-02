"""
Utility functions for handling symbolic links in DCC-ml-env system.
"""
import os
import shutil
import logging
from pathlib import Path
from typing import List
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SymlinkMode(Enum):
    """Enumeration for symlink creation modes."""
    TRAVERSE = "traverse"
    TOPLEVEL = "top-level"


def create_symlinks(input_directories: List[str], target_directory: str, mode: SymlinkMode) -> None:
    """
    Create symlinks from input directories to target directory.
    
    Args:
        input_directories: List of input directory paths
        target_directory: Target directory path where symlinks will be created
        mode: SymlinkMode enum value (TRAVERSE or TOPLEVEL)
        
    Raises:
        OSError: If directory operations fail
    """
    # Create target directory if it doesn't exist
    target_path = Path(target_directory)
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Clear existing symlinks in target directory if it exists
    if target_path.exists() and target_path.is_dir():
        if len(list(target_path.iterdir())) != 0:
            logger.warning(f"Found existing symlinks in {target_path}, deleting them")
        for item in target_path.iterdir():
            try:
                # Remove existing symlink or directory
                if item.is_symlink() or item.is_dir():
                    if item.is_symlink():
                        item.unlink()
                    else:
                        shutil.rmtree(item)
                else:
                    # Remove regular files
                    item.unlink()
            except Exception as e:
                logger.warning(f"Failed to remove existing item {item}: {e}")
    
    # Process input directories based on mode
    if mode == SymlinkMode.TOPLEVEL:
        _create_top_level_symlinks(input_directories, target_directory)
    elif mode == SymlinkMode.TRAVERSE:
        _create_traverse_symlinks(input_directories, target_directory)


def _create_top_level_symlinks(input_directories: List[str], target_directory: str) -> None:
    """
    Create symlinks to input directories themselves in target directory.
    
    Args:
        input_directories: List of input directory paths
        target_directory: Target directory path
    """
    target_path = Path(target_directory)
    
    for input_dir in input_directories:
        input_path = Path(input_dir)
        if not input_path.exists():
            logger.warning(f"Input directory does not exist: {input_dir}")
            continue
            
        if not input_path.is_dir():
            logger.warning(f"Input path is not a directory: {input_dir}")
            continue
            
        # Create symlink to the input directory
        symlink_name = input_path.name
        symlink_path = target_path / symlink_name
        
        try:
            # Create symlink
            symlink_path.symlink_to(input_dir)
            logger.info(f"Created symlink: {symlink_path} -> {input_dir}")
        except Exception as e:
            logger.error(f"Failed to create symlink {symlink_path} -> {input_dir}: {e}")


def _create_traverse_symlinks(input_directories: List[str], target_directory: str) -> None:
    """
    Create symlinks to files within input directories in target directory.
    
    Args:
        input_directories: List of input directory paths
        target_directory: Target directory path
    """
    target_path = Path(target_directory)
    
    for input_dir in input_directories:
        input_path = Path(input_dir)
        if not input_path.exists():
            logger.warning(f"Input directory does not exist: {input_dir}")
            continue
            
        if not input_path.is_dir():
            logger.warning(f"Input path is not a directory: {input_dir}")
            continue
            
        # Traverse the input directory and create symlinks to files
        for item in input_path.rglob('*'):
            if item.is_file():
                # Calculate relative path from input directory to file
                rel_path = item.relative_to(input_path)
                target_file = target_path / rel_path
                
                # Create parent directories if needed
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    # Create symlink to the file
                    target_file.symlink_to(item)
                    logger.info(f"Created symlink: {target_file} -> {item}")
                except Exception as e:
                    logger.error(f"Failed to create symlink {target_file} -> {item}: {e}")