#!/bin/bash

# Setup script for installing the HuggingFace pip modules.
# These modules are transformers, accelerate, evaluate,
# and datasets. While other modules are needed, some will
# need to built or downloaded manually -- these are the 
# official packages that work out-of-the-box.
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

# install transformers and co. in the venv
echo "##### Installing HuggingFace packages #####"
pip install transformers accelerate evaluate datasets
if [ $? -ne 0 ]; then
	echo "Pip install of transformers failed! Aborting"
	exit 1
fi

# exit venv
deactivate