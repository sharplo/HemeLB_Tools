#!/usr/bin/python3.6
import sys
import pandas as pd
from MyModules.InputOutput import *

# Single experiment
#InOut = InputOutput(sys.argv[1])
#InOut.ChangeParam(tau=0.9082, timeSteps=305000, Wo=2, Re=10, epsilon=0.1, \
#        geometry='FiveExit_1e-3', flowRateRatios=[3,4,5,6,7], gamma_R=1, gamma_C=1)
#InOut.ChangeParam(tau=0.9082, timeSteps=10000, Wo=1, Re=50, epsilon=0.1, \
#        geometry='ArteriesLegs_5e-3', flowRateRatios='Murray', gamma_R=0.01, gamma_C=100)
#InOut.WriteInput(sys.argv[2])



# Series of experiments
Exp = pd.read_csv('experiments.csv')
Dir = 'FiveExit_1e-3'
InFile = Dir + '/input_VfWKf.xml'
OutFilePrefix = Dir + '/input_'

for row in Exp.itertuples(index=False):
    print('caseNum', row.caseNum)
    InOut = InputOutput(InFile)
    InOut.ChangeParam(tau=row.tau, timeSteps=305000, Wo=2, Re=row.Re, epsilon=0.1, \
        geometry=Dir, flowRateRatios=[3,4,5,6,7], gamma_R=row.gamma_R, gamma_C=row.gamma_C)
    InOut.WriteInput(OutFilePrefix + str(row.caseNum) + '.xml')

