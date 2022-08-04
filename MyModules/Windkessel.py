import numpy as np
from MyModules.PipeFlow import *

class Windkessel(PipeFlow):
    def __init__(self, inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict=None):
        if dfDict == None:
            dfDict = {'iN':'inlet', 'oUT':'outlet'}
        PipeFlow.__init__(self, inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict)

        # Reference outlet
        self.ref = np.argsort(self.resistance)[len(self.resistance) // 2]
        #self.ref = np.argmin(self.resistance)
        print('Reference outlet:', self.ref)

    def CalFlowRate(self, df, clusters, normal=None):
        result = pd.DataFrame()
        for i in clusters:
            # Calculate the local flow rate of ith cluster
            new = df[df['cluster'] == i].copy()
            if normal is None:
                new['Q'] = self.NormalVelocity(new)
            else:
                new['Q'] = self.NormalVelocity(new, normal[i,:])
            # Aggregate the flow rates and find the average (area is the same for each lattice)
            new = new.groupby(['step', 'cluster'], as_index=False)['Q'].mean()
            # Concatenate results from different clusters
            result = pd.concat([result, new])
        result.name = df.name
        return result

    def CalFlowRateRatios(self, df):
        desired = self.resistance[self.ref] / self.resistance
        mean = df.groupby(['cluster'], as_index=False)['Q'].mean()
        measured = mean['Q'] / mean['Q'].loc[self.ref]
        relErr = (measured - desired) / desired
        result = pd.DataFrame({'Desired':desired, 'Measured':measured, 'RelErr':relErr})
        result = result.drop(index=self.ref)
        result.name = df.name + '_Qratios'
        return result

    def CheckMassConservation(self, Q_iN, Q_oUT):
        result = Q_iN.groupby(['step'], as_index=False)['Q'].sum()
        result = result.rename(columns={'Q':'Q_iN'})
        temp = Q_oUT.groupby(['step'], as_index=False)['Q'].sum()
        result['Q_oUT'] = temp['Q']
        result.name = Q_iN.name + Q_oUT.name
        super().Visualise_TimeSeries(result, 'Q_iN', 'Q_oUT')

    def CheckNormalAssumption(self, df_mag, df_norm, clusters):
        arr = np.array([])
        for i in clusters:
            view_mag = df_mag[df_mag['cluster'] == i].copy()
            view_norm = df_norm[df_norm['cluster'] == i].copy()
            diff = (view_mag['Q'] - view_norm['Q']) / view_norm['Q']
            _, L2, _ = self.CalErrNorms(diff)
            arr = np.append(arr, L2)
        print('L2 norm of relative differences:', arr)

    def CheckPressureAssumption(self, df):
        std = df.groupby(['step', 'cluster'], as_index=False)['P'].std()
        mean = std.groupby(['cluster'], as_index=False)['P'].mean()
        print('Time Averaged Standard Deviations:')
        print(mean['P'])

    def EmpiricalMurrayPower(self, Q_oUT):
        r_ratios = self.radius_oUT / self.radius_oUT[self.ref]
        r_ratios = np.delete(r_ratios, self.ref)
        power = np.log(Q_oUT) / np.log(r_ratios)
        print('Empirical Murray\'s law power:', power)

    def Visualise_Ratios(self, df, var, clusters):
        desired = self.resistance[self.ref] / self.resistance[clusters]
        desired = np.delete(desired, self.ref)
        return super().Visualise_Ratios(df, var, clusters, self.ref, desired)