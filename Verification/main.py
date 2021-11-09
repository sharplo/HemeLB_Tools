#!/usr/bin/python3.6

# Local modules
from PipeFlow import *
from Bifurcation import *
from Poiseuille import *
from SixBranch import *

"""

obj = Poiseuille(5e-5, 5e-5)
obj.CompareExSol_1D(obj.cL, 'grid_z', 'Uz')
obj.CompareExSol_1D(obj.cL, 'grid_z', 'P')
obj.CompareExSol_2D(obj.pZ, 'grid_x', 'grid_y', 'Uz')
obj.Visualise_TimeSeries(obj.pZ, 'P', 'Uz')
obj.WriteDiscErr(obj.cL, 'P')
obj.WriteDiscErr(obj.pZ, 'Uz')



obj = Bifurcation(dx=5e-5, dt=1e-5)
obj.Visualise_TimeSeries(obj.iNpYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Visualise_TimeSeries(obj.pZOUT1pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT0pYcEN, 'P', 'Uz')
obj.Compare_TimeSeries(obj.iNpYcEN, obj.pZOUT1pYcEN, 'P', 'Uz')

"""

normal_iN = np.array([[0.866025,-2.70088e-11,-0.5]])
position_iN = np.array([[8.02016,13.0403,123.482]])

normal_oUT = - np.array([[0.866025,-2.7027e-11,0.5],
                        [2.06435e-11,-2.48225e-10,-1],
                        [-1.16783e-12,-6.89079e-12,1],
                        [-0.866025,-2.69401e-11,-0.5],
                        [-0.866025,-2.68425e-11,0.5]]) # note the global minus sign
position_oUT = np.array([[8.02016,13.0403,73.2765],
                        [51.4991,13.0403,148.584],
                        [51.4991,13.0403,3],
                        [94.978,13.0403,123.482],
                        [94.978,13.0403,73.2765]])

obj = SixBranch(dx=2e-5, dt=1e-5)
obj.Clustering(obj.oUT, position_oUT)
flowRate_oUT = obj.CalFlowRate(obj.oUT, normal_oUT, range(5))
obj.Visualise_Clusters(flowRate_oUT, 'FlowRate', range(5))
obj.Visualise_Ratios(flowRate_oUT, 'FlowRate', range(5), 0)
obj.Visualise_TimeSeries(obj.oUT, 'P')