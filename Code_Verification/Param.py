import sys
import pandas as pd

# Read data file
directory = sys.argv[1] + 'Extracted/'
shotBeg = int(sys.argv[2])
shotEnd = int(sys.argv[3])

df_in = pd.DataFrame()
df_out = pd.DataFrame()
df_cL = pd.DataFrame()
df_pY = pd.DataFrame()
df_pZ = pd.DataFrame()
for shot in range(shotBeg, shotEnd+1):
    #df_in = df_in.append(pd.read_csv(directory + 'inlet/inlet' + str(shot) + '.txt', delimiter=' '))
    #df_out = df_out.append(pd.read_csv(directory + 'outlet/outlet' + str(shot) + '.txt', delimiter=' '))
    df_cL = df_cL.append(pd.read_csv(directory + 'centreLine/centreLine' + str(shot) + '.txt', delimiter=' '))
    #df_pY = df_pY.append(pd.read_csv(directory + 'planeY/planeY' + str(shot) + '.txt', delimiter=' '))
    df_pZ = df_pZ.append(pd.read_csv(directory + 'planeZ/planeZ' + str(shot) + '.txt', delimiter=' '))

dfList = [df_cL, df_pZ]

# Constants
mmHg = 133.3223874 # Pa
mu = 0.004 # dynamic viscosity (Pa*s)
PI = 3.14159265358979323846264338327950288

# ============================ Need Adaptation ===============================
# Input parameters
dt = 5e-5 # step_length (s)
dx = 5e-5 # voxel_size (m)
P_min = df_cL['pressure'].min() # 0 (mmHg)
P_max = df_cL['pressure'].max() # 0.01 (mmHg)
x_min = df_pZ['grid_x'].min() # 0.0002 (m)
x_max = df_pZ['grid_x'].max() # 0.0041 (m)
z_min = df_cL['grid_z'].min() # 0.0002 (m)
z_max = df_cL['grid_z'].max() # 0.0201 (m)
# ============================================================================

# Derived parameters
L = z_max - z_min + dx # length of pipe (m)
R = 0.5 * (x_max - x_min + dx) # radius of pipe (m)
R0 = 0.5 * (x_min + x_max) # x-ord of centre
dPdz = (P_min - P_max) / L # pressure gradient (mmHg / m)
G = - dPdz * mmHg # used in Poiseuille equation (Pa)
