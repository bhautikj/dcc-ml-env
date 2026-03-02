#!/usr/bin/env python3
"""
Main entry point for DCC-ml-env system

This script provides command-line interface for managing DCC workspaces.
"""
import sys
import json
import argparse
import shutil
from pathlib import Path
from src.utils.workspace import Workspace
from src.utils.tool_wan2gp import ToolWan2GP
from src.utils.tool_comfyui import ToolComfyUI
from src.utils.tool_rife import ToolRife

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from src.utils.workspace import ToolType, get_tool_type_from_string

def main():
    parser = argparse.ArgumentParser(description='DCC-Workon System - Creative work environment manager for small teams')
    parser.add_argument('workspace', nargs='?', help='Workspace config path')
    
    args = parser.parse_args()
    
    if not args.workspace:
        print("Error: Workspace path required")
        sys.exit(1)
    
    try:
        # Original DCC-Workon functionality would go here
        # For now, we'll just demonstrate the argument parsing
        print("Workspace:", args.workspace)        

        workspace = Workspace(args.workspace)
        toolwan2gp = ToolWan2GP(workspace)
        assert(toolwan2gp)
        toolcomfyui = ToolComfyUI(workspace)
        assert(toolcomfyui)
        toolrife = ToolRife(workspace)
        assert(toolrife)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()