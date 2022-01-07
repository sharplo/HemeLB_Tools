#!/usr/bin/python3.8
import sys
from Verification.InputOutput import *

InOut = InputOutput()
#InOut.RescaleSize(sys.argv[1], sys.argv[2], 1e-3)
InOut.ChangeParam(sys.argv[1], sys.argv[2])