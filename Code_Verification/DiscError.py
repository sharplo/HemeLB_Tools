from Param import * # local file
import numpy as np

def CalExact(df, var):
    if (var == 'P'):
        exSol = lambda z: P_max + dPdz * (z - z_min)
        df['exSol_P'] = exSol(df['grid_z'])
    elif (var == 'Uz'):
        exSol = lambda r: G / (4*mu) * (R**2 - r**2)
        df['exSol_Uz'] = exSol(df['r'])

def CalErrNorms(df, var):
    err = df[var] - df['exSol_' + var] # local error
    df['err_' + var] = err
    L1 = np.sum( np.abs(err) ) / err.size # L1-norm
    L2 = np.sqrt( np.dot(err, err) / err.size ) # L2-norm
    L8 = np.max( np.abs(err) ) # infinite-norm
    return L1, L2, L8

def WriteDiscErr(df, var):
    # Calculate error norms
    L1, L2, L8 = CalErrNorms(df, var)
    print('Error norms of', var, ':')
    print('dt = %f, L1 = %f, L2 = %f, L8 = %f' %(np.log(dt), np.log(L1), np.log(L2), np.log(L8)))

    # Write heading if file does not exist
    try:
        f = open('discErr_' + var + '.dat')
        f.close()
    except:
        f = open('discErr_' + var + '.dat', 'w')
        f.write('dt L1 L2 L8\n')
        f.close()

    # Write results
    with open('discErr_' + var + '.dat', 'a') as f:
        f.write("%f %f %f %f\n" %(np.log(dt), np.log(L1), np.log(L2), np.log(L8)))
