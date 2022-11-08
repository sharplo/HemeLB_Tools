#!/usr/bin/env bash

# Define paths
DIR=/net/storeptr1/heme/SharpLoWork
TOOLDIR=$DIR/HemeLB_Tools
EXE=$DIR/HemePure_Jon/src/build_Ladd_Nash_BFL/hemepure
INFILE=$DIR/HemePure_Jon/cases/SixBranch_r5/input.xml
OUTDIR=$DIR/test

# Run the simulation
rm -rf $OUTDIR
mpirun -n 8 $EXE -in $INFILE -out $OUTDIR
cp $INFILE $OUTDIR

# Post-process data
data=("inlet" "outlet" "surface")
for datum in "${data[@]}"
do
    bash $TOOLDIR/paraviewPreprocess.sh $OUTDIR/Extracted/$datum.dat
done

# Analyse data
python $TOOLDIR/verification.py $INFILE $OUTDIR/Extracted/ $OUTDIR/figures/ 0 9 1