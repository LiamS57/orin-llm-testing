#!/bin/bash

# Setup script for a full installation of the environment.
# 
# Due to the modularity of this setup system, this script
# simply runs all other setup scripts in the recommended
# order. If a failure occurs, the entire process will end.
# This allows for a user to pick up where the process left
# off after determining what fix is needed for the error.

MAIN_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )
source $MAIN_DIR/scripts/setup/setup_vars.sh

echo "##### Beginning full setup process #####"

source $SETUP_SH_DIR/setup_sysup.sh
source $SETUP_SH_DIR/setup_cuda.sh
source $SETUP_SH_DIR/setup_venv.sh
source $SETUP_SH_DIR/setup_pytorch.sh
source $SETUP_SH_DIR/setup_transformers.sh
source $SETUP_SH_DIR/setup_bitsandbytes.sh
source $SETUP_SH_DIR/setup_pip_extra.sh
source $SETUP_SH_DIR/setup_post_clean.sh

echo "##### Completed full setup process! #####"
echo "It is recommended to close this terminal window and open another one for the change to .bashrc to take effect! Otherwise, testing scripts may not work properly."