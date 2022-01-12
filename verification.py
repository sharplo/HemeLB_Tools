#!/usr/bin/python3.8
from MyModules.Poiseuille import *
from MyModules.Bifurcation import *
from MyModules.Windkessel import *

"""

obj = Poiseuille()
obj.CompareExSol_1D(obj.cL, 'grid_z', 'Uz')
obj.CompareExSol_1D(obj.cL, 'grid_z', 'P')
obj.CompareExSol_2D(obj.pZ, 'grid_x', 'grid_y', 'Uz')
obj.Visualise_TimeSeries(obj.pZ, 'P', 'Uz')
obj.WriteDiscErr(obj.cL, 'P')
obj.WriteDiscErr(obj.pZ, 'Uz')



obj = Bifurcation()
obj.Visualise_TimeSeries(obj.iNpYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT1pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT1pYcEN, 'P', 'Uz')

"""

obj = Windkessel(dfDict={'oUT':'outlet'})
obj.Clustering(obj.oUT, obj.position_oUT)
flowRate_oUT = obj.CalFlowRate(obj.oUT, obj.normal_oUT, range(5))
obj.Visualise_Clusters(flowRate_oUT, 'FlowRate', range(5))
obj.Visualise_Ratios(flowRate_oUT, 'FlowRate', range(5), 0)
obj.Visualise_TimeSeries(obj.oUT, 'P')
obj.AddDataFrame('oUT0cEN', ['oUT0', 'cEN'])
obj.Visualise_TimeSeries(obj.oUT0cEN, 'P')
obj.AddDataFrame('oUT1cEN', ['oUT1', 'cEN'])
obj.Visualise_TimeSeries(obj.oUT1cEN, 'P')
obj.AddDataFrame('oUT2cEN', ['oUT2', 'cEN'])
obj.Visualise_TimeSeries(obj.oUT2cEN, 'P')
obj.AddDataFrame('oUT3cEN', ['oUT3', 'cEN'])
obj.Visualise_TimeSeries(obj.oUT3cEN, 'P')
obj.AddDataFrame('oUT4cEN', ['oUT4', 'cEN'])
obj.Visualise_TimeSeries(obj.oUT4cEN, 'P')
flowRateRatios = obj.CalFlowRateRatios(flowRate_oUT, 0)
obj.Compare_Scatter(flowRateRatios, 0)
flowRateRatios.to_csv('figures/flowRateRatios.csv', index=False)