#!/usr/bin/python3.6
import sys
import pandas as pd
from MyModules.InputOutput import *

# Single experiment
#InOut = InputOutput(sys.argv[1])
#InOut.ChangeParam(tau=0.8, timeSteps=25800, Wo=2, Re=10, epsilon=0.1, \
#        geometry='FiveExit_1e-3', flowRateRatios=[3,4,5,6,7], gamma_R=1, gamma_C=1)
#InOut.ChangeParam(tau=0.9082, timeSteps=100000, Wo=2, Re=10, epsilon=0.1, \
#        geometry='ArteriesLegs_5e-3', flowRateRatios='Murray', gamma_R=1, gamma_C=8)
#InOut.WriteInput(sys.argv[2])



# Series of experiments
CaseName = 'FiveExit_coarse'
Exp = pd.read_csv(CaseName + '/experiments.csv')
InFile = CaseName + '/input_VfWKf.xml'
OutFilePrefix = '/input_'

for row in Exp.itertuples(index=False):
    print('caseNum', row.caseNum)
    InOut = InputOutput(InFile, CaseName + '/')
    InOut.ChangeParam(tau=0.8, timeSteps=row.timeSteps, Wo=2, Re=10, epsilon=0.1, \
        geometry='FiveExit_1e-3', flowRateRatios=[3,4,5,6,7], gamma_R=row.gamma_R, gamma_C=row.gamma_C)
    InOut.WriteInput(OutFilePrefix + str(row.caseNum) + '.xml')

