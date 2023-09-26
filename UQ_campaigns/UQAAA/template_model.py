#!/usr/bin/python3.8
import sys
import os
import json

# Define paths
DIR = '/work/e769/e769/sharplo4/'
TOOLDIR = DIR + 'HemeLB_Tools/'
EXE = DIR + 'HemePure/src/build_Ladd_Nash_TRT_GZSE/hemepure'

numPeriods = int(sys.argv[1])
outDir = sys.argv[2]
if not os.path.exists(outDir):
    os.mkdir(outDir)

# Import MyModules in TOOLDIR
sys.path.insert(1, TOOLDIR)
from MyModules.InputOutput import *
from MyModules.Windkessel import *

# Define function for executing bash commands
def execute(command):
    print('Executing "' + command + '"')
    ret = os.system(command)
    if ret != 0:
        print('Failed to run "' + command + '"')

## Make an input file of HemeLB
# Define parameters
InOut = InputOutput(inFile='template_input.xml', outDir='./')
param_sim = {'kernel':'TRT', 'tau':0.56, 'time':9.2, 'relaxationParameter':$Lambda, \
             'YoungsModulus':$E, 'BoundaryVelocityRatio':$F}
param_iN = {'type':'velocity', 'subtype':'file', 'Re':$Re, 'Wo':$Wo, \
            'profile':'ESM_File2_Q_d4.txt', 'offset':0.2}
param_oUT = {'type':'pressure', 'subtype':'WK', 'geometry':'0156_0001_7e-3', \
    'flowRateRatios':'Murray', 'power':$m, 'gamma_R':$gamma_R}
param_oUT['gamma_RC'] = $gamma_R * $gamma_C

# Make the new input file
InOut.ChangeParam(param_sim, param_iN, param_oUT, geometryPath=DIR + 'HemePure/cases/0156_0001v3_1e-4/')
InOut.WriteInput(fileName='input.xml')

# Run the HemeLB simulation
execute('srun --nodes=32 --ntasks=4096 --cpus-per-task=1 --mem-per-cpu=0 --overlap --exact ' + EXE + ' -in input.xml -out sim; sleep 10')

## Post-process results of the simulation (perform in the second run)
# Convert data to a human-readable format
data = ['inlet', 'outlet', 'sphereA', 'sphereB']
for datum in data:
    execute('bash ' + TOOLDIR + 'paraviewPreprocess.sh sim/Extracted/' + datum + '.dat')
    pass

# Set parameters for ranges
avgSteps = 20
stepsPerShot = int(InOut.outputPeriod / avgSteps)
shotEnd = int(InOut.timeSteps / stepsPerShot - 1 - $shotShift)
shotBeg = shotEnd - numPeriods * avgSteps + 1

# Calculate quantities related to the Windkessel BC for the outlets
obj = Windkessel(inFile='input.xml', dataDir='sim/Extracted/', outDir=outDir, \
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
obj2 = PipeFlow(inFile='input.xml', dataDir='sim/Extracted/', outDir=outDir, \
    shotBeg=shotBeg, shotEnd=shotEnd, shotStep=1, \
    dfDict={'sA':'sphereA', 'sB':'sphereB'})
AAA = pd.merge(obj2.sA, obj2.sB, how='outer')
AAA.name = 'AAA'
riskFactors = obj2.AneurysmsRiskFactors(AAA, range(InOut.timeSteps))
riskFactors.to_csv(outDir + 'riskFactors.csv', index=False)

## Write quantities of interest
# For the second run
qoi = {
    'Qratios_Desired': Qratios['Desired'].tolist(),
    'Qratios_Measured': Qratios['Measured'].tolist(),
    'Qratios_RelErr': Qratios['RelErr'].tolist(),
    'TAWSS': riskFactors['TAWSS'].describe().drop(['count']).tolist(),
    'OSI': riskFactors['OSI'].describe().drop(['count']).tolist(),
    'ECAP': riskFactors['ECAP'].describe().drop(['count']).tolist(),
    'RRT': riskFactors['RRT'].describe().drop(['count']).tolist()
}
"""
# For the first run
qoi = {
    'Qratios_Desired': 0,
    'Qratios_Measured': 0,
    'Qratios_RelErr': 0,
    'TAWSS': 0,
    'OSI': 0,
    'ECAP': 0,
    'RRT': 0
}
"""
with open(outDir + 'qoi.json', 'w') as f:
    json.dump(qoi, f, indent=2)
