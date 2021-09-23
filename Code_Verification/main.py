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

## Centre line
# Process results
RenameCol(df_cL)
CalExact(df_cL, 'Uz')
CalExact(df_cL, 'P')
WriteDiscErr(df_cL, 'P')

# Visualise results
Compare_1D(df_cL, 'Uz', 'grid_z')
Compare_1D(df_cL, 'P', 'grid_z')
Visualise_1D(df_cL, 'err_P', 'grid_z')

## Plane Z
# Process results
RenameCol(df_pZ)
CalExact(df_pZ, 'Uz')
CalExact(df_pZ, 'P')
WriteDiscErr(df_pZ, 'Uz')

# Visualise results
Compare_1D(df_pZ, 'Uz', 'grid_x')
Visualise_1D(df_pZ, 'err_Uz', 'grid_x')
Compare_1D(df_pZ, 'P', 'grid_x')
Compare_2D(df_pZ, 'Uz', 'grid_x', 'grid_y')
Visualise_2D(df_pZ, 'err_Uz', 'grid_x', 'grid_y')
