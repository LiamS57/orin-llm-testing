#!/bin/bash

# Removes all models stored in the huggingface cache.

# prevent running in sudo
if [ `id -u` -eq 0 ]; then
	echo "Please run with user level permissions (i.e. no sudo or root)!"
	exit 1
fi

HF_HUB_DIR=~/.cache/huggingface/hub

# check if hub dir exists
if [ ! -d $HF_HUB_DIR ]; then
	echo "$HF_HUB_DIR doesn't exist! Has a HuggingFace model been downloaded before?"
	exit 1
fi

# delete all models stored in hub dir
for MODEL in $HF_HUB_DIR/models*
do
	SIZE=`du -sh $MODEL | cut -f1`
	echo -n "Removing $MODEL ($SIZE)..."
	rm -Rf $MODEL
	echo "done"
done

echo -n "Syncing..."
sync
echo "done"
