# Code below runs on the Adafruit MacroPad running CircuitPython 7.0 and with all required libraries to support the MacroPad library

import time
from adafruit_macropad import MacroPad
from rainbowio import colorwheel

macropad = MacroPad()

TURNING_LEFT_1 = 0
TURNING_RIGHT = 1
TURNING_LEFT_2 = 2
CHECK_COMBINATION = 3
UNLOCKED = 4
WRONG_COMBINATION = 5
READY = 6

state = TURNING_LEFT_1

oldEncoder = macropad.encoder
newEncoder = oldEncoder
macropad.pixels.brightness = 0.1
encoderPressed = False
enteredNumbers = []
correctNumbers = [5,12,13]
wheel_offset = 0


text_lines = macropad.display_text(title="Entering Combination:")

def show_red():
    macropad.pixels.fill((255, 0, 0))
def show_yellow():
    macropad.pixels.fill((255, 155, 0))
def show_green():
    macropad.pixels.fill((0, 255, 0))
def show_pink():
    macropad.pixels.fill((255, 0, 255))
def show_number():
    text_lines[len(enteredNumbers)].text = "{}".format(newEncoder)
    text_lines.show()
def show_combination():
    text_lines[5].text = "{}    {}    {}".format(enteredNumbers[0],enteredNumbers[1],enteredNumbers[2])
    text_lines.show()
def show_unlocked():
    text_lines[2].text = "Unlocked!"
    text_lines.show()

def show_unlocked():
    text_lines = macropad.display_text(title="Ready for use.")
    text_lines[0].text = "              "
    text_lines[1].text = "              "
    text_lines[2].text = "              "

    text_lines.show()

def updateSystem():
    global oldEncoder
    global newEncoder
    global encoderPressed
    oldEncoder = newEncoder
    newEncoder = macropad.encoder
    encoderPressed = macropad.encoder_switch

def evaluateState(state):
    global oldEncoder
    global newEncoder
    global encoderPressed
    global enteredNumbers
    global correctNumbers

    if(state == TURNING_LEFT_1):
        if(newEncoder > oldEncoder):
            enteredNumbers.append(abs(newEncoder))
            return TURNING_RIGHT
    elif(state == TURNING_RIGHT):
        if(newEncoder < oldEncoder):
            enteredNumbers.append(abs(newEncoder))
            return TURNING_LEFT_2
    elif(state == TURNING_LEFT_2):
        if(encoderPressed):
            enteredNumbers.append(abs(newEncoder))
            return CHECK_COMBINATION
    elif(state == CHECK_COMBINATION):
        correctCombination = True
        for i in range(len(enteredNumbers)):
            correctCombination = (enteredNumbers[i]==correctNumbers[i])
        if(correctCombination):
            return UNLOCKED
        else:
            return WRONG_COMBINATION
    elif(state == WRONG_COMBINATION):
        enteredNumbers = []
        return TURNING_LEFT_1
    elif(state == UNLOCKED):
        return READY

    return state

def reactToState(state):
    global wheel_offset
    global lit_keys

    if(state == TURNING_LEFT_2):
        show_green()
        show_number()
    elif(state == TURNING_RIGHT):
        show_yellow()

        show_number()
    elif(state == TURNING_LEFT_1):
        show_red()
        show_number()
    elif(state == CHECK_COMBINATION):
        show_combination()
    elif(state == WRONG_COMBINATION):
        #macropad.play_file("DING.mp3")
    elif(state == UNLOCKED):
        show_pink()
        show_unlocked()
        #macropad.play_file("TADA.mp3")
    elif(state == READY):
        wheel_offset += 2  # Glow thru the colorwheel.
        for pixel in range(12):
            macropad.pixels[pixel] = colorwheel((pixel / 12 * 256) + wheel_offset)

    return state


while True:
    updateSystem()
    state = evaluateState(state)
    reactToState(state)
    time.sleep(0.01)
