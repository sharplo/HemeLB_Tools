import numpy as np
import matplotlib
matplotlib.use('Agg') # disable Xwindows backend
from matplotlib import pyplot as plt

def Visualise_1D(df, var, grid):
    plt.plot(df[grid], df[var], '.', markersize=2)
    plt.xlabel(grid)
    plt.ylabel(var)
    plt.savefig('figures/' + var + '-' + grid + '.png', bbox_inches='tight')
    plt.close()

def Compare_1D(df, var, grid):
    plt.plot(df[grid], df[var], '.', markersize=2, label='appSol')
    plt.plot(df[grid], df['exSol_' + var], '.', markersize=2, label='exSol')
    plt.xlabel(grid)
    plt.ylabel(var)
    plt.legend()
    plt.savefig('figures/compare_' + var + '-' + grid + '.png', bbox_inches='tight')
    plt.close()

def Visualise_2D(df, var, grid_1, grid_2):
    # Make mesh for contour plot
    X_unique = np.sort(df[grid_1].unique())
    Y_unique = np.sort(df[grid_2].unique())
    X, Y = np.meshgrid(X_unique, Y_unique)

    # Make plots
    Z = df.pivot_table(columns=grid_1, index=grid_2, values=var, fill_value=0)
    plt.contourf(X, Y, Z)
    plt.colorbar(label=var)
    plt.ylabel(grid_2)

    plt.subplots_adjust(hspace=0.4)
    plt.savefig('figures/' + var + '-' + grid_1 + '&' + grid_2 + '.png', bbox_inches='tight')
    plt.close()

def Compare_2D(df, var, grid_1, grid_2):
    # Make mesh for contour plot
    X_unique = np.sort(df[grid_1].unique())
    Y_unique = np.sort(df[grid_2].unique())
    X, Y = np.meshgrid(X_unique, Y_unique)

    # Make plots
    plt.subplot(2, 1, 1)
    Z = df.pivot_table(columns=grid_1, index=grid_2, values=var, fill_value=0)
    plt.contourf(X, Y, Z)
    plt.colorbar(label=var)
    plt.ylabel(grid_2)
    plt.title('appSol')

    plt.subplot(2, 1, 2)
    Z = df.pivot_table(columns=grid_1, index=grid_2, values='exSol_'+var, fill_value=0)
    plt.contourf(X, Y, Z)
    plt.colorbar(label=var)
    plt.xlabel(grid_1)
    plt.ylabel(grid_2)
    plt.title('exSol')

    plt.subplots_adjust(hspace=0.4)
    plt.savefig('figures/compare_' + var + '-' + grid_1 + '&' + grid_2 + '.png', bbox_inches='tight')
    plt.close()
