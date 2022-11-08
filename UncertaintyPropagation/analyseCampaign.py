#!/usr/bin/python3.8
import os
import pandas as pd
import easyvvuq as uq
from matplotlib import pyplot as plt

# Get the current working directory
cwd = os.getcwd()

# Get the grid of the simulation
for root, dirs, files in os.walk(os.path.join(cwd, 'run')):
    for name in files:
        if name == 'riskFactors.csv':
            pathToGrid = os.path.join(root, name)
            break
grid = pd.read_csv(pathToGrid, usecols=['grid_x', 'grid_y', 'grid_z'])

# Load campaign
campaign = uq.Campaign(name='UncertaintyPropagation', \
    db_location='sqlite:///' + os.path.join(cwd, 'run/campaign.db'))

# Analyse the results of simulations
results = campaign.analyse(qoi_cols=['ECAP', 'MNS'])
MNS_stat = results.describe('MNS')

# Visualise statistics
def Visualise_3D(grid, df, var, fileName, kwargs={}):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    img = ax.scatter3D(grid['grid_x'], grid['grid_y'], grid['grid_z'], \
        c=df.loc[var], **kwargs)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    cbaxes = fig.add_axes([0.2, 0.9, 0.8, 0.03])
    fig.colorbar(img, label=var, orientation='horizontal', cax=cbaxes)
    fig.savefig(fileName, bbox_inches='tight')
    plt.close()

Visualise_3D(grid, MNS_stat, 'mean', 'MNS_mean.pdf')
Visualise_3D(grid, MNS_stat, 'var', 'MNS_var.pdf')
