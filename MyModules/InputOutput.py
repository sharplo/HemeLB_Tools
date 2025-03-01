import os
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
WallThickness = 1.775e-3 # thickness of vessel walls (m)
medianRadius = 2.015e-3 # median radius of blood vessels (m)

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
        self.kernel = None # collision operator
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
        self.Rc = np.array([]) # characteristic resistance of the Windkessel model (kg/m^4*s)
        self.Rp = np.array([]) # peripheral resistance of the Windkessel model (kg/m^4*s)
        self.Cp = np.array([]) # peripheral capacitance of the Windkessel model (m^4*s^2/kg)
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

                if condition.find('area') is None:
                    value = condition.find('radius').attrib['value']
                    self.radius_iN = np.append(self.radius_iN, float(value))
                else:
                    value = condition.find('area').attrib['value']
                    self.area_iN = np.append(self.area_iN, float(value))
                    # Calculate equivalent radius
                    self.radius_iN = np.append(self.radius_iN, np.sqrt(float(value)/PI))
        #print('radius_iN', self.radius_iN)
        #print('area_iN', self.area_iN)

        # Find the pressure of inlets
        if self.type_iN == 'pressure' or self.type_iN == 'yangpressure':
            for elm in root.find('inlets').iter('inlet'):
                condition = elm.find('condition')
                if self.subtype_iN == 'cosine':
                    value = condition.find('mean').attrib['value']
                    self.P_iN = np.append(self.P_iN, float(value))
        #print('P_iN', self.P_iN)

        # Find the parmeters in the pressure condition for outlets
        if self.type_oUT == 'pressure' or self.type_oUT == 'yangpressure':
            for elm in root.find('outlets').iter('outlet'):
                condition = elm.find('condition')

                if self.subtype_oUT == 'cosine':
                    value = condition.find('mean').attrib['value']
                    self.P_oUT = np.append(self.P_oUT, float(value))
                elif self.subtype_oUT == 'WK2':

                    if condition.find('R') is None:
                        self.Rp = np.append(self.Rp, None)
                    else:
                        value = condition.find('R').attrib['value']
                        if value == 'CHANGE':
                            self.Rp = np.append(self.Rp, None)
                        else:
                            self.Rp = np.append(self.Rp, float(value))
                    
                    if condition.find('C') is None:
                        self.Cp = np.append(self.Cp, None)
                    else:
                        value = condition.find('C').attrib['value']
                        if value == 'CHANGE':
                            self.Cp = np.append(self.Cp, None)
                        else:
                            self.Cp = np.append(self.Cp, float(value))
                    
                    if condition.find('area') is None:
                        value = condition.find('radius').attrib['value']
                        self.radius_oUT = np.append(self.radius_oUT, float(value))
                    else:
                        value = condition.find('area').attrib['value']
                        self.area_oUT = np.append(self.area_oUT, float(value))
                        # Calculate equivalent radius
                        self.radius_oUT = np.append(self.radius_oUT, np.sqrt(float(value)/PI))
        #print('P_oUT', self.P_oUT)
        #print('Rp', self.Rp)
        #print('Cp', self.Cp)
        #print('radius_oUT', self.radius_oUT)
        #print('area_oUT', self.area_oUT)

                elif self.subtype_oUT == 'WK3':

                    if condition.find('Rc') is None:
                        self.Rc = np.append(self.Rc, None)
                    else:
                        value = condition.find('Rc').attrib['value']
                        if value == 'CHANGE':
                            self.Rc = np.append(self.Rc, None)
                        else:
                            self.Rc = np.append(self.Rc, float(value))

                    if condition.find('Rp') is None:
                        self.Rp = np.append(self.Rp, None)
                    else:
                        value = condition.find('Rp').attrib['value']
                        if value == 'CHANGE':
                            self.Rp = np.append(self.Rp, None)
                        else:
                            self.Rp = np.append(self.Rp, float(value))

                    if condition.find('Cp') is None:
                        self.Cp = np.append(self.Cp, None)
                    else:
                        value = condition.find('Cp').attrib['value']
                        if value == 'CHANGE':
                            self.Cp = np.append(self.Cp, None)
                        else:
                            self.Cp = np.append(self.Cp, float(value))

                    if condition.find('area') is None:
                        value = condition.find('radius').attrib['value']
                        self.radius_oUT = np.append(self.radius_oUT, float(value))
                    else:
                        value = condition.find('area').attrib['value']
                        self.area_oUT = np.append(self.area_oUT, float(value))
                        # Calculate equivalent radius
                        self.radius_oUT = np.append(self.radius_oUT, np.sqrt(float(value)/PI))
        #print('P_oUT', self.P_oUT)
        #print('Rc', self.Rc)
        #print('Rp', self.Rp)
        #print('Cp', self.Cp)
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

    def ChangeParam(self, param_sim, param_iN, param_oUT, geometryPath=None):
        root = self.tree.getroot()

        # Change parameters in simulation
        print('\nSetting parameters in simulation...')
        elm = root.find('simulation')
        Re = param_iN['Re'] # from inlet
        self.SetParam_Time(elm, param_sim, Re)
        self.SetParam_RelaxationParameter(elm, param_sim)
        if param_sim.get('YoungsModulus') is not None \
            and param_sim.get('BoundaryVelocityRatio') is not None:
            self.SetParam_ElasticWall(elm, param_sim)

        # Change parameters in inlets
        print('\nSetting parameters in inlets...')
        if self.type_iN != param_iN['type']:
            sys.exit('Error: Inlet types are different!')
        elif self.subtype_iN != param_iN['subtype']:
            sys.exit('Error: Inlet subtypes are different!')
        elif self.type_iN == 'velocity':
            maxSpeed = self.CalMaxSpeed(param_iN, Re)
            idx = 0
            for elm in root.find('inlets').iter('inlet'):
                condition = elm.find('condition')
                if self.subtype_iN == 'file':
                    self.SetParam_FileVelocity(condition, idx, param_iN, maxSpeed)
                elif self.subtype_iN == 'parabolic':
                    self.SetParam_ParabolicVelocity(condition, idx, param_iN, maxSpeed)
                elif self.subtype_iN == 'womersley':
                    self.SetParam_WomersleyVelocity(condition, idx, param_iN, maxSpeed)
                idx = idx + 1

        # Change parameters in outlets
        print('\nSetting parameters in outlets...')
        if self.type_oUT != param_oUT['type']:
            sys.exit('Error: Outlet types are different!')
        elif self.subtype_oUT != param_oUT['subtype']:
            sys.exit('Error: Outlet subtypes are different!')
        elif self.type_oUT == 'pressure' or self.type_oUT == 'yangpressure':
            # Obtain values used in common
            if self.subtype_oUT == 'WK2':
                geometry = param_oUT['geometry']
                maxLK = self.FindMaxLK(geometry)
                ratios = self.CalResistanceRatios(param_oUT)
            
            idx = 0
            for elm in root.find('outlets').iter('outlet'):
                condition = elm.find('condition')
                if self.subtype_oUT == 'WK2':
                    if param_iN.get('Wo') is not None:
                        Wo = param_iN['Wo'] # from the inlet
                        omega = self.AngularFrequency(self.radius_iN[0], Wo)
                    else:
                        omega = PI / self.radius_oUT[idx]
                    self.SetParam_Windkessel(condition, idx, param_oUT, maxLK, ratios, omega)
                idx = idx + 1

        # Change parameters in properties
        print('\nSetting parameters in properties...')
        if param_iN.get('Wo') is None:
            self.stepsPerPeriod = int(self.timeSteps / 10)
        else:
            period = self.OscillationPeriod(self.radius_iN[0], param_iN['Wo'])
            self.stepsPerPeriod = int(period / self.dt)
            print('period %lf s (%d steps)' %(period, self.stepsPerPeriod))

        for elm in root.find('properties').iter('propertyoutput'):
            self.SetParam_OutputPeriod(elm)

        # Make paths to be absolute paths
        if geometryPath is not None:
            elm = root.find('geometry').find('datafile')
            if not os.path.isabs(elm.get('path')):
                elm.set('path', geometryPath + elm.get('path'))
            for elm in root.find('outlets').iter('path'):
                if not os.path.isabs(elm.get('value')):
                    elm.set('value', geometryPath + elm.get('value'))

    def SetParam_Time(self, elm, param_sim, Re):
        self.kernel = param_sim['kernel']
        if self.kernel == 'LBGK' or self.kernel == 'TRT':
            if param_sim.get('dt') is None:
                tau = param_sim['tau']
                self.dt = cs2 * (tau - 0.5) * self.dx**2 / nu
            elif param_sim.get('tau') is None:
                self.dt = param_sim['dt']
            else:
                sys.exit('Error: dt and tau should not be specified simultaneously!')
            self.RelaxationTimeCheck()
        elif self.kernel == 'MRT':
            if self.type_iN == 'velocity':
                print('Note: since MRT is used, tau determines dt only.')
                # Find the characteristic velocity in the physical unit
                radius = self.radius_iN[0] # assuming inlet 0 is in the largest vessel
                Umax = self.CentralVelocity(radius, Re)
                # Calculate the time step size such that the maximum Ma2 is 0.002
                self.dt = np.sqrt(0.002 * cs2) * self.dx / Umax
            else:
                sys.exit('Error: Please use the velocity BC for the inlet along with MRT.')
        else:
            sys.exit('Error: The prescribed kernel is not registered!')

        if param_sim.get('time') is None:
            self.timeSteps = param_sim['timeSteps']
        elif param_sim.get('timeSteps') is None:
            time = param_sim['time']
            self.timeSteps = int(np.ceil(time / self.dt))
            print('Physical end time will be', self.timeSteps * self.dt)
        else:
            sys.exit('Error: time and timeSteps should not be specified simultaneously!')

        elm.find('step_length').set('value', '{:0.15e}'.format(self.dt))
        elm.find('steps').set('value', str(self.timeSteps))

    def SetParam_RelaxationParameter(self, elm, param_sim):
        self.kernel = param_sim['kernel']
        if self.kernel == 'LBGK':
            return
        elif self.kernel == 'TRT':
            if param_sim.get('relaxationParameter') is not None:
                relaxationParameter = param_sim['relaxationParameter']
            else:
                relaxationParameter = 3 / 16
                print('Warning: The relaxation parameter is set to the default value.')
        elif self.kernel == 'MRT':
            relaxationParameter = nu * self.dt / (cs2 * self.dx**2) + 0.5
            relaxationParameter = 1 / relaxationParameter
        else:
            sys.exit('Error: The prescribed kernel is not registered!')

        # Set relaxation parameter
        if elm.find('relaxation_parameter') is None:
            value = ET.Element('relaxation_parameter', {'units':'lattice', 'value':'{:0.15e}'.format(relaxationParameter)})
            value.tail = "\n" + 2 * "  "
            elm.insert(2, value)
        else:
            elm.find('relaxation_parameter').set('value', '{:0.15e}'.format(relaxationParameter))

    def SetParam_ElasticWall(self, elm, param_sim):
        E = param_sim['YoungsModulus']
        stiffness = E * WallThickness / (1 - PoissonsRatio**2) / medianRadius**2
        stiffness = stiffness * self.dt**2 / (rho * self.dx)
        F = param_sim['BoundaryVelocityRatio']

        # Set elastic wall stiffness
        if elm.find('elastic_wall_stiffness') is None:
            value = ET.Element('elastic_wall_stiffness', {'units':'lattice', 'value':'{:0.15e}'.format(stiffness)})
            value.tail = "\n" + 2 * "  "
            elm.insert(3, value)
        else:
            elm.find('elastic_wall_stiffness').set('value', '{:0.15e}'.format(stiffness))

        # Set boundary velocity ratio
        if elm.find('boundary_velocity_ratio') is None:
            value = ET.Element('boundary_velocity_ratio', {'units':'lattice', 'value':'{:0.15e}'.format(F)})
            value.tail = "\n" + 2 * "  "
            elm.insert(4, value)
        else:
            elm.find('boundary_velocity_ratio').set('value', '{:0.15e}'.format(F))

    def SetParam_FileVelocity(self, condition, idx, param_iN, maxSpeed):
        fileName = 'INLET' + str(idx) + '_VELOCITY.txt'
        condition.find('path').set('value', fileName)
        
        radius = self.radius_iN[idx]
        Wo = param_iN['Wo']
        Umax = maxSpeed[idx]
        self.CompressibilityErrorCheck(Umax)
        print('Umax', Umax)

        if param_iN.get('profile') is None:
            epsilon = param_iN['epsilon']
            Umean = Umax / (1 + epsilon)
            omega = self.AngularFrequency(radius, Wo)
            time = np.linspace(0, self.dt * self.timeSteps, self.timeSteps)
            vel = self.SinusoidalWave(Umean, epsilon, omega, time)
        else:
            # Reconstruct the given profile and add a warm-up period
            period = self.OscillationPeriod(radius, Wo)
            timeSteps = int(1000 * self.dt * self.timeSteps / period) # 1000 points per period
            time = np.linspace(period, self.dt * self.timeSteps, timeSteps)
            vel = self.Heartbeat(param_iN, period, Umax, time)
            time = np.insert(time, 0, [0, 0.618 * period]) # 0.618 is arbitrary
            vel = np.insert(vel, 0, [0, vel[0]])

        with open(self.outDir + fileName, 'w') as f:
            for i in range(len(time)):
                f.write(str(time[i]) + ' ' + str(vel[i]) + '\n')

    def SetParam_ParabolicVelocity(self, condition, idx, param_iN, maxSpeed):
        Umax = maxSpeed[idx]
        self.CompressibilityErrorCheck(Umax)
        condition.find('maximum').set('value', '{:0.15e}'.format(Umax))

    def SetParam_WomersleyVelocity(self, condition, idx, param_iN, maxSpeed):
        radius = self.radius_iN[idx]
        Wo = param_iN['Wo']
        Umax = maxSpeed[idx]
        self.CompressibilityErrorCheck(Umax)
        G = self.PressureGradient(radius, Umax)
        period = self.OscillationPeriod(radius, Wo)
        condition.find('pressure_gradient_amplitude').set('value', '{:0.15e}'.format(G / mmHg))
        condition.find('period').set('value', '{:0.15e}'.format(period))
        condition.find('womersley_number').set('value', '{:0.15e}'.format(Wo))

    def SetParam_Windkessel(self, condition, idx, param_oUT, maxLK, resistanceRatios, omega):
        # Find resistance
        resistance = param_oUT['gamma_R'] * resistanceRatios[idx] * maxLK

        # Find capacitance
        RC = 1 / omega
        capacitance = param_oUT['gamma_RC'] * RC / resistance

        # Set R and C
        if condition.find('R') is None:
            elm = ET.Element('R', {'units':'kg/m^4*s', 'value':'{:0.15e}'.format(resistance)})
            elm.tail = "\n" + 4 * "  "
            condition.insert(1, elm)
        else:
            condition.find('R').set('value', '{:0.15e}'.format(resistance))

        if condition.find('C') is None:
            elm = ET.Element('C', {'units':'m^4*s^2/kg', 'value':'{:0.15e}'.format(capacitance)})
            elm.tail = "\n" + 4 * "  "
            condition.insert(2, elm)
        else:
            condition.find('C').set('value', '{:0.15e}'.format(capacitance))

    def SetParam_OutputPeriod(self, elm):
        geometry = elm.find('geometry').attrib['type']
        if geometry == 'whole':
            elm.set('period', str(self.stepsPerPeriod))
        else:
            elm.set('period', str(int(self.stepsPerPeriod / 20)))

    def AngularFrequency(self, radius, Wo):
        omega = (Wo / radius)**2 * nu
        print('omega', omega, 'rad/s')
        return omega

    def OscillationPeriod(self, radius, Wo):
        period = 2 * PI / self.AngularFrequency(radius, Wo)
        return period

    def CentralVelocity(self, radius, Re):
        return Re * nu / (2 * radius)

    def PressureGradient(self, radius, Umax):
        return 4 * mu * Umax / (radius * radius)

    def RelaxationTimeCheck(self):
        tau = nu * self.dt / (cs2 * self.dx**2) + 0.5
        if tau < 0.51:
            sys.exit('Error: tau = %.3f falls below 0.51!' %(tau))
        elif tau < 0.55:
            print('Warning: tau = %.3f falls below 0.55!' %(tau))
        elif tau > 1:
            print('Warning: tau = %.3f exceeds 1!' %(tau))
        #print('tau', tau)

    def CalMaxSpeed(self, param_iN, Re):
        if self.radius_iN.shape[0] > 1:
            try:
                flowRateRatios = np.array(param_iN['flowRateRatios'])
            except:
                print('Error: flowRateRatios is required!')
            if self.radius_iN.shape != flowRateRatios.shape:
                sys.exit('Error: Invalid length of flowRateRatios!')
            ref = np.argmax(flowRateRatios)
            radius = self.radius_iN
            # Q_i / Q_j = (r_i^2)u_i / (r_j^2)u_j
            velRatios = (flowRateRatios / flowRateRatios[ref]) * (radius[ref] / radius)**2
            maxSpeed = self.CentralVelocity(radius[ref], Re) * velRatios
        else:
            maxSpeed = np.atleast_1d(self.CentralVelocity(self.radius_iN[0], Re))
        return maxSpeed

    def CompressibilityErrorCheck(self, Umax):
        Ma2 = (Umax * self.dt / self.dx)**2 / cs2
        if Ma2 > 0.1:
            sys.exit('Error: Ma2 = %.3f exceeds 0.1' %(Ma2))
        elif Ma2 > 0.01:
            print('Warning: Ma2 = %.3f exceeds 0.01!' %(Ma2))
        print('Ma2', Ma2)

    def SinusoidalWave(self, Umean, epsilon, omega, time):
        return Umean * (1 - epsilon * np.cos(omega * time))

    def Heartbeat(self, param_iN, period, Umax, time):
        profile = param_iN['profile']
        df = pd.read_csv(profile, sep=' ', header=None, names=['time', 'Umax'])
        # Scale the waveform to match the required period
        df['time'] = df['time'] * period / df['time'].iloc[-1]
        # Scale the waveform to match the required Umax on top of an offset
        if param_iN.get('offset') is None:
            df['Umax'] = df['Umax'] * Umax / df['Umax'].max()
        else:
            offset = param_iN['offset']
            df['Umax'] = Umax * (offset + (1 - offset) \
                * (df['Umax'] - df['Umax'].min()) / (df['Umax'].max() - df['Umax'].min()))
        # Roll the waveform such that it starts at the maximum speed
        df['Umax'] = np.roll(df['Umax'], -df['Umax'].idxmax())
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
        print('flowRateRatios', flowRateRatios)
        print('resistanceRatios', resistanceRatios)
        return resistanceRatios

    def FindMaxLK(self, geometry):
        # Expedient solution
        if geometry == 'bifurcation_1e-3': # radii=1e-3
            lengths = np.array([4.87e-3, 4.87e-3])
        elif geometry == 'FiveExit_2e-4': # radii=2e-4
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
        elif geometry == '0012_H_AO_H_2e-2': # inlet radius=2.00e-2
            lengths = [0.0909]*4
        elif geometry == '0012_H_AO_H_1e-2': # inlet radius=1.19e-2
            lengths = [0.0519]*4
        elif geometry == '0003_0001_8e-3': # inlet radius=8.40e-3
            lengths = [0.0462]*17
        elif geometry == '0149_1001_7e-3': # inlet radius=7.38e-3
            lengths = [0.0268]*10
        elif geometry == '0156_0001_7e-3': # inlet radius=7.17e-3
            lengths = [0.1209, 0.0357, 0.0315, 0.0367, 0.0596, 0.0392, 0.0526, 0.0374, 0.0454, 0.1109]
        else:
            sys.exit('Error: The prescribed geometry is not registered!')

        maxLK = 0
        for idx in range(len(self.radius_oUT)):
            radius = self.radius_oUT[idx]
            K = 8 * mu / (PI * radius**4)
            LK = lengths[idx] * K
            if LK > maxLK:
                maxLK = LK
        return maxLK
