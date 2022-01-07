import xml.etree.ElementTree as ET
import numpy as np

# Constants
mmHg = 133.3223874 # Pa
mu = 0.004 # dynamic viscosity (Pa*s)
PI = 3.14159265358979323846264338327950288

class InputOutput():
    dt = None
    dx = None
    normal_iN = np.array([])
    position_iN = np.array([])
    normal_oUT = np.array([])
    position_oUT = np.array([])

    def ReadInput(self, inFile):
        print('Reading inputs from "%s"' %(inFile))
        tree = ET.parse(inFile)
        root = tree.getroot()

        # Find grid sizes
        self.dt = float(root.find('simulation').find('step_length').attrib['value'])
        self.dx = float(root.find('simulation').find('voxel_size').attrib['value'])
        #print('dt', self.dt)
        #print('dx', self.dx)

        # Find normal and position vector of inlets
        for elm in root.find('inlets').iter('inlet'):
            normal = elm.find('normal').attrib['value']
            normal = normal.strip('(').strip(')').split(',')
            self.normal_iN = np.append(self.normal_iN, np.array(normal, dtype=np.float64))
            
            position = elm.find('position').attrib['value']
            position = position.strip('(').strip(')').split(',')
            self.position_iN = np.append(self.position_iN, np.array(position, dtype=np.float64))
        self.normal_iN = self.normal_iN.reshape(int(self.normal_iN.size/3), 3)
        self.position_iN = self.position_iN.reshape(int(self.position_iN.size/3), 3)
        #print('normal_iN', self.normal_iN)
        #print('position_iN', self.position_iN)

        # Find normal and position vector of outlets
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
        #print('normal_oUT', self.normal_oUT)
        #print('position_oUT', self.position_oUT)

        print('Reading inputs is finished.\n')

    def RescaleSize(self, inFile, outFile, scale):
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree = ET.parse(inFile, parser)
        root = tree.getroot()

        # Rescale voxel size
        value = float(root.find('simulation').find('voxel_size').attrib['value'])
        value = value * scale
        root.find('simulation').find('voxel_size').set('value', '{:0.5e}'.format(value))

        # Rescale radii
        for elm in root.iter('radius'):
            value = float(elm.attrib['value'])
            value = value * scale
            elm.set('value', '{:0.5e}'.format(value))
        
        # Rescale areas
        for elm in root.iter('area'):
            value = float(elm.attrib['value'])
            value = value * scale**2
            elm.set('value', '{:0.5e}'.format(value))

        tree.write(outFile, encoding='utf-8', xml_declaration=True)

    def ChangeParam(self, inFile, outFile):
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree = ET.parse(inFile, parser)
        root = tree.getroot()

        for elm in root.find('outlets').iter('outlet'):
            condition = elm.find('condition')
            if condition.attrib['type'] == 'windkessel':
                self.SetParam_Windkessel(condition)

        tree.write(outFile, encoding='utf-8', xml_declaration=True)

    def SetParam_Windkessel(self, condition):
        radius = float(condition.find('radius').attrib['value'])
        G = 8 * mu / (PI * radius**4)
        L = 10 / radius # under testing
        resistance = abs(G * L)
        capacitance = 0.2 # under testing

        if condition.attrib['subtype'] == 'fileGKmodel':
            condition.set('subtype', 'GKmodel')
            condition.remove(condition.find('path'))
            condition.remove(condition.find('area'))

        if condition.find('R') == None:
            elm = ET.Element('R', {'units':'kg/m^4*s', 'value':'{:0.5e}'.format(resistance)})
            elm.tail = "\n" + 4 * "  "
            condition.insert(0, elm)
        else:
            condition.find('R').set('value', '{:0.5e}'.format(resistance))

        if condition.find('C') == None:
            elm = ET.Element('C', {'units':'m^4*s^2/kg', 'value':'{:0.5e}'.format(capacitance)})
            elm.tail = "\n" + 4 * "  "
            condition.insert(1, elm)
        else:
            condition.find('C').set('value', '{:0.5e}'.format(capacitance))
        