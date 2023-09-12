from time import sleep

import yarp
import roboticslab_kinematics_dynamics as kd

DEFAULT_HEAD_PAN = -45.0
DEFAULT_HEAD_TILT = 0.0

DEFAULT_TRUNK_PAN = 45.0
DEFAULT_TRUNK_TILT = 30.0

#-- Prepare YARP
yarp.Network.init()
if not yarp.Network.checkNetwork():
    print('[error] Please try running yarp server')
    quit()

#-- Prepare Head (H)
optionsH = yarp.Property()
optionsH.put('device','remote_controlboard')
optionsH.put('remote','/teoSim/head')
optionsH.put('local','/alma/teoSim/head')
ddH = yarp.PolyDriver(optionsH)
if not ddH.isValid():
    print('[error] Cannot connect to: /teoSim/head')
    quit()
posH = ddH.viewIPositionControl()

#-- Prepare Trunk (T)
optionsT = yarp.Property()
optionsT.put('device','remote_controlboard')
optionsT.put('remote','/teoSim/trunk')
optionsT.put('local','/alma/teoSim/trunk')
ddT = yarp.PolyDriver(optionsT)
if not ddT.isValid():
    print('[error] Cannot connect to: /teoSim/trunk')
    quit()
posT = ddT.viewIPositionControl()

#-- Prepare Right Arm (RA)
optionsRA = yarp.Property()
optionsRA.put('device','remote_controlboard')
optionsRA.put('remote','/teoSim/rightArm')
optionsRA.put('local','/alma/teoSim/rightArm')
ddRA = yarp.PolyDriver(optionsRA)
if not ddRA.isValid():
    print('[error] Cannot connect to: /teoSim/rightArm')
    quit()
posRA = ddRA.viewIPositionControl()
axesRA = posRA.getAxes()

#-- Prepare Cartesian Control RA (CCRA)
optionsCCRA = yarp.Property()
optionsCCRA.put('device', 'CartesianControlClient')
optionsCCRA.put('cartesianRemote', '/teoSim/rightArm/CartesianControl')
optionsCCRA.put('cartesianLocal', '/alma/teoSim/rightArm/CartesianControl')
ddCCRA = yarp.PolyDriver(optionsCCRA)
if not ddCCRA.isValid():
    print('[error] Cannot connect to: /teoSim/rightArm/CartesianControl')
    quit()
ccRA = kd.viewICartesianControl(ddCCRA)

#-- Pre-prog
posT.positionMove(0, DEFAULT_TRUNK_PAN)
posT.positionMove(1, DEFAULT_TRUNK_TILT)

posH.positionMove(0, DEFAULT_HEAD_PAN)
posH.positionMove(1, DEFAULT_HEAD_TILT)

for i in range(axesRA):
    posRA.setRefSpeed(i, 35)

sleep(0.1)
q = yarp.DVector(axesRA,0.0)
posRA.positionMove(q)
while not posRA.checkMotionDone():
    sleep(0.1)

q = yarp.DVector(axesRA,0.0)
q[0] = -40
q[1] = -30
q[3] = 30
posRA.positionMove(q)
while not posRA.checkMotionDone():
    sleep(0.1)

q = yarp.DVector(axesRA,0.0)
q[0] = -40
q[1] = -70
q[3] = 30
posRA.positionMove(q)
while not posRA.checkMotionDone():
    sleep(0.1)

q = yarp.DVector(axesRA,0.0)
q[0] = 30
q[1] = -70
q[3] = 30
posRA.positionMove(q)
while not posRA.checkMotionDone():
    sleep(0.1)

q = yarp.DVector(axesRA,0.0)
q[0] = 6.860721
q[1] = -50.268563
q[2] = 0.00000
q[3] = 76.61138
q[4] = 59.0000
q[5] = -25.000
posRA.positionMove(q)
while not posRA.checkMotionDone():
    sleep(0.1)

print('> stat')
x = yarp.DVector()
ret, state, ts = ccRA.stat(x)
print('<', yarp.decode(state), '[%s]' % ', '.join(map(str, x)))
