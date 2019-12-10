# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain
import time
import datetime

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# Relay
from gpiozero import LED
relay = LED(8)
relay.on()

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

def temperature(pin = 1):
    temperature_lpf = 0
    adjustment = 0
    if pin == 1:
        adjustment = 3
    elif pin == 0:
        adjustment = -0.1
    for i in range(1, 200):
        value = mcp.read_adc(pin)
        temperature = (value*3.3/1023-0.5)/0.01
        temperature_lpf = temperature_lpf * 0.97 + temperature * 0.03

    return round(temperature_lpf, 1) + adjustment

def recordTemperature():
    current_temperature = temperature(pin = 0)
    now = str(datetime.datetime.now())
    with open("/home/pi/webserver/log.log", "a+") as f:
        f.write(now + ", " + str(current_temperature) + "\n")
    with open("/home/pi/webserver/setpoint.txt", "r") as f:
        setpoint = f.read()
        setpoint = float(setpoint)
        print("Setpoint:", setpoint)
        print("Temperature:", current_temperature)
        if current_temperature > setpoint:
            relay.on()
            print("OFF")
        else:
            relay.off()
            print("ON")

if __name__ == "__main__":
    print("Pin 0:", temperature(pin = 0))
    print("Pin 1:", temperature(pin = 1))
