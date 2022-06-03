import numpy as np
from MyModules.PipeFlow import *

class ElasticPipe(PipeFlow):
    def __init__(self, inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict):
        PipeFlow.__init__(self, inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict)

    def CalPulseWaveVelocity(self, df1, steps1, df2, steps2, var, distance):
        view1 = df1[df1['step'].isin(steps1)]
        view2 = df2[df2['step'].isin(steps2)]
        foot1 = self.FootToFoot(view1, var)
        foot2 = self.FootToFoot(view2, var)
        lapse = (foot2 - foot1) * self.dt
        return distance / lapse

    def FootToFoot(self, df, var):
        # Focus on the period before var attains its maximum
        view = df[df[var].index <= df[var].idxmax()]
        # Find the location and value of the minimum of var
        idxSum = np.argmin(self.SevenPointSum(view[var]))
        minSum = view[var].iat[idxSum]
        # Calculate gradients of var
        stepSize = view['step'].iat[1] - view['step'].iat[0]
        grad = self.SymmetricDerivative(view[var], stepSize)
        # Find the location and value of the maximum gradient of var
        idxGrad = np.argmax(grad)
        maxGrad = grad[idxGrad]
        # Calculate the y-intercept of the tangent at the maximum gradient
        intercept = view[var].iat[idxGrad] - maxGrad * view['step'].iat[idxGrad]
        # Calculate the intersection of the local minimum and the tangent
        foot = (minSum - intercept) / maxGrad
        return foot
    
    def SevenPointSum(self, arr):
        sum = 0
        for i in range(-3, 4):
            sum = sum + np.roll(arr, i)
        return sum

    def SymmetricDerivative(self, arr, h):
        return (np.roll(arr, -1) - np.roll(arr, 1)) / (2 * h)