#!/usr/bin/python3.6
import sys
import pandas as pd
from MyModules.InputOutput import *

# Single experiment
#InOut = InputOutput(sys.argv[1])
#InOut.RescaleSize(1e-3)
#InOut.ChangeParam(tau=0.9082, timeSteps=300000, Wo=2, Re=100, epsilon=0.2, \
#        flowRateRatios=[3,4,5,6,7], mulFact_R=1, mulFact_C=1)
#InOut.WriteInput(sys.argv[2])

# Series of experiments
exp = pd.read_csv('experiments.csv')
inFile = 'FiveExit_input.xml'
outFilePrefix = 'input_'

for row in exp.itertuples(index=False):
    InOut = InputOutput(inFile)
    InOut.ChangeParam(tau=0.9082, timeSteps=300000, Wo=2, Re=100, epsilon=0.2, \
        flowRateRatios=[3,4,5,6,7], mulFact_R=row.gamma_R, mulFact_C=row.gamma_C)
    InOut.WriteInput(outFilePrefix + str(row.caseNum) + '.xml')