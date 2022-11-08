from turtle import width
import numpy as np
import matplotlib
matplotlib.use('Agg') # disable Xwindows backend
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d # for 3D plotting

class Visual(object):
    def __init__(self, dfDict):
        plt.rc('lines', linewidth=2)
        plt.rc('font', family='serif')
        plt.rc('axes', labelsize=14)
        plt.rc('xtick', labelsize=12)
        plt.rc('ytick', labelsize=12)
        plt.rc('legend', fontsize=12)
        plt.rc('legend', handletextpad=0.5)
        plt.rc('axes', axisbelow=True)
        self.color = ['tab:blue', 'tab:orange', 'tab:gray']
        self.dfDict = dfDict

    def Visualise_1D(self, df, grid, var1, var2=None, steps=None, kwargs1={}, kwargs2={}):
        if steps is None:
            view = df[df['step'] == df['step'].max()]
        else:
            view = df[df['step'].isin(steps)]

        fig, ax1 = plt.subplots()
        h1, = ax1.plot(view[grid], view[var1], 'o', markersize=3, color=self.color[0], **kwargs1)
        ax1.grid(axis='both')
        ax1.minorticks_on()
        ax1.ticklabel_format(style='sci', scilimits=(0,3), useMathText=True)
        ax1.set_xlabel(grid)
        ax1.set_ylabel(var1)
        fileName = df.name + '_' + var1 + '-' + grid + '.pdf'

        if var2 is not None:
            if var2 == 'exSol_' + var1:
                # Plot var2 on the same axis
                ax1.plot(view[grid], view[var2], 'x', markersize=3, color=self.color[1], **kwargs2)
                plt.legend(bbox_to_anchor=(0, 1.04, 1, 0), loc="lower left", mode="expand", ncol=2)
            else:
                # Plot var2 on the right axis
                ax2 = ax1.twinx()
                h2, = ax2.plot(view[grid], view[var2], 'o', markersize=3, color=self.color[1], **kwargs2)
                ax2.yaxis.set_label_position('right')
                ax2.yaxis.tick_right()
                ax2.minorticks_on()
                ax2.set_ylabel(var2)
                ax1.grid(axis='y') # turn off grid line on y-axis
                plt.legend([h1, h2], [var1, var2], \
                    bbox_to_anchor=(0, 1.04, 1, 0), loc="lower left", mode="expand", ncol=2)
            fileName = df.name + '_' + var1 + '&' + var2 + '-' + grid + '.pdf'
        
        fig.savefig(self.outDir + fileName, bbox_inches='tight')
        plt.close()

    def Visualise_2D(self, df, grid_1, grid_2, var1, var2=None, steps=None):
        if steps is None:
            view = df[df['step'] == df['step'].max()]
        else:
            view = df[df['step'].isin(steps)]

        # Make mesh for contour plot
        X_unique = np.sort(view[grid_1].unique())
        Y_unique = np.sort(view[grid_2].unique())
        X, Y = np.meshgrid(X_unique, Y_unique)

        # Make plots
        Z1 = view.pivot_table(columns=grid_1, index=grid_2, values=var1, fill_value=0)

        fig, ax1 = plt.subplots()
        im1 = ax1.contourf(X, Y, Z1)
        fig.colorbar(im1, ax=ax1, label=var1)
        ax1.set_xlabel(grid_1)
        ax1.set_ylabel(grid_2)
        fileName = df.name + '_' + var1 + '-' + grid_1 + '&' + grid_2 + '.pdf'

        if var2 is not None:
            # Plot var2 on the 2nd row
            Z2 = view.pivot_table(columns=grid_1, index=grid_2, values=var2, fill_value=0)

            fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
            im1 = ax1.contourf(X, Y, Z1)
            fig.colorbar(im1, ax=ax1, label=var1)
            ax1.set_ylabel(grid_2)

            ax2.contourf(X, Y, Z2)
            fig.colorbar(im1, ax=ax2, label=var2)
            ax2.set_xlabel(grid_1)
            ax2.set_ylabel(grid_2)
            fileName = df.name + '_' + var1 + '&' + var2 + '-' + grid_1 + '&' + grid_2 + '.pdf'

        fig.subplots_adjust(hspace=0.4)
        fig.savefig(self.outDir + fileName, bbox_inches='tight')
        plt.close()

    def Visualise_3D(self, df, var, kwargs={}):
        if 'step' in df.columns:
            view = df[df['step'] == df['step'].max()]
        else:
            view = df
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        img = ax.scatter3D(view['grid_x'], view['grid_y'], view['grid_z'], \
            c=view[var], **kwargs)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        cbaxes = fig.add_axes([0.2, 0.9, 0.8, 0.03])
        fig.colorbar(img, label=var, orientation='horizontal', cax=cbaxes)
        fileName = df.name + '_' + var + '-3D' + '.pdf'
        fig.savefig(self.outDir + fileName, bbox_inches='tight')
        plt.close()

    def Visualise_TimeSeries(self, df, var1, var2=None):
        return self.Visualise_1D(df, 'step', var1, var2=var2, steps=range(int(df['step'].max())), \
            kwargs1={'linestyle':'-'}, kwargs2={'linestyle':'--'})

    def Compare_TimeSeries(self, df1, df2, var1, var2=None):
        fig, ax1 = plt.subplots()
        h1, = ax1.plot(df1['step'], df1[var1], '-', color=self.color[0])
        h2, = ax1.plot(df2['step'], df2[var1], '^-', markersize=6, color=self.color[0])
        ax1.grid(axis='both')
        ax1.minorticks_on()
        ax1.ticklabel_format(style='sci', scilimits=(0,3), useMathText=True)
        ax1.set_xlabel('Time step')
        ax1.set_ylabel(var1)
        fileName = df1.name + '_vs_' + df2.name + '-' + var1 + '-timeSeries.pdf'

        if var2 is not None:
            # Plot var2 on the right axis
            ax2 = ax1.twinx()
            h3, = ax2.plot(df1['step'], df1[var2], '--', color=self.color[1])
            h4, = ax2.plot(df2['step'], df2[var2], '^--', \
                markerfacecolor='none', markersize=6, color=self.color[1])
            ax2.yaxis.set_label_position('right')
            ax2.yaxis.tick_right()
            ax2.minorticks_on()
            ax2.set_ylabel(var2)
            ax1.grid(axis='y') # turn off grid line on y-axis
            plt.legend([h1, h2, h3, h4], \
                [var1 + ' in ' + df1.name, var1 + ' in ' + df2.name, \
                var2 + ' in ' + df1.name, var2 + ' in ' + df2.name], \
                bbox_to_anchor=(0, 1.04, 1, 0), loc="lower left", mode="expand", ncol=2)
            fileName = df1.name + '_vs_' + df2.name + '-' + var1 + '&' + var2 + '-timeSeries.pdf'

        fig.savefig(self.outDir + fileName, bbox_inches='tight')
        plt.close()

    def Check_Clustering(self, df):
        return self.Visualise_3D(df, 'cluster', {'cmap':'tab20'})

    def Visualise_Clusters(self, df, var, clusters):
        plt.figure()
        for i in clusters:
            view = df[df['cluster'] == i]
            plt.plot(view['step'], view[var], label=self.dfDict[df.name] + ' ' + str(i))
        plt.minorticks_on()
        plt.ticklabel_format(style='sci', scilimits=(0,3), useMathText=True)
        plt.xlabel('Time step')
        plt.ylabel(var)
        plt.legend(bbox_to_anchor=(0, 1.04, 1, 0), loc="lower left", mode="expand", ncol=3)
        fileName = df.name + '_' + var + '-clusters.pdf'
        plt.savefig(self.outDir + fileName, bbox_inches='tight')
        plt.close()

    def Visualise_Ratios(self, df, var, clusters, ref, desired):
        plt.figure()
        view_ref = df[df['cluster'] == ref]
        for i in clusters:
            if i != ref:
                view = df[df['cluster'] == i]
                plt.plot(view['step'], view[var] / view_ref[var], \
                    label=self.dfDict[df.name] + ' ' + str(i))
        for i in range(len(desired)):
            if i == 0:
                label = 'desired'
            else:
                label = None
            plt.hlines(desired[i], df['step'].min(), df['step'].max(), \
                colors=self.color[-1], linestyles='dashed', label=label)
        
        plt.ylim(np.min(desired) - 0.1, np.max(desired) + 0.1)
        plt.minorticks_on()
        plt.ticklabel_format(style='sci', scilimits=(0,3), useMathText=True)
        plt.xlabel('Time step')
        plt.ylabel(var + ' ratios with respect to ' + self.dfDict[df.name] + ' ' + str(ref))
        plt.legend(bbox_to_anchor=(0, 1.04, 1, 0), loc="lower left", mode="expand", ncol=3)
        fileName = df.name + '_' + var + '-ratios.pdf'
        plt.savefig(self.outDir + fileName, bbox_inches='tight')
        plt.close()

    def Compare_Scatter(self, df):
        fig, ax = plt.subplots()
        ax.scatter(df['Desired'], df['Measured'], color=self.color[1], label=None)
        ax.plot(ax.get_xlim(), ax.get_xlim(), '--', color=self.color[-1], label='y = x')
        ax.minorticks_on()
        ax.set_xlabel('Desired value')
        ax.set_ylabel('Measured value')
        ax.legend()
        fileName = df.name + '-scatter.pdf'
        fig.savefig(self.outDir + fileName, bbox_inches='tight')
        plt.close()