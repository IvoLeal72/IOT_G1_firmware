from lib import axp202

axp = axp202.PMU()
axp.enableADC(axp202.AXP202_ADC1, axp202.AXP202_VBUS_VOL_ADC1)
axp.enableADC(axp202.AXP202_ADC1, axp202.AXP202_VBUS_CUR_ADC1)
axp.enableADC(axp202.AXP202_ADC1, axp202.AXP202_BATT_VOL_ADC1)
axp.enableADC(axp202.AXP202_ADC1, axp202.AXP202_BATT_CUR_ADC1)

from network import LoRa
import socket
import ubinascii
import struct

import machine

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# create an ABP authentication params
dev_addr = struct.unpack(">l", ubinascii.unhexlify('260B004D'))[0]
nwk_swkey = ubinascii.unhexlify('F049E015F2331D2A678C9C9C87DFD04B')
app_swkey = ubinascii.unhexlify('BDE7A8238E6354F64A8D10726E7A2B92')

# Uncomment for US915 / AU915 & Pygate
# for i in range(0,8):
#     lora.remove_channel(i)
# for i in range(16,65):
#     lora.remove_channel(i)
# for i in range(66,72):
#     lora.remove_channel(i)


# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
s.setblocking(True)

# send some data
while True:
    
    try:
        temp=(int((axp.getTemp()+10)*2)) & 0x7f
        volt=int(axp.getVbusVoltage()/10)-250 & 0x1ff
        to_send = (temp<<9 | volt) & 0xffff
        print(hex(to_send))
        s.send(to_send.to_bytes(2, 'big'))
    except Exception:
        print('reseting')
        machine.sleep(1)
        machine.reset()
    machine.sleep(10)

# make the socket non-blocking
# (because if there's no data received it will block forever...)
s.setblocking(False)

# get any data received (if any...)
data = s.recv(64)
print(data)