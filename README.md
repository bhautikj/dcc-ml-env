# DCC-ML-Env

`DCC-ML-env` is a toy tool for testing bleeding edge ML tools in creative workflows. This is a partial re-creation of the convienience that many at studios/agencies have of creating work environments for each shot/project on the command line, and launching (version controlled!) versions of the tool that Just Work™.

Bleeding-edge ML tooling as of early 2026 tends to be pipeline-unfriendly, mixing up asset ingest/creation, configuration, data and code/binaries in the same directories. This is an attempt to use VFX-pipeline style symlinking to re-scaffold a handful of these tools so that they can be centrally managed and minimize breakage due to the (frequent!) tool upgrades.

`DCC-ML-env` provides a streamlined way to manage tools, models, and work environments for creative projects. It handles tool version management with conda environment isolation, model versioning, and workspace configuration.

*Disclaimer* this is a _toy implementation_ to explore the boundaries and gaps in current tooling. I would not recommend using this for serious production work but to inform the shape of more mature platforms that wish to add ML tooling to creative pipelines.

## Premise
 
### The Goal

In a VFX-/studio-/agency-style pipeline, shared tools across a production should probably do these things:
- They should stay a stable version during the production for stability & repeatability
  - ML tools update often and these changes can break stability/repeatability
- They should separate binaries/code, data to run the app, config files and assets
  - ML tools will sometimes cram these all together into one folder
- It should be easy to start work on a shot with a selection of curated tools and assets

### The fix

The basic idea this toy pipeline is exploring: re-wrap ML tools via symlinks so that there is a separation between
- Tool code/binaries + conda env for each (versioned)
- Tool models (versioned)

And in a workspace you have
- A selection of tools + models (versioned!)
- Per-workspace tool configs
- Per-workspace user assets (both inputs and outputs) 

## Prequisites

