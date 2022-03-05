#!/usr/bin/python3.6
import os
import matplotlib
matplotlib.use('Agg') # disable Xwindows backend
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

# Set figure parameters
plt.rc('lines', linewidth=2)
plt.rc('font', family='serif')
plt.rc('axes', labelsize=14)
plt.rc('xtick', labelsize=12)
plt.rc('ytick', labelsize=12)
plt.rc('legend', fontsize=12)
plt.rc('legend', handletextpad=0.3)
plt.rc('axes', axisbelow=True)

# Shorthand
Qratios = '/figures/Qratios.csv'
cmap_tend = matplotlib.cm.get_cmap('magma')

# Add a coloumn about stability in the data frame
def SetStability(exp, dir, caseNum):
    exp['stable'] = None
    for i in range(len(caseNum)):
        data = dir + str(caseNum[i]) + Qratios
        if not os.path.exists(data):
            exp['stable'].at[caseNum[i]-1] = False
        else:
            exp['stable'].at[caseNum[i]-1] = True

# Plot a map showing whether the simulations are stable
def StabilityMap(exp, dir, caseNum):
    SetStability(exp, dir, caseNum)

    row = [i-1 for i in caseNum]
    view = exp.iloc[row,:]
    stable = view[view['stable'] == True]
    unstable = view[view['stable'] == False]

    fig, ax = plt.subplots()
    ax.plot(np.log2(stable['gamma_R']), np.log2(stable['gamma_C']), \
        '.', color='tab:green', label='stable', markersize=15)
    ax.plot(np.log2(unstable['gamma_R']), np.log2(unstable['gamma_C']), \
        'x', color='tab:red', label='unstable', markersize=15)

    ax.minorticks_on()
    ax.tick_params(labelsize=18)
    ax.set_xlabel(r'$\log_2 \gamma_R$', fontsize=20)
    ax.set_ylabel(r'$\log_2 \gamma_C$', fontsize=20)
    ax.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=3, fontsize=20)
    return fig, ax

def CompareMeasuredDesired(exp, dir, caseNum, param, outFile):
    if param == 'gamma_R':
        tex = r'$\gamma_R$'
    elif param == 'gamma_C':
        tex = r'$\gamma_C$'
    tendency = np.linspace(0.85, 0.15, len(caseNum))

    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.set_size_inches(12.8, 4.8)
    for i in range(len(caseNum)):
        # Read data
        data = dir + str(caseNum[i]) + Qratios
        if not os.path.exists(data):
            continue
        df = pd.read_csv(data)

        # Compare desired and measured values in scatter plot
        ax1.scatter(df['Desired'], df['Measured'], color=cmap_tend(tendency[i]), \
            label= tex + ' = ' + str(exp[param].at[caseNum[i]-1]))
        
        # Plot relative error of desired and measured values against model parameters
        x = [ exp[param].at[caseNum[i]-1] ] * len(df['RelErr'])
        y = df['RelErr']*100
        ax2.scatter(np.log2(x), y, color=cmap_tend(tendency[i]))

    ax1.plot(ax1.get_xlim(), ax1.get_xlim(), '--', color='tab:gray', label='y = x')
    ax1.minorticks_on()
    ax1.set_xlabel('Desired Q ratios')
    ax1.set_ylabel('Simulated Q ratios')

    ax2.minorticks_on()
    ax2.tick_params(axis='x', which='minor', bottom=False)
    ax2.grid(axis='y')
    ax2.set_xlabel(r'$\log_2$' + tex)
    ax2.set_ylabel('% error')

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0,-0.01,1,1), \
        bbox_transform=plt.gcf().transFigure, ncol=10, columnspacing=1)
    fig.savefig(outFile, bbox_inches='tight')
    plt.close()

# ===========================================================================
# FiveExit_coarse
# ===========================================================================
dataDir = '/hppfs/work/pn72qu/di46kes/FiveExit_coarse/FiveExit_'
exp = pd.read_csv('FiveExit_coarse/experiments.csv')
figDir = 'FiveExit_coarse/figures/'
if not os.path.exists(figDir):
    os.mkdir(figDir)

# Stability map
fig, ax = StabilityMap(exp, dataDir, [i for i in range(1,92)])
fig.savefig(figDir + 'stability.pdf', bbox_inches='tight')

