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

# Main code
RenameCol(df_cL)
CalExact(df_cL, 'Uz')
CalExact(df_cL, 'P')
WriteDiscErr(df_cL, 'P')
Visualise_1D(df_cL, 'Uz', 'grid_z')
Visualise_1D(df_cL, 'P', 'grid_z')

RenameCol(df_pZ)
CalExact(df_pZ, 'Uz')
CalExact(df_pZ, 'P')
WriteDiscErr(df_pZ, 'Uz')
Visualise_1D(df_pZ, 'Uz', 'grid_x')
Visualise_1D(df_pZ, 'P', 'grid_x')
Visualise_2D(df_pZ, 'Uz', 'grid_x', 'grid_y')
