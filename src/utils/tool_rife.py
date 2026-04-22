from src.utils.workspace import Workspace, WorkspaceAuxDirs, ModelType, ToolType
from src.utils.tool_instances import ToolBase
from pathlib import Path
from glob import glob
import json, stat, os

# rife installed from https://github.com/nihui/rife-ncnn-vulkan/releases

rifeScript = """
#!/bin/bash
substr="rife4x"
UUID=`uuidgen`
FPS=`ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of default=noprint_wrappers=1:nokey=1 "$1" | cut -d "/" -f 1`
FRAMENUM=`ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$1"`
TARGETFPS=$(($FPS * 4))
TARGETFRAMES=$(($FRAMENUM * 4))

filename=$(basename "$1")
extension="${filename##*.}"
filename="${filename%.*}"
dirpath=$(dirname "$1")
target=$dirpath"/"$filename-$substr.$extension

if [[ -f "$target" ]]; then
  echo "exists, skipping " $filename
  exit 0
fi

if [[ $filename == *"$substr"* ]]; then
  echo "already processed, skipping " $filename
  exit 0
fi

FILE_SIZE=$(wc -c "$1" | awk '{print $1}')
if [[ "$FILE_SIZE" -lt "$MIN_SIZE" ]]; then
  echo "not ready, skipping " $filename
  exit 0
fi

echo /tmp/$UUID-input
echo /tmp/$UUID-output
echo $FPS
echo $TARGETFPS
echo $dirpath $filename $extension
echo $target
echo $FRAMENUM $TARGETFRAMES

# drop last frame
#ffmpeg -ss 0.0625 -i "$1" -c:v libx264 -c:a aac "$2"

# extract frames
echo "==EXTRACTING FRAMES=="
mkdir /tmp/$UUID-input
`ffmpeg -ss 0.0625 -i "$1" /tmp/$UUID-input/frame_%08d.png`

# gen frames
echo "==GENERATING FRAMES=="
mkdir /tmp/$UUID-output
`RIFE_PATH -n $TARGETFRAMES -u -m rife-v4.6 -i /tmp/$UUID-input -o /tmp/$UUID-output`

# recombine
echo "==RECOMBINING FRAMES=="
`ffmpeg -framerate $TARGETFPS -i /tmp/$UUID-output/%08d.png -crf 18 -c:v libx264 -pix_fmt yuv420p "$target"`
rm -rf /tmp/$UUID-output
rm -rf /tmp/$UUID-input
"""

class ToolRife(ToolBase):
    def _setup_tool_directories(self):
        """Set up tool directories and paths."""
        for tool_workspace in self.workspace.get_tools():
            tool_type = tool_workspace.get('type')
            if tool_type != ToolType.RIFE.value:
                continue
            tool_name = tool_workspace.get('name')
            tool_version = tool_workspace.get('version')
            tool_orig_path = tool_workspace.get('path')
            assert(tool_orig_path != None)

            tool_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.BINARIES.value/ tool_name / tool_version
            print("creating", tool_dest_path)
            tool_dest_path.mkdir(parents=True, exist_ok=True)
            assert(tool_dest_path != None)

    def _create_tool_symlinks(self):
        """Create symlinks for tool files."""
        for tool_workspace in self.workspace.get_tools():
            tool_type = tool_workspace.get('type')
            if tool_type != ToolType.RIFE.value:
                continue

            tool_name = tool_workspace.get('name')
            tool_version = tool_workspace.get('version')
            tool_orig_path = tool_workspace.get('path')
            
            tool_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.BINARIES.value/ tool_name / tool_version
            
            # symlink dir
            tool_orig_files = glob(str(Path(tool_orig_path) / '*'))
            for tool_orig_file in tool_orig_files:
                tool_orig_file_name = str(Path(tool_orig_file).name)
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

            # create shell script
            tool_code_path = str(tool_dest_path / "rife-ncnn-vulkan")
            shellScript = rifeScript.replace("RIFE_PATH", tool_code_path)
            shell_code_path = tool_dest_path / "rife4x.sh"
            
            shell_code_path.write_text(shellScript)
            # Get current mode
            current_mode = shell_code_path.stat().st_mode

            # Add execute permissions for the owner (user)
            shell_code_path.chmod(current_mode | stat.S_IXUSR)
            assert(os.access(shell_code_path, os.X_OK))

    def _handle_checkpoint_symlinks(self):
        """Handle checkpoint symlinks."""
        pass

    def _manage_config_files(self):
        """Manage configuration files."""
        pass

    def _create_launcher_script(self):
        """Create launcher script with proper permissions."""
        for tool_workspace in self.workspace.get_tools():
            tool_type = tool_workspace.get('type')
            if tool_type != ToolType.RIFE.value:
                continue

            tool_name = tool_workspace.get('name')
            tool_version = tool_workspace.get('version')
            tool_orig_path = tool_workspace.get('path')
            
            tool_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.BINARIES.value/ tool_name / tool_version
            output_dest_path = Path(self.workspace.get_working_directory()) / WorkspaceAuxDirs.OUT.value / (tool_name + '_' + tool_version)
            
            #create launcher
            tool_code_path = str(tool_dest_path / "rife4x.sh")
            
            #TODO: resolve why this just won't run in conda
            # conda_env = tool_workspace.get('env')
            # assert(conda_env != None)

            # launcherCmd =  ["conda",
            #                 "run",
            #                 "--no-capture-output",
            #                 "-n",
            #                 conda_env,
            #                 "sh",
            #                 tool_code_path]           
            # launcherCmd += ['"$@"']
            # print(launcherCmd)
            # launcherScript =  "#!/bin/bash \n"
            # launcherScript += "pushd " + str(tool_dest_path) + "\n"
            # launcherScript += " ".join(launcherCmd) + "\n"
            # launcherScript += "popd \n"

            # print(launcherScript)

            launcherFile =  Path(self.workspace.get_working_directory()) \
                            / WorkspaceAuxDirs.BINARIES.value \
                            / str("run_" + tool_name + "_" + tool_version + ".sh")
            
            src = Path(tool_code_path)
            dest = Path(launcherFile) 
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

            # launcherFile.write_text(launcherScript)
            # # Get current mode
            # current_mode = launcherFile.stat().st_mode

            # # Add execute permissions for the owner (user)
            # launcherFile.chmod(current_mode | stat.S_IXUSR)
            # assert(os.access(launcherFile, os.X_OK))
