#!/usr/bin/python3.6
import sys
import os

# Define paths
DIR = '/net/storeptr1/heme/SharpLoWork/'
TOOLDIR = DIR + 'HemeLB_Tools/'
EXE = DIR + 'HemePure_Jon/src/build_Ladd_Nash_BFL/hemepure'

# Import MyModules in TOOLDIR
sys.path.insert(1, TOOLDIR)
from MyModules.InputOutput import *
from MyModules.Windkessel import *

# Function definitions
def execute(command):
    print('Executing "' + command + '"')
    ret = os.system(command)
    if ret != 0:
        print('Failed to run "' + command + '"')

## Make an input file of HemeLB
# Define parameters in the normal condition
InOut = InputOutput(inFile='template_input.xml', outDir='./')
param_sim = {'kernel':'LBGK', 'tau':0.8, 'timeSteps':1000}
param_iN = {'type':'velocity', 'subtype':'file', 'Re':1, 'Wo':2, 'epsilon':0.1}
param_oUT = {'type':'pressure', 'subtype':'WK', 'geometry':'FiveExit_1e-3', \
    'flowRateRatios':[3,4,5,6,7], 'power':3, 'gamma_R':4, 'gamma_RC':4}

# Modify the flow rate ratios according to the degrees of stenosis (DoS)
Rratios = InOut.CalResistanceRatios(param_oUT)
Qratios = Rratios[0] / Rratios
Qratios[0] = Qratios[0] * (1 - $DoS_0)
Qratios[1] = Qratios[1] * (1 - $DoS_1)
Qratios[2] = Qratios[2] * (1 - $DoS_2)
Qratios[3] = Qratios[3] * (1 - $DoS_3)
Qratios[4] = Qratios[4] * (1 - $DoS_4)
param_oUT['flowRateRatios'] = list(Qratios)

# Make the new input file
InOut.ChangeParam(param_sim, param_iN, param_oUT)
InOut.WriteInput(fileName='input.xml')

# Run the simulation
execute('mpirun -n 3 ' + EXE + ' -in input.xml -out sim_results')

# Post-process data
data = ['inlet', 'outlet', 'surface']
for datum in data:
    execute('bash ' + TOOLDIR + 'paraviewPreprocess.sh sim_results/Extracted/' + datum + '.dat')
    pass

# Analyse data
dfDict = {'iN':'inlet', 'oUT':'outlet', 'sF':'surface'}
obj = PipeFlow(inFile='input.xml', dataDir='sim_results/Extracted/', outDir='./', \
    shotBeg=0, shotEnd=9, shotStep=1, dfDict=dfDict)
rng = range(600,1000)
riskFactors = obj.AneurysmsRiskFactors(obj.sF, rng)
riskFactors.to_csv('riskFactors.csv', index=False)
obj.Visualise_3D(riskFactors, 'ECAP')
obj.Visualise_3D(riskFactors, 'MNS')