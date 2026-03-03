from src.utils.workspace import Workspace, WorkspaceAuxDirs, ModelType, ToolType
from src.utils.tool_instances import ToolBase
from src.utils.symlink_utils import create_symlinks, SymlinkMode
from pathlib import Path
from glob import glob
import json, stat, os, logging

logger = logging.getLogger(__name__)

# wan2gp installed from https://github.com/deepbeepmeep/Wan2GP
MIRROREXCLUSIONLIST_WAN2GP = ['ckpts']
WAN2GP_CONFIG = "wgp_config.json"

class ToolWan2GP(ToolBase):
    def _setup_tool_directories(self):
        """Set up tool directories and paths."""
        for tool_workspace in self.workspace.get_tools():
            tool_type = tool_workspace.get('type')
            if tool_type != ToolType.WAN2GP.value:
                continue
            tool_name = tool_workspace.get('name')
            tool_version = tool_workspace.get('version')
            tool_orig_path = tool_workspace.get('path')
            assert(tool_orig_path != None)

            tool_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.BINARIES.value/ tool_name / tool_version
            tool_dest_path.mkdir(parents=True, exist_ok=True)
            ver_path = tool_name + '_' + tool_version
            output_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.OUT.value / ver_path
            output_dest_path.mkdir(parents=True, exist_ok=True)

    def _create_tool_symlinks(self):
        """Create symlinks for tool files."""
        for tool_workspace in self.workspace.get_tools():
            tool_type = tool_workspace.get('type')
            if tool_type != ToolType.WAN2GP.value:
                continue
            tool_name = tool_workspace.get('name')
            tool_version = tool_workspace.get('version')
            tool_orig_path = tool_workspace.get('path')
            
            tool_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.BINARIES.value/ tool_name / tool_version
            
            # symlink dir
            tool_orig_files = glob(str(Path(tool_orig_path) / '*'))
            for tool_orig_file in tool_orig_files:
                tool_orig_file_name = str(Path(tool_orig_file).name)
                if tool_orig_file_name not in MIRROREXCLUSIONLIST_WAN2GP:
                    src = Path(tool_orig_file)
                    dest = Path(tool_dest_path) / tool_orig_file_name
                    # Check if symlink already exists and is correct
                    if dest.is_symlink():
                        if dest.readlink() == src:
                            continue  # Already correctly linked
                        else:
                            # Remove incorrect symlink and create new one
                            dest.unlink()
                    elif dest.exists():
                        # If it's not a symlink but exists, remove it first
                        dest.unlink()
                    dest.symlink_to(src)

    def _handle_checkpoint_symlinks(self):
        """Handle checkpoint symlinks."""
        for tool_workspace in self.workspace.get_tools():
            tool_type = tool_workspace.get('type')
            if tool_type != ToolType.WAN2GP.value:
                continue
            tool_name = tool_workspace.get('name')
            tool_version = tool_workspace.get('version')
            tool_orig_path = tool_workspace.get('path')
            
            tool_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.BINARIES.value/ tool_name / tool_version
            
            #symlink checkpoints
            tool_models = tool_workspace.get('models', [])
            if 'ckpts' not in list(map(lambda x: x['subtype'], tool_models)):
                raise FileNotFoundError('ckpts not specified in workspace spec, is mandatory')
            ckpts_model = list(filter(lambda x: x['subtype']=='ckpts', tool_models))[0]
            src_ckpts = ckpts_model['path']
            dest_ckpts =  Path(tool_dest_path) / 'ckpts'
            try:
                dest_ckpts.symlink_to(src_ckpts)
            except:
                pass

    def _manage_config_files(self):
        """Manage configuration files."""
        for tool_workspace in self.workspace.get_tools():
            tool_type = tool_workspace.get('type')
            if tool_type != ToolType.WAN2GP.value:
                continue
            tool_name = tool_workspace.get('name')
            tool_version = tool_workspace.get('version')
            tool_orig_path = tool_workspace.get('path')
            
            tool_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.BINARIES.value/ tool_name / tool_version
            output_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.OUT.value / (tool_name + '_' + tool_version)
            
            #clone config
            dest_config_dir = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.CONFIG.value / tool_name / tool_version
            dest_config_dir.mkdir(parents=True, exist_ok=True)
            
            dest_config_path = dest_config_dir / WAN2GP_CONFIG
            
            config_orig = Path(tool_orig_path) / WAN2GP_CONFIG
            if not dest_config_path.is_file():
                # Check if original config exists and is valid
                if config_orig.exists() and config_orig.is_file():
                    try:
                        #open wgp config
                        with open(str(config_orig), 'r') as f:
                            wgpConfig = json.load(f)
                        wgpConfig["save_path"] = str(output_dest_path)
                        wgpConfig["image_save_path"] = str(output_dest_path)
                        wgpConfig["audio_save_path"] = str(output_dest_path)
                        with open(str(dest_config_path), "w") as f:
                            json.dump(wgpConfig, f, indent=2)
                    except (json.JSONDecodeError, IOError) as e:
                        # If we can't read the original config, create a minimal one
                        logger.warning(f"Could not read original config {config_orig}: {e}")
                        wgpConfig = {
                            "save_path": str(output_dest_path),
                            "image_save_path": str(output_dest_path),
                            "audio_save_path": str(output_dest_path)
                        }
                        with open(str(dest_config_path), "w") as f:
                            json.dump(wgpConfig, f, indent=2)
                else:
                    # Create a minimal config if original doesn't exist
                    wgpConfig = {
                        "save_path": str(output_dest_path),
                        "image_save_path": str(output_dest_path),
                        "audio_save_path": str(output_dest_path)
                    }
                    with open(str(dest_config_path), "w") as f:
                        json.dump(wgpConfig, f, indent=2)
            else:
                # Config already exists, just read it
                try:
                    with open(str(dest_config_path), 'r') as f:
                        wgpConfig = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Could not read existing config {dest_config_path}: {e}")
                    # Create a new config if existing one is corrupted
                    wgpConfig = {
                        "save_path": str(output_dest_path),
                        "image_save_path": str(output_dest_path),
                        "audio_save_path": str(output_dest_path)
                    }
                    with open(str(dest_config_path), "w") as f:
                        json.dump(wgpConfig, f, indent=2)

    def _create_launcher_script(self):
        """Create launcher script with proper permissions."""
        for tool_workspace in self.workspace.get_tools():
            tool_type = tool_workspace.get('type')
            if tool_type != ToolType.WAN2GP.value:
                continue
            tool_name = tool_workspace.get('name')
            tool_version = tool_workspace.get('version')
            tool_orig_path = tool_workspace.get('path')
            
            tool_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.BINARIES.value/ tool_name / tool_version
            output_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.OUT.value / (tool_name + '_' + tool_version)
            
            #create launcher
            tool_code_path = str(tool_dest_path / "wgp.py")
            conda_env = tool_workspace.get('env')
            assert(conda_env != None)
            config_file_path = str(Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.CONFIG.value / tool_name / tool_version)
            
            loras_args = []
            
            # get loras list for launcher script
            loras_args += self.loraConsolidator(tool_workspace, 'lora')
            loras_args += self.loraConsolidator(tool_workspace, 'i2v')
            loras_args += self.loraConsolidator(tool_workspace, 'lxtv')
            
            launcherCmd =  ["conda",
                            "run",
                            "--no-capture-output",
                            "-n",
                            conda_env,
                            "python",
                            tool_code_path,
                            "--config",
                            config_file_path]
            
            launcherCmd += loras_args
            launcherCmd += ["--listen", '"$@"', "\n"]
            print(launcherCmd)
            launcherScript =  "#!/bin/bash \n"
            launcherScript += "pushd " + str(tool_dest_path) + "\n"
            launcherScript += " ".join(launcherCmd)
            launcherScript += "popd \n"
            
            print(launcherScript)
            
            launcherFile =  Path(self.workspace.get_working_directory()) \
                            / WorkspaceAuxDirs.BINARIES.value \
                            / str("run_" + tool_name + "_" + tool_version + ".sh")
            
            # Only create launcher script if it doesn't exist or is different
            if not launcherFile.exists():
                launcherFile.write_text(launcherScript)
                # Get current mode
                current_mode = launcherFile.stat().st_mode
                
                # Add execute permissions for the owner (user)
                launcherFile.chmod(current_mode | stat.S_IXUSR)
                assert(os.access(launcherFile, os.X_OK))
            else:
                logger.info(f"Launcher script {launcherFile} already exists, skipping creation")

    def loraConsolidator(self, tool, lora_type: str):
        tool_models = tool.get('models', [])
        loras_set = list(filter(lambda x: x['subtype']==lora_type, tool_models))
        typeToArg = {
            "lora" : "--lora-dir",
            "i2v" : "--lora-dir-i2v",
            "lxtv" : "--lora-dir-ltxv"
        }
        loras_args = []
        if len(loras_set) == 0:
            return loras_args
        elif len(loras_set) == 1:
            path = loras_set[0]['path']
            loras_args += [typeToArg[lora_type], path]
        else:
            lora_output_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.MODELS.value / "LORAS" / lora_type
            lora_output_path.mkdir(parents=True, exist_ok=True)
            lora_dirs = []
            for model in loras_set:
                path = model['path']
                lora_dirs += [path]
            create_symlinks(lora_dirs, str(lora_output_path), SymlinkMode.TRAVERSE)
            loras_args += [typeToArg[lora_type], str(lora_output_path)]

        return loras_args