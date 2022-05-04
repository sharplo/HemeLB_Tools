import sys
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
    def __init__(self, inFile, outDir):
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
        self.P_iN = np.array([]) # pressure at inlets (mmHg)
        self.P_oUT = np.array([]) # pressure at outlets (mmHg)

        # Extract the above parameters from input.xml
        parser = ET.XMLParser(target=CommentedTreeBuilder())
        print('Reading inputs from "%s"' %(inFile))
        self.tree = ET.parse(inFile, parser)
        self.ReadInput()
        print('Finished reading inputs.')

        # Set the directory output files written to
        self.outDir = outDir

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

        # Find pressure of inlets
        if self.type_iN == 'pressure' or self.type_iN == 'yangpressure':
            for elm in root.find('inlets').iter('inlet'):
                value = elm.find('condition').find('mean').attrib['value']
                self.P_iN = np.append(self.P_iN, float(value))
        #print('P_iN', self.P_iN)

        # Find pressure of outlets
        if self.type_oUT == 'pressure' or self.type_oUT == 'yangpressure':
            for elm in root.find('outlets').iter('outlet'):
                value = elm.find('condition').find('mean').attrib['value']
                self.P_oUT = np.append(self.P_oUT, float(value))
        #sprint('P_oUT', self.P_oUT)

        # Find parameters of the Windkessel model
        if self.type_oUT == 'windkessel':
            for elm in root.find('outlets').iter('outlet'):
                condition = elm.find('condition')

                if condition.find('area') == None:
                    value = condition.find('radius').attrib['value']
                    self.radius_oUT = np.append(self.radius_oUT, float(value))
                else:
                    value = condition.find('area').attrib['value']
                    self.area_oUT = np.append(self.area_oUT, float(value))
                    # Calculate equivalent radius
                    self.radius_oUT = np.append(self.radius_oUT, np.sqrt(float(value)/PI))

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

    def WriteInput(self, fileName):
        self.tree.write(self.outDir + fileName, encoding='utf-8', xml_declaration=True)

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

    def ChangeParam(self, param_sim, param_iN, param_oUT):
        root = self.tree.getroot()

        # Change parameters in simulation
        if param_sim.get('dt') == None:
            tau = param_sim['tau']
            self.dt = cs2 * (tau - 0.5) * self.dx**2 / nu
        elif param_sim.get('tau') == None:
            self.dt = param_sim['dt']
            self.RelaxationTimeCheck()
        else:
            sys.exit('Error: dt and tau should not be specified simultaneously!')

        if param_sim.get('time') == None:
            self.timeSteps = param_sim['timeSteps']
        elif param_sim.get('timeSteps') == None:
            time = param_sim['time']
            self.timeSteps = int(np.ceil(time / self.dt))
            print('Physical end time will be', self.timeSteps * self.dt)
        else:
            sys.exit('Error: time and timeSteps should not be specified simultaneously!')

        elm = root.find('simulation')
        elm.find('step_length').set('value', '{:0.5e}'.format(self.dt))
        elm.find('steps').set('value', str(self.timeSteps))

        # Change parameters in inlets
        if self.type_iN != param_iN['type']:
            sys.exit('Error: Inlet types are different!')
        elif self.type_iN == 'velocity':
            idx = 0
            for elm in root.find('inlets').iter('inlet'):
                condition = elm.find('condition')
                self.SetParam_Velocity(condition, idx, param_iN)
                idx = idx + 1

        # Change parameters in outlets
        if self.type_oUT != param_oUT['type']:
            sys.exit('Error: Outlet types are different!')
        elif self.type_oUT == 'windkessel':
            outlets = root.find('outlets')
            geometry = param_oUT['geometry']
            maxLK = self.FindMaxLK(geometry)
            ratios = self.CalResistanceRatios(param_oUT)
            Wo = param_iN['Wo']  # from the inlet

            idx = 0
            for elm in outlets.iter('outlet'):
                condition = elm.find('condition')
                self.SetParam_Windkessel(condition, idx, param_oUT, maxLK, ratios, Wo)
                idx = idx + 1

    def SetParam_Velocity(self, condition, idx, param_iN):
        radius = self.radius_iN[idx]
        Re = param_iN['Re']

        subtype = condition.attrib['subtype']
        if subtype != param_iN['subtype']:
            print('Error: Subtypes are different at inlet %d!' %(idx))
            sys.exit()
        elif subtype == 'file':
            Wo = param_iN['Wo']
            epsilon = param_iN['epsilon']
            fileName = 'INLET' + str(idx) + '_VELOCITY.txt'
            condition.find('path').set('value', fileName)
            self.WriteInletProfile(radius, Re, Wo, epsilon, fileName)
        elif subtype == 'parabolic':
            Umax = self.CentralVelocity(radius, Re)
            self.CompressibilityErrorCheck(Umax)
            condition.find('maximum').set('value', '{:0.5e}'.format(Umax))

    def SetParam_Windkessel(self, condition, idx, param_oUT, maxLK, resistanceRatios, Wo):
        subtype = condition.attrib['subtype']
        if subtype != param_oUT['subtype']:
            if subtype == 'fileGKmodel' and param_oUT['subtype'] == 'GKmodel':
                # Change from fileGKmodel to GKmodel
                condition.set('subtype', 'GKmodel')
                condition.remove(condition.find('path'))
                condition.remove(condition.find('area'))

        # Find resistance
        resistance = param_oUT['gamma_R'] * resistanceRatios[idx] * maxLK

        # Find capacitance
        radius = self.radius_oUT[idx]
        omega = self.AngularFrequency(radius, Wo)
        RC = 1 / omega
        capacitance = param_oUT['gamma_RC'] * RC / resistance

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

    def AngularFrequency(self, radius, Wo):
        return (Wo / radius)**2 * nu

    def CentralVelocity(self, radius, Re):
        return Re * nu / (2 * radius)

    def RelaxationTimeCheck(self):
        tau = nu * self.dt / (cs2 * self.dx**2) + 0.5
        if tau < 0.55:
            sys.exit('Error: tau = %.3f falls below 0.55' %(tau))
        elif tau < 0.6:
            print('Warning: tau = %.3f falls below 0.6!' %(tau))
        elif tau > 1:
            print('Warning: tau = %.3f exceeds 1!' %(tau))
        #print('tau', tau)

    def CompressibilityErrorCheck(self, Umax):
        Ma2 = (Umax * self.dt / self.dx)**2 / cs2
        if Ma2 > 0.1:
            sys.exit('Error: Ma2 = %.3f exceeds 0.1' %(Ma2))
        elif Ma2 > 0.01:
            print('Warning: Ma2 = %.3f exceeds 0.01!' %(Ma2))
        print('Ma2', Ma2)

    def WriteInletProfile(self, radius, Re, Wo, epsilon, fileName):
        Umean = self.CentralVelocity(radius, Re)
        Umax = Umean * (1 + epsilon)
        self.CompressibilityErrorCheck(Umax)
        omega = self.AngularFrequency(radius, Wo)
        #print('Umean', Umean)
        print('omega', omega)

        time = np.linspace(0, self.dt * self.timeSteps, self.timeSteps)
        vel = Umean * (1 + epsilon * np.cos(omega * time))

        with open(self.outDir + fileName, 'w') as f:
            for i in range(len(time)):
                f.write(str(time[i]) + ' ' + str(vel[i]) + '\n')

    def CalResistanceRatios(self, param_oUT):
        flowRateRatios = param_oUT['flowRateRatios']
        if type(flowRateRatios) == list:
            pass
        elif flowRateRatios == 'Murray':
            n = param_oUT['power']
            sumRadiusCube = 0
            for radius in self.radius_oUT:
                sumRadiusCube = sumRadiusCube + float(radius)**n
            flowRateRatios = self.radius_oUT**n / sumRadiusCube
        else:
            print('flowRateRatios does not admit this option!')
        resistanceRatios = np.amax(flowRateRatios) / flowRateRatios
        print('resistanceRatios', resistanceRatios)
        return resistanceRatios

    def FindMaxLK(self, geometry):
        # Expedient solution
        if geometry == 'FiveExit_2e-4': # radii=2e-4
            lengths = np.array([9.7e-4, 9.7e-4, 1.94e-3, 9.7e-4, 9.7e-4])
        elif geometry == 'FiveExit_1e-3': # radii=1e-3
            lengths = np.array([4.83e-3, 4.83e-3, 9.67e-3, 4.83e-3, 4.83e-3])
        elif geometry == 'ArteriesLegs_5e-3': # inlet radius=5e-3
            lengths = [0.02297]*38
        elif geometry == 'ProfundaFemoris_2e-3': # inlet radius=1.88e-3
            lengths = [0.00874]*10
        elif geometry == 'ProfundaFemoris2_2e-3': # version 2
            lengths = [0.0198]*10
        else:
            print('This geometry is not registered!')

        maxLK = 0
        for idx in range(len(self.radius_oUT)):
            radius = self.radius_oUT[idx]
            K = 8 * mu / (PI * radius**4)
            LK = lengths[idx] * K
            if LK > maxLK:
                maxLK = LK
        return maxLK
