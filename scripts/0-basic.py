from time import sleep

import yarp
import roboticslab_kinematics_dynamics as kd

DEFAULT_HEAD_PAN = -45.0
DEFAULT_HEAD_TILT = 0.0

DEFAULT_TRUNK_PAN = 52.6225703136347036093 # 45.0
DEFAULT_TRUNK_TILT = 11.3726854400002164169 # 30.0

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

#-- Prepare Cartesian Control T and RA (ccTRA)
optionsCCTRA = yarp.Property()
optionsCCTRA.put('device', 'CartesianControlClient')
optionsCCTRA.put('cartesianRemote', '/teoSim/trunkAndRightArm/CartesianControl')
optionsCCTRA.put('cartesianLocal', '/alma/teoSim/trunkAndRightArm/CartesianControl')
ddccTRA = yarp.PolyDriver(optionsCCTRA)
if not ddccTRA.isValid():
    print('[error] Cannot connect to: /teoSim/trunkAndRightArm/CartesianControl')
    quit()
ccTRA = kd.viewICartesianControl(ddccTRA)

#-- Pre-prog
posT.positionMove(0, DEFAULT_TRUNK_PAN)
posT.positionMove(1, DEFAULT_TRUNK_TILT)

posH.positionMove(0, DEFAULT_HEAD_PAN)
posH.positionMove(1, DEFAULT_HEAD_TILT)

for i in range(axesRA):
    posRA.setRefSpeed(i, 25)

sleep(0.1)
q = yarp.DVector(axesRA,0.0)
posRA.positionMove(q)
while not posRA.checkMotionDone():
    sleep(0.1)

q = yarp.DVector(axesRA,0.0)
q[0] = 40
q[1] = -30
q[3] = -30
posRA.positionMove(q)
while not posRA.checkMotionDone():
    sleep(0.1)

q = yarp.DVector(axesRA,0.0)
q[0] = 40
q[1] = -70
q[3] = -30
posRA.positionMove(q)
while not posRA.checkMotionDone():
    sleep(0.1)

q = yarp.DVector(axesRA,0.0)
q[0] = -30
q[1] = -70
q[3] = -30
posRA.positionMove(q)
while not posRA.checkMotionDone():
    sleep(0.1)

q = yarp.DVector(axesRA,0.0)
q[0] = 10.5923737193064262385
q[1] = -48.1872899894004476096
q[2] = -12.2954651161971284523
q[3] = -57.3412518945380753621
q[4] = -62.5312112926755006015 
q[5] = 23.2866408525290893294
posRA.positionMove(q)
while not posRA.checkMotionDone():
    sleep(0.1)

sleep(0.2)
print('> stat')
x = yarp.DVector()
ret, state, ts = ccTRA.stat(x)
print('<', yarp.decode(state), '[%s]' % ', '.join(map(str, x)))

xds = [
    #[0.740, -0.300, 0.025, -0.3202451834152276, 2.504523320657104, 0.11523093239360085],
    [0.740, -0.300, -0.025, -0.3202451834152276, 2.504523320657104, 0.11523093239360085],
    [0.740, -0.200, -0.025, -0.3202451834152276, 2.504523320657104, 0.11523093239360085],
    [0.740, -0.100, -0.025, -0.3202451834152276, 2.504523320657104, 0.11523093239360085],
    [0.740, 0.000, -0.025, -0.3202451834152276, 2.504523320657104, 0.11523093239360085],
    [0.640, 0.000, -0.025, -0.3202451834152276, 2.504523320657104, 0.11523093239360085],
    [0.540, 0.000, -0.025, -0.3202451834152276, 2.504523320657104, 0.11523093239360085],
    [0.640, 0.000, -0.025, -0.3202451834152276, 2.504523320657104, 0.11523093239360085],
    [0.740, 0.000, -0.025, -0.3202451834152276, 2.504523320657104, 0.11523093239360085],
    [0.840, 0.000, -0.025, -0.3202451834152276, 2.504523320657104, 0.11523093239360085],
    [0.940, 0.000, -0.025, -0.3202451834152276, 2.504523320657104, 0.11523093239360085],
]

for i in range(len(xds)):
    sleep(0.2)
    print('-- movement ' + str(i + 1) + ':')
    xd = yarp.DVector(xds[i])
    print('>', '[%s]' % ', '.join(map(str, xd)))
    if ccTRA.movl(xd):
        print('< [ok]')
        print('< [wait...]')
        sleep(0.2)
        ok = ccTRA.wait()
        print('> ok', ok)
        print('> stat')
        x = yarp.DVector()
        ret, state, ts = ccTRA.stat(x)
        print('<', yarp.decode(state), '[%s]' % ', '.join(map(str, x)))
    else:
        print('< [fail]')
        quit()
