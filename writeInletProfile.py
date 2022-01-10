import numpy as np
import matplotlib.pyplot as plt

omega = 0.16
stepSize = 5e-3
timeSteps = 200000
Umean = 0.002
Ufluc = 0.1*Umean

time = np.linspace(0, stepSize * timeSteps, timeSteps)
vel = Umean + Ufluc * np.cos(omega*time)

plt.plot(time, vel)
plt.savefig("inletProfile.png")

with open('inletProfile.txt', 'w') as f:
    for i in range(len(time)):
        f.write(str(time[i]) + ' ' + str(vel[i]) + '\n')
