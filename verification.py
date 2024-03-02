#!/usr/bin/python3.6
import os
import json
from MyModules.Windkessel import *

# Define paths
DIR = '/work/e769/e769/sharplo4/0156_0001v3_1e-4/case_0/'
inFile = DIR + 'input_0.xml'
dataDir = DIR + 'Extracted/'
outDir = DIR + 'verification/'

# Set parameters for ranges
avgSteps = 20
shotEnd = 230
numPeriods = 3
shotBeg = shotEnd - numPeriods * avgSteps + 1

# Create the output directory if it is absent
if not os.path.exists(outDir):
    os.mkdir(outDir)

# Calculate quantities related to the Windkessel BC for the outlets
obj = Windkessel(inFile=inFile, dataDir=dataDir, outDir=outDir, \
    shotBeg=shotBeg, shotEnd=shotEnd, shotStep=1, ref=2)
obj.CheckMassConservation()

# Calculate the flow rate
Q_iN = obj.CalAverageFlowRates(obj.iN, range(obj.numInlets))
Q_oUT = obj.CalAverageFlowRates(obj.oUT, range(obj.numOutlets))
Qavg_oUT = obj.CalAverageFlowRates(obj.oUT, range(obj.numOutlets), avgSteps=avgSteps)
obj.Visualise_Clusters(Q_iN, 'Q', range(obj.numInlets))
obj.Visualise_Clusters(Q_oUT, 'Q', range(obj.numOutlets))
obj.Visualise_Ratios(Qavg_oUT, 'Q', range(obj.numOutlets))

# Calculate the flow rate ratios
Qratios = obj.CalFlowRateRatios(Q_oUT)
obj.Compare_Scatter(Qratios)
Qratios.to_csv(outDir + 'Qratios.csv', index=False)
Qratios = Qratios.drop(index=obj.ref)

# Plot the pressure and normal velocity at the centre of the outlets
obj.Visualise_TimeSeries(obj.iN0cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT0cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT1cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT2cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT3cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT4cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT5cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT6cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT7cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT8cEN, 'P', 'Un')
obj.Visualise_TimeSeries(obj.oUT9cEN, 'P', 'Un')

# Calculate the risk factors for aneurysm
obj2 = PipeFlow(inFile=inFile, dataDir=dataDir, outDir=outDir, \
    shotBeg=shotBeg, shotEnd=shotEnd, shotStep=1, \
    dfDict={'sA':'sphereA', 'sB':'sphereB'})
AAA = pd.merge(obj2.sA, obj2.sB, how='outer')
AAA.name = 'AAA'
avgU = AAA[['step', 'grid_x', 'grid_y', 'grid_z', 'Ux', 'Uy', 'Uz']]
avgU = obj2.CalTemporalAverage(avgU, range(1000000))
avgU = avgU.drop(columns=['step'])
riskFactors = obj2.AneurysmsRiskFactors(AAA, range(1000000))
fields = pd.merge(avgU, riskFactors, how='outer')
fields.to_csv(outDir + 'fields.csv', index=False)

# Write quantities of interest
qoi = {
    'Qratios_Desired': Qratios['Desired'].tolist(),
    'Qratios_Measured': Qratios['Measured'].tolist(),
    'Qratios_RelErr': Qratios['RelErr'].tolist(),
    'TAWSS': riskFactors['TAWSS'].describe().drop(['count']).tolist(),
    'OSI': riskFactors['OSI'].describe().drop(['count']).tolist(),
    'ECAP': riskFactors['ECAP'].describe().drop(['count']).tolist(),
    'RRT': riskFactors['RRT'].describe().drop(['count']).tolist()
}
with open(outDir + 'qoi.json', 'w') as f:
    json.dump(qoi, f, indent=2)