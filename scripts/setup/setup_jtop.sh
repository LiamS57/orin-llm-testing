#!/bin/bash

# Setup script for installing the jetson-stats pip module.
# This module contains JTop for utilizing stats in a Python
# script.
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

# install jetson-stats (jtop)
echo "##### Installing jetson-stats #####"
pip install -U jetson-stats
if [ $? -ne 0 ]; then
	echo "Pip install of jetson-stats failed! Aborting"
	exit 1
fi

# exit venv
deactivate