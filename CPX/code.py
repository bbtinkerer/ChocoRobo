# Copyright (c) 2018 bbtinkerer
#
# Simple and easy to build face following robot with off the shelf parts 
# for anyone to build. For use on Adafruit's Circuit Playground 
# Express (CPX) and Crickit. ChocoRobo is connected to a Google AIY Vision
# that sends data serially. Google AIY Vision sends the mid X coordinate
# of the detected face along with the size of the bounding box around the
# face. This code then adjust the left and right motor speeds to move
# the robot towards the direction of the face. Also, the NeoPixels on the
# CPX light up in the direction of the face.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
""" ChocoRobo - Autonomous Chocolate Delivery Robot """
import board
import busio
import time
import ure
from adafruit_crickit import crickit
from adafruit_circuitplayground.express import cpx

# Settings for the NeoPixels
PIXEL_DIRECTION_COLOR = (0, 0x10, 0)  #green
PIXEL_OFF_COLOR = (0, 0, 0)  #black
PIXEL_BRIGHTNESS = 0.2
PIXEL_DEFAULT_DIRECTION_INDEX = 2

# Time in seconds to allow FaceBot to keep moving after the last time received data
# Lower if overturning, but too low makes for a twitchy robot
MAX_DATA_IN_TIME_MARGIN = 0.18

# Time in seconds to start scanning around for faces when no data received
IDLE_TIME_SCAN_START = 10
IDLE_TIME_SCAN_END = 30
# Cannot continously rotate due to video being blurry and the Google AIY Vision not able to pick up faces.
# Only rotating a small amount of time then pausing. Pause up to start time, then rotates till end time.
SCAN_INCREMENT_START_TIME = 1.3
SCAN_INCREMENT_END_TIME = 1.5

# Base speeds for the motors. Not all motors are the same so may need to tweak where they rotate at the same starting speed.
MOTOR_BASE_SPEED_RIGHT = 0.5
MOTOR_BASE_SPEED_LEFT = 0.425

# I had to put in some correction for the motor speeds, I just guessed and trial and error till looked right.
# The left motor was slower than the right so needed more speed and vice versa for the right motor.
MOTOR_RIGHT_ERROR_CORRECTION = 1.05
MOTOR_LEFT_ERROR_CORRECTION = 0.90

# Constants to do proportional and derivative control of movement, you may need to tweak to get your bot to move smoothly.
Kp = 0.0003
Kd = 0.0005

# The center position. Google AIY Vision takes 1640 wide video.
CENTER_FACE_POSITION = 820

# Stops the robot from moving when the face exceeds this width so the bot doesn't run into the person.
MAX_FACE_WIDTH = 650

# For the proportional and derivative control of movement
errorCurrent = 0
errorLast = 0
motorSpeed = 0

# Initialze serial communication.
uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=10)

# Initialize the NeoPixels.
pixels = cpx.pixels
pixels.auto_write = False
pixels.brightness = PIXEL_BRIGHTNESS
currentPixelDirection = PIXEL_DEFAULT_DIRECTION_INDEX

# Initalize for the motors.
leftMotor = crickit.dc_motor_1
rightMotor = crickit.dc_motor_2
leftMotorSpeed = 0
rightMotorSpeed = 0

# Regular expression to help extract the data from the serial communication.
re = ure.compile('\D')

# And the last of initialization of variables.
lastDataTime = 0
elapsedTime = 0
facePosition = CENTER_FACE_POSITION
faceWidth = 0

def showPixelDirection(facePosition):
    """
    Lights the corresponding NeoPixel that points in the direction of of the parameter facePosition.
    """
    global currentPixelDirection
    pixels[currentPixelDirection] = PIXEL_OFF_COLOR
    
    if facePosition <= 328:
        currentPixelDirection = 4
    elif facePosition <= 656:
        currentPixelDirection = 3
    elif facePosition <= 984:
        currentPixelDirection = 2
    elif facePosition <= 1312:
        currentPixelDirection = 1
    else:
        currentPixelDirection = 0
        
    pixels[currentPixelDirection] = PIXEL_DIRECTION_COLOR
    pixels.show()

def boundMotorSpeed(speed):
    """
    Bound speed to the limits allowed by crickit motor.throttle
    """
    if speed < -1:
        return -1
    if speed > 1:
        return 1
    return speed

def resetMotorSpeeds():
    """
    Stop the motors.
    """
    leftMotor.throttle = 0
    rightMotor.throttle = 0
    errorCurrent = 0
    errorLast = 0

showPixelDirection(currentPixelDirection)

while True:
    data = uart.read(9)
    if data is not None and len(data) == 9:  # Data was received
        #print(data) # should be in form b'NNNN,NNNN' where NNNN is a leading zero padded 4 digit number, first NNNN is horizontal position of face, second NNNN is width of face
        data = re.split(str(data))  # splits to ['', '', 'NNNN', 'NNNN']
        facePosition = int(data[2])  
        faceWidth = int(data[3])
        lastDataTime = time.monotonic()
        #print("serial facePosition: {0}, faceWidth: {1}, lastDataTime: {2}".format(facePosition, faceWidth, lastDataTime))

    elapsedTime = time.monotonic() - lastDataTime
    #print('elapsedTime', elapsedTime)
    
    if IDLE_TIME_SCAN_START < elapsedTime % IDLE_TIME_SCAN_END and SCAN_INCREMENT_START_TIME < elapsedTime % SCAN_INCREMENT_END_TIME:
        # Have to only rotate the bot a little a time because the video is blurry during rotation and the Google AIY Vision
        # will not recognize a face
        leftMotor.throttle = MOTOR_BASE_SPEED_LEFT
        rightMotor.throttle = -MOTOR_BASE_SPEED_RIGHT
    elif elapsedTime > MAX_DATA_IN_TIME_MARGIN or faceWidth > MAX_FACE_WIDTH:
        resetMotorSpeeds()
    else:
        # Yay, we got face data. Compute the PD motor speeds to get the bot to the person smoothly.
        errorCurrent = CENTER_FACE_POSITION - facePosition
        motorSpeed = Kp * errorCurrent + Kd * (errorCurrent - errorLast)
        errorLast = errorCurrent
        
        leftMotorSpeed = MOTOR_BASE_SPEED_LEFT - (motorSpeed * MOTOR_LEFT_ERROR_CORRECTION)
        rightMotorSpeed = MOTOR_BASE_SPEED_RIGHT + (motorSpeed * MOTOR_RIGHT_ERROR_CORRECTION)
        
        leftMotor.throttle = boundMotorSpeed(leftMotorSpeed)
        rightMotor.throttle = boundMotorSpeed(rightMotorSpeed)
        print('left: {0}, right: {1}'.format(leftMotor.throttle, rightMotor.throttle))
        
    showPixelDirection(facePosition)