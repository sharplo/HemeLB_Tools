import numpy as np

class WallStress(object):
    def CalTemporalAverage(self, df, steps):
        view = df[df['step'].isin(steps)]
        if {'grid_x', 'grid_y', 'grid_z'}.issubset(view.columns):
            view = view.groupby(['grid_x', 'grid_y', 'grid_z'], as_index=False).mean()
            if hasattr(df, 'name'):
                view.name = 'TA_' + df.name
        else: # df is a spatial average
            view = view.mean()
            if hasattr(df, 'name'):
                view.name = 'T' + df.name # so that the name is TSA_XXX
        return view

    def CalSpatialAverage(self, df):
        result = df.groupby(['step'], as_index=False).mean()
        if hasattr(df, 'name'):
            result.name = 'SA_' + df.name
        return result

    def CalTemporalSpatialAverage(self, df, steps):
        return self.CalTemporalAverage(self.CalSpatialAverage(df), steps)

    def TimeAveragedWallShearStress(self, df, steps):
        if 'WSS' not in df.columns:
            df['WSS'] = np.linalg.norm(df[['WSS_x', 'WSS_y', 'WSS_z']], axis=1)
        result = self.CalTemporalAverage(df, steps)
        result.rename(columns={'WSS':'TAWSS'}, inplace=True)
        result = result[['grid_x', 'grid_y', 'grid_z', 'TAWSS']]
        result.name = df.name
        return result

    def OscillationShearIndex(self, df, steps):
        temp = self.CalTemporalAverage(df, steps)
        temp = np.linalg.norm(temp[['WSS_x', 'WSS_y', 'WSS_z']], axis=1)
        result = self.TimeAveragedWallShearStress(df, steps)
        result['OSI'] = 0.5 * (1 - temp / result['TAWSS'])
        return result

    def RelativeResidenceTime(self, df, steps):
        result = self.OscillationShearIndex(df, steps)
        result['RRT'] = 1 / ( (1 - 2 * result['OSI']) * result['TAWSS'] )
        return result

    def EndothelialCellActivationPotential(self, df, steps):
        result = self.OscillationShearIndex(df, steps)
        result['ECAP'] = result['OSI'] / result['TAWSS']
        return result

    def MaximumNormalStress(self, df, steps):
        if 'WNS' not in df.columns:
            df['WNS'] = np.linalg.norm(df[['WNS_x', 'WNS_y', 'WNS_z']], axis=1)
        result = df[df['step'].isin(steps)]
        result = result.groupby(['grid_x', 'grid_y', 'grid_z'], as_index=False)['WNS'].max()
        result.rename(columns={'WNS':'MNS'}, inplace=True)
        result.name = df.name
        return result

    def AneurysmsRiskFactors(self, df, steps):
        ECAP = self.EndothelialCellActivationPotential(df, steps)
        MNS = self.MaximumNormalStress(df, steps)
        result = ECAP.merge(MNS)
        result.name = df.name
        return result
