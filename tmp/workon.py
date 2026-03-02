import sys, os, argparse
from pathlib import Path
import json

TOOLS = ["wan2gp"]
CONFIG_DIR = "config"
CONFIG_GLOBAL = "config.json"
WORKPATH_KEY = "workpath"
CONFIGPATH_KEY = "configpath"
WAN2GP_PATH = "/home/bjoshi/src/Wan2GP"
WAN2GP_CONFIG = "wgp_config.json"
WAN2GP_OUTPUT = "wan2gp_output"
INPUTS_KEY = "inputs"
INPUTS_DIR = "inputs"
WAN2GP_LORAS = "wan2gp_loras"
WAN2GP_CONFIG_KEY = "wgp_config"
WAN2GP_LAUNCHER = "runwgp.sh"
WAN2GP_CONDA_ENV = "wan2gp"

parser = argparse.ArgumentParser(description="Workon script")
parser.add_argument("-t", "--tool", type=str, required=True)
parser.add_argument("-w", "--workpath", type=str, required=True)

def dumpConfig(configDict, dest):
  [json.dump(configDict, open(dest, "w"), indent=2)]

def initWorkDir(workpath):
  Path(workpath).mkdir(parents=True, exist_ok=True)
  Path(os.path.join(workpath, CONFIG_DIR)).mkdir(parents=True, exist_ok=True)

  configDict = {}
  configDict[WORKPATH_KEY] = workpath
  globalConfigFile = os.path.join(workpath, CONFIG_DIR, CONFIG_GLOBAL)
  configDict[CONFIGPATH_KEY] = os.path.join(workpath, CONFIG_DIR)

  configDict[INPUTS_KEY] = os.path.join(workpath, INPUTS_DIR)
  Path(configDict[INPUTS_KEY]).mkdir(parents=True, exist_ok=True)
  
  if not os.path.exists(globalConfigFile):
    dumpConfig(configDict, globalConfigFile)
  else:
    configDict = json.load(open(globalConfigFile))
    
  return configDict, globalConfigFile
  
def initWan2GP(workpath, configDict):
  wanOutputPath = os.path.join(workpath, WAN2GP_OUTPUT)
  Path(wanOutputPath).mkdir(parents=True, exist_ok=True)

  wgpConfigPath = os.path.join(workpath, CONFIG_DIR, WAN2GP_CONFIG)
  configDict[WAN2GP_CONFIG_KEY] = wgpConfigPath

  # wanLorasPath = os.path.join(workpath, WAN2GP_LORAS)
  # Path(wanLorasPath).mkdir(parents=True, exist_ok=True)
  
  if not os.path.exists(wgpConfigPath):
    #open wgp config
    wgpConfig = json.load(open(os.path.join(WAN2GP_PATH, WAN2GP_CONFIG)))
    wgpConfig["save_path"] = wanOutputPath
    wgpConfig["image_save_path"] = wanOutputPath
    wgpConfig["audio_save_path"] = wanOutputPath
    #wgpConfig["loras_root"] = wanLorasPath
    dumpConfig(wgpConfig, wgpConfigPath)
  else:
    wgpConfig = json.load(open(wgpConfigPath))
    
  wgpLauncherPath = os.path.join(workpath, WAN2GP_LAUNCHER)
  if not os.path.exists(wgpLauncherPath):
    launcherScript =  "#!/bin/bash \n"
    launcherScript += "pushd " + WAN2GP_PATH + "\n"
    launcherScript += " ".join(["conda", 
                                "run", 
                                "--no-capture-output", 
                                "-n", 
                                WAN2GP_CONDA_ENV, 
                                "python", 
                                os.path.join(WAN2GP_PATH,"wgp.py"), 
                                "--config", 
                                configDict[CONFIGPATH_KEY], 
                                "--lora-dir",
                                "/home/bjoshi/models/video/wan2gp-loras-wan2.1",
                                "--lora-dir-i2v",
                                "/home/bjoshi/models/video/wan2gp-loras-wan2.1",
                                "--listen", 
                                "\n"])
    launcherScript += "popd \n"
    launcherPath = os.path.join(configDict[WORKPATH_KEY],WAN2GP_LAUNCHER)
    with open(launcherPath, "w") as f:
      f.write(launcherScript)
    import stat
    st = os.stat(launcherPath)
    os.chmod(launcherPath, st.st_mode | stat.S_IEXEC)
  
  
  # ltxPath = os.path.join(wanLorasPath,"ltx2")
  # if not os.path.islink(ltxPath):
  #   os.symlink(os.path.join(os.path.join(WAN2GP_PATH,"loras"),"ltx2"), ltxPath)
  #
  # wani2vlorasPath = os.path.join(wanLorasPath, "wan_i2v")
  # Path(wani2vlorasPath).mkdir(parents=True, exist_ok=True)
  # import glob
  # loraswan21List = glob.glob("/home/bjoshi/models/video/wan2gp-loras-wan2.1/*")
  # for item in loraswan21List:
  #   fn = Path(item).name
  #   dst = os.path.join(wani2vlorasPath, "21Lora-"+fn)
  #   if not os.path.islink(dst):
  #     os.symlink(item, dst)
  
  return configDict
  

def main(tool, workpath):
  configDict, globalConfigFile = initWorkDir(workpath)
  configDict = initWan2GP(workpath, configDict)
  dumpConfig(configDict, globalConfigFile)
  print(configDict)

if __name__ == "__main__":
  args = parser.parse_args()
  tool = args.tool
  if tool.lower() not in TOOLS:
    print(tool, "not supported, exiting")
    sys.exit(1)

  workpath = os.path.abspath(args.workpath)
  
  main(tool, workpath)
