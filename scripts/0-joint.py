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
    print('[error] Please launch robot side')
    quit()
trunkPos = trunkDd.viewIPositionControl()
trunkPos.positionMove(0, 45) # pan
trunkPos.positionMove(1, 30) # tilt
