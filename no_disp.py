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

base = DriveBase(Motor(Port.A),Motor(Port.D), 70, 120)
sensor = ColorSensor(Port.S2)
gyro = GyroSensor(Port.S1)


# Interact with the buttons or the screen
ev3 = EV3Brick()
ev3.light.on(Color.YELLOW)
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

def open_claw():
    claw_motor.run_until_stalled(255)

def close_claw():
    claw_motor.run_until_stalled(-255)

# goforward
def goforward():
    ev3.light.on(Color.RED)
    base.settings(255, 255) # tells how quick it goes
    run = True
    base.reset()
    turn = 0
    while(run):
        #base.settings(straight_speed=200,straight_acceleration=75,turn_rate=turn)
        base.drive(255, turn)
        dist = base.distance()
        if dist >= 1600: 
            run = False
        if sensor.reflection() > 15:
            turn = turn - 4
            ev3.light.on(Color.ORANGE)
        elif sensor.reflection() < 5: 
            turn = turn + 2
            ev3.light.on(Color.ORANGE)
        else:
            turn = 0
            ev3.light.on(Color.GREEN)
        wait(50)
        ev3.light.on(Color.GREEN)
    base.stop()
    open_claw()

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

def auto():
    goforward() 
    # after goforward claw opens
    reverse()
    wait(1000)
    close_claw()
    wait(1000)
    goforward()
    reverse()
# Find the PS3 Gamepad:
# /dev/input/event3 is the usual file handler for the gamepad.
# look at contents of /proc/bus/input/devices if it doesn't work.
infile_path = "/dev/input/event3"

# open file in binary mode
try:
    in_file = open(infile_path, "rb")
except:
    ev3.speaker.beep(60, 1000)

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

XButton = 304
obutton = 305
sbutton = 308
tbutton = 307

# start_position = scooper_motor.angle()


ev3.speaker.beep(500,200)
ev3.speaker.beep(1000,200)
ev3.speaker.beep(600,200)

ev3.light.on(Color.GREEN)

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
    if ev_type == 1 and code == XButton and value==1:
        scooper_motor.run_until_stalled(255)
        claw_motor.run_until_stalled(255,Stop.BRAKE)        
        scooper_motor.reset_angle(0)
        scooper_motor.run_angle(255,-570)
        claw_motor.run_until_stalled(-255)
        scooper_motor.run_angle(255,150) 
    if ev_type == 1 and code == obutton and value==1:
        auto()
    if ev_type == 1 and code == sbutton and value==1:
        reverse()
        ev3.light.on(Color.ORANGE)
        wait(1000)
        ev3.light.on(Color.GREEN)
    if ev_type == 1 and code == tbutton and value==1:
        right_motor.dc(25)
        left_motor.dc(25)
        wait(5000)
        claw_motor.run_until_stalled(200)
    # Type 1 events are Button Presses 
    #if ev_type == 1:
    #    ev3.screen.draw_box(0,0,64,20,fill=True, color=Color.WHITE)
    #    ev3.screen.draw_text(0,0, str(code) + " " + str(value))
    
    # Type 3 events are Analog presses
    #if ev_type == 3:
    #    ev3.screen.draw_box(80+16,code*20,80+64,(code+1)*20,fill=True, color=Color.WHITE)
    #    ev3.screen.draw_text(80+0,code*20, str(code) + " " + str(value))
    

    # Scale stick positions to -100,100
    forward = scale(right_stick_y, (0,255), (70,-70))
    left = scale(right_stick_x, (0,255), (30,-30))
    claw_speed = scale(left_stick_x, (0,255),(80,-80))
    bucket_speed = scale(left_stick_y, (0,255),(70,-70))
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

