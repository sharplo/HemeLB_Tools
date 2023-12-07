#!/usr/bin/python3.6
import os
import sys
from MyModules.Poiseuille import *
from MyModules.Bifurcation import *
from MyModules.Windkessel import *
from MyModules.ElasticPipe import *

inFile=sys.argv[1]
dataDir=sys.argv[2]
outDir=sys.argv[3]
shotBeg=int(sys.argv[4])
shotEnd=int(sys.argv[5])
shotStep=int(sys.argv[6])

if not os.path.exists(outDir):
    os.mkdir(outDir)

"""

obj = Poiseuille(inFile, dataDir, outDir, shotBeg, shotEnd, shotStep)
obj.CompareExSol_1D(obj.cL, 'grid_z', 'Un')
obj.CompareExSol_1D(obj.cL, 'grid_z', 'P')
obj.Visualise_1D(obj.cL, 'grid_z', 'err_P')
obj.WriteDiscErr(obj.cL, 'P')
obj.CompareExSol_1D(obj.pN, 'grid_x', 'Un')
obj.CompareExSol_2D(obj.pN, 'grid_x', 'grid_y', 'Un')
obj.Visualise_1D(obj.pN, 'grid_x', 'err_Un')
obj.Visualise_2D(obj.pN, 'grid_x', 'grid_y', 'err_Un')
obj.WriteDiscErr(obj.pN, 'Un')



obj = Bifurcation(inFile, dataDir, outDir, shotBeg, shotEnd, shotStep)
obj.Visualise_TimeSeries(obj.iNpYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT1pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT1pYcEN, 'P', 'Uz')

"""

obj = Windkessel(inFile, dataDir, outDir, shotBeg, shotEnd, shotStep)
period = 20
Q_iN = obj.CalAverageFlowRates(obj.iN, range(obj.numInlets))
Q_oUT = obj.CalAverageFlowRates(obj.oUT, range(obj.numOutlets))
Qavg_oUT = obj.CalAverageFlowRates(obj.oUT, range(obj.numOutlets), avgSteps=period)
Qratios = obj.CalFlowRateRatios(Q_oUT)

# Check implementations and assumptions
obj.Check_Clustering(obj.oUT)
obj.CheckMassConservation()
Q_mag = obj.CalAverageFlowRates(obj.oUT, range(obj.numOutlets))
obj.CheckNormalAssumption(Q_mag, Q_oUT, range(obj.numOutlets))
obj.CheckPressureAssumption(obj.oUT)
obj.EmpiricalMurrayPower(Qratios['Measured'].to_numpy())

# Collective analysis
obj.Visualise_Clusters(Q_iN, 'Q', range(obj.numInlets))
obj.Visualise_Clusters(Q_oUT, 'Q', range(obj.numOutlets))
obj.Visualise_Ratios(Qavg_oUT, 'Q', range(obj.numOutlets))
obj.Compare_Scatter(Qratios)
Qratios.to_csv(outDir + 'Qratios.csv', index=False)

# Individual analysis
obj.Visualise_TimeSeries(obj.iN0cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT0cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT1cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT2cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT3cEN, 'P', 'Un')

"""

dfDict = {'iN':'inlet', 'oUT':'outlet', 'pN':'planeN'}
rng1 = range(12000, 15500)
rng2 = range(12200, 15500)

obj = ElasticPipe(inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict)
obj.AddDataFrame('iNcEN', ['iN', 'cEN'])
obj.AddDataFrame('oUTcEN', ['oUT', 'cEN'])
obj.AddDataFrame('pNcEN', ['pN', 'cEN'])
obj.Visualise_TimeSeries(obj.iNcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pNcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.oUTcEN, 'P', 'Uz')
#obj.Compare_TimeSeries(obj.iNcEN, obj.pNcEN, 'P', 'Uz')
obj.Visualise_1D(obj.iNcEN, 'Uz', 'P', steps=rng1)
obj.Visualise_1D(obj.pNcEN, 'Uz', 'P', steps=rng2)
obj.Visualise_1D(obj.iNcEN, 'step', 'P', 'Uz', steps=rng1)
obj.Visualise_1D(obj.pNcEN, 'step', 'P', 'Uz', steps=rng2)
pwv_P = obj.CalPulseWaveVelocity(obj.iNcEN, rng1, obj.pNcEN, rng2, 'P', 5e-3)
pwv_Uz = obj.CalPulseWaveVelocity(obj.iNcEN, rng1, obj.pNcEN, rng2, 'Uz', 5e-3)
print('pwv_P', pwv_P, 'pwv_Uz', pwv_Uz)



dfDict = {'iN':'inlet', 'oUT':'outlet', 'sF':'surface'}
obj = PipeFlow(inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict)
rng = range(0,600)
riskFactors = obj.AneurysmsRiskFactors(obj.sF, rng)
obj.Visualise_3D(obj.sF, 'WSS')
obj.Visualise_3D(riskFactors, 'TAWSS')
obj.Visualise_3D(riskFactors, 'OSI')
obj.Visualise_3D(riskFactors, 'ECAP')
obj.Visualise_3D(riskFactors, 'MNS')

"""