# Compare measured and desired value of Q-ratios
CompareMeasuredDesired(exp, dataDir, [i for i in range(1,50,7)], 'gamma_C', figDir + 'err-R1.pdf')
CompareMeasuredDesired(exp, dataDir, [43,44,45,46], 'gamma_R', figDir + 'err-C8.pdf')

# ===========================================================================
# FiveExit_medium
# ===========================================================================
dataDir = '/hppfs/work/pn72qu/di46kes/FiveExit_medium/FiveExit_'
exp = pd.read_csv('FiveExit_medium/experiments.csv')
figDir = 'FiveExit_medium/figures/'
if not os.path.exists(figDir):
    os.mkdir(figDir)

# Stability map
fig, ax = StabilityMap(exp, dataDir, [i for i in range(1,92)])
fig.savefig(figDir + 'stability.pdf', bbox_inches='tight')

# Compare measured and desired value of Q-ratios
CompareMeasuredDesired(exp, dataDir, [43,44,45,46], 'gamma_R', figDir + 'err-C8.pdf')

# ===========================================================================
# FiveExit_fine
# ===========================================================================
dataDir = '/hppfs/work/pn72qu/di46kes/FiveExit_fine/FiveExit_'
exp = pd.read_csv('FiveExit_fine/experiments.csv')
figDir = 'FiveExit_fine/figures/'
if not os.path.exists(figDir):
    os.mkdir(figDir)

# Stability map
fig, ax = StabilityMap(exp, dataDir, [i for i in range(1,92)])
fig.savefig(figDir + 'stability.pdf', bbox_inches='tight')

# Compare measured and desired value of Q-ratios
CompareMeasuredDesired(exp, dataDir, [i for i in range(1,50,7)], 'gamma_C', figDir + 'err-R1.pdf')
CompareMeasuredDesired(exp, dataDir, [43,44,45,46], 'gamma_R', figDir + 'err-C8.pdf')

# ===========================================================================
# ProfundaFemoris_coarse
# ===========================================================================
dataDir = '/hppfs/work/pn72qu/di46kes/ProfundaFemoris_coarse/ProfundaFemoris_'
exp = pd.read_csv('ProfundaFemoris_coarse/experiments.csv')
figDir = 'ProfundaFemoris_coarse/figures/'
if not os.path.exists(figDir):
    os.mkdir(figDir)

# Stability map with a line
fig, ax = StabilityMap(exp, dataDir, [i for i in range(1,61)])
ax.plot([-0.3,10.3], [4.7,15.3], color='tab:blue')
fig.savefig(figDir + 'stability.pdf', bbox_inches='tight')

# Compare measured and desired value of Q-ratios
CompareMeasuredDesired(exp, dataDir, [i for i in range(25,61,7)], 'gamma_R', figDir + 'err-opt.pdf')
CompareMeasuredDesired(exp, dataDir, [53,61,62,63,59], 'gamma_C', figDir + 'err-R256.pdf')

# ===========================================================================
# ProfundaFemoris_medium
# ===========================================================================
dataDir = '/hppfs/work/pn72qu/di46kes/ProfundaFemoris_medium/ProfundaFemoris_'
exp = pd.read_csv('ProfundaFemoris_fine/experiments.csv') # trick to avoid decimal R in exp 61-78
figDir = 'ProfundaFemoris_medium/figures/'
if not os.path.exists(figDir):
    os.mkdir(figDir)

# Stability map with a line
fig, ax = StabilityMap(exp, dataDir, [i for i in range(1,61)])
ax.plot([-0.3,10.3], [4.7,15.3], color='tab:blue')
fig.savefig(figDir + 'stability.pdf', bbox_inches='tight')

# Compare measured and desired value of Q-ratios
CompareMeasuredDesired(exp, dataDir, [i for i in range(25,61,7)], 'gamma_R', figDir + 'err-opt.pdf')

# ===========================================================================
# ProfundaFemoris_fine
# ===========================================================================
dataDir = '/hppfs/work/pn72qu/di46kes/ProfundaFemoris_fine/ProfundaFemoris_'
exp = pd.read_csv('ProfundaFemoris_fine/experiments.csv')
figDir = 'ProfundaFemoris_fine/figures/'
if not os.path.exists(figDir):
    os.mkdir(figDir)

# Stability map with a line
fig, ax = StabilityMap(exp, dataDir, [i for i in range(1,61)])
ax.plot([-0.3,10.3], [2.7,13.3], color='tab:blue')
fig.savefig(figDir + 'stability.pdf', bbox_inches='tight')
