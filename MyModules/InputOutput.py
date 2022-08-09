import sys
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

# Constants
PI = 3.14159265358979323846264338327950288
mmHg = 133.3223874 # Pa
cs2 = 1.0 / 3.0 # speed of sound squared (lattice unit)
mu = 0.004 # dynamic viscosity (Pa*s)
rho = 1000 # fluid density (kg/m^3)
PoissonsRatio = 0.5 # Poisson's ratio of blood vessels (dimensionless)
WallToLumenRatio = 0.1 # wall-to-lumen ratio of blood vessels (dimensionless)

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
        self.subtype_iN = None # subtype of boundary condition in inlets
        self.type_oUT = None # type of boundary condition in outlets
        self.subtype_oUT = None # subtype of boundary condition in outlets

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

        # Find the type and subtype of boundary conditions
        self.type_iN = root.find('inlets').find('inlet').find('condition').attrib['type']
        self.subtype_iN = root.find('inlets').find('inlet').find('condition').attrib['subtype']
        self.type_oUT = root.find('outlets').find('outlet').find('condition').attrib['type']
        self.subtype_oUT = root.find('outlets').find('outlet').find('condition').attrib['subtype']
        #print('type_iN', self.type_iN)
        #print('subtype_iN', self.subtype_iN)
        #print('type_oUT', self.type_oUT)
        #print('subtype_oUT', self.subtype_oUT)

        # Find the radius and area of inlets
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

        # Find the pressure of inlets
        if self.type_iN == 'pressure' or self.type_iN == 'yangpressure':
            for elm in root.find('inlets').iter('inlet'):
                value = elm.find('condition').find('mean').attrib['value']
                self.P_iN = np.append(self.P_iN, float(value))
        #print('P_iN', self.P_iN)

        # Find the parmeters in the pressure condition for outlets
        if self.type_oUT == 'pressure' or self.type_oUT == 'yangpressure':
            for elm in root.find('outlets').iter('outlet'):
                condition = elm.find('condition')

                if self.subtype_oUT == 'cosine' or self.subtype_oUT == 'file':
                    value = condition.find('mean').attrib['value']
                    self.P_oUT = np.append(self.P_oUT, float(value))
                elif self.subtype_oUT == 'WK' or self.subtype_oUT == 'fileWK':

                    if condition.find('R') == None:
                        self.resistance = np.append(self.resistance, None)
                    else:
                        value = condition.find('R').attrib['value']
                        if value == 'CHANGE':
                            self.resistance = np.append(self.resistance, None)
                        else:
                            self.resistance = np.append(self.resistance, float(value))
                    
                    if condition.find('C') == None:
                        self.capacitance = np.append(self.capacitance, None)
                    else:
                        value = condition.find('C').attrib['value']
                        if value == 'CHANGE':
                            self.capacitance = np.append(self.capacitance, None)
                        else:
                            self.capacitance = np.append(self.capacitance, float(value))
                    
                    if condition.find('area') == None:
                        value = condition.find('radius').attrib['value']
                        self.radius_oUT = np.append(self.radius_oUT, float(value))
                    else:
                        value = condition.find('area').attrib['value']
                        self.area_oUT = np.append(self.area_oUT, float(value))
                        # Calculate equivalent radius
                        self.radius_oUT = np.append(self.radius_oUT, np.sqrt(float(value)/PI))
        #print('P_oUT', self.P_oUT)
        #print('resistance', self.resistance)
        #print('capacitance', self.capacitance)
        #print('radius_oUT', self.radius_oUT)
        #print('area_oUT', self.area_oUT)

    def WriteInput(self, fileName):
        self.tree.write(self.outDir + fileName, encoding='utf-8', xml_declaration=True)

    def RescaleSize(self, scale):
        root = self.tree.getroot()

        # Rescale voxel size
        value = self.dx * scale
        root.find('simulation').find('voxel_size').set('value', '{:0.15e}'.format(value))

        # Rescale radii
        for elm in root.iter('radius'):
            value = float(elm.attrib['value'])
            value = value * scale
            elm.set('value', '{:0.15e}'.format(value))
        
        # Rescale areas
        for elm in root.iter('area'):
            value = float(elm.attrib['value'])
            value = value * scale**2
            elm.set('value', '{:0.15e}'.format(value))

    def ChangeParam(self, param_sim, param_iN, param_oUT):
        root = self.tree.getroot()

        # Change parameters in simulation
        elm = root.find('simulation')
        self.SetParam_Time(elm, param_sim)
        if param_sim.get('YoungsModulus') != None \
            and param_sim.get('BoundaryVelocityRatio') != None:
            self.SetParam_ElasticWall(elm, param_sim)

        # Change parameters in inlets
        if self.type_iN != param_iN['type']:
            sys.exit('Error: Inlet types are different!')
        elif self.subtype_iN != param_iN['subtype']:
            sys.exit('Error: Inlet subtypes are different!')
        elif self.type_iN == 'velocity':
            idx = 0
            for elm in root.find('inlets').iter('inlet'):
                condition = elm.find('condition')
                if self.subtype_iN == 'file':
                    self.SetParam_FileVelocity(condition, idx, param_iN)
                elif self.subtype_iN == 'parabolic':
                    self.SetParam_ParabolicVelocity(condition, idx, param_iN)
                elif self.subtype_iN == 'womersley':
                    self.SetParam_WomersleyVelocity(condition, idx, param_iN)
                idx = idx + 1

        # Change parameters in outlets
        if self.type_oUT != param_oUT['type']:
            sys.exit('Error: Outlet types are different!')
        elif self.subtype_oUT != param_oUT['subtype']:
            sys.exit('Error: Outlet subtypes are different!')
        elif self.type_oUT == 'pressure' or self.type_oUT == 'yangpressure':
            # Obtain values used in common
            if self.subtype_oUT == 'WK' or self.subtype_oUT == 'fileWK':
                geometry = param_oUT['geometry']
                maxLK = self.FindMaxLK(geometry)
                ratios = self.CalResistanceRatios(param_oUT)
                Wo = param_iN['Wo'] # from the inlet
            
            idx = 0
            for elm in root.find('outlets').iter('outlet'):
                condition = elm.find('condition')
                if self.subtype_oUT == 'WK' or self.subtype_oUT == 'fileWK':
                    self.SetParam_Windkessel(condition, idx, param_oUT, maxLK, ratios, Wo)
                idx = idx + 1

    def SetParam_Time(self, elm, param_sim):
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

        elm.find('step_length').set('value', '{:0.15e}'.format(self.dt))
        elm.find('steps').set('value', str(self.timeSteps))

    def SetParam_ElasticWall(self, elm, param_sim):
        E = param_sim['YoungsModulus']
        stiffness = E * WallToLumenRatio / (1 - PoissonsRatio**2) / self.radius_iN[0]
        stiffness = stiffness * self.dt**2 / (rho * self.dx)
        F = param_sim['BoundaryVelocityRatio']

        # Set elastic wall stiffness
        if elm.find('elastic_wall_stiffness') == None:
            value = ET.Element('elastic_wall_stiffness', {'units':'lattice', 'value':'{:0.15e}'.format(stiffness)})
            value.tail = "\n" + 2 * "  "
            elm.insert(3, value)
        else:
            elm.find('elastic_wall_stiffness').set('value', '{:0.15e}'.format(stiffness))

        # Set boundary velocity ratio
        if elm.find('boundary_velocity_ratio') == None:
            value = ET.Element('boundary_velocity_ratio', {'units':'lattice', 'value':'{:0.15e}'.format(F)})
            value.tail = "\n" + 2 * "  "
            elm.insert(4, value)
        else:
            elm.find('boundary_velocity_ratio').set('value', '{:0.15e}'.format(F))

    def SetParam_FileVelocity(self, condition, idx, param_iN):
        fileName = 'INLET' + str(idx) + '_VELOCITY.txt'
        condition.find('path').set('value', fileName)
        
        radius = self.radius_iN[idx]
        Re = param_iN['Re']
        Wo = param_iN['Wo']
        epsilon = param_iN['epsilon']

        Umax = self.CentralVelocity(radius, Re)
        Umean = Umax / (1 + epsilon)
        self.CompressibilityErrorCheck(Umax)
        time = np.linspace(0, self.dt * self.timeSteps, self.timeSteps)
        #print('Umax', Umax)
        #print('Umean', Umean)

        if param_iN.get('profile') == None:
            omega = self.AngularFrequency(radius, Wo)
            vel = self.SinusoidalWave(Umean, epsilon, omega, time)
        else:
            profile = param_iN['profile']
            period = self.OscillationPeriod(radius, Wo)
            vel = self.Heartbeat(profile, period, Umax, time)
        
        with open(self.outDir + fileName, 'w') as f:
            for i in range(len(time)):
                f.write(str(time[i]) + ' ' + str(vel[i]) + '\n')

    def SetParam_ParabolicVelocity(self, condition, idx, param_iN):
        radius = self.radius_iN[idx]
        Re = param_iN['Re']
        Umax = self.CentralVelocity(radius, Re)
        self.CompressibilityErrorCheck(Umax)
        condition.find('maximum').set('value', '{:0.15e}'.format(Umax))

    def SetParam_WomersleyVelocity(self, condition, idx, param_iN):
        radius = self.radius_iN[idx]
        Re = param_iN['Re']
        Wo = param_iN['Wo']
        Umax = self.CentralVelocity(radius, Re)
        self.CompressibilityErrorCheck(Umax)
        G = self.PressureGradient(radius, Umax)
        period = self.OscillationPeriod(radius, Wo)
        condition.find('pressure_gradient_amplitude').set('value', '{:0.15e}'.format(G / mmHg))
        condition.find('period').set('value', '{:0.15e}'.format(period))
        condition.find('womersley_number').set('value', '{:0.15e}'.format(Wo))

    def SetParam_Windkessel(self, condition, idx, param_oUT, maxLK, resistanceRatios, Wo):
        if param_oUT['subtype'] == 'WK':
            condition.remove(condition.find('path'))

        # Find resistance
        resistance = param_oUT['gamma_R'] * resistanceRatios[idx] * maxLK

        # Find capacitance
        # Note: it is crucial to use the same Wo as the inlet instead of omega
        radius = self.radius_oUT[idx]
        omega = self.AngularFrequency(radius, Wo)
        RC = 1 / omega
        capacitance = param_oUT['gamma_RC'] * RC / resistance

        # Set R and C
        if condition.find('R') == None:
            elm = ET.Element('R', {'units':'kg/m^4*s', 'value':'{:0.15e}'.format(resistance)})
            elm.tail = "\n" + 4 * "  "
            condition.insert(1, elm)
        else:
            condition.find('R').set('value', '{:0.15e}'.format(resistance))

        if condition.find('C') == None:
            elm = ET.Element('C', {'units':'m^4*s^2/kg', 'value':'{:0.15e}'.format(capacitance)})
            elm.tail = "\n" + 4 * "  "
            condition.insert(2, elm)
        else:
            condition.find('C').set('value', '{:0.15e}'.format(capacitance))

    def AngularFrequency(self, radius, Wo):
        omega = (Wo / radius)**2 * nu
        print('omega', omega)
        return omega

    def OscillationPeriod(self, radius, Wo):
        return 2 * PI / self.AngularFrequency(radius, Wo)

    def CentralVelocity(self, radius, Re):
        return Re * nu / (2 * radius)

    def PressureGradient(self, radius, Umax):
        return 4 * mu * Umax / (radius * radius)

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

    def SinusoidalWave(self, Umean, epsilon, omega, time):
        return Umean * (1 - epsilon * np.cos(omega * time))

    def Heartbeat(self, profile, period, Umax, time):
        df = pd.read_csv(profile, sep=' ', header=None, names=['time', 'Umax'])
        # Scale the waveform to match the required period
        df['time'] = df['time'] * period / df['time'].iloc[-1]
        # Scale the waveform to match the required Umax
        df['Umax'] = df['Umax'] * Umax / df['Umax'].max()
        # Roll the waveform such that it starts in the diastolic period
        df['Umax'] = np.roll(df['Umax'], int(df.shape[0] / 4))
        # Construct an interpolation function
        func = interp1d(df['time'], df['Umax'], 'cubic')
        # Calculate the equivalent time in the cardiac cycle
        eqTime = time % df['time'].iloc[-1]
        # Interpolate the velocity at the equivalent time
        vel = func(eqTime)
        return vel

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
        elif geometry == 'AortaElastic_5e-3': # inlet radius=5.47e-3
            lengths = [0.00853]*4
        elif geometry == '0130_0000_9e-3': # inlet radius=9.28e-3
            lengths = [0.0191]*4
        elif geometry == '0003_0001_8e-3': # inlet radius=8.40e-3
            lengths = [0.0462]*17
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
