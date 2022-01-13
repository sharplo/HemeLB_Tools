#!/usr/bin/python3.6
import os
import matplotlib
matplotlib.use('Agg') # disable Xwindows backend
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

if not os.path.exists('./figures'):
    os.mkdir('./figures')

Dir = '/dss/dsshome1/04/di46kes/'
CaseName = 'FiveExit_'
FileName = '/figures/flowRateRatios.csv'

# Compare desired and measured values in scatter plot
def Scatter(caseNum, fileName):
    fig, ax = plt.subplots()
    for i in range(len(caseNum)):
        file = Dir + CaseName + str(caseNum[i]) + FileName
        if not os.path.exists(file):
            print('Case %d has failed.' %(caseNum[i]))
            continue
        df = pd.read_csv(file)
        ax.scatter(df['desired'], df['measured'], label='case' + str(caseNum[i]))
    ax.plot(ax.get_xlim(), ax.get_ylim(), '--', color='tab:gray', label='y=x')
    ax.set_xlabel('desired')
    ax.set_ylabel('measured')
    ax.legend()
    fig.savefig(fileName, bbox_inches='tight')
    plt.close()

# Plot relative error of desired and measured values against model parameters
def ErrorAlongParam(caseNum, param, fileName):
    fig, ax = plt.subplots()
    for i in range(len(caseNum)):
        file = Dir + CaseName + str(caseNum[i]) + FileName
        if not os.path.exists(file):
            print('Case %d has failed.' %(caseNum[i]))
            continue
        df = pd.read_csv(file)
        x = [param[i]]*len(df['relErr'])
        y = df['relErr']*100
        ax.scatter(np.log(x), y, label='case' + str(caseNum[i]))
    ax.set_xlabel('log (gamma)')
    ax.set_ylabel('% error')
    ax.legend()
    fig.savefig(fileName, bbox_inches='tight')
    plt.close()

Scatter([i for i in range(1,9)], 'figures/scatter_1-8.png')
Scatter([i for i in range(9,20)], 'figures/scatter_9-19.png')
ErrorAlongParam([i for i in range(1,9)], [2**(i-1) for i in range(1,9)], 'figures/errR_1-8.png')
ErrorAlongParam([i for i in range(9,20)], [0.01*2**(i-1) for i in range(1,12)], 'figures/errC_9-19.png')