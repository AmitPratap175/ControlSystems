import numpy as np
import matplotlib.pyplot as plt
import os
import yaml

flag = False
version = 1

with open('config.yaml','r') as file:
    data = yaml.safe_load(file)
    SAFELIMITS = data['SAFELIMITS']
    PANFACTOR, TILTFACTOR = data['pan_factor'], data['tilt_factor']  

#open the latest version
while not flag:
    if f'PIDvsLinearControl_{version}.txt' not in os.listdir(f'./PAN_TILT_{PANFACTOR}/'):
        filename = f'./PAN_TILT_{PANFACTOR}/PIDvsLinearControl_{version-1}.txt'
        flag = True
    else:
        version += 1    

# open the specified version
# version = 3
# filename = f'./PAN_TILT_0.5/PIDvsLinearControl_{version-1}.txt'

offset_x, offset_y, pan, pan_PID, tilt, tilt_PID = [], [], [] ,[], [], []
with open(filename,'r') as file:
    # lines = file.read()
    for line in file:
        elements = line.replace('\n','').split('  ')

        offset_x.append(float(elements[0]))
        offset_y.append(float(elements[1]))
        pan.append(float(elements[2]))
        pan_PID.append(float(elements[3]))
        tilt.append(float(elements[4]))
        tilt_PID.append(float(elements[5]))
plt.figure()
plt.scatter(offset_x,pan, label = 'Normal PWM')
plt.scatter(offset_x,pan_PID, label = 'PID PWM')
plt.title('X axis offset')
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()


plt.figure()
plt.scatter(offset_y,tilt, label = 'Normal PWM')
plt.scatter(offset_y,tilt_PID, label = 'PID PWM')
plt.title('Y axis offset')
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.show()