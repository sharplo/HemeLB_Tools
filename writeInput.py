#!/usr/bin/python3.8
import sys
from Verification.InputOutput import *

InOut = InputOutput()
#InOut.RescaleSize(sys.argv[1], sys.argv[2], 1e-3)
InOut.ChangeParam(sys.argv[1], sys.argv[2], tau=0.9082, timeSteps=300000, \
    Wo=1, Re=1, epsilon=0.2, flowRateRatios=[3,4,5,6,7], mulFact_R=1, mulFact_C=1)