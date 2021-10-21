import sys
import pandas as pd

# Local modules
from Visual import *
from DiscError import *

# Constants
mmHg = 133.3223874 # Pa
mu = 0.004 # dynamic viscosity (Pa*s)
PI = 3.14159265358979323846264338327950288

class PipeFlow(Visual, DiscError):
    def __init__(self, dx, dt, dfDict):
        Visual.__init__(self)
        DiscError.__init__(self)

        self.dir = sys.argv[1] # directory where data reside
        self.shotBeg = int(sys.argv[2]) # first file to be read
        self.shotEnd = int(sys.argv[3]) # last file to be read
        
        self.dfDict = dfDict # dictionary between data frame names and data file names
        self.dt = dt # step_length (s)
        self.dx = dx # voxel_size (m)
        self.R = None # radius of pipe (m)
        self.P_in = [] # pressure at inlets (mmHg)
        self.P_out = [] # pressure at outlets (mmHg)

        # General procedures
        self.MakeDataFrames()
        self.ExtractParams()
        self.DeriveParams()

    def MakeDataFrames(self):
        for key in self.dfDict.keys():
            values = self.dfDict[key]
            if type(values) is str:
                # Load data from file
                setattr(self, key, self.LoadData(values))
            elif type(values) is list:
                # Intersect data frames
                setattr(self, key, self.JoinDataFrames(values))
            setattr(getattr(self, key), 'name', key) # df.name = key
            self.RenameCol(getattr(self, key))

    def LoadData(self, file):
        df = pd.DataFrame()
        for shot in range(self.shotBeg, self.shotEnd+1):
            # TODO: make it compatible with all operating system, e.g. using sys.path
            df = df.append(pd.read_csv(self.dir + file + '/' + file + str(shot) + '.txt', delimiter=' '))
        return df

    def JoinDataFrames(self, values):
        df = getattr(self, values[0])
        for i in range(1, len(values)):
            if values[i] == 'cEN':
                df = self.CentrePoint(df)
            else:
                df = pd.merge(df, getattr(self, values[i]))
        return df
    
    def CentrePoint(self, df):
        return df[(df['grid_x'] > df['grid_x'].mean() - 0.5 * self.dx) \
            & (df['grid_x'] < df['grid_x'].mean() + 0.5 * self.dx) \
            & (df['grid_y'] > df['grid_y'].mean() - 0.5 * self.dx) \
            & (df['grid_y'] < df['grid_y'].mean() + 0.5 * self.dx) \
            & (df['grid_z'] > df['grid_z'].mean() - 0.5 * self.dx) \
            & (df['grid_z'] < df['grid_z'].mean() + 0.5 * self.dx)]

    def RenameCol(self, df):
        df.rename(columns={
                        'velocity(0)':'Ux',
                        'velocity(1)':'Uy',
                        'velocity(2)':'Uz',
                        'pressure':'P',}, inplace=True)

    def ExtractParams(self):
        pass # defined in each daughter calss

    def DeriveParams(self):
        pass # defined in each daughter class

        
class Poiseuille(PipeFlow):
    def __init__(self, dx, dt, dfDict=None):
        if dfDict == None:
            dfDict = {'iN':'inlet', 'oUT':'outlet', 'cL':'centreLine', 'pZ':'planeZ'}
        PipeFlow.__init__(self, dx, dt, dfDict)

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

class Bifurcation(PipeFlow):
    def __init__(self, dx, dt, dfDict=None):
        if dfDict == None:
            dfDict = {'iN':'inlet', 'pY':'planeY', 'pZOUT0':'planeZ_out0', \
                'pZOUT1':'planeZ_out1', 'iNpYcEN':['iN', 'pY', 'cEN'], \
                'pZOUT0pYcEN':['pZOUT0', 'pY', 'cEN'], 'pZOUT1pYcEN':['pZOUT1', 'pY', 'cEN']}
        PipeFlow.__init__(self, dx, dt, dfDict)

    def ExtractParams(self):
        self.x_min = self.iN['grid_x'].min() # (m)
        self.x_max = self.iN['grid_x'].max() # (m)

    def DeriveParams(self):
        self.R = 0.5 * (self.x_max - self.x_min + self.dx) # radius of pipe (m)
