#!/usr/bin/python3.6
import sys
import pandas as pd
from pytest import param
from MyModules.InputOutput import *

## Single experiment
InOut = InputOutput(sys.argv[1], sys.argv[2])

# General
param_sim = {'tau':0.8, 'timeSteps':1000}

# Pipe
param_iN = {'type':'velocity', 'subtype':'parabolic', 'Re':10}
param_oUT = {'type':'pressure'}

# FiveExit
#param_iN = {'type':'velocity', 'subtype':'file', 'Re':10, 'Wo':2, 'epsilon':0.1}
#param_oUT = {'type':'windkessel', 'subtype':'GKmodel', 'geometry':'FiveExit_1e-3', \
#    'flowRateRatios':[3,4,5,6,7], 'gamma_R':1, 'gamma_C':1}

InOut.ChangeParam(param_sim, param_iN=param_iN, param_oUT=param_oUT)
InOut.WriteInput(sys.argv[3])

"""

## Series of experiments
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

"""