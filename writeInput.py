#!/usr/bin/python3.6
import sys
import pandas as pd
from MyModules.InputOutput import *

## Single experiment
#--------------------------------------------------------------------------------------
#InOut = InputOutput(sys.argv[1], sys.argv[2])

# General
#param_sim = {'tau':0.9082, 'timeSteps':340000}

# Pipe
#param_iN = {'type':'velocity', 'subtype':'parabolic', 'Re':10}
#param_oUT = {'type':'pressure'}

# FiveExit
#param_iN = {'type':'velocity', 'subtype':'file', 'Re':10, 'Wo':2, 'epsilon':0.1}
#param_oUT = {'type':'windkessel', 'subtype':'GKmodel', 'geometry':'FiveExit_1e-3', \
#    'flowRateRatios':[3,4,5,6,7], 'gamma_R':1, 'gamma_C':1}

# ProfundaFemoris
#param_iN = {'type':'velocity', 'subtype':'file', 'Re':10, 'Wo':2, 'epsilon':0.1}
#param_oUT = {'type':'windkessel', 'subtype':'fileGKmodel', 'geometry':'ProfundaFemoris2_2e-3', \
#    'flowRateRatios':'Murray', 'power':3, 'gamma_R':1, 'gamma_C':1}

#InOut.ChangeParam(param_sim, param_iN=param_iN, param_oUT=param_oUT)
#InOut.WriteInput(sys.argv[3])

#--------------------------------------------------------------------------------------



## Series of experiments
#--------------------------------------------------------------------------------------
CaseName = 'ProfundaFemoris2_fine'
Exp = pd.read_csv(CaseName + '/experiments.csv')
InFile = CaseName + '/input_VfWKf.xml'
OutFilePrefix = '/input_'

for row in Exp.itertuples(index=False):
    print('caseNum', row.caseNum)
    InOut = InputOutput(InFile, CaseName + '/')
    param_sim = {'tau':0.9082, 'timeSteps':row.timeSteps}
    param_iN = {'type':'velocity', 'subtype':'file', 'Re':10, 'Wo':2, 'epsilon':0.1}
    param_oUT = {'type':'windkessel', 'subtype':'fileGKmodel', 'geometry':'ProfundaFemoris2_2e-3', \
    'flowRateRatios':'Murray', 'power':3, 'gamma_R':row.gamma_R, 'gamma_C':row.gamma_C}
    InOut.ChangeParam(param_sim, param_iN=param_iN, param_oUT=param_oUT)
    InOut.WriteInput(OutFilePrefix + str(row.caseNum) + '.xml')

