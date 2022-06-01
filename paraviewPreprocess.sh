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

# Find the full directory name of this script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Translate into readable format using submodule hemeXtract
$SCRIPT_DIR/submodules/hemeXtract/hemeXtract -X ../$FILE -o $OUT_ALL

# Replace "| " with "" and "# step" with "step" in the first 30 lines and save
HEADER=$(sed -n '1,30s/| //g;1,30s/# step/step/p' $OUT_ALL)

# Delete all empty lines
sed -i '/^$/d' $OUT_ALL

# Separate time series into individual files
awk -v var=$VAR -v header="$HEADER" -F ' ' \
'
    BEGIN{N=-2; last_step=-1}
    {
        if(last_step != $1)
        {
            N++;
            print header > var N".txt";
            print >> var N".txt";
            last_step=$1;
        }
        else
        {
            print >> var N".txt"
        }
    }
' $OUT_ALL

# Go back to the original directory
popd
