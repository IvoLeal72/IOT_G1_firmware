# display.py -- Test displays with ssd1306 controller
import time
from machine import I2C
from lib import ssd1306
import os
from time import sleep
import math
from lib import axp202
from machine import Pin

print("Running main")
print("Testing the display (SSD1306 controller)")

pmu=axp202.PMU()
pmu.setDC1Voltage(3300)
pmu.enablePower(axp202.AXP192_DCDC1)

# Test Display SSD1306 controller
# ESP32 Pin assignment
# i2c = I2C(0, mode=I2C.MASTER, pins=('G21','G22'), baudrate=100000)

# oled_width = 128
# oled_height = 64
# oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
# line=0
# for option in ('A....', 'B....','C....'):
#     oled.text(option, 0, line)
#     line+=8
# oled.text('A...',0,0,0,0)
# pdata=[0,] * 100
# for i in range(100):
#     pdata[i]=int((math.cos(i/5)+1)*20.0)
# oled.plot(1,pdata)
# oled.show()

test=Pin('G39', mode=Pin.IN)
value1=0
print(value1)
while True:
    var_test=test()
    if var_test!=value1:
        value1=var_test
        print(value1)
