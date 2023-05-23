
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
import utime
import pycom
from lib import settings
from lib.door_sensor import DoorSensor, DoorSensorEvent, MemoryDoorSensorEvent
from lib.tamper import Tamper
from lib.door_control import DoorControl
from lib.bt_server import BTServer
from lib import gps
from network import LoRa
from lib import axp202
import socket
import ubinascii
import struct
from lib.ubitstring import Bits


ds_events = []


def door_sensor_handler(open):
    ds_events.append(DoorSensorEvent(open))


def bt_cred_handler(valid):
    pass


def get_saved_events():
    saved_events=0
    try:
        saved_events = pycom.nvs_get('e_count')
    except ValueError:
        pass
    mem_events = []
    for i in range(saved_events):
        mem_events.append(MemoryDoorSensorEvent(pycom.nvs_get('e'+str(i))))
    return mem_events


def save_events():
    if not ds_events:
        return
    my_gps = gps.GPS()
    gps_uart = machine.UART(2, pins=(gps.GPS_TX_PIN, gps.GPS_RX_PIN))
    while True:
        line = gps_uart.readline()
        if line != None:
            my_gps.update(line)
            if my_gps.timestamp[0] != 0:
                break
            
    hours, minutes, seconds=my_gps.timestamp
    seconds=int(seconds)
    day, month, year=my_gps.date
    year+=2000

    ts = utime.mktime((year, month, day, hours, minutes, seconds, None, None))
    ts_ticks = my_gps.fix_time
    saved_events = pycom.nvs_get('e_count')
    if saved_events is None:
        saved_events = 0
    for event in ds_events:
        pycom.nvs_set('e'+str(saved_events), event.to_memory(ts, ts_ticks))


def shutdown():
    machine.pin_sleep_wakeup([settings.TAMPER_SENSOR, settings.DOOR_SENSOR, settings.BTN_PIN], mode=machine.WAKEUP_ANY_HIGH)
    machine.deepsleep()
    while True:
        print('UPS')


reason, detail = machine.wake_reason()



has_tamper = False
check_ds = False
enable_bt = False
send_events = False

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
# payload+=Bits(uint=0b000000001, length=9)
# payload+=Bits(uint=0b000000010, length=9)
# payload+=Bits(uint=0b001011, length=6)
# payload+=Bits(uint=0b001100, length=6)
# payload+=Bits(uint=0x200ff, length=19)
# payload+=Bits(uint=0x2000f, length=19)
# payload+=Bits(uint=0b011100000000000000000, length=21)
# payload+=Bits(uint=0b011000000000000000001, length=21)
# payload+=Bits(uint=0b111, length=3)

tamper_pin=Pin(settings.TAMPER_SENSOR, mode=Pin.IN)
ds_pin=Pin(settings.DOOR_SENSOR, mode=Pin.IN)
dc_pin=Pin(settings.DOOR_RELAY, mode=Pin.OUT)
dc_pin(1)
btn_pin=Pin(settings.BTN_PIN, mode=Pin.IN)

if reason == machine.PIN_WAKE:
    detail=[x.id() for x in detail]
    if tamper_pin.id() in detail:
        has_tamper = True
    if ds_pin.id() in detail:
        check_ds = True
    if btn_pin.id() in detail:
        enable_bt = True
if reason == machine.RTC_WAKE:
    send_events = True

if not send_events and machine.remaining_sleep_time() < 15*60*1000:
    send_events = True



tamper = Tamper(tamper_pin, has_tamper)
door_sensor = DoorSensor(ds_pin, door_sensor_handler, check_ds)
door_control = DoorControl(dc_pin)


lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
dev_addr = struct.unpack(">l", ubinascii.unhexlify('260B004D'))[0]
nwk_swkey = ubinascii.unhexlify('F049E015F2331D2A678C9C9C87DFD04B')
app_swkey = ubinascii.unhexlify('BDE7A8238E6354F64A8D10726E7A2B92')

if not tamper.active and not send_events and not enable_bt:
    save_events()
    shutdown()

if tamper.active:
    payload+=Bits(uint=0b001, length=3)
    payload+=Bits(uint=1, length=3)

if send_events:
    for event in get_saved_events():
        payload+=Bits(uint=0b011, length=3)
        payload+=Bits(uint=event.to_lora(), length=18)

lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

machine.sleep(1000)
print('after first sleep')

s.setblocking(True)
for i in range(2):
    print(i)
    s.send(payload.tobytes())
    machine.sleep(1000)

#print('done')
save_events()
shutdown()



