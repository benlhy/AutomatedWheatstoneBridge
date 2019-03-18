import board
import busio
import digitalio
import time
import analogio

# Setup SPI
cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True
spi = busio.SPI(board.SCK, MOSI=board.MOSI)

def spiSetup():
    while not spi.try_lock():
        pass
    spi.configure(baudrate=5000000, phase=0, polarity=0)

def spiSendRecv(send):
    result = bytearray(4)
    cs.value = False
    spi.write(send)
    spi.readinto(result)
    cs.value = True
    return result

def setVoltage(pin,gain,number):
    pin_array = {0:0b0,1:0b1}
    gain_array = {1:0b1,2:0b0}
    command = pin_array[pin]<<7|0b0<<6|gain_array[gain]<<5|0b1<<4|(number>>8)
    command2 = number&0xff
    cs.value = False
    spi.write(bytes([command,command2]))
    cs.value = True
    
    
    
    

# Setup Sensor
voltageA = analogio.AnalogIn(board.A3)
voltageB = analogio.AnalogIn(board.A4)

def getVoltage(pin):  # helper
    return (pin.value * 3.3) / 65536


# setup
spiSetup()
setVoltage(0,1,2000)
setVoltage(1,1,2100) # channel B, gain 1, set to 2100/4096 counts

    
# Main loop
while True:
    print("Analog Voltage A: %f, Analog Voltage B : %f" % (getVoltage(voltageA), getVoltage(voltageB)))
    time.sleep(0.1)