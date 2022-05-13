from MyModules.PipeFlow import *

class Poiseuille(PipeFlow):
    # Assumptions:
    # 1) the pipe is cylindrical and has constant cross-section
    # 2) the cylindrical axis is in the z direction

    def __init__(self, inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict=None):
        if dfDict == None:
            dfDict = {'iN':'inlet', 'oUT':'outlet', 'cL':'centreLine', 'pZ':'planeZ'}
        PipeFlow.__init__(self, inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict)

        for key in self.dfDict.keys():
            self.AddRadialDistance(getattr(self, key))
        self.CalExact(self.cL, 'P')
        self.CalExact(self.cL, 'Uz')
        self.CalExact(self.pZ, 'P')
        self.CalExact(self.pZ, 'Uz')

    def ExtractParams(self):
        self.P_ref = self.iN['P'].mean() # default value
        self.z_ref = self.iN['grid_z'].mean() # default value
        self.x_cEN = self.position_iN[0,0] * self.dx # x-ord of centre
        self.radius = self.x_cEN - 3 * self.dx # padding of 3 lattice units

    def DeriveParams(self):
        # If the inlet is imposed with pressure condition
        if self.P_iN.size > 0:
            P_max = self.P_iN[0]
            z_max = self.position_iN[0,2] * self.dx
            self.P_ref = P_max
            self.z_ref = z_max
        else:
            P_max = self.iN['P'].mean()
            z_max = self.iN['grid_z'].mean()

        # If the outlet is imposed with pressure condition
        if self.P_oUT.size > 0:
            P_min = self.P_oUT[0]
            z_min = self.position_oUT[0,2] * self.dx
            self.P_ref = P_min
            self.z_ref = z_min
        else:
            P_min = self.oUT['P'].mean()
            z_min = self.oUT['grid_z'].mean()
        
        # Calculate the pressure gradient (mmHg/m)
        self.dPdz = (P_min - P_max) / (z_min - z_max)

    def AddRadialDistance(self, df):
        df['r'] = np.sqrt((df['grid_x'] - self.x_cEN)**2 + (df['grid_y'] - self.x_cEN)**2)

    def CalExact(self, df, var):
        if (var == 'P'):
            exSol = lambda z: self.P_ref + self.dPdz * (z - self.z_ref)
            df['exSol_P'] = exSol(df['grid_z'])
        elif (var == 'Uz'):
            G = - self.dPdz * mmHg # need SI unit (Pa/m)
            exSol = lambda r: G / (4 * mu) * (self.radius**2 - r**2)
            df['exSol_Uz'] = exSol(df['r'])
        # Use absolute error to avoid division by 0
        df['err_' + var] = df[var] - df['exSol_' + var]

    def CompareExSol_1D(self, df, grid, var1, kwargs1=..., kwargs2=...):
        return super().Visualise_1D(df, grid, var1, 'exSol_' + var1, kwargs1={'label':'appSol'}, kwargs2={'label':'exSol'})

    def CompareExSol_2D(self, df, grid_1, grid_2, var1, var2=None):
        return super().Visualise_2D(df, grid_1, grid_2, var1, var2='exSol_' + var1)
