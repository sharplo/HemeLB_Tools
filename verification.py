#!/usr/bin/python3.6
import os
import sys
from MyModules.Poiseuille import *
from MyModules.Bifurcation import *
from MyModules.Windkessel import *

inFile=sys.argv[1]
dataDir=sys.argv[2]
outDir=sys.argv[3] + 'figures/'
shotBeg=int(sys.argv[4])
shotEnd=int(sys.argv[5])
shotStep=int(sys.argv[6])

if not os.path.exists(outDir):
    os.mkdir(outDir)

"""

obj = Poiseuille(inFile, dataDir, outDir, shotBeg, shotEnd, shotStep)
obj.CompareExSol_1D(obj.cL, 'grid_z', 'Uz')
obj.CompareExSol_1D(obj.cL, 'grid_z', 'P')
obj.Visualise_1D(obj.cL, 'grid_z', 'err_P')
obj.CompareExSol_2D(obj.pZ, 'grid_x', 'grid_y', 'Uz')
obj.Visualise_2D(obj.pZ, 'grid_x', 'grid_y', 'err_Uz')
obj.WriteDiscErr(obj.cL, 'P')
obj.WriteDiscErr(obj.pZ, 'Uz')



obj = Bifurcation(inFile, dataDir, outDir, shotBeg, shotEnd, shotStep)
obj.Visualise_TimeSeries(obj.iNpYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT1pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT1pYcEN, 'P', 'Uz')

"""

obj = Windkessel(inFile, dataDir, outDir, shotBeg, shotEnd, shotStep)
obj.Clustering(obj.oUT, obj.position_oUT)
Q_oUT = obj.CalFlowRate(obj.oUT, range(10), obj.normal_oUT)
Qratios = obj.CalFlowRateRatios(Q_oUT)

Q_mag = obj.CalFlowRate(obj.oUT, range(10))
obj.CheckNormalAssumption(Q_mag, Q_oUT, range(10))
obj.CheckPressureAssumption(obj.oUT)
obj.EmpiricalMurrayPower(Qratios['Measured'].to_numpy())

obj.Compare_Scatter(Qratios)
Qratios.to_csv(outDir + 'Qratios.csv', index=False)
obj.AddDataFrame('iNcEN', ['iN', 'cEN'])
obj.Visualise_TimeSeries(obj.iNcEN, 'P', 'Uz')
obj.Visualise_Clusters(Q_oUT, 'Q', range(10))
obj.Visualise_Ratios(Q_oUT, 'Q', range(10))
obj.AddDataFrame('oUT0cEN', ['oUT0', 'cEN'])
obj.Visualise_TimeSeries(obj.oUT0cEN, 'P', 'Uz')
obj.AddDataFrame('oUT1cEN', ['oUT1', 'cEN'])
obj.Visualise_TimeSeries(obj.oUT1cEN, 'P', 'Uz')
obj.AddDataFrame('oUT2cEN', ['oUT2', 'cEN'])
obj.Visualise_TimeSeries(obj.oUT2cEN, 'P', 'Uz')
obj.AddDataFrame('oUT3cEN', ['oUT3', 'cEN'])
obj.Visualise_TimeSeries(obj.oUT3cEN, 'P', 'Uz')
obj.AddDataFrame('oUT4cEN', ['oUT4', 'cEN'])
obj.Visualise_TimeSeries(obj.oUT4cEN, 'P', 'Uz')
