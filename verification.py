#!/usr/bin/python3.6
import os
import sys
from MyModules.Poiseuille import *
from MyModules.Bifurcation import *
from MyModules.Windkessel import *

if not os.path.exists('./figures'):
    os.mkdir('./figures')

inFile=sys.argv[1]
dir=sys.argv[2]
shotBeg=int(sys.argv[3])
shotEnd=int(sys.argv[4])
shotStep=int(sys.argv[5])

"""

obj = Poiseuille(inFile, dir, shotBeg, shotEnd, shotStep)
obj.CompareExSol_1D(obj.cL, 'grid_z', 'Uz')
obj.CompareExSol_1D(obj.cL, 'grid_z', 'P')
obj.CompareExSol_2D(obj.pZ, 'grid_x', 'grid_y', 'Uz')
obj.Visualise_TimeSeries(obj.pZ, 'P', 'Uz')
obj.WriteDiscErr(obj.cL, 'P')
obj.WriteDiscErr(obj.pZ, 'Uz')



obj = Bifurcation(inFile, dir, shotBeg, shotEnd, shotStep)
obj.Visualise_TimeSeries(obj.iNpYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT1pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT1pYcEN, 'P', 'Uz')

"""

obj = Windkessel(inFile, dir, shotBeg, shotEnd, shotStep)
obj.Clustering(obj.oUT, obj.position_oUT)
flowRate_oUT = obj.CalFlowRate(obj.oUT, obj.normal_oUT, range(5))
flowRateRatios = obj.CalFlowRateRatios(flowRate_oUT)

obj.AddDataFrame('iNcEN', ['iN', 'cEN'])
obj.Visualise_TimeSeries(obj.iNcEN, 'P', 'Uz')
obj.Visualise_Clusters(flowRate_oUT, 'FlowRate', range(5))
obj.Visualise_Ratios(flowRate_oUT, 'FlowRate', range(5))
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
obj.Compare_Scatter(flowRateRatios)
flowRateRatios.to_csv('figures/flowRateRatios.csv', index=False)
