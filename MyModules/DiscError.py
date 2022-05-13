import numpy as np

class DiscError(object):
    def CalErrNorms(self, err):
        L1 = np.sum( np.abs(err) ) / err.size # L1-norm
        L2 = np.sqrt( np.dot(err, err) / err.size ) # L2-norm
        L8 = np.max( np.abs(err) ) # infinite-norm
        return L1, L2, L8

    def WriteDiscErr(self, df, var):
        # Calculate error norms
        L1, L2, L8 = self.CalErrNorms(df['err_' + var])
        print('Absolute errors of', var, 'in base 10:')
        print('dt:%f, L1:%f, L2:%f, L8:%f' %(np.log10(self.dt), np.log10(L1), np.log10(L2), np.log10(L8)))

        # Write heading if file does not exist
        fileName = self.outDir + 'discErr_' + var + '.dat'
        try:
            f = open(fileName)
            f.close()
        except:
            f = open(fileName, 'w')
            f.write('dt L1 L2 L8\n')
            f.close()

        # Write results
        with open(fileName, 'a') as f:
            f.write("%f %f %f %f\n" %(np.log10(self.dt), np.log10(L1), np.log10(L2), np.log10(L8)))
