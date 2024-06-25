# Setup Scripts

### [setup_all.sh](./setup_all.sh)
The default script to run for a full installation.
This script will call every other setup script in the folder to perform the installation.

### [setup_sysup.sh](./setup_sysup.sh)
Performs system upgrades and installs several required packages for the environment. This is one of the longest portions of the process, as it installs the JetPack SDK components manually (required for CUDA after flashing with flash.sh).

### [setup_cuda.sh](./setup_cuda.sh)
Verifies that CUDA is installed properly and adds the CUDA bin directory to the PATH. This script assumes that the user is using bash (default for Ubuntu) -- if this is changed, then the user will need to change ".bashrc" in the script to the appropriate file.

### [setup_venv.sh](./setup_venv.sh)
Creates the virtual environment where HuggingFace's Python packages (and any other necessary Pytyhon packages) are installed. 

:warning: Erases any previous venv that may exist when run! This *will* remove any previously installed packages in the venv folder!

### [setup_pytorch.sh](./setup_pytorch.sh)
Downloads and installs NVIDIA's prebuilt PyTorch wheel file for JetPack 6.0 and CUDA 12.2. In case the file to download needs to be changed, it can be edited in ```setup_vars.sh```.

### [setup_transformers.sh](./setup_transformers.sh)
Performs the pip installation of all the official HuggingFace packages that work out-of-the-box. These include ```transformers```, ```accelerate```, ```evaluate```, and ```datasets```.

### [setup_bitsandbytes.sh](./setup_bitsandbytes.sh)
Compiles and installs the bitsandbytes quantization library from source. This is required for ```bitsandbytes``` to work with NVIDIA's provided PyTorch wheel file. In the event that the installed CUDA version is not 12.2, you will need to edit the version number variable in ```setup_vars.sh```.

### [setup_pip_extra.sh](./setup_pip_extra.sh)
Performs the pip installation of ```jetson-stats``` (JTop), ```matplotlib```, and ```pandas```.

### [setup_post_clean.sh](./setup_post_clean.sh)
Removes any remaining temporary files, in case they have been left by the installation process.

### [setup_vars.sh](./setup_vars.sh)
Utility script (sourced by every other script) to ensure installation variables are correct and things are being run in the correct directories.
