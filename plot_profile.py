import sys
import pandas as pd
import matplotlib.pyplot as plt

file = sys.argv[1]

df = pd.read_table(file, sep=' ', header=None, names=['time', 'Umax'])
plt.plot(df['time'], df['Umax'])
plt.xlabel('time (s)')
plt.ylabel('Umax (m/s)')
plt.savefig(file[:-4] + '.png')