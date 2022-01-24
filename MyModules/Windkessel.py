import numpy as np
from MyModules.PipeFlow import *

class Windkessel(PipeFlow):
    def __init__(self, dfDict=None):
        if dfDict == None:
            dfDict = {'iN':'inlet', 'oUT':'outlet'}
        PipeFlow.__init__(self, dfDict)

    def CalFlowRate(self, df, normal, clusters):
        result = pd.DataFrame()
        for i in clusters:
            # Calculate the local flow rate of ith cluster
            new = df[df['cluster'] == i].copy()
            new['FlowRate'] = new['Ux'] * normal[i,0] + new['Uy'] * normal[i,1] + new['Uz'] * normal[i,2]
            # Aggregate the flow rates and find the average (area is taken into account)
            new = new.groupby(['step', 'cluster'], as_index=False)['FlowRate'].mean()
            # Concatenate results from different clusters
            result = pd.concat([result, new])
        result.name = df.name
        return result

    def CalFlowRateRatios(self, df, ref):
        desired = self.resistance[ref] / self.resistance
        mean = df.groupby(['cluster'], as_index=False)['FlowRate'].mean()
        measured = mean['FlowRate'] / mean['FlowRate'].loc[ref]
        relErr = (measured - desired) / desired
        result = pd.DataFrame({'Desired':desired, 'Measured':measured, 'RelErr':relErr})
        result = result.drop(index=ref)
        result.name = df.name + '_FlowRateRatios'
        return result

    def Visualise_Ratios(self, df, var, clusters, ref):
        desired = self.resistance[ref] / self.resistance[clusters]
        desired = np.delete(desired, ref)
        return super().Visualise_Ratios(df, var, clusters, ref, desired)