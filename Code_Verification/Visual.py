import numpy as np
import matplotlib
matplotlib.use('Agg') # disable Xwindows backend
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches

def Visualise_1D(df, var, grid):
    df_last = df[df['step'] == df['step'].max()]
    plt.plot(df_last[grid], df_last[var], '.', markersize=2)
    plt.xlabel(grid)
    plt.ylabel(var)
    plt.savefig('figures/' + df.name + '_' + var + '-' + grid + '.png', bbox_inches='tight')
    plt.close()

def Compare_1D(df, var, grid):
    df_last = df[df['step'] == df['step'].max()]
    plt.plot(df_last[grid], df_last[var], '.', markersize=2, label='appSol')
    plt.plot(df_last[grid], df_last['exSol_' + var], '.', markersize=2, label='exSol')
    plt.xlabel(grid)
    plt.ylabel(var)
    plt.legend()
    plt.savefig('figures/' + df.name + '_compare_' + var + '-' + grid + '.png', bbox_inches='tight')
    plt.close()

def Visualise_2D(df, var, grid_1, grid_2):
    df_last = df[df['step'] == df['step'].max()]

    # Make mesh for contour plot
    X_unique = np.sort(df_last[grid_1].unique())
    Y_unique = np.sort(df_last[grid_2].unique())
    X, Y = np.meshgrid(X_unique, Y_unique)

    # Make plots
    Z = df_last.pivot_table(columns=grid_1, index=grid_2, values=var, fill_value=0)
    plt.contourf(X, Y, Z)
    plt.colorbar(label=var)
    plt.ylabel(grid_2)

    plt.subplots_adjust(hspace=0.4)
    plt.savefig('figures/' + df.name + '_' + var + '-' + grid_1 + '&' + grid_2 + '.png', bbox_inches='tight')
    plt.close()

def Compare_2D(df, var, grid_1, grid_2):
    df_last = df[df['step'] == df['step'].max()]

    # Make mesh for contour plot
    X_unique = np.sort(df_last[grid_1].unique())
    Y_unique = np.sort(df_last[grid_2].unique())
    X, Y = np.meshgrid(X_unique, Y_unique)

    # Make plots
    plt.subplot(2, 1, 1)
    Z = df_last.pivot_table(columns=grid_1, index=grid_2, values=var, fill_value=0)
    plt.contourf(X, Y, Z)
    plt.colorbar(label=var)
    plt.ylabel(grid_2)
    plt.title('appSol')

    plt.subplot(2, 1, 2)
    Z = df_last.pivot_table(columns=grid_1, index=grid_2, values='exSol_'+var, fill_value=0)
    plt.contourf(X, Y, Z)
    plt.colorbar(label=var)
    plt.xlabel(grid_1)
    plt.ylabel(grid_2)
    plt.title('exSol')

    plt.subplots_adjust(hspace=0.4)
    plt.savefig('figures/' + df.name + '_compare_' + var + '-' + grid_1 + '&' + grid_2 + '.png', bbox_inches='tight')
    plt.close()

def Visualise_TimeSeries(df, var1, var2=None):
    fig, ax1 = plt.subplots()
    ax1.plot(df['step'], df[var1], '.-', color='tab:blue')
    ax1.set_xlabel('Time step')
    ax1.set_ylabel(var1, color='tab:blue')
    fileName = 'figures/' + df.name + '_timeSeries_' + var1 + '.png'
    if var2 != None:
        ax2 = ax1.twinx()
        ax2.plot(df['step'], df[var2], '.-', color='tab:orange')
        ax2.set_ylabel(var2, color='tab:orange')
        ax2.yaxis.set_label_position('right')
        ax2.yaxis.tick_right()
        fileName = 'figures/' + df.name + '_timeSeries_' + var1 + '&' + var2 + '.png'
    fig.savefig(fileName, bbox_inches='tight')
    plt.close()

def Compare_TimeSeries(df1, df2, var1, var2=None):
    fig, ax1 = plt.subplots()
    h1, = ax1.plot(df1['step'], df1[var1], '.-', color='tab:blue')
    ax1.plot(df2['step'], df2[var1], '^--', markerfacecolor='none', color='tab:blue')
    ax1.set_xlabel('Time step')
    ax1.set_ylabel(var1, color='tab:blue')
    fileName = 'figures/' + df1.name + '_vs_' + df2.name + '-' + var1 + '-timeSeries.png'

    if var2 != None:
        # Plot var2 on the right axis
        ax2 = ax1.twinx()
        h2, = ax2.plot(df1['step'], df1[var2], '.-', color='tab:orange')
        ax2.plot(df2['step'], df2[var2], '^--', markerfacecolor='none', color='tab:orange')
        ax2.set_ylabel(var2, color='tab:orange')
        ax2.yaxis.set_label_position('right')
        ax2.yaxis.tick_right()

        plt.legend([h1, h2], [df1.name, df2.name], \
            bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=2)
        fileName = 'figures/' + df1.name + '_vs_' + df2.name + '-' + var1 + '&' + var2 + '-timeSeries.png'

    fig.savefig(fileName, bbox_inches='tight')
    plt.close()
