import re, shlex
import subprocess
import time

def readCPUTemp():
    cmd = "vcgencmd measure_temp"
    msg = subprocess.check_output(shlex.split(cmd)).decode("utf-8") 
    m = re.search(r'-?\d\.?\d*', msg)   # https://stackoverflow.com/a/49563120/3904031
    temp = 1000
    try:
        temp = float(m.group())
    except:
        pass
    return temp



ison = False
#fan = gpiozero.LED(4)

def managefan():
    while(True):
        cpuTemp = readCPUTemp()
        print(cpuTemp)
        if fan.value:
            print("Switching off")
            fan.off()
        else:
            print("Switching on")
            fan.on()
        time.sleep(2)

def average(inputList):
    return sum(inputList)/len(inputList)

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
io = 26
GPIO.setup(io, GPIO.OUT)
pwmOut = GPIO.PWM(io, 50)
pwmOut.start(0)
    
def fancontrol():
    import time
    # Remember, the fan is connected to an inverter (BJT)

    # so the duty cycle is the opposite ;)
    dutyCycle = 0
    minTemp = 48.
    maxTemp = 60.
    lastTemps = [0,0,0];
    while(1):
        time.sleep(1.0)
        cpuTemp = readCPUTemp()
        lastTemps.pop(0)
        lastTemps.append(cpuTemp)
        filterTemp = average(lastTemps)
        dutyCycle = (filterTemp - minTemp) / (maxTemp - minTemp) * 100
        if dutyCycle > 100:
            dutyCycle = 100
        if dutyCycle < 0:
            dutyCycle = 0
        print("CPU: %f" % (cpuTemp))
        print("Last avg: %f" % (filterTemp))
        print("dutyCycle: %f" % (dutyCycle))
        pwmOut.ChangeDutyCycle(dutyCycle)
try:
    fancontrol()
except: 
    print("Resetting Duty Cycle to full power")
    pwmOut.stop()
    GPIO.output(io, GPIO.LOW) 
    GPIO.cleanup() 
    exit()

