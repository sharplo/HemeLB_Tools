#!/usr/bin/python3.6
import sys
import pandas as pd
from MyModules.InputOutput import *

## Single experiment
#--------------------------------------------------------------------------------------
InOut = InputOutput(sys.argv[1], sys.argv[2])

# General
param_sim = {'kernel':'LBGK', 'tau':0.54, 'time':5}

# Cylinder
#param_iN = {'type':'velocity', 'subtype':'parabolic', 'Re':10}
#param_oUT = {'type':'pressure', 'subtype':'cosine'}

# bifurcation
#param_iN = {'type':'velocity', 'subtype':'file', 'Re':400, 'Wo':5.9, 'epsilon':0.9}
#param_oUT = {'type':'pressure', 'subtype':'WK', 'geometry':'bifurcation_1e-3', \
#    'flowRateRatios':[1,2], 'gamma_R':1e3, 'gamma_RC':1e5}

# FiveExit
#param_iN = {'type':'velocity', 'subtype':'file', 'Re':10, 'Wo':2, 'epsilon':0.1}
#param_oUT = {'type':'pressure', 'subtype':'fileWK', 'geometry':'FiveExit_1e-3', \
#    'flowRateRatios':[3,4,5,6,7], 'gamma_R':4, 'gamma_RC':4}

# ProfundaFemoris
#param_iN = {'type':'velocity', 'subtype':'file', 'Re':10, 'Wo':2, 'epsilon':0.1}
#param_oUT = {'type':'pressure', 'subtype':'fileWK', 'geometry':'ProfundaFemoris2_2e-3', \
#    'flowRateRatios':'Murray', 'power':3, 'gamma_R':1, 'gamma_RC':1}

# Aorta
param_iN = {'type':'velocity', 'subtype':'file', 'Re':309, 'Wo':11.2, 'profile':'ESM_File2_Q_d4.txt'}
param_oUT = {'type':'pressure', 'subtype':'fileWK', 'geometry':'0149_1001_7e-3', \
    'flowRateRatios':'Murray', 'power':3, 'gamma_R':1e3, 'gamma_RC':1e5}

#InOut.RescaleSize(1e-3)
InOut.ChangeParam(param_sim, param_iN=param_iN, param_oUT=param_oUT)
InOut.WriteInput(sys.argv[3])

#--------------------------------------------------------------------------------------

"""

## Series of experiments
#--------------------------------------------------------------------------------------
CaseName = 'ProfundaFemoris2_coarse'
Exp = pd.read_csv(CaseName + '/experiments.csv')
InFile = CaseName + '/input_VfWKf.xml'
OutFilePrefix = '/input_'

for row in Exp.itertuples(index=False):
    print('caseNum', row.caseNum)
    InOut = InputOutput(InFile, CaseName + '/')
    param_sim = {'tau':0.9082, 'timeSteps':row.timeSteps}
    param_iN = {'type':'velocity', 'subtype':'file', 'Re':10, 'Wo':2, 'epsilon':0.1}
    param_oUT = {'type':'pressure', 'subtype':'fileWK', 'geometry':'ProfundaFemoris2_2e-3', \
    'flowRateRatios':'Murray', 'power':3, 'gamma_R':row.gamma_R, 'gamma_RC':row.gamma_RC}
    InOut.ChangeParam(param_sim, param_iN=param_iN, param_oUT=param_oUT)
    InOut.WriteInput(OutFilePrefix + str(row.caseNum) + '.xml')

"""
