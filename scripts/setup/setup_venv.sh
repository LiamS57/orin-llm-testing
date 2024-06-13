#!/bin/bash

# Setup script for virtual environment.
# If a previous environment exists, removes it.
# 
# Liam Seymour 6/13/24

MAIN_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )
source $MAIN_DIR/scripts/setup/setup_vars.sh

if [ -d $HF_ENV ]; then
    echo "##### Removing old virtual environment #####"
    rm -Rf $HF_ENV
fi
echo "##### Creating virtual environment #####"
python -m venv $HF_ENV
if [ $? -ne 0 ]; then
	echo "Something went wrong with creating the virtual environment! Aborting"
	exit 1
fi