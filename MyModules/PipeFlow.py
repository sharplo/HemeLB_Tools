import pandas as pd
from MyModules.InputOutput import *
from MyModules.Visual import *
from MyModules.DiscError import *

class PipeFlow(InputOutput, Visual, DiscError):
    def __init__(self, inFile, dataDir, outDir, shotBeg, shotEnd, shotStep, dfDict):
        InputOutput.__init__(self, inFile, outDir)
        Visual.__init__(self, dfDict)
        DiscError.__init__(self)

        self.dataDir = dataDir # directory where data reside
        self.shotBeg = shotBeg # first file to be read
        self.shotEnd = shotEnd # last file to be read
        self.shotStep = shotStep # step of file reading
        self.dfDict = dfDict # dictionary between data frame names and data file names
        
        self.R = None # radius of pipe (m)
        self.P_in = [] # pressure at inlets (mmHg)
        self.P_out = [] # pressure at outlets (mmHg)

        # General procedures
        for key in self.dfDict.keys():
            values = self.dfDict[key]
            self.MakeDataFrames(key, values)
        self.ExtractParams()
        self.DeriveParams()

    def MakeDataFrames(self, key, values):
        if type(values) is str:
            # Load data from file
            setattr(self, key, self.LoadData(values))
        elif type(values) is list:
            # Intersect data frames
            setattr(self, key, self.JoinDataFrames(values))
        setattr(getattr(self, key), 'name', key) # df.name = key
        self.RenameCol(getattr(self, key))
    
    def AddDataFrame(self, key, values):
        self.MakeDataFrames(key, values)
        self.dfDict[key] = values

    def LoadData(self, file):
        df = pd.DataFrame()
        for shot in range(self.shotBeg, self.shotEnd+1, self.shotStep):
            # TODO: make it compatible with all operating system, e.g. using sys.path
            fileName = self.dataDir + file + '/' + file + str(shot) + '.txt'
            df = df.append(pd.read_csv(fileName, delimiter=' '), ignore_index=True)
        return df

    def JoinDataFrames(self, values):
        df = getattr(self, values[0]).copy() # to ensure it is not a view
        for i in range(1, len(values)):
            if values[i] == 'cEN':
                df = self.CentrePoint(df)
            elif type(values[i]) == int:
                df = df[df['cluster'] == values[i]]
            else:
                df = pd.merge(df, getattr(self, values[i]))
        return df
    
    def CentrePoint(self, df):
        return df[(df['grid_x'] >= df['grid_x'].mean() - 0.5 * self.dx) \
            & (df['grid_x'] <= df['grid_x'].mean() + 0.5 * self.dx) \
            & (df['grid_y'] >= df['grid_y'].mean() - 0.5 * self.dx) \
            & (df['grid_y'] <= df['grid_y'].mean() + 0.5 * self.dx) \
            & (df['grid_z'] >= df['grid_z'].mean() - 0.5 * self.dx) \
            & (df['grid_z'] <= df['grid_z'].mean() + 0.5 * self.dx)]

    def RenameCol(self, df):
        df.rename(columns={
                        'velocity(0)':'Ux',
                        'velocity(1)':'Uy',
                        'velocity(2)':'Uz',
                        'pressure':'P',}, inplace=True)

    def ExtractParams(self):
        pass # defined in each daughter calss

    def DeriveParams(self):
        pass # defined in each daughter class

    def Clustering(self, df, position):

        num_plane = len(position)
        num_row = len(df)

        # Convert from lattice unit to physical unit
        position = self.dx * position

        # Calculate distance from each given position
        grid = np.array([df['grid_x'], df['grid_y'], df['grid_z']]).transpose()
        distance = np.array([])
        for i in range(num_plane):
            # Using axis 0 is the most efficient
            dist = np.linalg.norm(np.transpose(grid - position[i,:]), axis=0)
            distance = np.append(distance, dist)
        distance = distance.reshape(num_plane, num_row)

        planeIdx = np.argmin(distance, axis=0)

        # Alternative implementation
        '''
        planeIdx = np.array([], dtype=np.int)
        for x, y, z in zip(df['grid_x'], df['grid_y'], df['grid_z']):
            grid = np.array([x, y, z])
            distMin = np.inf
            for i in range(num_plane):
                dist = np.linalg.norm(grid - position[i])
                if (dist < distMin):
                    distMin = dist
                    num = i
            planeIdx = np.append(planeIdx, num)
        '''

        # Record results
        df['cluster'] = planeIdx

        # Make dataframe for each cluster
        for i in range(num_plane):
            key = df.name + str(i)
            values = [df.name, i]
            self.AddDataFrame(key, values)
        