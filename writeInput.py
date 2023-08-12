#!/usr/bin/python3.6
import sys
import pandas as pd
from MyModules.InputOutput import *

## Single experiment
#--------------------------------------------------------------------------------------
InOut = InputOutput(sys.argv[1], sys.argv[2])

# General
param_sim = {'kernel':'TRT', 'tau':0.56, 'time':9.2, 'relaxationParameter':0.25, \
             'YoungsModulus':9000000, 'BoundaryVelocityRatio':0.45}

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

# Abdominal aorta
param_iN = {'type':'velocity', 'subtype':'file', 'Re':600, 'Wo':11.2, \
            'profile':'ESM_File2_Q_d4.txt', 'offset':0.2}
param_oUT = {'type':'pressure', 'subtype':'WK', 'geometry':'0156_0001_7e-3', \
    'flowRateRatios':'Murray', 'power':2, 'gamma_R':1024, 'gamma_RC':256}

#InOut.RescaleSize(1e-3)
InOut.ChangeParam(param_sim, param_iN=param_iN, param_oUT=param_oUT)
InOut.WriteInput(sys.argv[3])

#--------------------------------------------------------------------------------------

"""

## Series of experiments
#--------------------------------------------------------------------------------------
CaseName = '0156_0001v3_1e-4'
Exp = pd.read_csv(CaseName + '/exp.csv')
InFile = CaseName + '/input_VfWKf.xml'
OutFilePrefix = '/input_'

for row in Exp.itertuples(index=False):
    print('caseNum', row.caseNum)
    InOut = InputOutput(InFile, CaseName + '/')
    param_sim = {'kernel':'TRT', 'tau':0.56, 'time':9.2, 'relaxationParameter':row.Lambda, \
                 'YoungsModulus':row.E, 'BoundaryVelocityRatio':row.F}
    param_iN = {'type':'velocity', 'subtype':'file', 'Re':row.Re, 'Wo':row.Wo, \
                'profile':'ESM_File2_Q_d4.txt', 'offset':0.2}
    param_oUT = {'type':'pressure', 'subtype':'WK', 'geometry':'0156_0001_7e-3', \
                 'flowRateRatios':'Murray', 'power':row.m, 'gamma_R':row.gamma_R, 'gamma_RC':row.gamma_RC}
    InOut.ChangeParam(param_sim, param_iN=param_iN, param_oUT=param_oUT)
    InOut.WriteInput(OutFilePrefix + str(row.caseNum) + '.xml')

"""
