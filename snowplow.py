# Try to connect to coppeliasim python API library
try:
    import sim
except ImportError:
    print('--------------------------------------------------------------')
    print('"sim.py" could not be imported. This means very probably that')
    print('either "sim.py" or the remoteApi library could not be found.')
    print('Make sure both are in the same folder as this file,')
    print('or appropriately adjust the file "sim.py"')
    print('--------------------------------------------------------------')
    print('')
    raise  # Kill the program after

import time as t
import math
import random

from sim import simxReadVisionSensor

global clientID

def setWheelVelocity(handle, velocity):
    return sim.simxSetJointTargetVelocity(clientID, handle, velocity, sim.simx_opmode_oneshot)


def getObjectHandle(obj_name):
    return sim.simxGetObjectHandle(clientID, obj_name, sim.simx_opmode_blocking)


def startSimulation():
    print('Program started')
    sim.simxFinish(-1)
    return sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)

if __name__ == "__main__":

    clientID = startSimulation()