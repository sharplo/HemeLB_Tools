#!/usr/bin/python3.6
# Local modules
from PipeFlow import *

"""

obj = Poiseuille(5e-5, 5e-5)
obj.CompareExSol_1D(obj.cL, 'grid_z', 'Uz')
obj.CompareExSol_1D(obj.cL, 'grid_z', 'P')
obj.CompareExSol_2D(obj.pZ, 'grid_x', 'grid_y', 'Uz')
obj.Visualise_TimeSeries(obj.pZ, 'P', 'Uz')
obj.WriteDiscErr(obj.cL, 'P')
obj.WriteDiscErr(obj.pZ, 'Uz')

"""

obj = Bifurcation(dx=5e-5, dt=1e-5)
obj.Visualise_TimeSeries(obj.iNpYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT1pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT1pYcEN, 'P', 'Uz')
