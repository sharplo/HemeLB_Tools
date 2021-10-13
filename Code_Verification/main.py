#!/usr/bin/python3.6
from Param import * # local file
from DiscError import * # local file
from Visual import * # local file

def RenameCol(df):
    df.rename(columns={
                        'velocity(0)':'Ux',
                        'velocity(1)':'Uy',
                        'velocity(2)':'Uz',
                        'pressure':'P',}, inplace=True)

def AddRadialDistance(df):
    df['r'] = np.sqrt((df['grid_x'] - R0)**2 + (df['grid_y'] - R0)**2)

# Prepare data frames
for df in dfList:
    RenameCol(df)
    AddRadialDistance(df)

# ============================ Pipe ===============================
## Centre line
# Process results
CalExact(df_cL, 'Uz')
CalExact(df_cL, 'P')
WriteDiscErr(df_cL, 'P')

# Visualise results
Compare_1D(df_cL, 'Uz', 'grid_z')
Compare_1D(df_cL, 'P', 'grid_z')
Visualise_1D(df_cL, 'err_P', 'grid_z')

## Plane Z
# Process results
CalExact(df_pZ, 'Uz')
CalExact(df_pZ, 'P')
WriteDiscErr(df_pZ, 'Uz')

# Visualise results
Compare_1D(df_pZ, 'P', 'grid_x')
Compare_1D(df_pZ, 'Uz', 'grid_x')
Compare_2D(df_pZ, 'Uz', 'grid_x', 'grid_y')
Visualise_1D(df_pZ, 'err_Uz', 'grid_x')
Visualise_2D(df_pZ, 'err_Uz', 'grid_x', 'grid_y')

## Intersection of centre line and plane Z
df_cLpZ = pd.merge(df_cL, df_pZ)
Visualise_TimeSeries(df_cLpZ, 'P', 'Uz')
Visualise_TimeSeries(df_cLpZ, 'Ux', 'Uy')
# ============================ Pipe ===============================

"""

# ============================ Bifurcation ===============================
## Intersection of plane Y and Z
df_pYpZ = pd.merge(df_pY, df_pZ)
Visualise_1D(df_pYpZ, 'P', 'grid_x')
Visualise_1D(df_pYpZ, 'Ux', 'grid_x')
Visualise_1D(df_pYpZ, 'Uz', 'grid_x')
# ============================ Bifurcation ===============================

"""