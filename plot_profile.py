import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

file = sys.argv[1]

df = pd.read_table(file, sep=' ', header=None, names=['time', 'Umax'])
plt.plot(df['time'], df['Umax'])
plt.grid()
plt.minorticks_on()
plt.xticks(np.arange(df['time'].min(), df['time'].max()+1, 1.0))
plt.xlabel('Time (s)')
plt.ylabel('Flow velocity (m/s)')
plt.savefig(file[:-4] + '.png')