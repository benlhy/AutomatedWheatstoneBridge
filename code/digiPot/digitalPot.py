import board
import busio
import digitalio
import time
import analogio

# Setup SPI
cs = digitalio.DigitalInOut(board.D2)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

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

def stepWiper1(number):
    cs.value = False
    spi.write(bytes([0x03,number]))
    cs.value = True
    
    
    
    

# Setup Sensor
wiper = analogio.AnalogIn(board.A2)

def getVoltage(pin):  # helper
    return (pin.value * 3.3) / 65536


# setup
spiSetup()
test = bytearray(2)
test[0] = 0x32
test[1] = 0x0
print(test[0])
cs.value = False
spi.write(bytes([0x03,0xf]))
cs.value = True



    
# Main loop
while True:
    for i in range(0,128):
        stepWiper1(i)
        print("Analog Voltage: %f" % getVoltage(wiper))
        time.sleep(0.1)