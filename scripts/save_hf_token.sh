#!/bin/bash

# Saves a hf_token from args to a file for use by the
# testing scripts.

MAIN_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && cd .. && pwd )
TOKEN_FILE=$MAIN_DIR/tests/access_token
echo "Saving $1 to $TOKEN_FILE"
echo $1 > $TOKEN_FILE