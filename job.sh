#!/usr/bin/env bash

# Define paths
DIR=/work/e723/e723-hemelbalya/sharplo5
TOOLDIR=$DIR/HemeLB_Tools
INFILE=$DIR/cylinder/r10/input_1.xml
OUTDIR=$DIR/cylinder/r10

# Post-process data
data=("inlet" "outlet" "centreLine" "planeN" "planeY")
for datum in "${data[@]}"
do
    bash $TOOLDIR/postprocess_essential.sh $OUTDIR/Extracted/$datum.dat
done

# Analyse data
python $TOOLDIR/verification.py $INFILE $OUTDIR/Extracted/ $OUTDIR/figures_18/ 5400 5400
python $TOOLDIR/verification.py $INFILE $OUTDIR/Extracted/ $OUTDIR/figures_20/ 6000 6000