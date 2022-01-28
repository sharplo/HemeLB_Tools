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

class InputOutput():
    def __init__(self, inFile):
        self.type_iN = None # type of boundary condition in inlets
        self.type_oUT = None # type of boundary condition in outlets

        self.dt = None # step_length (s)
        self.dx = None # voxel_size (m)
        self.normal_iN = np.array([]) # normal vector of inlets (no unit)
        self.position_iN = np.array([]) # position vector of inlets (lattice unit)
        self.normal_oUT = np.array([]) # normal vector of outlets (no unit)
        self.position_oUT = np.array([]) # position vector of inlets (lattice unit)
        self.radius_iN = np.array([]) # radius of inlets (m)
        self.area_iN = np.array([]) # area of inlets (m^2)
        self.radius_oUT = np.array([]) # radius of outlets (m)
        self.area_oUT = np.array([]) # area of outlets (m^2)
        self.resistance = np.array([]) # resistance of the Windkessel model (kg/m^4*s)
        self.capacitance = np.array([]) # capacitance of the Windkessel model (m^4*s^2/kg)

        # Extract the above parameters from input.xml
        parser = ET.XMLParser(target=CommentedTreeBuilder())
        print('Reading inputs from "%s"' %(inFile))
        self.tree = ET.parse(inFile, parser)
        self.ReadInput()
        print('Finished reading inputs.')

    def ReadInput(self):
        root = self.tree.getroot()

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

        # Find the type of boundary conditions
        self.type_iN = root.find('inlets').find('inlet').find('condition').attrib['type']
        self.type_oUT = root.find('outlets').find('outlet').find('condition').attrib['type']
        #print('type_iN', self.type_iN)
        #print('type_oUT', self.type_oUT)

        # Find radius and area of inlets
        if self.type_iN == 'velocity':
            for elm in root.find('inlets').iter('inlet'):
                condition = elm.find('condition')

                value = condition.find('radius').attrib['value']
                self.radius_iN = np.append(self.radius_iN, float(value))

                if condition.find('area') != None:
                    value = condition.find('area').attrib['value']
                    self.area_iN = np.append(self.area_iN, float(value))
        #print('radius_iN', self.radius_iN)
        #print('area_iN', self.area_iN)

        # Find parameters of the Windkessel model
        if self.type_oUT == 'windkessel':
            for elm in root.find('outlets').iter('outlet'):
                condition = elm.find('condition')

                value = condition.find('radius').attrib['value']
                self.radius_oUT = np.append(self.radius_oUT, float(value))

                if condition.find('area') != None:
                    value = condition.find('area').attrib['value']
                    self.area_oUT = np.append(self.area_oUT, float(value))

                if condition.find('R') != None:
                    value = condition.find('R').attrib['value']
                    if value == 'CHANGE':
                        self.resistance = np.append(self.resistance, None)
                    else:
                        self.resistance = np.append(self.resistance, float(value))

                if condition.find('C') != None:
                    value = condition.find('C').attrib['value']
                    if value == 'CHANGE':
                        self.capacitance = np.append(self.capacitance, None)
                    else:
                        self.capacitance = np.append(self.capacitance, float(value))
        #print('radius_oUT', self.radius_oUT)
        #print('area_oUT', self.area_oUT)
        #print('resistance', self.resistance)
        #print('capacitance', self.capacitance)

    def WriteInput(self, outFile):
        self.tree.write(outFile, encoding='utf-8', xml_declaration=True)

    def RescaleSize(self, scale):
        root = self.tree.getroot()

        # Rescale voxel size
        value = self.dx * scale
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

    def ChangeParam(self, tau, timeSteps, Wo, Re, epsilon, geometry, flowRateRatios, gamma_R, gamma_C):
        root = self.tree.getroot()

        # Change parameters in simulation
        elm = root.find('simulation')
        self.dt = cs2 * (tau - 0.5) * self.dx**2 / nu
        elm.find('step_length').set('value', '{:0.5e}'.format(self.dt))
        elm.find('steps').set('value', str(timeSteps))

        # Change parameters in inlets
        if self.type_iN == 'velocity':
            elm = root.find('inlets')[0].find('condition')
            radius_iN = self.radius_iN[0]
            fileName = 'INLET0_VELOCITY.txt'
            elm.find('path').set('value', fileName)
            self.WriteInletProfile(fileName, timeSteps, radius_iN, Wo, Re, epsilon)

        # Change parameters in outlets
        if self.type_oUT == 'windkessel':
            outlets = root.find('outlets')
            maxGL = self.FindMaxGL(geometry, outlets)
            ratios = self.CalResistanceRatios(flowRateRatios)
            idx = 0
            for elm in outlets.iter('outlet'):
                condition = elm.find('condition')
                self.SetParam_Windkessel(condition, idx, Wo, ratios, maxGL, gamma_R, gamma_C)
                idx = idx + 1

    def SetParam_Windkessel(self, condition, idx, Wo, resistanceRatios, maxGL, gamma_R, gamma_C):
        # Find radius of the pipe
        if condition.attrib['subtype'] == 'GKmodel':
            radius = self.radius_oUT[idx]
        elif condition.attrib['subtype'] == 'fileGKmodel':
            area = self.area_oUT[idx]
            radius = np.sqrt(area / PI)

        # Find resistance
        resistance = gamma_R * resistanceRatios[idx] * maxGL

        # Find capacitance
        omega = (Wo / radius)**2 * nu
        RC = 1 / omega
        capacitance = gamma_C * RC / resistance

        # Set R and C
        if condition.find('R') == None:
            elm = ET.Element('R', {'units':'kg/m^4*s', 'value':'{:0.5e}'.format(resistance)})
            elm.tail = "\n" + 4 * "  "
            condition.insert(1, elm)
        else:
            condition.find('R').set('value', '{:0.5e}'.format(resistance))

        if condition.find('C') == None:
            elm = ET.Element('C', {'units':'m^4*s^2/kg', 'value':'{:0.5e}'.format(capacitance)})
            elm.tail = "\n" + 4 * "  "
            condition.insert(2, elm)
        else:
            condition.find('C').set('value', '{:0.5e}'.format(capacitance))

        # Change from fileGKmodel to GKmodel
        #if condition.attrib['subtype'] == 'fileGKmodel':
        #    condition.set('subtype', 'GKmodel')
        #    condition.remove(condition.find('path'))
        #    condition.remove(condition.find('area'))
        
    def WriteInletProfile(self, fileName, timeSteps, radius, Wo, Re, epsilon):
        omega = (Wo / radius)**2 * nu
        Umean = Re * nu / (2 * radius)
        Umax = Umean * (1 + epsilon)
        Ma2 = (Umax * self.dt / self.dx)**2 / cs2
        if Ma2 > 0.01:
            print('Warning -- Ma2 = %.3f exceeds the limit!' %(Ma2))
        print('omega', omega)
        print('Umean', Umean)
        print('Ma2', Ma2)

        time = np.linspace(0, self.dt * timeSteps, timeSteps)
        vel = Umean * (1 + epsilon * np.cos(omega*time))

        with open(fileName, 'w') as f:
            for i in range(len(time)):
                f.write(str(time[i]) + ' ' + str(vel[i]) + '\n')

    def CalResistanceRatios(self, flowRateRatios):
        if type(flowRateRatios) == list:
            pass
        elif flowRateRatios == 'Murray':
            sumRadiusCube = 0
            for radius in self.radius_oUT:
                sumRadiusCube = sumRadiusCube + float(radius)**3
            flowRateRatios = self.radius_oUT**3 / sumRadiusCube
        else:
            print('flowRateRatios does not admit this option!')
        resistanceRatios = np.amax(flowRateRatios) / flowRateRatios
        print('resistanceRatios', resistanceRatios)
        return resistanceRatios

    def FindMaxGL(self, geometry, outlets):
        # Expedient solution
        if geometry == 'FiveExit_2e-4': # radii=2e-4
            lengths = np.array([9.7e-4, 9.7e-4, 1.94e-3, 9.7e-4, 9.7e-4])
        elif geometry == 'FiveExit_1e-3': # radii=1e-3
            lengths = np.array([4.83e-3, 4.83e-3, 9.67e-3, 4.83e-3, 4.83e-3])
        elif geometry == 'ArteriesLegs_5e-3':  # inlet radius=5e-3
            lengths = [0.02297]*38
        elif geometry == 'InferiorGluteal_2e-3': # inlet radius=1.88e-3
            lengths = [0.00874]*10
        else:
            print('This geometry is not registered!')

        idx = 0
        maxGL = 0
        for elm in outlets.iter('outlet'):
            condition = elm.find('condition')
            if condition.attrib['subtype'] == 'GKmodel':
                radius = self.radius_oUT[idx]
            elif condition.attrib['subtype'] == 'fileGKmodel':
                area = self.area_oUT[idx]
                radius = np.sqrt(area / PI)
            G = 8 * mu / (PI * radius**4)
            GL = G * lengths[idx]
            if GL > maxGL:
                maxGL = GL
            idx = idx + 1
        return maxGL