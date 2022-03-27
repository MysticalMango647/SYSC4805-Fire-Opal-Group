# Make sure to have the server side running in CoppeliaSim:
# in a child script of a CoppeliaSim scene, add following command
# to be executed just once, at simulation start:
#
# simRemoteApi.start(19999)
#
# then start simulation, and run this program.
#
# IMPORTANT: for each successful call to simxStart, there
# should be a corresponding call to simxFinish at the end!
import time as time
import math
import random

try:
    import sim
except:
    print ('--------------------------------------------------------------')
    print ('"sim.py" could not be imported. This means very probably that')
    print ('either "sim.py" or the remoteApi library could not be found.')
    print ('Make sure both are in the same folder as this file,')
    print ('or appropriately adjust the file "sim.py"')
    print ('--------------------------------------------------------------')
    print ('')



print ('Program started')
sim.simxFinish(-1) # just in case, close all opened connections
clientID=sim.simxStart('127.0.0.1',19999,True,True,5000,5) # Connect to CoppeliaSim



def rotateRobot(direction):
    Velocity = 1
    if (direction == True):
        rightWheelVelocity = .5
        leftWheelVelocity = -.5
    if (direction == False):
        rightWheelVelocity = -.5
        leftWheelVelocity = .5
    rotatingRobot = True
    while rotatingRobot:
        sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, leftWheelVelocity, sim.simx_opmode_blocking)
        sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, rightWheelVelocity, sim.simx_opmode_blocking)
        time.sleep(2)
        sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, Velocity, sim.simx_opmode_blocking)
        sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, Velocity, sim.simx_opmode_blocking)
        time.sleep(1)
        sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, leftWheelVelocity, sim.simx_opmode_blocking)
        sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, rightWheelVelocity, sim.simx_opmode_blocking)
        time.sleep(4)
        rotatingRobot = False

def dumpSnow():
    dumpingsnow = True
    while dumpingsnow:
        sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, 1, sim.simx_opmode_blocking)
        sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, 1, sim.simx_opmode_blocking)
        time.sleep(2)
        sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, -Velocity, sim.simx_opmode_blocking)
        sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, -Velocity, sim.simx_opmode_blocking)
        time.sleep(2)
        dumpingsnow = False


if clientID!=-1:
    print ('Connected to remote API server')
    sim.simxAddStatusbarMessage(clientID, 'Hello CoppeliaSim! -Fire Opal Team', sim.simx_opmode_oneshot)
    # Start simulation:
    sim.simxStartSimulation(clientID, sim.simx_opmode_blocking)
    # Now try to retrieve data in a blocking fashion (i.e. a service call):
    res,objs=sim.simxGetObjects(clientID,sim.sim_handle_all,sim.simx_opmode_blocking)

    #Variable Declaration
    timeout = 150 #5 minutes simulation time
    timeout_start = time.time()
    FLM = "Front_Left_Motor"
    FRM = "Front_Right_Motor"
    RLM = "Rear_Left_Motor"
    RRM = "Rear_Right_Motor"
    BLS = "Bottom_Left_Sensor"
    BRS = "Bottom_Right_Sensor"
    PS = "Proximity_sensor"
    visionSensor = [-1, -1]
    numOfBottomSensor = 2
    visionSensorReading = [False,False]
    Velocity = 1

    turnRight = True
    turnLeft = False


    #Getting Object Handle
    FrontLeftMotorHandle, FrontLeftMotor = sim.simxGetObjectHandle(clientID, FLM, sim.simx_opmode_blocking)
    FrontRightMotorHandle, FrontRightMotor = sim.simxGetObjectHandle(clientID, FRM, sim.simx_opmode_blocking)
    RearLeftMotorHandle, RearLeftMotor = sim.simxGetObjectHandle(clientID, RLM, sim.simx_opmode_blocking)
    RearRightMotorHandle, RearRightMotor = sim.simxGetObjectHandle(clientID, RRM, sim.simx_opmode_blocking)
    visionSensorLeftHandle, visionSensor[0] = sim.simxGetObjectHandle(clientID, BLS, sim.simx_opmode_blocking)
    visionSensorRightHandle, visionSensor[1] = sim.simxGetObjectHandle(clientID, BRS, sim.simx_opmode_blocking)
    proximitySensorHandle, prox_sensor = sim.simxGetObjectHandle(clientID, PS, sim.simx_opmode_blocking)

    while time.time() < timeout_start + timeout:
        velocity = 1
        floorReading = [0,0]
        #vision sensor code
        for i in range(0, numOfBottomSensor, 1):
            print("reading floor sensors")
            resultFloorSensor, visionSensorReading, auxPackets=sim.simxReadVisionSensor(clientID,visionSensor[i],sim.simx_opmode_blocking)
            print("auxPackets: ", auxPackets)
            #print("visionSensorReading: ",visionSensorReading)
            #print("resultFloorSensor: ",resultFloorSensor)
            #if (resultFloorSensor>=0):
            if (visionSensorReading > -1):
                print("Vision Sensor Reading", visionSensorReading)
                if (auxPackets[0][1] < .7):
                    floorReading[i] = 1
                    print("line detected")
                else:
                    floorReading[i] = 0

            rightSideVelocity = velocity
            leftSideVelocity = velocity
            adjustSpeedBy = 0.5
            print(floorReading)


        if (floorReading[0] == 1 or floorReading[1] == 1):
            print("both sensors detected line")
            dumpSnow()
            if(floorReading[0] == 1):
                rotateRobot(turnRight)

            if(floorReading[1] == 1):
                rotateRobot(turnLeft)



        #proximity sensor code

        RC, proximdetect, DP, DOH, DSNV = sim.simxReadProximitySensor(clientID, prox_sensor, sim.simx_opmode_blocking)
        print("proximity dected: ", proximdetect)
        adjustSpeedBy = 0.5

        if proximdetect:
            rightSideVelocity = -velocity * adjustSpeedBy
            leftSideVelocity = velocity * adjustSpeedBy

        sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, leftSideVelocity, sim.simx_opmode_blocking)
        sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, rightSideVelocity, sim.simx_opmode_blocking)
        #time.sleep(random.randrange(10, 60, 20) / 20)
        #sim.simxSetJointTargetVelocity(clientID, RearLeftMotor, leftSideVelocity, sim.simx_opmode_blocking)
        #sim.simxSetJointTargetVelocity(clientID, RearRightMotor, rightSideVelocity, sim.simx_opmode_blocking)

        print("visionSensorReading: ", visionSensorReading)



    # Before closing the connection to CoppeliaSim, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
    sim.simxGetPingTime(clientID)
    sim.simxStopSimulation(clientID, sim.simx_opmode_blocking)
    # Now close the connection to CoppeliaSim:
    sim.simxFinish(clientID)

else:
    print ('Failed connecting to remote API server')

print ('Program ended')


