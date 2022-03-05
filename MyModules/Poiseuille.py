from MyModules.PipeFlow import *

class Poiseuille(PipeFlow):
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
        self.x_min = self.iN['grid_x'].min() # 0.0002 (m)
        self.x_max = self.iN['grid_x'].max() # 0.0041 (m)
        self.z_min = self.cL['grid_z'].min() # 0.0002 (m)
        self.z_max = self.cL['grid_z'].max() # 0.0201 (m)
        self.P_in.append(self.iN['P'].max()) # 0 (mmHg)
        self.P_out.append(self.oUT['P'].min()) # 0.01 (mmHg)

    def DeriveParams(self):
        self.P_min = min(self.P_out)
        self.P_max = max(self.P_in)
        self.L = self.z_max - self.z_min + self.dx # length of pipe (m)
        self.R = 0.5 * (self.x_max - self.x_min + self.dx) # radius of pipe (m)
        self.R0 = 0.5 * (self.x_min + self.x_max) # x-ord of centre
        self.dPdz = (self.P_min - self.P_max) / self.L # pressure gradient (mmHg / m)
        self.G = - self.dPdz * mmHg # used in Poiseuille equation (Pa)

    def AddRadialDistance(self, df):
        df['r'] = np.sqrt((df['grid_x'] - self.R0)**2 + (df['grid_y'] - self.R0)**2)

    def CalExact(self, df, var):
        if (var == 'P'):
            exSol = lambda z: self.P_max + self.dPdz * (z - self.z_min)
            df['exSol_P'] = exSol(df['grid_z'])
        elif (var == 'Uz'):
            exSol = lambda r: self.G / (4*mu) * (self.R**2 - r**2)
            df['exSol_Uz'] = exSol(df['r'])
        df['err_' + var] = df[var] - df['exSol_' + var]

    def CompareExSol_1D(self, df, grid, var1, kwargs1=..., kwargs2=...):
        return super().Visualise_1D(df, grid, var1, 'exSol_' + var1, kwargs1={'label':'appSol'}, kwargs2={'label':'exSol'})

    def CompareExSol_2D(self, df, grid_1, grid_2, var1, var2=None):
        return super().Visualise_2D(df, grid_1, grid_2, var1, var2='exSol_' + var1)
