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

sensorArray = [False, False, False, False]

'''
Doa180 will performat a robot do change its oreintation if it is stuck in one area with a lot of the sensors going off
'''
def doa180():
    global velocity
    doinga180 = True
    while doinga180:
        sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, -velocity, sim.simx_opmode_blocking)
        sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, velocity, sim.simx_opmode_blocking)
        numberRandomToSleep = random.randrange(3, 8)/10
        time.sleep(numberRandomToSleep)
        doinga180 = False

'''
Rotate Robot requires an input parameter for the direction, true is clockwise
false is counter clockwise. The robot will turn, move forward a little bit
then it will turn again so it starts a new line
'''
def rotateRobot(direction):
    global velocity
    if (direction == True):
        rightWheelVelocity = -.5 * velocity
        leftWheelVelocity = .5 * velocity
        print("turning right")
    if (direction == False):
        rightWheelVelocity = .5 * velocity
        leftWheelVelocity = -.5 * velocity
        print("turning left")
    rotatingRobot = True

    sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, leftWheelVelocity, sim.simx_opmode_blocking)
    sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, rightWheelVelocity, sim.simx_opmode_blocking)
    time.sleep(0.5)
    sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, velocity, sim.simx_opmode_blocking)
    sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, velocity, sim.simx_opmode_blocking)
    time.sleep(0.4)
    sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, leftWheelVelocity, sim.simx_opmode_blocking)
    sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, rightWheelVelocity, sim.simx_opmode_blocking)
    time.sleep(0.65)

