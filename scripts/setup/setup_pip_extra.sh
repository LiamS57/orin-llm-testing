#!/bin/bash

# Setup script for installing the additional required pip 
# modules. This module contains JTop (jetson-stats) for 
# utilizing stats in a Python script, and matplotlib + pandas
# for building graphs and visualizing data post-testing.
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
echo "##### Installing additional required pip packages #####"
pip install -U jetson-stats matplotlib pandas
if [ $? -ne 0 ]; then
	echo "Pip install of additional required packages failed! Aborting"
	exit 1
fi

# exit venv
deactivate