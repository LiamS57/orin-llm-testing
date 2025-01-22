#!/bin/bash

# Setup script for installing NVIDIA's pre-built PyTorch
# package. The official PyTorch package does not come with
# CUDA compatibility with JetPack, but NVIDIA produces
# PyTorch wheel files for each version. This script 
# downloads and installs the file specified in
# setup_vars.sh.

MAIN_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )
source $MAIN_DIR/scripts/setup/setup_vars.sh

# check that venv exists
if [ ! -d $HF_ENV ]; then
    # no venv created, running creation script
    source $SETUP_SH_DIR/setup_venv.sh
fi

# enter venv
source $HF_ENV/bin/activate

# make temp directory for building if it doesn't exist
if [ ! -d $TMP_DIR ]; then
    mkdir $TMP_DIR
fi
cd $TMP_DIR

# download nvidia's pytorch wheel file
if [ -d torch ]; then
	# this might only happen if you're running the script after a failed attempt
	echo "##### Erasing previous PyTorch download #####"
	rm -Rf torch
fi
echo "##### Downloading PyTorch from NVIDIA #####"
mkdir torch
cd torch
wget https://developer.download.nvidia.com/compute/redist/jp/v60/pytorch/$TORCHFILE
if [ ! -f ./$TORCHFILE ]; then
	echo "Unable to download PyTorch wheel file! Aborting"
	exit 1
fi

# install downloaded wheel file
echo "##### Installing PyTorch #####"
export TORCH_INSTALL=./$TORCHFILE
pip install --no-cache $TORCH_INSTALL
if [ $? -ne 0 ]; then
	echo "Pip install of downloaded PyTorch wheel file failed! Aborting"
	exit 1
fi

# exit venv and return
deactivate
cd $MAIN_DIR