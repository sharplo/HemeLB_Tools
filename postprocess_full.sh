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
$SCRIPT_DIR/submodules/hemeXtract/hemeXtract -X ../$FILE -o $OUT_ALL

# Find the first line containing "step" and store it in a variable
HEADER=$(grep -m 1 'step' $OUT_ALL)

# Delete all empty lines
sed -i '/^$/d' $OUT_ALL

# Separate time series into individual files (THIS MAY TAKE A LONG TIME!)
awk -v var=$VAR -v header="$HEADER" -F ' ' \
'
    BEGIN{N=-3; last_step=-1}
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

# Remove temporary files
rm $VAR\-1.txt $VAR\-2.txt

# Go back to the original directory
popd
