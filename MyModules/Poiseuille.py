import numpy as np
from MyModules.PipeFlow import *

class Poiseuille(PipeFlow):
    # Assumptions:
    # 1) the geometry is a cylinder
    # 2) the centre of the inlet is placed at the origin
    # 3) the cylindrical axis lies on the y-z plane

    def __init__(self, inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict=None):
        if dfDict == None:
            dfDict = {'iN':'inlet', 'oUT':'outlet', 'cL':'centreLine', 'pN':'planeN'}
        PipeFlow.__init__(self, inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict)

        for key in self.dfDict.keys():
            self.AddRadialDistance(getattr(self, key))
            self.AddNormalVelocity(getattr(self, key))
        self.CalExact(self.cL, 'P')
        self.CalExact(self.cL, 'Un')
        self.CalExact(self.pN, 'P')
        self.CalExact(self.pN, 'Un')

    def ExtractParams(self):
        self.P_ref = self.iN['P'].mean() # default value of reference pressure
        self.x_ref = self.iN[['grid_x', 'grid_y', 'grid_z']].mean() # default reference position
        self.radius = (self.position_iN[0,0] - 3) * self.dx # padding of 3 lattice units

    def DeriveParams(self):
        # If the inlet is imposed with a pressure condition
        if self.P_iN.size > 0:
            P_max = self.P_iN[0]
            x_max = self.position_iN[0,:] * self.dx
            self.P_ref = P_max
            self.x_ref = x_max
        else:
            P_max = self.iN['P'].mean()
            x_max = self.iN[['grid_x', 'grid_y', 'grid_z']].mean()

        # If the outlet is imposed with a pressure condition
        if self.P_oUT.size > 0:
            P_min = self.P_oUT[0]
            x_min = self.position_oUT[0,:] * self.dx
            self.P_ref = P_min
            self.x_ref = x_min
        else:
            P_min = self.oUT['P'].mean()
            x_min = self.oUT[['grid_x', 'grid_y', 'grid_z']].mean()

        # Calculate the pressure gradient (mmHg/m)
        self.delP = (P_min - P_max) / np.linalg.norm(x_min - x_max) * self.normal_iN[0,:]

    def AddRadialDistance(self, df):
        dist = df[['grid_x', 'grid_y', 'grid_z']] - self.position_iN[0,:] * self.dx
        dist = np.cross(dist, self.normal_iN[0,:])
        df['r'] = np.linalg.norm(dist, axis=1)

    def AddNormalVelocity(self, df):
        df['Un'] = df[['Ux', 'Uy', 'Uz']].dot(self.normal_iN[0,:])

    def CalExact(self, df, var):
        if (var == 'P'):
            dl = df[['grid_x', 'grid_y', 'grid_z']] - self.x_ref
            df['exSol_P'] = self.P_ref + dl.dot(self.delP)
        elif (var == 'Un'):
            G = - np.dot(self.delP, self.normal_iN[0,:]) * mmHg # need SI unit (Pa/m)
            exSol = lambda r: G / (4 * mu) * (self.radius**2 - r**2)
            df['exSol_Un'] = exSol(df['r'])
        # Use absolute error to prevent impacts arising from division by a small number
        df['err_' + var] = df[var] - df['exSol_' + var]

    def CompareExSol_1D(self, df, grid, var1, kwargs1=..., kwargs2=...):
        return super().Visualise_1D(df, grid, var1, 'exSol_' + var1, kwargs1={'label':'appSol'}, kwargs2={'label':'exSol'})

    def CompareExSol_2D(self, df, grid_1, grid_2, var1, var2=None):
        return super().Visualise_2D(df, grid_1, grid_2, var1, var2='exSol_' + var1)
