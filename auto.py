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

# Interact with the buttons or the screen
ev3 = EV3Brick()
ev3.light.on(Color.YELLOW)

# Declare motors 
left_motor = Motor(Port.A)
right_motor = Motor(Port.D)
scooper_motor = Motor(Port.B)
claw_motor = Motor(Port.C)

base = DriveBase(Motor(Port.A),Motor(Port.D), 70, 120)

# Initialize variables. 
# Assuming sticks are in the middle when starting.
right_stick_x = 124
right_stick_y = 124
left_stick_y = 124
left_stick_x = 124

# A helper function for converting stick values (0 - 255)
# to more usable numbers (-100 - 100)
"""
Scale the given value from the scale of src to the scale of dst.

val: float or int
src: tuple
dst: tuple

example: print(scale(99, (0.0, 99.0), (-1.0, +1.0)))
"""
def scale(val, src, dst):
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def drive_straight():
    base.drive(200, 0)
    wait(3000)

# Find the PS3 Gamepad:
# /dev/input/event3 is the usual file handler for the gamepad.
# look at contents of /proc/bus/input/devices if it doesn't work.

bucket_speed = 0

# ev_type = 3 are the pressure sensitive axe, eg joystcks and bottom triggers
# code 2 = left trigger, 
# code 5 = right trigger
# code 0 = left joystick left-right
# code 1 = left joy up-down
# code 3 = right joy left-right
# code 4 = right joy up-down

XButton = 304
obutton = 305
sbutton = 308
tbutton = 307

start_poition = scooper_motor.angle()

sensor = ColorSensor(Port.S2)
gyro = GyroSensor(Port.S1)

stop = False
turn = 0
base.reset()
# anounce ready
ev3.speaker.beep(500,200)
ev3.speaker.beep(1000,200)
ev3.speaker.beep(600,200)

ev3.light.on(Color.GREEN)
# after auto moves back
def reverse():
    gyro.reset_angle(0)
    run = True
    base.reset()
    base.settings(255, 255) # here i am MEOW
    while(run):
        turn=gyro.angle()
        base.drive(-200,-turn)
        if base.distance() <= -1600:
            run=False
        wait(50)
    base.stop()

def foreward():
    ev3.light.on(Color.RED)
    base.settings(255, 255) # here i am MEOW
    run = True
    base.reset()
    turn = 0
    while(run):
        #base.settings(straight_speed=200,straight_acceleration=75,turn_rate=turn)
        base.drive(255, turn)
        dist = base.distance()
        if dist >= 1570: 
            run = False
        if sensor.reflection() > 15:
            turn = turn - 5
            ev3.light.on(Color.ORANGE)
        elif sensor.reflection() < 5: 
            turn = turn + 3
            ev3.light.on(Color.ORANGE)
        else:
            turn = 0
            ev3.light.on(Color.GREEN)
        wait(50)
        ev3.light.on(Color.GREEN)
    base.stop()
    claw_motor.run_until_stalled(255)

#base.settings(straight_speed=200,straight_acceleration=75,turn_rate=turn)

foreward()
reverse()



