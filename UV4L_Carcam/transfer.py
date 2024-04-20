from signal import signal
import socket
import time
import os
import serial
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit

# I2C PCA9685 Servo Control Setup
kit = ServoKit(channels=16)

horizontalServo = kit.servo[1]
verticalServo = kit.servo[0]

homeHorizontalAngle = 90
homeVerticalAngle = 90

minVerticalAngle = 85
maxVerticalAngle = 180

minHorizontalAngle = 0
maxHorizontalAngle = 180

horizontalServo.angle = homeHorizontalAngle
verticalServo.angle = homeVerticalAngle

GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)

# this just sets nightvision to false
GPIO.output(16,True)
GPIO.output(26,True)

isNightVision = False

batteryVoltage = 8.4

# Serial Communication Control Setup
ser = serial.Serial('/dev/ttyS0',9600,timeout=1)
ser.reset_input_buffer()

# Network Setup
socket_path = '/tmp/uv4l.socket'

try:
    os.unlink(socket_path)
except OSError:
    if os.path.exists(socket_path):
        raise

s = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)


print('socket_path: %s' % socket_path)
s.bind(socket_path)
s.listen(1)

def handleMotorSignal(data):
    #100
    #50

    data = data.split()
    xData = int(data[0]) + 100
    yData = int(data[1]) + 100

    print("sending x as " + str(xData) + " and y as " + str(yData))

    try:
        ser.write(b'x')
        ser.write(xData.to_bytes(1,'big'))
        ser.write(yData.to_bytes(1,'big'))
    except:
        print("Negative value error. Attempting to proceed...")

    # If we want to write something back, e.g. battery voltage, we can go in the while True loop and do
    # line = ser.readline().decode('utf-8').rstrip()
    # and then we can call signalParse using line as the data input. Just use an identifying letter at the start, like
    # b'p 76'
    # where p indicates power and the 76 would mean 76%.

def handleServoSignal(data):
    
    if(data[0] == 'u'):
        amt = int(data[2:])
        print("Servo up " + str(amt))
        if(verticalServo.angle + amt <= maxVerticalAngle):
            verticalServo.angle += amt
        else:
            verticalServo.angle = maxVerticalAngle

    elif(data[0] == 'd'):
        amt = int(data[2:])
        print("Servo down " + str(amt))
        if(verticalServo.angle - amt >= minVerticalAngle):
            verticalServo.angle -= amt
        else:
            verticalServo.angle = minVerticalAngle

    elif(data[0] == 'l'):
        amt = int(data[2:])
        print("Servo left " + str(amt))
        if(horizontalServo.angle - amt >= minHorizontalAngle):
            horizontalServo.angle -= amt
        else:
            horizontalServo.angle = minHorizontalAngle

    elif(data[0] == 'r'):
        amt = int(data[2:])
        print("Servo right " + str(amt))
        if(horizontalServo.angle + amt <= maxHorizontalAngle):
            horizontalServo.angle += amt
        else:
            horizontalServo.angle = maxHorizontalAngle

    elif(data[0] == 'c'):
        print("Servo recenter")
        horizontalServo.angle = homeHorizontalAngle
        verticalServo.angle = homeVerticalAngle


def handleNightVisionSignal(connection, data):
    global isNightVision
    print(data)
    if(data == "QUERY"):
        if(isNightVision == True):
            tmpString = "NVSTATE ON"
            connection.sendall(tmpString.encode('utf-8'))
        else:
            tmpString = "NVSTATE OFF"
            connection.sendall(tmpString.encode('utf-8'))
    elif(data == "ON"):
        GPIO.output(16,False)
        GPIO.output(26,False)
        isNightVision = True
    elif(data == "OFF"):
        GPIO.output(16,True)
        GPIO.output(26,True)
        isNightVision = False

def handleBatterySignal(connection, data):
    global batteryVoltage
    if(data == "QUERY"):
        tmpString = "BATSTATE " + str(batteryVoltage)
        connection.sendall(tmpString.encode('utf-8'))

def signalParse(connection, data):
    if(data[0] == 'm'):
        handleMotorSignal(data[2:])
    elif(data[0] == 's'):
        handleServoSignal(data[2:])
    elif(data[0] == 'n'):
        handleNightVisionSignal(connection, data[2:])
    elif(data[0] == 'b'):
        handleBatterySignal(connection, data[2:])
        

while True:
    print('awaiting connection...')
    connection, client_address = s.accept()
    print('client_address %s' % client_address)
    try:
        print('established connection with', client_address)

        while True:
            # Data from the webserver
            data = connection.recv(16)
            print('received message "%s"' % data)

            time.sleep(0.01)

            if data: # This is where all the good data flows
                #print('echo data to client')
                #connection.sendall(data)
                strData = str(data)
                strData = strData[:-1]
                print("strData: " + strData)
                signalParse(connection, strData[2:])

            else:
                print('no more data from', client_address)
                break

            # Data from the serial connection
            #data = ser.readline().decode('utf-8').rstrip()

            #if(data != b''):
            #    strData = str(data)
            #    strData = strData[:-1]
            #    signalParse(strData[2:])

    finally:
        # Clean up the connection
        connection.close()

