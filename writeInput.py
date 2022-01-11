#!/usr/bin/python3.8
import sys
from Verification.InputOutput import *

InOut = InputOutput()
#InOut.RescaleSize(sys.argv[1], sys.argv[2], 1e-3)
InOut.ChangeParam(sys.argv[1], sys.argv[2], tau=0.9082, timeSteps=10000, \
    Wo=2, Re=1, epsilon=0.2, resistanceFactor=1, flowRateRatios=[3,4,5,6,7])