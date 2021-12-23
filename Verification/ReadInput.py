import sys
import xml.etree.ElementTree as ET
import numpy as np

tree = ET.parse(sys.argv[5])
root = tree.getroot()
print('Reading inputs from "%s"\n' %(sys.argv[5]))

# Find grid sizes
dt = float(root.find('simulation').find('step_length').attrib['value'])
dx = float(root.find('simulation').find('voxel_size').attrib['value'])
#print('dt', dt)
#print('dx', dx)

# Find normals and positions at inlets
normal_iN = np.array([])
position_iN = np.array([])
for elm in root.find('inlets').iter('inlet'):
    normal = elm.find('normal').attrib['value']
    normal = normal.strip('(').strip(')').split(',')
    normal_iN = np.append(normal_iN, np.array(normal, dtype=np.float64))
    
    position = elm.find('position').attrib['value']
    position = position.strip('(').strip(')').split(',')
    position_iN = np.append(position_iN, np.array(position, dtype=np.float64))
normal_iN = normal_iN.reshape(int(normal_iN.size/3), 3)
position_iN = position_iN.reshape(int(position_iN.size/3), 3)
#print('normal_iN', normal_iN)
#print('position_iN', position_iN)

# Find normals and positions at outlets
normal_oUT = np.array([])
position_oUT = np.array([])
for elm in root.find('outlets').iter('outlet'):
    normal = elm.find('normal').attrib['value']
    normal = normal.strip('(').strip(')').split(',')
    normal_oUT = np.append(normal_oUT, np.array(normal, dtype=np.float64))
    
    position = elm.find('position').attrib['value']
    position = position.strip('(').strip(')').split(',')
    position_oUT = np.append(position_oUT, np.array(position, dtype=np.float64))
normal_oUT = normal_oUT.reshape(int(normal_oUT.size/3), 3)
position_oUT = position_oUT.reshape(int(position_oUT.size/3), 3)
normal_oUT = - normal_oUT # normal vectos point inwards in HemeLB
#print('normal_oUT', normal_oUT)
#print('position_oUT', position_oUT)

print('Reading inputs is finished.\n')