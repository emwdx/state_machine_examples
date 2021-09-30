# Write your code here :-)
# Fan Tachometer by Evan Weinberg (GitHub: emwdx, Twitter: @emwdx)
# This program uses the Circuit Playground Express on the back of a fan pointed at a light source to calculate rotation frequency.
# The units of frequency are in rotations/second. See the repository for more details.
# A state machine uses the light sensor to detect whether it sees a fan blade (SENSOR_BLOCKED) or not (SENSOR_UNBLOCKED).
# After the sensor goes from unblocked to blocked and then to unblocked, we know that a fan blade has passed (TRANSITION_OCCURRED)
# The calculateRotationFrequency function uses the transition count and a running average to calculate an average rotation frequency.


import time
import board
from adafruit_circuitplayground import cp

#Set the light sensor threshold between light and dark here.
SENSITIVITY = 28
#Set the number of fan blades
NUM_OF_BLADES = 10
#Set the number of frequency values to store in the array. More values results in smoother data, but slows down the responsiveness.
FREQ_SIZE = 100
freqs = [0]*FREQ_SIZE

#Define how frequently we want the frequency to be calculated (CALCULATE_INTERVAL) and how often to report data (REPORT_INTERVAL)
CALCULATE_INTERVAL = 100
REPORT_INTERVAL = 2000

#Define states for the light sensor
TRANSITION_OCCURRED = 2
SENSOR_BLOCKED = 1
SENSOR_UNBLOCKED = 0

currentState = SENSOR_UNBLOCKED

#Set global variables for keeping track of the system
transitions = 0
oldTime = 0
currentTime = 0
rotation_frequency = 0
average_rotation_frequency = 0
loopCount = 0
oldTransitions = 0
elapsedTime = 0

def evaluateState(currentState):
    global lightValue

    if(currentState == SENSOR_UNBLOCKED):
        if(lightValue < SENSITIVITY):
            currentState = SENSOR_BLOCKED

    elif(currentState == SENSOR_BLOCKED):
        if(lightValue>SENSITIVITY):
            currentState = TRANSITION_OCCURRED
    else:
        currentState = SENSOR_UNBLOCKED
    return currentState

def updateSystem(currentState):
    global lightValue

    #update the lightValue variable to be equal to the light sensor value (cp.light)
    lightValue = cp.light


def reactToState(currentState):
    global transitions
    #If a transition has occurred, increase the transitions by 1.
    if(currentState == TRANSITION_OCCURRED):
        transitions += 1

#This function calculates the rotation speed of the fan.
def calculateRotationFrequency():
    global oldTime
    global oldTransitions
    global elapsedTime
    global average_rotation_frequency
    global freqs
    global changeInTime

    #See how much time has elapsed since the last calculation.
    currentTime = time.monotonic()
    changeInTransitions = transitions - oldTransitions
    changeInTime = currentTime - oldTime

    #This is necessary for the first loop to keep the elapsedTime variable from being the same as the clock of the CPE.
    if(changeInTime < 1.0):
        elapsedTime += changeInTime

    #This logic prevents errors that sometimes happen when there are no transitions.
    if(changeInTransitions > 0):
        if(currentTime > oldTime):
            #The fan blade constant ensures the frequency calculated is for the entire fan to rotate around.
            rotation_frequency = changeInTransitions / changeInTime / NUM_OF_BLADES
        else:
            rotation_frequency = average_rotation_frequency
    else:
        rotation_frequency = 0

    #This uses an array of frequency values to smooth out the frequency calculation.
    freqs.pop(0)
    freqs.append(changeInTransitions)
    average_rotation_frequency = (average_rotation_frequency*(FREQ_SIZE - 1)+ rotation_frequency)/FREQ_SIZE

    #Store values from this loop in the global variables.
    oldTransitions = transitions
    oldTime = currentTime

while True:
    global lightValue
    updateSystem(currentState)
    currentState = evaluateState(currentState)
    reactToState(currentState)

    #The two intervals let us report and calculate the frequency at different rates. Not part of the state machine :)
    if(loopCount % CALCULATE_INTERVAL == 0):
        calculateRotationFrequency()
    if(loopCount == REPORT_INTERVAL):
        if(cp.switch):
            print(str(elapsedTime) + "\t" + str(transitions) + "\t" + str(average_rotation_frequency) + "\t" + str(lightValue))
            loopCount = 0
    else:
        loopCount += 1

    time.sleep(0.00005)
