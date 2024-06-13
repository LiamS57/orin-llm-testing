#!/bin/bash

# Post-setup script for cleaning up any remaining temp
# files.
# 
# Liam Seymour 6/13/24

MAIN_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )
source $MAIN_DIR/scripts/setup/setup_vars.sh

if [ -d $TMP_DIR ]; then
    echo "##### Cleaning up $TMP_DIR #####"
    rm -Rf $TMP_DIR
fi