For now I'm assuming a unix-flavoured filesystem that can support symlinks (ie linux or macos, unsure if windows will work). I'm also assuming that you are using a separate [conda](https://www.anaconda.com/docs/getting-started/miniconda/main) for each tool.

## Quick Start

Get up and running quickly with these simple steps:

### Installation

```bash
git clone https://github.com/bhautikj/dcc-ml-env
pip install -r requirements.txt
pip install -e .
```

### Initialize and use a workspace

Copy the test yaml file and edit it to configure it for your workspace. 
```bash
cp test.yaml.orig my_workspace.yaml
```

Sample:
```
working_directory: "/home/username/workspace/my_shot"

tools:
  - name: "comfyui"
    type: "comfyui"
    version: "20260219"
    path: "/home/username/source/ComfyUI-20260219"
    env: "comfyui"
    models:
      - name: "ckpts"
        subtype: "ckpts"
        path: "/home/username/models/models.comfy"
```
(see sections below on tool setup)

```bash
dcc-ml-env my_workspace.yaml
```

This will create a directory structure like so:

```
my_shot/
├──bin            # symlink trees of tools and run_XYZ_APP.sh launchers
├──config         # config files for the tools
├──in             # where to place input assets (apps will point to this)
├──out            # where output assets are put by default
├──models         # symlinks to the ML models
├──tmp            # temp dirs for the tools; cleared up on exit
└──var            # var dirs for the tools; not cleared up on exit 
```

### Creative iteration in a workspace

```bash
cd /home/username/workspace/my_shot
cp /shared/assets/assets_for_my_shot/* /home/username/workspace/my_shot/in
bin/run_comfyui_20260219.sh
#..
#..creative iteration in comfyui
#..

# output assets
ls /home/username/workspace/my_shot/out
```

You can pass in any extra arguments to comfyui at the end of the `run_XYZ.sh` command; they will automatically be passed through to the tool.

## Tool Setup

### Supported tools

For the moment this `DCC-ML-env` only supports [Wan2GP](https://github.com/deepbeepmeep/Wan2GP), [ComfyUI](https://github.com/Comfy-Org/ComfyUI) and [rife](https://github.com/nihui/rife-ncnn-vulkan/releases). I've included instructions to set these up with `DCC-ML-env` but you will likely have to customise it for your own setup.

#### Base directories

I'd _highly_ recommend creating a base directory for your tools to keep them all in one place. In a multi-user env, this should be accessible to all users. Something like

```
mkdir /shared/tools
```

I'd also recommend creating a base directory for the models. You can easily use up comically large amounts of redundant storage for models; the idea is to create common model directories to share between app versions to minimise that wastage that at least. 

```
mkdir /shared/models
```

Advanced users could create meta-model directories that symlink to specific model versions if finer-grained model versioning or access is required. 

I'm going to use `/shared/models` and `/shared/tools` for the examples below; customise this as needed.

### Wan2GP

[Wan2GP](https://github.com/deepbeepmeep/Wan2GP) is pleasant surprise - a low-frills, mostly no-nonsese tool for image, video and audio generation. Under the hood it supports a wide variety of models (notably video gen models) and can easily be configured to work on low-spec systems. It just needs a bit of extra scaffolding to make it pipeline-ready.

#### Checking out and setting up Wan2GP

Navigate [here](https://github.com/deepbeepmeep/Wan2GP/) and look for the [Latest Updates](https://github.com/deepbeepmeep/Wan2GP/?tab=readme-ov-file#-latest-updates-). Make a note of the date for the update and sketch it down in ISO8601 format (eg. 19 Feb 2026->`20260219`).

Check out the code using a version
```
git clone https://github.com/deepbeepmeep/Wan2GP /shared/tools/Wan2GP-20260219
```

Of course, you can check out other versions - just use the correct version (as a date) for each.

#### Linking models

*If you haven't done this yet* create a folder that will contain the models that `Wan2GP` will download.

```
mkidir /shared/models/wan2gp-ckpts
```

Now point the checkpoints folder in the tool you just checked out to that shared model folder

```
cd /shared/tools/Wan2GP-20260219
mv ckpts ckpts.old
ln -s /shared/models/wan2gp-ckpts .
```

Luckily you can confgure `Wan2GP` to look for LORA's in certain directories using command-line options, so no symlinking required. I'd still recommend creating shared directories for these:

```
mkidir /shared/models/wan2gp-loras
mkidir /shared/models/wan2gp-i2v
```

#### Conda env for Wan2GP
Now create a conda env for `Wan2GP`

```
conda create -n wan2gp-20260219 python=3.10.9
```

You don't _have_ to create a separate conda env for each `Wan2GP` version but you're less likely to run into version skew issues if you do when checking out a newer version later. Keep a note of the version. 

Finish following the setup instructions in the [installation guide](https://github.com/deepbeepmeep/Wan2GP/blob/main/docs/INSTALLATION.md).

#### Adding it to your workspace

Under `tools` in your workspace yaml you can link to the tool like so - note the `env` matches the conda env abocve and the `path` likewise etc. The `subtype` supported by the models currently are `ckpts` (ie the main models), `lora` (a general directory for LORA's), `i2v` (Image to Video specific) and `lxtv` (LORA's for LTXv2).

```
tools:
  - name: "wan2gp"
    type: "wan2gp"
    version: "20260219"
    path: "/shared/tools/Wan2GP-20260219
    env: "wan2gp-20260219"
    models:
      - name: "ckpts"
        subtype: "ckpts"
        path: "/shared/models/wan2gp-ckpts"
      - name: "lora"
        subtype: "lora"
        path: "/shared/models/wan2gp-loras"
      - name: "i2v"
        subtype: "i2v"
        path: "/shared/models/wan2gp-loras-i2v"
```

When creating the workspace

- It will add a shell script to launch that automatically manages the directories eg `bin/run_wan2gp_20260219.sh`. A symlink copy of the code will be put into `bin/wan2gp/20260219`.
- You can access the WebUI for running it at `http://0.0.0.0:7860` 
- Extra shell script options will automatically be passed through to the launcher.
- Generations will automatically be placed into `out/wan2gp/20260219`


### ComfyUI
[ComfyUI](https://github.com/Comfy-Org/ComfyUI) is a swiss-army-knife node-based editor. It has a focus on image generation and editing but can be configured for video and audio editing/generation as well. It has an extensive plugin/nodes extension system which in turn offers gives you multiple feet and a variety of weapons ranging from pistols to automatic rifles to shoot them with. A key feature is the concept of `ComfyUI workflows` write out the node graphs to disk and can be shared. The thought here is that version locking in the tool itself combined with versioned workflows could lead to more stable production usage (though a `TODO` is to version the comfyui nodes themselves alongside the other versioning).

#### Checking out and setting up ComfyUI

Navigate [here](https://github.com/Comfy-Org/ComfyUI); make a note of today date for the update and sketch it down in ISO8601 format (eg. 20 Feb 2026->`20260220`).

Check out the code using a version
```
git clone https://github.com/Comfy-Org/ComfyUI /shared/tools/ComfyUI-20260220
```

Of course, you can check out other versions - just use the correct version (as a date) for each.

#### Linking models

*If you haven't done this yet* create a folder that will contain the models that `ComfyUI` will download.

```
mkdir /shared/models/comfyui_models
```

Now point the models folder in the tool you just checked out to that shared model folder

```
cd /shared/tools/ComfyUI-20260220
mv ckpts models.old
ln -s /shared/models/comfyui_models .
```

#### Conda env for ComfyUI
Now create a conda env for `ComfyUI`

```
conda create -n comfyui-20260220 python=3.12
```

You don't _have_ to create a separate conda env for each `ComfyUI` version but you're less likely to run into version skew issues if you do when checking out a newer version later. Keep a note of the version. 

Finish following the setup instructions in the [installation guide](https://github.com/Comfy-Org/ComfyUI?tab=readme-ov-file#manual-install-windows-linux).

#### Adding it to your workspace

Under `tools` in your workspace yaml you can link to the tool like so - note the `env` matches the conda env abocve and the `path` likewise etc. Note that the LORA's and other models are stored in the overall shared `models` directory, not separately.

```
  - name: "comfyui"
    type: "comfyui"
    version: "20260220"
    path: "/shared/tools/ComfyUI-20260220"
    env: "comfyui"
    models:
      - name: "ckpts"
        subtype: "ckpts"
        path: "/shared/models/comfyui_models"
```

When creating the workspace

- It will add a shell script to launch that automatically manages the directories eg `bin/run_comfyui_20260220.sh`. A symlink copy of the code will be put into `bin/comfyui/20260220`.
- You can access the WebUI for running it at `http://0.0.0.0:8188` 
- Extra shell script options will automatically be passed through to the launcher.
- Generations will automatically be placed into `out/comfyui/20260220`

### Rife temporal video upscaling
I put in [Rife](https://github.com/nihui/rife-ncnn-vulkan/), a command-line video-in-video-out tool for frame interpolation in the mix to round it out with a tool that doesn't have a web interface. It's not ridiculously amazing quality but it's fast and more than enough for creative experiments, and is nicely paired with Wan2.x video generation which natively only exports at 16fps.

#### Checking out and setting up Rife

Navigate [here](https://github.com/nihui/rife-ncnn-vulkan/releases) and download the version for the platform; latest should be fine (note the ISO8601 dates, which makes my nerd heart very happy to see)

Unzip it
```
unzip rife-ncnn-vulkan-20221029-ubuntu.zip /shared/tools/
```

Note the version eg `20221029` and directory eg `/shared/tools/rife-ncnn-vulkan-20221029-ubuntu`. This comes with everything you need - no conda env or model downloads are required.

#### Adding it to your workspace

Under `tools` in your workspace yaml you can link to the tool like so - note the `env` matches the conda env abocve and the `path` likewise etc. This just uses the default `base` conda env.

```
  - name: "rife"
    type: "rife"
    version: "20221029"
    path: "/shared/tools/rife-ncnn-vulkan-20221029-ubuntu"
    env: "base"
```

When creating the workspace

- It will add a shell script to launch that automatically manages the directories eg `bin/run_rife_20221029.sh`. A symlink copy of the code will be put into `bin/rife/20221029`.
- Simply run it with `bin/run_rife_20221029.sh NAME_OF_VIDEO.mp4` and it will create a Rife 4x temporally upscaled version next to it.
- Extra shell script options will automatically be passed through to the launcher.

## Running tests
```
cd dcc-ml-env
pytest tests
```

## Contributing

Contributions are but at least for the near future I'm going to be a bit slow at reviewing PRs.

## License

This project is licensed under the MIT License - see the LICENSE file for details.