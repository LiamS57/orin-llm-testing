#!/bin/bash

# Setup script for environment variables used during setup.
# All setup scripts will source this just in case, to make 
# sure things run smoothly.
# 
# Liam Seymour 6/13/24

MAIN_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )
SETUP_SH_DIR=$MAIN_DIR/scripts/setup

HF_ENV=$MAIN_DIR/hf-env
TORCHFILE=torch-2.4.0a0+07cecf4168.nv24.05.14710581-cp310-cp310-linux_aarch64.whl
CUDA_VER=122
CUDA_BIN=/usr/local/cuda/bin

# prevent running in sudo
if [ `id -u` -eq 0 ]; then
	echo "Please run with user level permissions (i.e. no sudo or root)!"
	exit 1
fi

# move to main directory if not already there
if [ ! pwd -ef $MAIN_DIR ]; then
    echo "Moving to $MAIN_DIR"
    cd $MAIN_DIR
fi