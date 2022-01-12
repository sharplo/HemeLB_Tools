import numpy as np
import matplotlib
matplotlib.use('Agg') # disable Xwindows backend
from matplotlib import pyplot as plt

class Visual(object):
    def __init__(self):
        self.color = ['tab:blue', 'tab:orange', 'tab:gray']

    def Visualise_1D(self, df, grid, var1, var2=None, kwargs1={}, kwargs2={}):
        df_last = df[df['step'] == df['step'].max()]

        fig, ax1 = plt.subplots()
        ax1.plot(df_last[grid], df_last[var1], '.', markersize=2, color=self.color[0], **kwargs1)
        ax1.set_xlabel(grid)
        ax1.set_ylabel(var1, color=self.color[0])
        fileName = 'figures/' + df.name + '_' + var1 + '-' + grid + '.png'

        if var2 != None:
            # Plot var2 on the right axis
            ax2 = ax1.twinx()
            ax2.plot(df_last[grid], df_last[var2], '.', markersize=2, color=self.color[1], **kwargs2)
            ax2.set_ylabel(var2, color=self.color[1])
            ax2.yaxis.set_label_position('right')
            ax2.yaxis.tick_right()
            fileName = 'figures/' + df.name + '_' + var1 + '&' + var2 + '-' + grid + '.png'
        
        fig.savefig(fileName, bbox_inches='tight')
        plt.close()

    def Visualise_2D(self, df, grid_1, grid_2, var1, var2=None):
        df_last = df[df['step'] == df['step'].max()]

        # Make mesh for contour plot
        X_unique = np.sort(df_last[grid_1].unique())
        Y_unique = np.sort(df_last[grid_2].unique())
        X, Y = np.meshgrid(X_unique, Y_unique)

        # Make plots
        Z1 = df_last.pivot_table(columns=grid_1, index=grid_2, values=var1, fill_value=0)

        fig, ax1 = plt.subplots()
        im1 = ax1.contourf(X, Y, Z1)
        fig.colorbar(im1, ax=ax1, label=var1)
        ax1.set_xlabel(grid_1)
        ax1.set_ylabel(grid_2)
        fileName = 'figures/' + df.name + '_' + var1 + '-' + grid_1 + '&' + grid_2 + '.png'

        if var2 != None:
            # Plot var2 on the 2nd row
            Z2 = df_last.pivot_table(columns=grid_1, index=grid_2, values=var2, fill_value=0)

            fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
            im1 = ax1.contourf(X, Y, Z1)
            fig.colorbar(im1, ax=ax1, label=var1)
            ax1.set_ylabel(grid_2)

            ax2.contourf(X, Y, Z2)
            fig.colorbar(im1, ax=ax2, label=var2)
            ax2.set_xlabel(grid_1)
            ax2.set_ylabel(grid_2)
            fileName = 'figures/' + df.name + '_' + var1 + '&' + var2 + '-' + grid_1 + '&' + grid_2 + '.png'

        fig.subplots_adjust(hspace=0.4)
        fig.savefig(fileName, bbox_inches='tight')
        plt.close()

    def Visualise_TimeSeries(self, df, var1, var2=None):
        fig, ax1 = plt.subplots()
        ax1.plot(df['step'], df[var1], '.-', color=self.color[0])
        ax1.set_xlabel('Time step')
        ax1.set_ylabel(var1, color=self.color[0])
        fileName = 'figures/' + df.name + '_' + var1 + '-timeSeries.png'

        if var2 != None:
            # Plot var2 on the right axis
            ax2 = ax1.twinx()
            ax2.plot(df['step'], df[var2], '.-', color=self.color[1])
            ax2.set_ylabel(var2, color=self.color[1])
            ax2.yaxis.set_label_position('right')
            ax2.yaxis.tick_right()
            fileName = 'figures/' + df.name + '_' + var1 + '&' + var2 + '-timeSeries.png'

        fig.savefig(fileName, bbox_inches='tight')
        plt.close()

    def Compare_TimeSeries(self, df1, df2, var1, var2=None):
        fig, ax1 = plt.subplots()
        h1, = ax1.plot(df1['step'], df1[var1], '.-', color=self.color[0])
        ax1.plot(df2['step'], df2[var1], '^--', markerfacecolor='none', color=self.color[0])
        ax1.set_xlabel('Time step')
        ax1.set_ylabel(var1, color=self.color[0])
        fileName = 'figures/' + df1.name + '_vs_' + df2.name + '-' + var1 + '-timeSeries.png'

        if var2 != None:
            # Plot var2 on the right axis
            ax2 = ax1.twinx()
            h2, = ax2.plot(df1['step'], df1[var2], '.-', color=self.color[1])
            ax2.plot(df2['step'], df2[var2], '^--', markerfacecolor='none', color=self.color[1])
            ax2.set_ylabel(var2, color=self.color[1])
            ax2.yaxis.set_label_position('right')
            ax2.yaxis.tick_right()

            plt.legend([h1, h2], [df1.name, df2.name], \
                bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=2)
            fileName = 'figures/' + df1.name + '_vs_' + df2.name + '-' + var1 + '&' + var2 + '-timeSeries.png'

        fig.savefig(fileName, bbox_inches='tight')
        plt.close()

    def Visualise_Clusters(self, df, var, clusters):
        plt.figure()
        for i in clusters:
            view = df[df['cluster'] == i]
            plt.plot(view['step'], view[var], label=df.name + str(i))
        plt.xlabel('Time step')
        plt.ylabel(var)
        plt.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=3)
        fileName = 'figures/' + df.name + '_' + var + '-clusters.png'
        plt.savefig(fileName, bbox_inches='tight')
        plt.close()

    def Visualise_Ratios(self, df, var, clusters, ref, desired):
        plt.figure()
        view_ref = df[df['cluster'] == ref]
        for i in clusters:
            if i != ref:
                view = df[df['cluster'] == i]
                plt.plot(view['step'], view[var] / view_ref[var], label=df.name + str(i))
        for i in range(len(desired)):
            if i == 0:
                label = 'desired'
            else:
                label = None
            plt.hlines(desired[i], df['step'].min(), df['step'].max(), colors='black', linestyles='dashed', label=label)
        plt.xlabel('Time step')
        plt.ylabel(var + ' ratio w.r.t. ' + df.name + str(ref))
        plt.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=3)
        fileName = 'figures/' + df.name + '_' + var + '-ratios.png'
        plt.savefig(fileName, bbox_inches='tight')
        plt.close()

    def Compare_Scatter(self, df, ref):
        fig, ax = plt.subplots()
        view = df.drop(index=ref)
        ax.scatter(view['desired'], view['measured'], color=self.color[1], label=None)
        ax.plot(ax.get_xlim(), ax.get_ylim(), '--', color=self.color[2], label='y=x')
        ax.set_xlabel('desired')
        ax.set_ylabel('measured')
        ax.legend()
        fileName = 'figures/' + df.name + '-scatter.png'
        fig.savefig(fileName, bbox_inches='tight')
        plt.close()