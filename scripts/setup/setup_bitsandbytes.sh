#!/bin/bash

# Setup script for building and installing HuggingFace's 
# quantization module (bitsandbytes). The official pip
# module does not work with the installed CUDA and PyTorch
# and must be built from source for it to work.
# 
# The compilation at the 'make' stage will take longer than
# expected and make a large number of repeated warnings --
# this is fine! Allow it to complete, and as long as the
# correct PyTorch package is installed it should be fine.
# 
# NOTE: If you run this script before setup_pytorch.sh, the
# testing phase will automatically install the official 
# PyTorch pip package which does not work! Please ensure 
# the correct PyTorch package is installed beforehand!
# 
# Liam Seymour 6/13/24

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

# clone bitsandbytes source
if [ -d bitsandbytes ]; then
	# this might only happen if you're running the script after a failed attempt
	echo "##### Erasing previous bitsandbytes source #####"
	rm -Rf bitsandbytes
fi
echo "##### Building bitsandbytes from source #####"
git clone https://github.com/TimDettmers/bitsandbytes.git
if [ $? -ne 0 ]; then
	echo "Unable to clone bitsandbytes source from github! Aborting"
	exit 1
fi
cd bitsandbytes

# run cmake
cmake -DCOMPUTE_BACKEND=cuda -S .
if [ $? -ne 0 ]; then
	echo "bitsandbytes cmake failed! Aborting"
	exit 1
fi

# run make
make -j4 CUDA_VERSION=$CUDA_VER
if [ $? -ne 0 ]; then
	echo "bitsandbytes make failed! Aborting"
	exit 1
fi

# install module and verify
echo "##### Installing bitsandbytes #####"
python setup.py install
if [ $? -ne 0 ]; then
	echo "Failed to install built bitsandbytes module! Aborting"
	exit 1
fi
echo "##### Testing bitsandbytes #####"
python -m bitsandbytes
if [ $? -ne 0 ]; then
	echo "Bitsandbytes compilation did not produce a working module! Aborting"
	exit 1
fi

# exit venv and return
deactivate
cd $MAIN_DIR