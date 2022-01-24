#!/usr/bin/python3.6
import os
import matplotlib
matplotlib.use('Agg') # disable Xwindows backend
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

if not os.path.exists('./figures'):
    os.mkdir('./figures')

Dir = '/hppfs/work/pn72qu/di46kes/FiveExit_1e-3_fine/FiveExit_'
Exp = pd.read_csv('FiveExit_1e-3_fine/experiments.csv')
Qratios = '/figures/flowRateRatios.csv'

# Colour map
cmap_tend = matplotlib.cm.get_cmap('magma')

# Add a coloumn about stability in the data frame
def SetStability(exp, caseNum):
    exp['stable'] = None
    for i in range(len(caseNum)):
        data = Dir + str(caseNum[i]) + Qratios
        if not os.path.exists(data):
            exp['stable'].at[caseNum[i]-1] = False
        else:
            exp['stable'].at[caseNum[i]-1] = True

# Plot a map showing whether the simulations are stable
def StabilityMap(exp, caseNum, outFile):
    row = [i-1 for i in caseNum]
    view = exp.iloc[row,:]
    stable = view[view['stable'] == True]
    unstable = view[view['stable'] == False]

    fig, ax = plt.subplots()
    ax.plot(np.log2(stable['gamma_R']), np.log2(stable['gamma_C']), \
        '.', color='tab:green', label='stable', markersize=10)
    ax.plot(np.log2(unstable['gamma_R']), np.log2(unstable['gamma_C']), \
        'x', color='tab:red', label='unstable', markersize=10)

    ax.set_xlabel(r'$\log_2 \ \gamma_R$')
    ax.set_ylabel(r'$\log_2 \ \gamma_C$')
    ax.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=5)
    fig.savefig(outFile, bbox_inches='tight')
    plt.close()

# Compare desired and measured values in scatter plot
def Desired_Measured(exp, caseNum, param, outFile):
    if param == 'gamma_R':
        tex = r'$\gamma_R$'
    elif param == 'gamma_C':
        tex = r'$\gamma_C$'
    tendency = np.linspace(0.85, 0, len(caseNum))

    fig, ax = plt.subplots()
    for i in range(len(caseNum)):
        data = Dir + str(caseNum[i]) + Qratios
        if not os.path.exists(data):
            continue
        df = pd.read_csv(data)
        ax.scatter(df['Desired'], df['Measured'], color=cmap_tend(tendency[i]), \
            label= tex + ' = ' + str(exp[param].at[caseNum[i]-1]))
    ax.plot(ax.get_xlim(), ax.get_xlim(), '--', color='tab:gray', label='y = x')

    ax.set_xlabel('Desired value')
    ax.set_ylabel('Measured value')
    ax.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=4)
    fig.savefig(outFile, bbox_inches='tight')
    plt.close()

# Plot relative error of desired and measured values against model parameters
def PercentError(exp, caseNum, param, outFile):
    if param == 'gamma_R':
        tex = r'$\gamma_R$'
    elif param == 'gamma_C':
        tex = r'$\gamma_C$'
    tendency = np.linspace(0.85, 0, len(caseNum))

    fig, ax = plt.subplots()
    for i in range(len(caseNum)):
        data = Dir + str(caseNum[i]) + Qratios
        if not os.path.exists(data):
            continue
        df = pd.read_csv(data)
        x = [ exp[param].at[caseNum[i]-1] ] * len(df['RelErr'])
        y = df['RelErr']*100
        ax.scatter(np.log2(x), y, color=cmap_tend(tendency[i]))

    ax.set_xlabel(r'$\log_2 \ $' + tex)
    ax.set_ylabel('% error')
    fig.savefig(outFile, bbox_inches='tight')
    plt.close()

SetStability(Exp, [i for i in range(1,92)])
StabilityMap(Exp, [i for i in range(1,92)], 'figures/stability.png')
Desired_Measured(Exp, [i for i in range(1,50,7)], 'gamma_C', 'figures/dm-R_1.png')
Desired_Measured(Exp, [i for i in range(2,50,7)], 'gamma_C', 'figures/dm-R_2.png')
Desired_Measured(Exp, [i for i in range(3,50,7)], 'gamma_C', 'figures/dm-R_4.png')
Desired_Measured(Exp, [i for i in range(4,50,7)], 'gamma_C', 'figures/dm-R_8.png')
Desired_Measured(Exp, [i for i in range(5,50,7)], 'gamma_C', 'figures/dm-R_16.png')
Desired_Measured(Exp, [i for i in range(6,50,7)], 'gamma_C', 'figures/dm-R_32.png')
Desired_Measured(Exp, [i for i in range(7,50,7)], 'gamma_C', 'figures/dm-R_64.png')
Desired_Measured(Exp, [i for i in range(1,8)], 'gamma_R', 'figures/dm-C_0.125.png')
Desired_Measured(Exp, [i for i in range(8,15)], 'gamma_R', 'figures/dm-C_0.25.png')
Desired_Measured(Exp, [i for i in range(15,22)], 'gamma_R', 'figures/dm-C_0.5.png')
Desired_Measured(Exp, [i for i in range(22,29)], 'gamma_R', 'figures/dm-C_1.png')
Desired_Measured(Exp, [i for i in range(29,36)], 'gamma_R', 'figures/dm-C_2.png')
Desired_Measured(Exp, [i for i in range(36,43)], 'gamma_R', 'figures/dm-C_4.png')
Desired_Measured(Exp, [i for i in range(43,50)], 'gamma_R', 'figures/dm-C_8.png')
PercentError(Exp, [i for i in range(1,50,7)], 'gamma_C', 'figures/err-R_1.png')
PercentError(Exp, [i for i in range(2,50,7)], 'gamma_C', 'figures/err-R_2.png')
PercentError(Exp, [i for i in range(3,50,7)], 'gamma_C', 'figures/err-R_4.png')
PercentError(Exp, [i for i in range(4,50,7)], 'gamma_C', 'figures/err-R_8.png')
PercentError(Exp, [i for i in range(5,50,7)], 'gamma_C', 'figures/err-R_16.png')
PercentError(Exp, [i for i in range(6,50,7)], 'gamma_C', 'figures/err-R_32.png')
PercentError(Exp, [i for i in range(7,50,7)], 'gamma_C', 'figures/err-R_64.png')
PercentError(Exp, [i for i in range(1,8)], 'gamma_R', 'figures/err-C_0.125.png')
PercentError(Exp, [i for i in range(8,15)], 'gamma_R', 'figures/err-C_0.25.png')
PercentError(Exp, [i for i in range(15,22)], 'gamma_R', 'figures/err-C_0.5.png')
PercentError(Exp, [i for i in range(22,29)], 'gamma_R', 'figures/err-C_1.png')
PercentError(Exp, [i for i in range(29,36)], 'gamma_R', 'figures/err-C_2.png')
PercentError(Exp, [i for i in range(36,43)], 'gamma_R', 'figures/err-C_4.png')
PercentError(Exp, [i for i in range(43,50)], 'gamma_R', 'figures/err-C_8.png')
