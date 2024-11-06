#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase

from pybricks.hubs import EV3Brick

import struct

# Declare motors 
left_motor = Motor(Port.A)
right_motor = Motor(Port.D)
scooper_motor = Motor(Port.B)
claw_motor = Motor(Port.C)

# Interact with the buttons or the screen
ev3 = EV3Brick()

# Initialize variables. 
# Assuming sticks are in the middle when starting.
right_stick_x = 124
right_stick_y = 124
left_stick_y = 124
left_stick_x = 124

# A helper function for converting stick values (0 - 255)
# to more usable numbers (-100 - 100)
def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
 
    val: float or int
    src: tuple
    dst: tuple
 
    example: print(scale(99, (0.0, 99.0), (-1.0, +1.0)))
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]


# Find the PS3 Gamepad:
# /dev/input/event3 is the usual file handler for the gamepad.
# look at contents of /proc/bus/input/devices if it doesn't work.
infile_path = "/dev/input/event3"

# open file in binary mode
in_file = open(infile_path, "rb")

# Read from the file
# long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'    
EVENT_SIZE = struct.calcsize(FORMAT)
event = in_file.read(EVENT_SIZE)
bucket_speed = 0

# ev_type = 3 are the pressure sensitive axe, eg joystcks and bottom triggers
# code 2 = left trigger, 
# code 5 = right trigger
# code 0 = left joystick left-right
# code 1 = left joy up-down
# code 3 = right joy left-right
# code 4 = right joy up-down


while event:
    (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)
    if ev_type == 3 and code == 3:
        right_stick_x = value
    if ev_type == 3 and code == 4:
        right_stick_y = value
    if ev_type == 3 and code == 0:
        left_stick_x = value
    if ev_type == 3 and code == 1:
        left_stick_y = value

    # Type 1 events are Button Presses
    if ev_type == 1:
        ev3.screen.draw_box(0,0,64,20,fill=True, color=Color.WHITE)
        ev3.screen.draw_text(0,0, str(code) + " " + str(value))
    
    # Type 3 events are Analog presses
    if ev_type == 3:
        ev3.screen.draw_box(80+16,code*20,80+64,(code+1)*20,fill=True, color=Color.WHITE)
        ev3.screen.draw_text(80+0,code*20, str(code) + " " + str(value))
    

    # Scale stick positions to -100,100
    forward = scale(right_stick_y, (0,255), (100,-100))
    left = scale(right_stick_x, (0,255), (100,-100))
    claw_speed = scale(left_stick_x, (0,255),(100,-100))
    bucket_speed = scale(left_stick_y, (0,255),(100,-100))
    # Set motor voltages. If we're steering left, the left motor
    # must run backwards so it has a -left component
    # It has a forward component for going forward too. 
    left_motor.dc(forward - left)
    right_motor.dc(forward + left)
    scooper_motor.dc(bucket_speed)
    claw_motor.dc(claw_speed)
    # Finally, read another event
    event = in_file.read(EVENT_SIZE)

in_file.close()