# Local modules
from PipeFlow import *

obj = Poiseuille(5e-5, 5e-5)
obj.CompareExSol_1D(obj.cL, 'grid_z', 'Uz')
obj.Visualise_2D(obj.pZ, 'grid_x', 'grid_y', 'Uz')
obj.Visualise_2D(obj.pZ, 'grid_x', 'grid_y', 'Uz', 'Ux')
obj.CompareExSol_2D(obj.pZ, 'grid_x', 'grid_y', 'Uz')
obj.Visualise_TimeSeries(obj.pZ, 'P', 'Ux')
obj.WriteDiscErr(obj.cL, 'P')
obj.WriteDiscErr(obj.pZ, 'Uz')