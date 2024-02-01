import numpy as np
from MyModules.PipeFlow import *

class Windkessel(PipeFlow):
    def __init__(self, inFile, dataDir, outDir, stepBeg, stepEnd, dfDict=None, ref=None):
        if dfDict is None:
            dfDict = {'iN':'inlet', 'oUT':'outlet'}
        PipeFlow.__init__(self, inFile, dataDir, outDir, stepBeg, stepEnd, dfDict)

        # Set the reference outlet
        if ref is None:
            self.ref = np.argsort(self.resistance)[self.numOutlets // 2]
            #self.ref = np.argmin(self.resistance)
        else:
            self.ref = ref
        print('Reference outlet:', self.ref)

        self.Clustering(self.iN, self.position_iN)
        self.Clustering(self.oUT, self.position_oUT)
        self.AddCentreDataFrames()
        for key in self.dfDict.keys():
            if key[:2] == 'iN':
                normal = getattr(self, 'normal_iN')
                area = getattr(self, 'area_iN')
            elif key[:3] == 'oUT':
                normal = getattr(self, 'normal_oUT')
                area = getattr(self, 'area_oUT')
            else:
                sys.exit('Error: No normal vector is found for this data frame!')
            setattr(self, key, self.AddColumns(getattr(self, key), normal, area))

    def DeriveParams(self):
        self.numInlets = len(self.position_iN)
        self.numOutlets = len(self.position_oUT)

    def AddCentreDataFrames(self):
        for i in range(self.numInlets):
            super().AddDataFrame('iN' + str(i) + 'cEN', ['iN' + str(i), 'cEN'])
        for i in range(self.numOutlets):
            super().AddDataFrame('oUT' + str(i) + 'cEN', ['oUT' + str(i), 'cEN'])

    def AddColumns(self, df, normal, area):
        result = pd.DataFrame()
        for i in range(int(df['cluster'].max()) + 1):
            new = df[df['cluster'] == i].copy()
            new['Un'] = self.NormalVelocity(new, normal[i,:])
            new['Q'] = self.LocalFlowRate(new, 'volume', area[i])
            result = pd.concat([result, new])
        result.name = df.name
        return result

    def LocalFlowRate(self, df, type, area):
        if type == 'volume':
            density = 1
        elif type == 'mass':
            density = df['P'] * mmHg / (cs2 * self.dx**2 / self.dt**2)
        else:
            sys.exit('Error: The prescribed flow rate type is not available!')
        return density * df['Un'] * area

    def CalAverageFlowRates(self, df, clusters, avgSteps=1):
        result = pd.DataFrame()
        for i in clusters:
            new = df[df['cluster'] == i].copy()
            # Calculate the spatial average
            new = new.groupby(['step', 'cluster'], as_index=False)['Q'].mean()
            # Calculate the temporal average over the given period
            new = new.groupby([new.index // avgSteps, 'cluster'], as_index=False).mean()
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
        result.name = df.name + '_Qratios'
        return result

    def CheckMassConservation(self):
        Q_iN = self.iN.groupby(['step'], as_index=False)['Q'].sum()
        Q_iN['cum_Q'] = np.cumsum(Q_iN['Q'])
        Q_iN.name = self.iN.name
        Q_oUT = self.oUT.groupby(['step'], as_index=False)['Q'].sum()
        Q_oUT['cum_Q'] = np.cumsum(Q_oUT['Q'])
        Q_oUT.name = self.oUT.name
        super().Compare_TimeSeries(Q_iN, Q_oUT, 'cum_Q')
        super().Compare_TimeSeries(Q_iN, Q_oUT, 'Q')

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
        mean = df.groupby(['step', 'cluster'], as_index=False)['P'].mean()
        std_TA = std.groupby(['cluster'], as_index=False)['P'].mean()
        mean_TA = mean.groupby(['cluster'], as_index=False)['P'].mean()
        print('Time-averaged coefficient of variation:')
        print(std_TA['P'] / mean_TA['P'])

    def EmpiricalMurrayPower(self, Q_oUT):
        r_ratios = self.radius_oUT / self.radius_oUT[self.ref]
        with np.errstate(invalid='ignore'):
            power = np.log(Q_oUT) / np.log(r_ratios)
        print('Empirical Murray\'s law power:', power)

    def Visualise_Ratios(self, df, var, clusters):
        desired = self.resistance[self.ref] / self.resistance[clusters]
        return super().Visualise_Ratios(df, var, clusters, self.ref, desired)