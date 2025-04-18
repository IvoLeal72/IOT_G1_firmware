
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

# my_gps=gps.GPS()
# gps_uart=UART(2, pins=(gps.GPS_TX_PIN, gps.GPS_RX_PIN))
# while True:
#     line=gps_uart.readline()
#     if line!=None:
#         my_gps.update(line)
#         print(my_gps.latitude_string())
#         print(my_gps.longitude_string())
#         print(my_gps.compass_direction())

#from lib.door_sensor import DoorSensor
#ds=DoorSensor('G36', lambda x: print(x))

#from lib.tamper import Tamper
#tamp=Tamper('G39', lambda x: print(x))

#from lib.door_control import DoorControl
# dc=DoorControl('G0')

#from lib.bt_server import BTServer
#bt=BTServer('t1 g1', lambda x:print(x), ['12346'])

import machine
from machine import Pin
from lib import settings
from network import LoRa
from lib import axp202
import socket
import ubinascii
import struct
from lib.ubitstring import Bits

payload=Bits()
payload+=Bits(uint=settings.HW_VERSION, length=2)
payload+=Bits(uint=settings.API_VERSION, length=2)

axp = axp202.PMU()
axp.enableADC(axp202.AXP202_ADC1, axp202.AXP202_VBUS_VOL_ADC1)
axp.enableADC(axp202.AXP202_ADC1, axp202.AXP202_VBUS_CUR_ADC1)
axp.enableADC(axp202.AXP202_ADC1, axp202.AXP202_BATT_VOL_ADC1)
axp.enableADC(axp202.AXP202_ADC1, axp202.AXP202_BATT_CUR_ADC1)

voltage=axp.getBattVoltage()
if voltage==0:
    voltage=axp.getVbusVoltage()
if voltage>5000:
    voltage=5000
voltage_cod=int((voltage/10-250)/2) & 0x7f
payload+=Bits(uint=voltage_cod, length=7)




lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868, tx_retries=4)
dev_addr = struct.unpack(">l", ubinascii.unhexlify('260B004D'))[0]
nwk_swkey = ubinascii.unhexlify('F049E015F2331D2A678C9C9C87DFD04B')
app_swkey = ubinascii.unhexlify('BDE7A8238E6354F64A8D10726E7A2B92')

# if not tamper.active and not send_events and not enable_bt:
#     save_events()
#     shutdown()

# if tamper.active:
#     payload+=Bits(uint=0b001, length=3)
#     payload+=Bits(uint=1, length=3)

# if send_events:
#     for event in get_saved_events():
#         payload+=Bits(uint=0b011, length=3)
#         payload+=Bits(uint=event.to_lora(), length=18)

lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

payload+=Bits(uint=0b011, length=3)+Bits(uint=0b1, length=1)+Bits(uint=3661, length=17) # open reg
payload+=Bits(uint=0b011, length=3)+Bits(uint=0b0, length=1)+Bits(uint=3600, length=17) # open reg

payload+=Bits(uint=0b001, length=3)+Bits(uint=1, length=3) #hw alarms
payload+=Bits(uint=0b001, length=3)+Bits(uint=3, length=3) #hw alarms

payload+=Bits(uint=0b000, length=3)+Bits(uint=2, length=6) #sw alarms
payload+=Bits(uint=0b000, length=3)+Bits(uint=4, length=6) #sw alarms

payload+=Bits(uint=0b010, length=3)+Bits(uint=72, length=16) #open_request

payload+=Bits(uint=0b111, length=3)

machine.sleep(1000)
print('after first sleep')

s.setblocking(True)
for i in range(2):
    print(i)
    s.send(payload.tobytes())
    machine.sleep(1000)

led=Pin('G4', mode=Pin.OUT)
led(0)
#print('done')
while True:
    pass
#shutdown()



