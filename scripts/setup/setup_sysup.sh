#!/bin/bash

# Setup script for updating the system and installing
# additional packages needed for the environment.
# 
# This script will take longer than expected, but running
# it with an ethernet cable connected may considerably
# speed up the process.

MAIN_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )
source $MAIN_DIR/scripts/setup/setup_vars.sh

# getting upgrades, jetpack stuff (cuda), and python stuff
echo "##### Updating, upgrading, and installing packages #####"
sudo -- sh -c 'apt update && apt -y upgrade && apt -y install nvidia-jetpack python3-pip python3-venv libopenblas-dev git cmake wget nano'
if [ $? -ne 0 ]; then
	echo "Unable to update/upgrade and/or install packages! Aborting"
	exit 1
fi