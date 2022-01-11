import xml.etree.ElementTree as ET
import numpy as np

# Constants
PI = 3.14159265358979323846264338327950288
mmHg = 133.3223874 # Pa
cs2 = 1.0 / 3.0 # speed of sound squared (lattice unit)
mu = 0.004 # dynamic viscosity (Pa*s)
rho = 1000 # fluid density (kg/m^3)

# Derived constants
nu = mu / rho # kinematic viscosity

# For preserving comments in the xml file
class CommentedTreeBuilder(ET.TreeBuilder):
    def comment(self, data):
        self.start(ET.Comment, {})
        self.data(data)
        self.end(ET.Comment)
parser = ET.XMLParser(target=CommentedTreeBuilder())

class InputOutput():
    dt = None # step_length (s)
    dx = None # voxel_size (m)
    normal_iN = np.array([]) # normal vector of inlets (no unit)
    position_iN = np.array([]) # position vector of inlets (lattice unit)
    normal_oUT = np.array([]) # normal vector of outlets (no unit)
    position_oUT = np.array([]) # position vector of inlets (lattice unit)
    resistance = np.array([]) # resistance of the Windkessel model (kg/m^4*s)
    capacitance = np.array([]) # capacitance of the Windkessel model (m^4*s^2/kg)

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
            value = elm.find('normal').attrib['value']
            value = value.strip('(').strip(')').split(',')
            self.normal_iN = np.append(self.normal_iN, np.array(value, dtype=np.float64))
            
            value = elm.find('position').attrib['value']
            value = value.strip('(').strip(')').split(',')
            self.position_iN = np.append(self.position_iN, np.array(value, dtype=np.float64))
        self.normal_iN = self.normal_iN.reshape(int(self.normal_iN.size/3), 3)
        self.position_iN = self.position_iN.reshape(int(self.position_iN.size/3), 3)
        #print('normal_iN', self.normal_iN)
        #print('position_iN', self.position_iN)

        # Find normal and position vector of outlets
        for elm in root.find('outlets').iter('outlet'):
            value = elm.find('normal').attrib['value']
            value = value.strip('(').strip(')').split(',')
            self.normal_oUT = np.append(self.normal_oUT, np.array(value, dtype=np.float64))
            
            value = elm.find('position').attrib['value']
            value = value.strip('(').strip(')').split(',')
            self.position_oUT = np.append(self.position_oUT, np.array(value, dtype=np.float64))
        self.normal_oUT = self.normal_oUT.reshape(int(self.normal_oUT.size/3), 3)
        self.position_oUT = self.position_oUT.reshape(int(self.position_oUT.size/3), 3)
        self.normal_oUT = - self.normal_oUT # normal vectos point inwards in HemeLB
        #print('normal_oUT', self.normal_oUT)
        #print('position_oUT', self.position_oUT)

        # Find parameters of the Windkessel model
        for elm in root.find('outlets').iter('outlet'):
            condition = elm.find('condition')
            if condition.attrib['type'] == 'windkessel':
                value = condition.find('R').attrib['value']
                self.resistance = np.append(self.resistance, float(value))

                value = condition.find('C').attrib['value']
                self.capacitance = np.append(self.capacitance, float(value))
        #print('resistance', self.resistance)
        #print('capacitance', self.capacitance)

        print('Reading inputs is finished.\n')

    def RescaleSize(self, inFile, outFile, scale):
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

    def ChangeParam(self, inFile, outFile, tau, timeSteps, Wo, Re, epsilon, \
            flowRateRatios, mulFact_R, mulFact_C):

        tree = ET.parse(inFile, parser)
        root = tree.getroot()

        elm = root.find('simulation')
        dx = float(elm.find('voxel_size').attrib['value'])
        dt = cs2 * (tau - 0.5) * dx**2 / nu
        elm.find('step_length').set('value', '{:0.5e}'.format(dt))
        elm.find('steps').set('value', str(timeSteps))

        elm = root.find('inlets').find('inlet').find('condition')
        radius_iN = float(elm.find('radius').attrib['value'])
        fileName = 'inletProfile.txt'
        elm.find('path').set('value', fileName)
        self.WriteInletProfile(fileName, dt, dx, timeSteps, radius_iN, Wo, Re, epsilon)

        i = 0
        for elm in root.find('outlets').iter('outlet'):
            condition = elm.find('condition')
            if condition.attrib['type'] == 'windkessel':
                self.SetParam_Windkessel(condition, i, Wo, flowRateRatios, mulFact_R, mulFact_C)
            i = i + 1

        tree.write(outFile, encoding='utf-8', xml_declaration=True)

    def SetParam_Windkessel(self, condition, i, Wo, flowRateRatios, mulFact_R, mulFact_C):
        # Find equivalent length of the pipe
        length = np.array([9.7e-4, 9.7e-4, 1.94e-3, 9.7e-4, 9.7e-4]) # SixBranch
        if condition.attrib['subtype'] == 'GKmodel':
            radius = float(condition.find('radius').attrib['value'])
            L = np.amax(length)
        elif condition.attrib['subtype'] == 'fileGKmodel':
            area = float(condition.find('area').attrib['value'])
            radius = np.sqrt(area / PI)
            L = 10 / radius # under testing
            #condition.set('subtype', 'GKmodel')
            #condition.remove(condition.find('path'))
            #condition.remove(condition.find('area'))

        # Find resistance
        G = 8 * mu / (PI * radius**4)
        ratio = np.amax(flowRateRatios) / flowRateRatios[i]
        resistance = mulFact_R * ratio * abs(G * L)

        # Find capacitance
        omega = (Wo / radius)**2 * nu
        RC = 0.1 / omega
        capacitance = mulFact_C * RC / resistance

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
        
    def WriteInletProfile(self, fileName, dt, dx, timeSteps, radius, Wo, Re, epsilon):
        omega = (Wo / radius)**2 * nu
        Umean = Re * nu / radius
        Ma2 = (Umean * dx / dt)**2 / cs2
        if Ma2 > 0.1:
            print('Warning -- Mach number = %.3f exceeds the limit!' %(Ma2))
        #print('omega', omega)
        #print('Umean', Umean)
        #print('Ma2', Ma2)

        time = np.linspace(0, dt * timeSteps, timeSteps)
        vel = Umean * (1 + epsilon * np.cos(omega*time))

        with open(fileName, 'w') as f:
            for i in range(len(time)):
                f.write(str(time[i]) + ' ' + str(vel[i]) + '\n')