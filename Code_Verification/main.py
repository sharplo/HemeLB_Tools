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

"""

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
df_cLpZ.name = 'cLpZ'
Visualise_TimeSeries(df_cLpZ, 'P', 'Uz')
# ============================ Pipe ===============================

"""

# ============================ Bifurcation ===============================
## Intersection of plane Y and Z
df_pYpZ = pd.merge(df_pY, df_pZ)
df_pYpZ.name = 'pYpZ'
df_pYpZcen = df_pYpZ[df_pYpZ['r'] == df_pYpZ['r'].min()]
df_pYpZcen.name = 'pYpZcen'
Visualise_TimeSeries(df_pYpZcen, 'P', 'Uz')

## Intersection of planeY and inlet
df_pYin = pd.merge(df_pY, df_in)
df_pYin.name = 'pYin'
df_pYincen = df_pYin[df_pYin['r'] == df_pYin['r'].min()]
df_pYincen.name = 'pYincen'
Visualise_TimeSeries(df_pYincen, 'P', 'Uz')

## Intersection of planeY and planeZ_outlet0
df_pYpZout0 = pd.merge(df_pY, df_pZout0)
df_pYpZout0.name = 'pYpZout0'
df_pYpZout0cen = df_pYpZout0[df_pYpZout0['r'] == df_pYpZout0['r'].min()]
df_pYpZout0cen.name = 'pYpZout0cen'
Visualise_TimeSeries(df_pYpZout0cen, 'P', 'Uz')

## Intersection of planeY and planeZ_outlet1
df_pYpZout1 = pd.merge(df_pY, df_pZout1)
df_pYpZout1.name = 'pYpZout1'
df_pYpZout1cen = df_pYpZout1[df_pYpZout1['r'] == df_pYpZout1['r'].min()]
df_pYpZout1cen.name = 'pYpZout1cen'
Visualise_TimeSeries(df_pYpZout1cen, 'P', 'Uz')

Compare_TimeSeries(df_pYincen, df_pYpZcen, 'P', 'Uz')
Compare_TimeSeries(df_pYincen, df_pYpZout0cen, 'P', 'Uz')
Compare_TimeSeries(df_pYincen, df_pYpZout1cen, 'P', 'Uz')
# ============================ Bifurcation ===============================
