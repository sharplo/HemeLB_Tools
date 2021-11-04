# Local modules
from PipeFlow import *

class SixBranch(PipeFlow):
    def __init__(self, dx, dt, dfDict=None):
        if dfDict == None:
            dfDict = {'iN':'inlet', 'oUT':'outlet'}
        PipeFlow.__init__(self, dx, dt, dfDict)

    def CalFlowRate(self, df, normal, clusters):
        result = pd.DataFrame()
        for i in clusters:
            # Calculate the local flow rate of ith cluster
            new = df[df['cluster'] == i].copy()
            new['FlowRate'] = new['Ux'] * normal[i,0] + new['Uy'] * normal[i,1] + new['Uz'] * normal[i,2]
            # Aggregate and sum the flow rates
            new = new.groupby(['step', 'cluster'], as_index=False)['FlowRate'].sum()
            # Concatenate results from different clusters
            result = pd.concat([result, new])
        result.name = df.name
        return result