from signal import signal
import socket
import time
import os
import serial
import RPi.GPIO as GPIO
import threading
from adafruit_servokit import ServoKit

# I2C PCA9685 Servo Control Setup
try:
    kit = ServoKit(channels=16)
except:
    print("Unable to initialize PCA9685! Ensure proper wire connections")
    exit()

horizontalServo = kit.servo[1]
verticalServo = kit.servo[0]

homeHorizontalAngle = 85
homeVerticalAngle = 90

minVerticalAngle = 75
maxVerticalAngle = 180

minHorizontalAngle = 10
maxHorizontalAngle = 170

horizontalServo.angle = homeHorizontalAngle
verticalServo.angle = homeVerticalAngle

GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)

# this just sets nightvision to false
GPIO.output(16,True)
GPIO.output(26,True)

isNightVision = False

needToQueryBattery = False
batteryVoltage = 0

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
    try:
        ser.write(f"m {data}\n".encode())

    except:
        print("Error sending serial motor data. Attempting to proceed...")

def handleServoSignal(data):
    
    if(data[0] == 'u'):
        amt = int(data[2:])
        print("[Camera Control] Servo up " + str(amt))
        if(verticalServo.angle + amt <= maxVerticalAngle):
            verticalServo.angle += amt
        else:
            verticalServo.angle = maxVerticalAngle

    elif(data[0] == 'd'):
        amt = int(data[2:])
        print("[Camera Control] Servo down " + str(amt))
        if(verticalServo.angle - amt >= minVerticalAngle):
            verticalServo.angle -= amt
        else:
            verticalServo.angle = minVerticalAngle

    elif(data[0] == 'l'):
        amt = int(data[2:])
        print("[Camera Control] Servo left " + str(amt))
        if(horizontalServo.angle - amt >= minHorizontalAngle):
            horizontalServo.angle -= amt
        else:
            horizontalServo.angle = minHorizontalAngle

    elif(data[0] == 'r'):
        amt = int(data[2:])
        print("[Camera Control] Servo right " + str(amt))
        if(horizontalServo.angle + amt <= maxHorizontalAngle):
            horizontalServo.angle += amt
        else:
            horizontalServo.angle = maxHorizontalAngle

    elif(data[0] == 'c'):
        print("[Camera Control] Servo recenter")
        horizontalServo.angle = homeHorizontalAngle
        verticalServo.angle = homeVerticalAngle

def handleNightVisionSignal(connection, data):
    global isNightVision
    
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
        print("[Camera Control] Nightvision enabled")
    elif(data == "OFF"):
        GPIO.output(16,True)
        GPIO.output(26,True)
        isNightVision = False
        print("[Camera Control] Nightvision disabled")

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
    else:
        print('[UV4L] Received unknown client message: "%s"' % strData[2:])

def parseSerialData(data):
    global batteryVoltage
    if(data[0] == "b" and data[1] == " "):
        try:
            batteryVoltage = data[2:]
            print("[Battery Voltage Monitor] Read voltage:",batteryVoltage)
        except:
            print("[Battery Voltage Monitor] Unable to parse battery voltage! Perhaps data was corrupted?")
            print('\tExpected: b <voltage>')
            print('\tReceived:',data)
    else:
        print("[Serial] No command found for message:",data)

def queryArduinoBatteryVoltage():
    global needToQueryBattery
    while True:
        needToQueryBattery = True
        time.sleep(5)

batteryMonitorThread = threading.Thread(target=queryArduinoBatteryVoltage)

try:
    print("[Serial] Channel open on /dev/ttyS0")

    batteryMonitorThread.start()
    print("[Battery Voltage Monitor] Started monitor with interval of 5 seconds.")

    while True:
        print('[UV4L] Awaiting server connection...')
        connection, client_address = s.accept()
        connection.setblocking(0)
        print('[UV4L] Connecting to %s...' % client_address)
        try:
            print('[UV4L] Established connection with client', client_address)

            while True:
                # Data from the webserver
                try:
                    data = connection.recv(16)
                    #print('[UV4L] Received byte message: "%s"' % data)

                    time.sleep(0.01)

                    if data: # This is where all the good data flows
                        strData = str(data)
                        strData = strData[:-1]
                        print(strData[2:])
                        signalParse(connection, strData[2:])

                    else:
                        print('[UV4L] Disconnected from client', client_address)
                        break
                except BlockingIOError:
                    pass

                if needToQueryBattery:
                    ser.write("b\n".encode())
                    needToQueryBattery = False

                if ser.in_waiting > 0:
                    serialByteData = ser.readline()
                    serialDataString = serialByteData.decode('utf-8').rstrip()
                    parseSerialData(serialDataString)

        finally:
            # Clean up the connection
            connection.close()

finally:
    # Clean up the serial connection
    ser.close()
    print("Goodbye!")