from MyModules.PipeFlow import *

class Bifurcation(PipeFlow):
    def __init__(self, inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict=None):
        if dfDict is None:
            dfDict = {'iN':'inlet', 'pY':'planeY', 'pZOUT0':'planeZ_out0', \
                'pZOUT1':'planeZ_out1', 'iNpYcEN':['iN', 'pY', 'cEN'], \
                'pZOUT0pYcEN':['pZOUT0', 'pY', 'cEN'], 'pZOUT1pYcEN':['pZOUT1', 'pY', 'cEN']}
        PipeFlow.__init__(self, inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict)

    def ExtractParams(self):
        self.x_min = self.iN['grid_x'].min() # (m)
        self.x_max = self.iN['grid_x'].max() # (m)

    def DeriveParams(self):
        self.radius = 0.5 * (self.x_max - self.x_min + self.dx)
