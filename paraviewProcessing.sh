#!/usr/bin/env bash
INPUT=${1?No input provided}
DIR=${INPUT%/*} # trim everything after the last '/' to get the directory path
FILE=${INPUT##*/} # trim everything before the last '/' to get the file name
VAR=${FILE%.dat} # trim file extension to get the variable name
OUT_ALL=$VAR-all.txt

# Push the current directory to stack, and go to the directory that contains the file
pushd $DIR

# Make a new directory to avoid acidentally changing other files
mkdir $VAR && cd $VAR

# Translate into readable format using submodule hemeXtract
submodules/hemeXtract/hemeXtract -X ../$FILE -o $OUT_ALL

# Delete the first 2 lines
sed -i '1,2d' $OUT_ALL

# Delete all empty lines
sed -i '/^$/d' $OUT_ALL

# Separate time series into individual files
awk -v out=$VAR -F ' ' 'BEGIN{N=-2; last_step=-1}{if(last_step != $1) {N++; print>out N".txt"; last_step=$1;} else {print>>out N".txt"}}' $OUT_ALL

# Insert headers to the 1st line:
# search for "| " in the first few lines in file A,
# replace them with "", and insert them in file B
sed -i "1e sed -n '1,30s/| //pg' $OUT_ALL" $VAR*
# remove "# " on the 1st line
sed -i "1s/# //" $VAR*

# Go back to the original directory
popd
