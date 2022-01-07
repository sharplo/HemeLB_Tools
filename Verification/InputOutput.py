import xml.etree.ElementTree as ET
import numpy as np

class InputOutput():
    dt = None
    dx = None
    normal_iN = np.array([])
    position_iN = np.array([])
    normal_oUT = np.array([])
    position_oUT = np.array([])

    def ReadInput(self, inFile):
        tree = ET.parse(inFile)
        root = tree.getroot()
        print('Reading inputs from "%s"\n' %(inFile))

        # Find grid sizes
        self.dt = float(root.find('simulation').find('step_length').attrib['value'])
        self.dx = float(root.find('simulation').find('voxel_size').attrib['value'])
        #print('dt', dt)
        #print('dx', dx)

        # Find normals and positions at inlets
        for elm in root.find('inlets').iter('inlet'):
            normal = elm.find('normal').attrib['value']
            normal = normal.strip('(').strip(')').split(',')
            self.normal_iN = np.append(self.normal_iN, np.array(normal, dtype=np.float64))
            
            position = elm.find('position').attrib['value']
            position = position.strip('(').strip(')').split(',')
            self.position_iN = np.append(self.position_iN, np.array(position, dtype=np.float64))
        self.normal_iN = self.normal_iN.reshape(int(self.normal_iN.size/3), 3)
        self.position_iN = self.position_iN.reshape(int(self.position_iN.size/3), 3)
        #print('self.normal_iN', self.normal_iN)
        #print('self.position_iN', self.position_iN)

        # Find normals and positions at outlets
        for elm in root.find('outlets').iter('outlet'):
            normal = elm.find('normal').attrib['value']
            normal = normal.strip('(').strip(')').split(',')
            self.normal_oUT = np.append(self.normal_oUT, np.array(normal, dtype=np.float64))
            
            position = elm.find('position').attrib['value']
            position = position.strip('(').strip(')').split(',')
            self.position_oUT = np.append(self.position_oUT, np.array(position, dtype=np.float64))
        self.normal_oUT = self.normal_oUT.reshape(int(self.normal_oUT.size/3), 3)
        self.position_oUT = self.position_oUT.reshape(int(self.position_oUT.size/3), 3)
        self.normal_oUT = - self.normal_oUT # normal vectos point inwards in HemeLB
        #print('self.normal_oUT', self.normal_oUT)
        #print('self.position_oUT', self.position_oUT)

        print('Reading inputs is finished.\n')