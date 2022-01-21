#!/usr/bin/python3.6
import os
import matplotlib
matplotlib.use('Agg') # disable Xwindows backend
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

if not os.path.exists('./figures'):
    os.mkdir('./figures')

Exp = pd.read_csv('experiments.csv')
Dir = '/hppfs/work/pn72qu/di46kes/'
CaseName = 'FiveExit_1e-3_fine/FiveExit_'
FileName = '/figures/flowRateRatios.csv'

def SetStability(exp, caseNum):
    exp['stable'] = None
    for i in range(len(caseNum)):
        file = Dir + CaseName + str(caseNum[i]) + FileName
        if not os.path.exists(file):
            exp['stable'].at[caseNum[i]-1] = False
        else:
            exp['stable'].at[caseNum[i]-1] = True

def StabilityMap(exp, caseNum, fileName):
    fig, ax = plt.subplots()
    row = [i-1 for i in caseNum]
    view = exp.iloc[row,:]
    stable = view[view['stable'] == True]
    unstable = view[view['stable'] == False]
    ax.plot(np.log2(stable['gamma_R']), np.log2(stable['gamma_C']), \
        '.', color='tab:green', label='stable')
    ax.plot(np.log2(unstable['gamma_R']), np.log2(unstable['gamma_C']), \
        'x', color='tab:red', label='unstable')
    ax.set_xlabel('log2(gamma_R)')
    ax.set_ylabel('log2(gamma_C)')
    ax.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=5)
    fig.savefig(fileName, bbox_inches='tight')
    plt.close()

# Compare desired and measured values in scatter plot
def Scatter(caseNum, fileName):
    fig, ax = plt.subplots()
    for i in range(len(caseNum)):
        file = Dir + CaseName + str(caseNum[i]) + FileName
        if not os.path.exists(file):
            continue
        df = pd.read_csv(file)
        ax.scatter(df['desired'], df['measured'], label='case' + str(caseNum[i]))
    ax.plot(ax.get_xlim(), ax.get_ylim(), '--', color='tab:gray', label='y=x')
    ax.set_xlabel('desired')
    ax.set_ylabel('measured')
    ax.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=5)
    fig.savefig(fileName, bbox_inches='tight')
    plt.close()

# Plot relative error of desired and measured values against model parameters
def ErrorAlongParam(exp, caseNum, param, fileName):
    fig, ax = plt.subplots()
    for i in range(len(caseNum)):
        file = Dir + CaseName + str(caseNum[i]) + FileName
        if not os.path.exists(file):
            continue
        df = pd.read_csv(file)
        x = [ exp[param].at[caseNum[i]-1] ] * len(df['relErr'])
        y = df['relErr']*100
        ax.scatter(np.log2(x), y, label='case' + str(caseNum[i]))
    ax.set_xlabel('log2(' + param + ')')
    ax.set_ylabel('% error')
    ax.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=5)
    fig.savefig(fileName, bbox_inches='tight')
    plt.close()

SetStability(Exp, [i for i in range(1,50)])
StabilityMap(Exp, [i for i in range(1,50)], 'figures/stability.png')
Scatter([i for i in range(1,50,7)], 'figures/scatter_R-1.png')
Scatter([i for i in range(2,50,7)], 'figures/scatter_R-2.png')
Scatter([i for i in range(3,50,7)], 'figures/scatter_R-4.png')
Scatter([i for i in range(4,50,7)], 'figures/scatter_R-8.png')
Scatter([i for i in range(5,50,7)], 'figures/scatter_R-16.png')
Scatter([i for i in range(6,50,7)], 'figures/scatter_R-32.png')
Scatter([i for i in range(7,50,7)], 'figures/scatter_R-64.png')
Scatter([i for i in range(1,8)], 'figures/scatter_C-0.125.png')
Scatter([i for i in range(8,15)], 'figures/scatter_C-0.25.png')
Scatter([i for i in range(15,22)], 'figures/scatter_C-0.5.png')
Scatter([i for i in range(22,29)], 'figures/scatter_C-1.png')
Scatter([i for i in range(29,36)], 'figures/scatter_C-2.png')
Scatter([i for i in range(36,43)], 'figures/scatter_C-4.png')
Scatter([i for i in range(43,50)], 'figures/scatter_C-8.png')
ErrorAlongParam(Exp, [i for i in range(36,43)], 'gamma_R', 'figures/err_R_C-4.png')
ErrorAlongParam(Exp, [i for i in range(1,50)], 'gamma_C', 'figures/err_C.png')
