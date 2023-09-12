import yarp

yarp.Network.init()
if not yarp.Network.checkNetwork():
    print('[error] Please try running yarp server')
    quit()

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

trunkPos.positionMove(0, 45) # pan
trunkPos.positionMove(1, 30) # tilt

rightArmPos.positionMove(3, 90) # elbow
