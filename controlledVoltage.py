# This program combines the mcp4922.py and the digiPot.py
# to create a digital potentiometer with a higher resolution.

# csDigi: D2, csDAC: D5

import board
import busio
import digitalio
import time
import analogio
import mcp3422 as MCP

# Globals
top_dac_value = 0
bottom_dac_value = 0
wiper_value = 0


# Setup ADC
bits = 16 # 18, 16, 14, 12
channel = 2 # 1, 2
gain = 1 # 1, 2, 4, 8
 
mcp = MCP.MCP3422(bits,channel,gain)
mcp.setup()

# Setup DAC
offset = 0.0201

# Resistance
R3 = 10000

# Setup SPI
csDigi = digitalio.DigitalInOut(board.D2)
csDigi.direction = digitalio.Direction.OUTPUT
csDigi.value = True
csDAC = digitalio.DigitalInOut(board.D5)
csDAC.direction = digitalio.Direction.OUTPUT
csDAC.value = True
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

def spiSetup():
    while not spi.try_lock():
        pass
    spi.configure(baudrate=5000000, phase=0, polarity=0)
# Changes the wiper's value, 0-128
def setWiper1(number):
    csDigi.value = False
    spi.write(bytes([0x03,number]))
    csDigi.value = True

def setVoltage(pin,gain,number):
    pin_array = {0:0b0,1:0b1}
    gain_array = {1:0b1,2:0b0}
    command = pin_array[pin]<<7|0b0<<6|gain_array[gain]<<5|0b1<<4|(number>>8)
    command2 = number&0xff
    csDAC.value = False
    spi.write(bytes([command,command2]))
    csDAC.value = True

# Setup Sensor
wiper = analogio.AnalogIn(board.A2)
voltageA = analogio.AnalogIn(board.A3)
voltageB = analogio.AnalogIn(board.A4)

# Helper functions

def getDACV(dac):
    return dac/4096*3.3+offset
        
    
def averageVoltage():
    sumV = 0
    for x in range(5):
        sumV = sumV + mcp.read()/1000000
        time.sleep(0.05)
    return sumV/5

def getVoltage(pin):  # helper
    return (pin.value * 3.3) / 65536

def calculateResistance(k,V1,V2,supply,R):
    return (R/(supply/((V1-V2)*k+V2)-1))

def fastRupdate(k,V1,V2,supply,R,Vo):
    return (R/(supply/((V1-V2)*k+V2+Vo)-1))

# The autoRanger sets values    
def autoRanger(lowVal,highVal,limit):
    start = highVal - lowVal
    while start>limit:
        setVoltage(0,1,lowVal)
        setVoltage(1,1,highVal)
        setWiper1(64)
        if (getVoltage(wiper)/3.3)>0.5:
            return getVoltage(wiper)
            
def autoRange1():
    global wiper_value
    global top_dac_value
    global bottom_dac_value
    #print("Starting Scan")
    setVoltage(0,1,0)
    setVoltage(1,1,0) 
    setWiper1(127) 
    time.sleep(1)
    currentV = averageVoltage()
    time.sleep(1)
    while currentV>0:
        print("STOP")
        print(currentV)
        currentV = averageVoltage() # 62.5uV
        time.sleep(1)
    # every step is 3.3/4098
    #print(currentV)
    skip = int(-currentV/(3.3/4098)) # counts for the DAC
    #print(skip)
    #time.sleep(5)
    step = skip
    currentV = averageVoltage()
    while currentV<0:
        step = step+1
        #print(step)
        setVoltage(0,1,step)
        setVoltage(1,1,step)
        currentV = averageVoltage()
        #print(currentV)
    #print("DAC scan complete.")
    # Now we have the step value
    wiperStep = 0
    minus = 0
    setWiper1(0)
    while currentV>0:
        minus = minus + 1
        setVoltage(0,1,step-minus)# take one step back to negative
        currentV = averageVoltage()
        
        
    #print(currentV)
    wiperSkip = int(currentV/(3.3/(4096)))
    #wiperSkip = 65
    #setWiper1(wiperSkip)
    currentV = averageVoltage()
    #print(currentV)
    #time.sleep(5)
    
    wiperStep = 64

    
    if currentV>0:
        #wiperStep=wiperStep-wiperSkip
        while currentV>0:
            wiperStep=wiperStep-1
            if wiperStep == 128:
                print("Error!")
                return 0
            #print(wiperStep)
            setWiper1(wiperStep)
            currentV = averageVoltage()
            #print(currentV)
    else:
        #wiperStep=wiperStep-wiperSkip
        while currentV<0:
            wiperStep=wiperStep+1
            if wiperStep == -1:
                print("Error!")
                return 0
            #print(wiperStep)
            setWiper1(wiperStep)
            currentV = averageVoltage()
            #print(currentV)
    wiper_value = wiperStep 
    top_dac_value = step
    bottom_dac_value = step - minus
    #print(wiperStep)
    #print(step)
    #print(wiper_value) 
    #print(top_dac_value)
    #print("Wiper scan complete.")
    #data = mcp.read() 
    #print("{:.7f} V".format(data/1000000))    

    
# setup
top_dac_value = 10
bottom_dac_value = 10
wiper_value = 127
spiSetup()
setVoltage(0,1,top_dac_value)
#setVoltage(0,1,180)
setVoltage(1,1,bottom_dac_value) # channel B, gain 1, set to 2400/4096 counts
setWiper1(wiper_value)

# calibrating

while autoRange1()==0:() # do nothing
rValue = calculateResistance(wiper_value/128,getDACV(top_dac_value),getDACV(bottom_dac_value),3.3,9875)
print("{:.3f}".format(rValue))
print("%d %d %d" %(wiper_value,top_dac_value,bottom_dac_value))
#wiper_value = 0
#top_dac_value = 0
#bottom_dac_value = 0

    
    #print(getDACV(1))
    #data = mcp.read() 
    #print("{:.7f} V".format(data/1000000))
        
# Main loop
while True:
    for i in range(0,128):
        Vo = mcp.read()/1000000;
        R = fastRupdate(wiper_value/128,getDACV(top_dac_value),getDACV(bottom_dac_value),3.3,9875,Vo)-rValue;
        print("(%f,)"%(R));
        time.sleep(0.1);
        
        #stepWiper1(i)
        #print("Analog Voltage A: %f, Analog Voltage B : %f, Wiper: %f" % (getVoltage(voltageA), getVoltage(voltageB), getVoltage(wiper)))
        