'''dump function will move the robot forward out of the boundary and then move it back'''
def dumpSnow():
    dumpingsnow = True
    global velocity
    while dumpingsnow:
        sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, velocity, sim.simx_opmode_blocking)
        sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, velocity, sim.simx_opmode_blocking)
        time.sleep(0.3)
        sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, -velocity, sim.simx_opmode_blocking)
        sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, -velocity, sim.simx_opmode_blocking)
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
    timeout = 300 #5 minutes simulation time
    timeout_start = time.time()
    FLM = "Front_Left_Motor"
    FRM = "Front_Right_Motor"
    BLS = "Bottom_Left_Sensor"
    BRS = "Bottom_Right_Sensor"
    PS = "Proximity_sensor"
    LPS = "Left_Proximity_sensor"
    RPS = "Right_Proximity_sensor"
    RB = "Robot_Body"
    visionSensor = [-1, -1]
    numOfBottomSensor = 2
    visionSensorReading = [False,False]
    #Velocity = 10

    turnRight = True
    turnLeft = False
    dobounceFloorSensorCounter = 0

    #Getting Object Handle
    FrontLeftMotorHandle, FrontLeftMotor = sim.simxGetObjectHandle(clientID, FLM, sim.simx_opmode_blocking)
    FrontRightMotorHandle, FrontRightMotor = sim.simxGetObjectHandle(clientID, FRM, sim.simx_opmode_blocking)
    visionSensorLeftHandle, visionSensorLeft = sim.simxGetObjectHandle(clientID, BLS, sim.simx_opmode_blocking)
    visionSensorRightHandle, visionSensorRight = sim.simxGetObjectHandle(clientID, BRS, sim.simx_opmode_blocking)
    proximitySensorHandle, prox_sensor = sim.simxGetObjectHandle(clientID, PS, sim.simx_opmode_blocking)
    LeftproximitySensorHandle, Left_prox_sensor = sim.simxGetObjectHandle(clientID, LPS, sim.simx_opmode_blocking)
    LeftproximitySensorHandle, Right_prox_sensor = sim.simxGetObjectHandle(clientID, RPS, sim.simx_opmode_blocking)
    RobotBodyHandle, RobotBody = sim.simxGetObjectHandle(clientID, RB, sim.simx_opmode_blocking)

    #set our entire code to run in a while loop that will stop at the 5 minute timer
    while time.time() < timeout_start + timeout:
        velocity = 8
        floorReading = [0,0]
        #vision sensor code
        resultFloorSensor, visionSensorReadingLeft, auxPacketLeft = sim.simxReadVisionSensor(clientID, visionSensorLeft,
                                                                                             sim.simx_opmode_blocking)
        resultFloorSensor, visionSensorReadingRight, auxPacketRight = sim.simxReadVisionSensor(clientID,
                                                                                               visionSensorRight,
                                                                                               sim.simx_opmode_blocking)

        debounceFloorSensorCounter = 0
        #checking the floor sensors on the robot, if either reach the black line
        #we update our floorReading array to be 1 and treat it accordingly
        if (auxPacketLeft[0][1] < 0.7):
            floorReading[0] = 1
            debounceFloorSensorCounter += 1
        elif (auxPacketRight[0][1] < 0.7):
            floorReading[1] = 1
            debounceFloorSensorCounter += 1
        else:
            floorReading[0] = 0
            floorReading[1] = 0


        rightSideVelocity = velocity
        leftSideVelocity = velocity
        adjustSpeedBy = 0.5
        print(floorReading)

        #Orientation of Robot Detection
        RC, eulerAngles=sim.simxGetObjectOrientation(clientID,RobotBody, sim.sim_handle_parent, sim.simx_opmode_blocking)
        print(eulerAngles)



        #proximity  and vision sensor code
        RC, proximdetect, DP, DOH, DSNV = sim.simxReadProximitySensor(clientID, prox_sensor, sim.simx_opmode_blocking)
        RC, left_proximdetect, DP, DOH, DSNV = sim.simxReadProximitySensor(clientID, Left_prox_sensor, sim.simx_opmode_blocking)
        RC, right_proximdetect, DP, DOH, DSNV = sim.simxReadProximitySensor(clientID, Right_prox_sensor, sim.simx_opmode_blocking)
        print("proximity dected: ", proximdetect)
        adjustSpeedBy = 0.5

        if (floorReading[0] == 1 or floorReading[1] == 1):
            sensorArray[0] = True

        sensorArray[1] = proximdetect
        sensorArray[2] = left_proximdetect
        sensorArray[3] = right_proximdetect
        count = 0

        #Sensor Heiarchy code
        for i in range(len(sensorArray)):
            if sensorArray[i] == True:
                count += 1

        if (count > 1):
            #Floor reading detection dump snow and rotate robot according
            if (floorReading[0] == 1 or floorReading[1] == 1):
                #print("both sensors detected line")
                dumpSnow()
                #rotateRobot(turnRight)
                debounceFloorSensorCounter = 0
            else:
                doa180()

            if (floorReading[0] == 1):
                rotateRobot(turnLeft)
            elif (floorReading[1] == 1):
                rotateRobot(turnRight)

        else:
            #Center Proximity Detection
            if proximdetect:
                print("prox detected")
                rightSideVelocity = -velocity * adjustSpeedBy
                leftSideVelocity = velocity * adjustSpeedBy
            #Left Proximity Detection
            if left_proximdetect:
                print("left front sensor detect")
                rightSideVelocity = -velocity * adjustSpeedBy
                leftSideVelocity = velocity * adjustSpeedBy
            # Right Proximity Detection
            if right_proximdetect:
                print("right front sensor detect")
                rightSideVelocity = velocity * adjustSpeedBy
                leftSideVelocity = -velocity * adjustSpeedBy
            #Floor Sensor Detection
            if (floorReading[0] == 1 or floorReading[1] == 1):
                print("both sensors detected line")
                dumpSnow()
                rotateRobot(turnRight)
                dobounceFloorSensorCounter = 0

        #Set the robot velocity to go straight, or turn based on the proximity sensor readings
        sim.simxSetJointTargetVelocity(clientID, FrontLeftMotor, leftSideVelocity, sim.simx_opmode_blocking)
        sim.simxSetJointTargetVelocity(clientID, FrontRightMotor, rightSideVelocity, sim.simx_opmode_blocking)
        #print("visionSensorReading: ", visionSensorReading)



    # Before closing the connection to CoppeliaSim, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
    sim.simxGetPingTime(clientID)
    #Robot will automatically stop simulation when 5 minute timer has been reached
    sim.simxStopSimulation(clientID, sim.simx_opmode_blocking)
    # Now close the connection to CoppeliaSim:
    sim.simxFinish(clientID)

else:
    print ('Failed connecting to remote API server')

print ('Program ended')


