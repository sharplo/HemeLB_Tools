#!/usr/bin/env bash
INPUT=${1?No input provided}
DIR=${INPUT%/*} # trim everything after the last '/' to get the directory path
FILE=${INPUT##*/} # trim everything before the last '/' to get the file name
VAR=${FILE%.dat} # trim file extension to get the variable name
OUT_ALL=$VAR-all.txt

# Push the current directory to stack, and go to the directory that contains the file
pushd $DIR

# Make a new directory to avoid acidentally changing other files
mkdir -p $VAR && cd $VAR

# Find the full directory name of this script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Translate into readable format using submodule hemeXtract
$MyDir/HemeLB_Tools/submodules/hemeXtract/hemeXtract -X ../$FILE -o $OUT_ALL

# Delete all empty lines
sed -i '/^$/d' $OUT_ALL

# Go back to the original directory
popd
