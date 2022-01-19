#!/usr/bin/python3.6
import sys
from MyModules.InputOutput import *

InOut = InputOutput(sys.argv[1])
#InOut.RescaleSize(1e-3)
InOut.ChangeParam(tau=0.9082, timeSteps=300000, \
    Wo=2, Re=100, epsilon=0.2, flowRateRatios=[3,4,5,6,7], mulFact_R=1, mulFact_C=1)
InOut.WriteInput(sys.argv[2])