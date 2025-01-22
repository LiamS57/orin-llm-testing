#!/bin/bash

# Setup script for enabling CUDA post-flashing. 
# While CUDA is installed during the flashing and JetPack 
# SDK installation, it is not necessarily accessible. This 
# script verifies the installation was successful and adds
# the CUDA bin directory to the path.

MAIN_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )
source $MAIN_DIR/scripts/setup/setup_vars.sh

echo "##### Verifying CUDA installation #####"
which nvcc
if [ $? -ne 0 ]; then
	if [ ! -f $CUDA_BIN/nvcc ]; then
		echo "Could not find nvcc binary in CUDA directory! Aborting"
		exit 1
	fi
    echo "##### Fixing PATH in .bashrc to include CUDA bin #####"
	echo "export PATH=$CUDA_BIN:\$PATH" >> ~/.bashrc
	export PATH=$CUDA_BIN:$PATH
fi
nvcc --version
if [ $? -ne 0 ]; then
	echo "Something went wrong with CUDA installation (probably an issue during the flash)! Aborting"
	exit 1
fi