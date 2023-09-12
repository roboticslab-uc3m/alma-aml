import yarp

DEFAULT_HEAD_PAN = -45.0
DEFAULT_HEAD_TILT = 0.0

DEFAULT_TRUNK_PAN = 45.0
DEFAULT_TRUNK_TILT = 30.0

yarp.Network.init()
if not yarp.Network.checkNetwork():
    print('[error] Please try running yarp server')
    quit()

headOptions = yarp.Property()
headOptions.put('device','remote_controlboard')
headOptions.put('remote','/teoSim/head')
headOptions.put('local','/alma/teoSim/head')
headDd = yarp.PolyDriver(headOptions)
if not headDd.isValid():
    print('[error] Cannot connect to: /teoSim/head')
    quit()
headPos = headDd.viewIPositionControl()

trunkOptions = yarp.Property()
trunkOptions.put('device','remote_controlboard')
trunkOptions.put('remote','/teoSim/trunk')
trunkOptions.put('local','/alma/teoSim/trunk')
trunkDd = yarp.PolyDriver(trunkOptions)
if not trunkDd.isValid():
    print('[error] Cannot connect to: /teoSim/trunk')
    quit()
trunkPos = trunkDd.viewIPositionControl()

rightArmOptions = yarp.Property()
rightArmOptions.put('device','remote_controlboard')
rightArmOptions.put('remote','/teoSim/rightArm')
rightArmOptions.put('local','/alma/teoSim/rightArm')
rightArmDd = yarp.PolyDriver(rightArmOptions)
if not rightArmDd.isValid():
    print('[error] Cannot connect to: /teoSim/rightArm')
    quit()
rightArmPos = rightArmDd.viewIPositionControl()

trunkPos.positionMove(0, DEFAULT_TRUNK_PAN)
trunkPos.positionMove(1, DEFAULT_TRUNK_TILT)

headPos.positionMove(0, DEFAULT_HEAD_PAN)
headPos.positionMove(1, DEFAULT_HEAD_TILT)

rightArmPos.positionMove(3, 90) # elbow
