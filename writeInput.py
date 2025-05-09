#!/usr/bin/python3.9
import sys
import pandas as pd
from MyModules.InputOutput import *

## Single experiment
#--------------------------------------------------------------------------------------
InOut = InputOutput(sys.argv[1], sys.argv[2])

# General
param_sim = {'kernel':'LBGK', 'tau':0.9, 'time':2.4}

# Cylinder
param_iN = {'type':'yangpressure', 'subtype':'cosine', 'Re':5.7}
param_oUT = {'type':'yangpressure', 'subtype':'cosine'}

InOut.ChangeParam(param_sim, param_iN=param_iN, param_oUT=param_oUT)
InOut.WriteInput(sys.argv[3])

#--------------------------------------------------------------------------------------