#!/usr/bin/python3.9
import os
import sys
from MyModules.Poiseuille import *

inFile=sys.argv[1]
dataDir=sys.argv[2]
outDir=sys.argv[3]
stepBeg=int(sys.argv[4])
stepEnd=int(sys.argv[5])

if not os.path.exists(outDir):
    os.mkdir(outDir)

obj = Poiseuille(inFile, dataDir, outDir, stepBeg, stepEnd)
obj.CompareExSol_1D(obj.cL, 'grid_z', 'Un')
obj.CompareExSol_1D(obj.cL, 'grid_z', 'P')
obj.Visualise_1D(obj.cL, 'grid_z', 'err_P')
obj.WriteDiscErr(obj.cL, 'P')
obj.CompareExSol_1D(obj.pN, 'grid_x', 'Un')
obj.CompareExSol_2D(obj.pN, 'grid_x', 'grid_y', 'Un')
obj.Visualise_1D(obj.pN, 'grid_x', 'err_Un')
obj.Visualise_2D(obj.pN, 'grid_x', 'grid_y', 'err_Un')
obj.WriteDiscErr(obj.pN, 'Un')